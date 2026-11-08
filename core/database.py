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
UPLOADS_DIR = DATA_DIR / "uploads"
DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

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
# Database Initialization, Migrations & Schema Definition
# ------------------------------------------------------------------------------
def run_migrations(conn: sqlite3.Connection):
    """Dynamically applies schema migrations for Phase 2 without data loss."""
    cursor = conn.cursor()

    # 1. Users table migrations
    user_cols = {row["name"] for row in cursor.execute("PRAGMA table_info(users)").fetchall()}
    if "username" not in user_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN username TEXT DEFAULT ''")
    if "bank_name" not in user_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN bank_name TEXT DEFAULT ''")
    if "bank_account_number" not in user_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN bank_account_number TEXT DEFAULT ''")
    if "biometric_credential_id" not in user_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN biometric_credential_id TEXT DEFAULT ''")
    if "biometric_enabled" not in user_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN biometric_enabled INTEGER DEFAULT 0")

    # 2. Loans table migrations
    loan_cols = {row["name"] for row in cursor.execute("PRAGMA table_info(loans)").fetchall()}
    if "disbursed_at" not in loan_cols:
        cursor.execute("ALTER TABLE loans ADD COLUMN disbursed_at TEXT")
    if "month_end_deduction_date" not in loan_cols:
        cursor.execute("ALTER TABLE loans ADD COLUMN month_end_deduction_date TEXT")
    if "payment_requested" not in loan_cols:
        cursor.execute("ALTER TABLE loans ADD COLUMN payment_requested INTEGER DEFAULT 0")
    if "payment_requested_at" not in loan_cols:
        cursor.execute("ALTER TABLE loans ADD COLUMN payment_requested_at TEXT")
    if "payment_requested_notes" not in loan_cols:
        cursor.execute("ALTER TABLE loans ADD COLUMN payment_requested_notes TEXT DEFAULT ''")
    if "paid_amount" not in loan_cols:
        cursor.execute("ALTER TABLE loans ADD COLUMN paid_amount REAL DEFAULT 0.0")

    conn.commit()


def init_db():
    """Initializes tables, applies migrations, and seeds default Master Admin (Hein / 1234)."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_number TEXT UNIQUE NOT NULL,
        full_name TEXT NOT NULL,
        phone TEXT UNIQUE NOT NULL,
        username TEXT DEFAULT '',
        id_number TEXT DEFAULT '',
        address TEXT DEFAULT '',
        bank_name TEXT DEFAULT '',
        bank_account_number TEXT DEFAULT '',
        guarantor_name TEXT DEFAULT '',
        guarantor_phone TEXT DEFAULT '',
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        role TEXT DEFAULT 'client',
        biometric_credential_id TEXT DEFAULT '',
        biometric_enabled INTEGER DEFAULT 0,
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
        interest_rate REAL NOT NULL DEFAULT 30.0,
        total_repayable REAL NOT NULL,
        purpose TEXT DEFAULT '',
        collateral_note TEXT DEFAULT '',
        status TEXT DEFAULT 'pending',
        first_payment_due TEXT NOT NULL,
        disbursed_at TEXT,
        month_end_deduction_date TEXT,
        payment_requested INTEGER DEFAULT 0,
        payment_requested_at TEXT,
        payment_requested_notes TEXT DEFAULT '',
        paid_amount REAL DEFAULT 0.0,
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

    # KYC Documents Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS kyc_documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        doc_type TEXT NOT NULL,
        filename TEXT NOT NULL,
        file_path TEXT NOT NULL,
        file_size INTEGER NOT NULL,
        mime_type TEXT NOT NULL,
        uploaded_at TEXT NOT NULL,
        ocr_status TEXT DEFAULT 'pending',
        ocr_extracted_text TEXT DEFAULT '',
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    # Affordability Reports Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS affordability_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        loan_id INTEGER,
        identity_match_status TEXT DEFAULT 'NEEDS MANUAL REVIEW',
        identity_match_notes TEXT DEFAULT '',
        estimated_monthly_income REAL DEFAULT 0.0,
        estimated_monthly_expenses REAL DEFAULT 0.0,
        estimated_disposable_income REAL DEFAULT 0.0,
        max_recommended_loan REAL DEFAULT 0.0,
        admin_override_disposable REAL,
        admin_notes TEXT DEFAULT '',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
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

    # Run any missing column migrations
    run_migrations(conn)

    # Seed/Update Master Admin: Hein / 1234
    admin_pw_hash, admin_salt = hash_password("1234")
    now_iso = datetime.now(timezone.utc).isoformat()
    existing_admin = cursor.execute("SELECT id FROM users WHERE username = 'Hein' OR phone = 'Hein' OR account_number = '#888888'").fetchone()

    if existing_admin:
        cursor.execute("""
        UPDATE users SET 
            username = 'Hein',
            full_name = 'Hein (Master Admin)',
            phone = 'Hein',
            password_hash = ?,
            salt = ?,
            role = 'admin'
        WHERE id = ?
        """, (admin_pw_hash, admin_salt, existing_admin["id"]))
        print("[DATABASE] Updated Master Admin Account -> Username: Hein / Password: 1234")
    else:
        cursor.execute("""
        INSERT INTO users (
            account_number, full_name, phone, username, id_number, address,
            bank_name, bank_account_number, guarantor_name, guarantor_phone,
            password_hash, salt, role, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "#888888", "Hein (Master Admin)", "Hein", "Hein", "8001010000088",
            "HH Cash Solutions HQ", "Capitec Bank", "1000888888", "Executive Desk", "0821234567",
            admin_pw_hash, admin_salt, "admin", now_iso
        ))
        print("[DATABASE] Seeded Master Admin: Hein / 1234")

    # Seed Default Settings (30% interest rate as required)
    default_settings = [
        ("default_interest_rate", "30.0"),
        ("min_loan_amount", "500"),
        ("max_loan_amount", "20000"),
        ("support_whatsapp", "27821234567"),
        ("support_phone", "0821234567")
    ]
    for key, val in default_settings:
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, val))

    conn.commit()
    conn.close()
    print("[DATABASE] Database initialized successfully at:", DB_PATH)


# ------------------------------------------------------------------------------
# Automated Google Drive Sync Hook (Database + Uploaded KYC Documents)
# ------------------------------------------------------------------------------
def trigger_auto_backup() -> dict:
    """
    Copies data/loanhub.db, KYC uploaded documents, and dumps a full JSON snapshot to Google Drive.
    Triggered on registration, document upload, loan lifecycle changes, or repayment.
    """
    now = datetime.now(timezone.utc)
    ts = now.strftime("%Y-%m-%d_%H-%M-%S")
    backup_target_dir = None

    candidates = get_backup_candidates()
    for candidate in candidates:
        try:
            if candidate and str(candidate).strip() and str(candidate) != ".":
                candidate.mkdir(parents=True, exist_ok=True)
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

    # 2. Sync KYC uploaded documents folder to Google Drive
    backup_uploads_dir = backup_target_dir / "uploads"
    backup_uploads_dir.mkdir(parents=True, exist_ok=True)
    if UPLOADS_DIR.exists():
        try:
            for item in UPLOADS_DIR.rglob("*"):
                if item.is_file():
                    rel_path = item.relative_to(UPLOADS_DIR)
                    dest_file = backup_uploads_dir / rel_path
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, dest_file)
        except Exception as e:
            print(f"[BACKUP ERROR] Failed to sync KYC uploads: {e}")

    # 3. Export JSON snapshot of all tables for zero-loss recovery
    snapshot_json = backup_target_dir / f"loanhub_snapshot_{ts}.json"
    latest_json = backup_target_dir / "loanhub_latest.json"
    conn = get_db_connection()
    try:
        users = [dict(r) for r in conn.execute("SELECT id, account_number, full_name, phone, username, id_number, address, bank_name, bank_account_number, role, created_at FROM users").fetchall()]
        loans = [dict(r) for r in conn.execute("SELECT * FROM loans").fetchall()]
        repayments = [dict(r) for r in conn.execute("SELECT * FROM repayments").fetchall()]
        docs = [dict(r) for r in conn.execute("SELECT id, user_id, doc_type, filename, file_size, uploaded_at, ocr_status FROM kyc_documents").fetchall()]
        affordability = [dict(r) for r in conn.execute("SELECT * FROM affordability_reports").fetchall()]

        data_dump = {
            "snapshot_timestamp": now.isoformat(),
            "users_count": len(users),
            "loans_count": len(loans),
            "repayments_count": len(repayments),
            "kyc_docs_count": len(docs),
            "users": users,
            "loans": loans,
            "repayments": repayments,
            "kyc_documents": docs,
            "affordability_reports": affordability
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
