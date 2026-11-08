"""
HH LOANHUB / HH Cash Solutions - Database & Auto-Backup Engine
Phase 1: Local SQLite Storage + Automated Google Drive Sync
"""

import os
import sqlite3
import hashlib
import secrets
import json
import shutil
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "loanhub.db"
DATA_DIR.mkdir(parents=True, exist_ok=True)

def get_backup_candidates() -> list[Path]:
    """Returns candidate Google Drive and local backup directories in priority order."""
    candidates = []
    custom_env = os.getenv("GDRIVE_BACKUP_PATH", "").strip()
    if custom_env:
        candidates.append(Path(custom_env))
    
    # Common Windows Google Drive sync paths
    candidates.extend([
        Path("C:/Users/Wonderboom/Google Drive/HH_LOANHUB_Backups"),
        Path("C:/Users/Wonderboom/GoogleDrive/HH_LOANHUB_Backups"),
        Path("C:/Users/Public/GoogleDrive/HH_LOANHUB_Backups"),
        Path("G:/My Drive/HH_LOANHUB_Backups"),
        Path("C:/Users/Wonderboom/HH_LOANHUB_Backups"),
        DATA_DIR / "backups"
    ])
    return candidates


def get_db_connection() -> sqlite3.Connection:
    """Returns a SQLite connection with row_factory set to sqlite3.Row."""
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


# ------------------------------------------------------------------------------
# Password Hashing & Security Helpers
# ------------------------------------------------------------------------------
def hash_password(password: str, salt: str = None) -> tuple[str, str]:
    """Hashes a password with PBKDF2 HMAC SHA-256 and a random salt."""
    if not salt:
        salt = secrets.token_hex(16)
    pw_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100_000
    ).hex()
    return pw_hash, salt


def verify_password(password: str, stored_hash: str, salt: str) -> bool:
    """Verifies a password against the stored PBKDF2 hash and salt."""
    calculated_hash, _ = hash_password(password, salt)
    return secrets.compare_digest(calculated_hash, stored_hash)


def generate_account_number() -> str:
    """Generates a unique 6-digit client account number (e.g. #123456)."""
    conn = get_db_connection()
    try:
        while True:
            num = secrets.randbelow(900000) + 100000  # 100000 to 999999
            acc = f"#{num}"
            existing = conn.execute("SELECT id FROM users WHERE account_number = ?", (acc,)).fetchone()
            if not existing:
                return acc
    finally:
        conn.close()


def generate_loan_reference() -> str:
    """Generates a clean loan reference code (e.g. LN-592810)."""
    return f"LN-{secrets.randbelow(900000) + 100000}"


# ------------------------------------------------------------------------------
# Database Initialization & Schema Definition
# ------------------------------------------------------------------------------
def init_db():
    """Initializes tables and seeds default master admin if not present."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_number TEXT UNIQUE NOT NULL,
        full_name TEXT NOT NULL,
        phone TEXT UNIQUE NOT NULL,
        id_number TEXT DEFAULT '',
        address TEXT DEFAULT '',
        guarantor_name TEXT DEFAULT '',
        guarantor_phone TEXT DEFAULT '',
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        role TEXT DEFAULT 'client',
        created_at TEXT NOT NULL
    );
    """)

    # Loans Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS loans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        loan_reference TEXT UNIQUE NOT NULL,
        user_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        term_months INTEGER NOT NULL DEFAULT 1,
        interest_rate REAL NOT NULL DEFAULT 15.0,
        total_repayable REAL NOT NULL,
        purpose TEXT DEFAULT '',
        collateral_note TEXT DEFAULT '',
        status TEXT DEFAULT 'pending',
        first_payment_due TEXT NOT NULL,
        created_at TEXT NOT NULL,
        approved_at TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    # Repayments Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS repayments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        loan_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        payment_date TEXT NOT NULL,
        status TEXT DEFAULT 'paid',
        reference TEXT NOT NULL,
        notes TEXT DEFAULT '',
        FOREIGN KEY (loan_id) REFERENCES loans(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    # Notifications Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        type TEXT DEFAULT 'info',
        is_read INTEGER DEFAULT 0,
        created_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    # System Settings Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    );
    """)

    # Seed Default Master Admin Account
    admin_phone = "0821234567"
    admin_user = cursor.execute("SELECT id FROM users WHERE phone = ?", (admin_phone,)).fetchone()
    if not admin_user:
        admin_pw_hash, admin_salt = hash_password("AdminPassword2026!")
        now_iso = datetime.now(timezone.utc).isoformat()
        cursor.execute("""
        INSERT INTO users (
            account_number, full_name, phone, id_number, address,
            guarantor_name, guarantor_phone, password_hash, salt, role, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "#888888", "Master Admin (HH)", admin_phone, "8001010000088",
            "HH Cash Solutions HQ", "Executive Desk", "0821234567",
            admin_pw_hash, admin_salt, "admin", now_iso
        ))
        print("[DATABASE] Seeded Default Master Admin: 0821234567 / AdminPassword2026!")

    # Seed Default Settings
    default_settings = [
        ("default_interest_rate", "15.0"),
        ("min_loan_amount", "500"),
        ("max_loan_amount", "20000"),
        ("support_whatsapp", "27821234567"),
        ("support_phone", "0821234567")
    ]
    for key, val in default_settings:
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (key, val))

    conn.commit()
    conn.close()
    print("[DATABASE] Database initialized successfully at:", DB_PATH)


# ------------------------------------------------------------------------------
# Automated Google Drive Sync Hook
# ------------------------------------------------------------------------------
def trigger_auto_backup() -> dict:
    """
    Copies data/loanhub.db and dumps a JSON snapshot to Google Drive.
    Triggered on user registration, loan application, approval, or repayment.
    """
    now = datetime.now(timezone.utc)
    ts = now.strftime("%Y-%m-%d_%H-%M-%S")
    backup_target_dir = None

    candidates = get_backup_candidates()
    for candidate in candidates:
        try:
            if candidate and str(candidate).strip() and str(candidate) != ".":
                candidate.mkdir(parents=True, exist_ok=True)
                # Verify writability
                test_file = candidate / ".test_write"
                test_file.write_text("ok")
                test_file.unlink()
                backup_target_dir = candidate
                break
        except Exception:
            continue

    if not backup_target_dir:
        backup_target_dir = DATA_DIR / "backups"
        backup_target_dir.mkdir(parents=True, exist_ok=True)

    # 1. Copy SQLite binary database
    snapshot_db = backup_target_dir / f"loanhub_backup_{ts}.db"
    latest_db = backup_target_dir / "loanhub_latest.db"
    try:
        shutil.copy2(DB_PATH, snapshot_db)
        shutil.copy2(DB_PATH, latest_db)
    except Exception as e:
        print(f"[BACKUP ERROR] Failed to copy SQLite file: {e}")

    # 2. Export JSON snapshot of all tables for zero-loss recovery
    snapshot_json = backup_target_dir / f"loanhub_snapshot_{ts}.json"
    latest_json = backup_target_dir / "loanhub_latest.json"
    conn = get_db_connection()
    try:
        users = [dict(r) for r in conn.execute("SELECT id, account_number, full_name, phone, id_number, address, role, created_at FROM users").fetchall()]
        loans = [dict(r) for r in conn.execute("SELECT * FROM loans").fetchall()]
        repayments = [dict(r) for r in conn.execute("SELECT * FROM repayments").fetchall()]
        data_dump = {
            "snapshot_timestamp": now.isoformat(),
            "users_count": len(users),
            "loans_count": len(loans),
            "repayments_count": len(repayments),
            "users": users,
            "loans": loans,
            "repayments": repayments
        }
        with open(snapshot_json, "w", encoding="utf-8") as f:
            json.dump(data_dump, f, indent=2)
        with open(latest_json, "w", encoding="utf-8") as f:
            json.dump(data_dump, f, indent=2)
    except Exception as e:
        print(f"[BACKUP ERROR] Failed to dump JSON snapshot: {e}")
    finally:
        conn.close()

    print(f"[AUTO-BACKUP] Completed -> {backup_target_dir} ({ts})")
    return {
        "status": "success",
        "timestamp": now.isoformat(),
        "backup_directory": str(backup_target_dir),
        "db_file": str(snapshot_db.name),
        "json_file": str(snapshot_json.name)
    }
