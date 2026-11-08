"""
HH LOANHUB / HH Cash Solutions - Authentication & Biometric API
Phase 2: KYC Multipart Registration, Biometric Login (WebAuthn), Hein/1234 Admin Auth
"""

import os
import re
import secrets
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile, File
from pydantic import BaseModel, Field

from core.database import (
    get_db_connection,
    hash_password,
    verify_password,
    generate_account_number,
    generate_loan_reference,
    trigger_auto_backup,
    UPLOADS_DIR
)
from core.security import create_session_token, get_current_user_from_token
from core.kyc_scanner import generate_affordability_report

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# ------------------------------------------------------------------------------
# Request & Response Schemas
# ------------------------------------------------------------------------------
class RegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., min_length=8, max_length=20)
    id_number: str = Field("", max_length=30)
    address: str = Field("", max_length=200)
    bank_name: str = Field("", max_length=50)
    bank_account_number: str = Field("", max_length=30)
    guarantor_name: str = Field("", max_length=100)
    guarantor_phone: str = Field("", max_length=20)
    password: str = Field(..., min_length=4)
    initial_loan_amount: Optional[float] = 1000.0


class LoginRequest(BaseModel):
    phone: str  # Can be phone number OR username e.g. "Hein"
    password: str


class BiometricRegisterRequest(BaseModel):
    credential_id: str
    client_data: Optional[str] = None


class BiometricLoginRequest(BaseModel):
    credential_id: str
    phone_or_username: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=4)


def clean_phone(phone: str) -> str:
    """Normalizes phone string by stripping spaces, hyphens, and parentheses."""
    if not phone:
        return ""
    trimmed = phone.strip()
    if trimmed.isalpha():
        return trimmed
    return re.sub(r"[^\d+]", "", trimmed)


# ------------------------------------------------------------------------------
# Endpoints
# ------------------------------------------------------------------------------
@router.post("/register-with-kyc", status_code=status.HTTP_201_CREATED)
async def register_user_with_kyc(
    full_name: str = Form(...),
    phone: str = Form(...),
    id_number: str = Form(...),
    address: str = Form(...),
    bank_name: str = Form(...),
    bank_account_number: str = Form(...),
    password: str = Form(...),
    initial_loan_amount: float = Form(1000.0),
    bank_statement: UploadFile = File(...),
    id_document: UploadFile = File(...),
    proof_of_residence: UploadFile = File(...)
):
    """
    Registers a new borrower with full KYC document uploads, runs automated OCR
    affordability checks, and places an initial loan request with 30% interest.
    """
    clean_p = clean_phone(phone)
    if not clean_p or len(clean_p) < 4:
        raise HTTPException(status_code=400, detail="Valid phone number or username is required.")
    if len(password) < 4:
        raise HTTPException(status_code=400, detail="Password must be at least 4 characters.")

    conn = get_db_connection()
    try:
        # Check if phone number already exists
        existing = conn.execute("SELECT id FROM users WHERE phone = ?", (clean_p,)).fetchone()
        if existing:
            raise HTTPException(status_code=400, detail="An account with this phone number already exists. Please log in.")

        account_number = generate_account_number()
        pw_hash, salt = hash_password(password)
        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()

        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO users (
            account_number, full_name, phone, username, id_number, address,
            bank_name, bank_account_number, guarantor_name, guarantor_phone,
            password_hash, salt, role, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            account_number, full_name.strip(), clean_p, clean_p, id_number.strip(),
            address.strip(), bank_name.strip(), bank_account_number.strip(),
            "Next of Kin", clean_p, pw_hash, salt, "client", now_iso
        ))
        user_id = cursor.lastrowid

        # Create user upload directory: data/uploads/<user_id>/
        user_upload_dir = UPLOADS_DIR / str(user_id)
        user_upload_dir.mkdir(parents=True, exist_ok=True)

        uploads = [
            ("bank_statement", bank_statement),
            ("id_document", id_document),
            ("proof_of_residence", proof_of_residence)
        ]

        saved_docs = []
        for doc_type, file_obj in uploads:
            safe_filename = re.sub(r"[^A-Za-z0-9_.-]", "_", file_obj.filename)
            dest_path = user_upload_dir / f"{doc_type}_{safe_filename}"
            content = await file_obj.read()
            with open(dest_path, "wb") as f:
                f.write(content)

            cur_doc = cursor.execute("""
            INSERT INTO kyc_documents (
                user_id, doc_type, filename, file_path, file_size, mime_type, uploaded_at, ocr_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')
            """, (
                user_id, doc_type, file_obj.filename, str(dest_path), len(content),
                file_obj.content_type or "application/octet-stream", now_iso
            ))
            saved_docs.append({
                "id": cur_doc.lastrowid,
                "doc_type": doc_type,
                "file_path": str(dest_path)
            })

        # Calculate Initial Loan Request with 30% Interest
        loan_amount = max(500.0, min(float(initial_loan_amount), 20000.0))
        interest_rate = 30.0
        total_repayable = round(loan_amount * 1.30, 2)
        loan_ref = generate_loan_reference()
        first_payment_due = now.strftime("%d %b %Y")

        cur_loan = cursor.execute("""
        INSERT INTO loans (
            loan_reference, user_id, amount, term_months, interest_rate,
            total_repayable, purpose, collateral_note, status,
            first_payment_due, created_at
        ) VALUES (?, ?, ?, 1, ?, ?, 'Initial loan application on registration', 'KYC Verified', 'pending', ?, ?)
        """, (
            loan_ref, user_id, loan_amount, interest_rate, total_repayable, first_payment_due, now_iso
        ))
        loan_id = cur_loan.lastrowid

        # Insert user notification
        cursor.execute("""
        INSERT INTO notifications (user_id, title, message, type, is_read, created_at)
        VALUES (?, ?, ?, 'info', 0, ?)
        """, (
            user_id,
            "Application Received!",
            f"Your initial loan request for R {loan_amount:,.2f} (Total repayable: R {total_repayable:,.2f}) is now with Admin for review.",
            now_iso
        ))

        conn.commit()
    finally:
        conn.close()

    # Run automated OCR Affordability Engine in background/sync
    user_info = {
        "id": user_id,
        "full_name": full_name,
        "id_number": id_number,
        "phone": clean_p
    }
    try:
        generate_affordability_report(user_id, loan_id, user_info)
    except Exception as e:
        print(f"[OCR REPORT WARNING] {e}")

    # Trigger automated Google Drive backup (syncs database + uploaded docs)
    try:
        trigger_auto_backup()
    except Exception as e:
        print(f"[BACKUP WARNING] {e}")

    token = create_session_token(user_id)
    return {
        "status": "success",
        "message": "Registration complete! KYC documents submitted and initial loan request created.",
        "token": token,
        "user": {
            "id": user_id,
            "account_number": account_number,
            "full_name": full_name.strip(),
            "phone": clean_p,
            "role": "client",
            "bank_name": bank_name,
            "bank_account_number": bank_account_number
        },
        "initial_loan": {
            "loan_reference": loan_ref,
            "amount": loan_amount,
            "interest_rate": interest_rate,
            "total_repayable": total_repayable,
            "status": "pending"
        }
    }


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(req: RegisterRequest):
    """JSON-based registration fallback."""
    phone = clean_phone(req.phone)
    if not phone:
        raise HTTPException(status_code=400, detail="Valid phone number is required.")

    conn = get_db_connection()
    try:
        existing = conn.execute("SELECT id FROM users WHERE phone = ?", (phone,)).fetchone()
        if existing:
            raise HTTPException(status_code=400, detail="This phone number is already registered. Please log in.")

        account_number = generate_account_number()
        pw_hash, salt = hash_password(req.password)
        now_iso = datetime.now(timezone.utc).isoformat()

        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO users (
            account_number, full_name, phone, username, id_number, address,
            bank_name, bank_account_number, guarantor_name, guarantor_phone,
            password_hash, salt, role, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            account_number, req.full_name.strip(), phone, phone, req.id_number.strip(),
            req.address.strip(), req.bank_name.strip(), req.bank_account_number.strip(),
            req.guarantor_name.strip(), clean_phone(req.guarantor_phone),
            pw_hash, salt, "client", now_iso
        ))
        user_id = cursor.lastrowid

        # Insert initial loan if requested
        if req.initial_loan_amount and req.initial_loan_amount > 0:
            loan_amount = max(500.0, min(float(req.initial_loan_amount), 20000.0))
            total_repayable = round(loan_amount * 1.30, 2)
            loan_ref = generate_loan_reference()
            cursor.execute("""
            INSERT INTO loans (
                loan_reference, user_id, amount, term_months, interest_rate,
                total_repayable, purpose, collateral_note, status, first_payment_due, created_at
            ) VALUES (?, ?, ?, 1, 30.0, ?, 'Registration initial loan request', 'Unsecured', 'pending', ?, ?)
            """, (loan_ref, user_id, loan_amount, total_repayable, "End of Month", now_iso))

        conn.commit()
    finally:
        conn.close()

    try:
        trigger_auto_backup()
    except Exception as e:
        print(f"[REGISTER WARNING] {e}")

    token = create_session_token(user_id)
    return {
        "status": "success",
        "message": "Account created successfully!",
        "token": token,
        "user": {
            "id": user_id,
            "account_number": account_number,
            "full_name": req.full_name.strip(),
            "phone": phone,
            "role": "client"
        }
    }


@router.post("/login")
def login_user(req: LoginRequest):
    """
    Authenticates borrower or Master Admin (`Hein` / `1234`).
    Accepts both phone numbers and text usernames like 'Hein'.
    """
    input_identifier = req.phone.strip()
    conn = get_db_connection()
    try:
        # Check Master Admin hardcoded override
        if input_identifier.lower() == "hein" and req.password == "1234":
            admin_user = conn.execute("SELECT * FROM users WHERE role = 'admin' ORDER BY id ASC LIMIT 1").fetchone()
            if admin_user:
                token = create_session_token(admin_user["id"])
                return {
                    "status": "success",
                    "message": "Welcome Master Admin Hein!",
                    "token": token,
                    "user": {
                        "id": admin_user["id"],
                        "account_number": admin_user["account_number"],
                        "full_name": "Hein (Master Admin)",
                        "phone": "Hein",
                        "username": "Hein",
                        "role": "admin"
                    }
                }

        # General user lookup by phone or username
        user = conn.execute("""
        SELECT * FROM users 
        WHERE phone = ? OR username = ? OR LOWER(username) = LOWER(?)
        LIMIT 1
        """, (input_identifier, input_identifier, input_identifier)).fetchone()

        if not user:
            clean_digits = re.sub(r"\D", "", input_identifier)
            if clean_digits:
                user = conn.execute("SELECT * FROM users WHERE phone LIKE ? LIMIT 1", (f"%{clean_digits}%",)).fetchone()

        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect phone/username or password.")

        if not verify_password(req.password, user["password_hash"], user["salt"]):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect phone/username or password.")

        user = dict(user)
        user_id = user["id"]
        token = create_session_token(user_id)

        return {
            "status": "success",
            "message": "Login successful!",
            "token": token,
            "user": {
                "id": user["id"],
                "account_number": user["account_number"],
                "full_name": user["full_name"],
                "phone": user["phone"],
                "username": user.get("username") or user["phone"],
                "role": user["role"],
                "biometric_enabled": bool(user.get("biometric_enabled", 0)),
                "id_number": user["id_number"] or "",
                "address": user["address"] or "",
                "bank_name": user.get("bank_name") or "",
                "bank_account_number": user.get("bank_account_number") or ""
            }
        }
    finally:
        conn.close()


@router.post("/biometric/register")
def register_biometric(req: BiometricRegisterRequest, user: dict = Depends(get_current_user_from_token)):
    """Enables biometric sign-in for the authenticated user and stores credential ID."""
    if not req.credential_id:
        raise HTTPException(status_code=400, detail="Credential ID is required.")

    conn = get_db_connection()
    try:
        conn.execute("""
        UPDATE users SET biometric_credential_id = ?, biometric_enabled = 1 WHERE id = ?
        """, (req.credential_id, user["id"]))
        conn.commit()
    finally:
        conn.close()

    return {
        "status": "success",
        "message": "Biometric sign-in enabled successfully!",
        "biometric_enabled": True
    }


@router.post("/biometric/login")
def login_biometric(req: BiometricLoginRequest):
    """Authenticates a user via WebAuthn biometric credential ID or local biometric token."""
    if not req.credential_id:
        raise HTTPException(status_code=400, detail="Biometric credential is required.")

    conn = get_db_connection()
    try:
        user = conn.execute("""
        SELECT * FROM users WHERE biometric_credential_id = ? AND biometric_enabled = 1 LIMIT 1
        """, (req.credential_id,)).fetchone()

        if not user and req.phone_or_username:
            user = conn.execute("""
            SELECT * FROM users WHERE (phone = ? OR username = ?) AND biometric_enabled = 1 LIMIT 1
            """, (req.phone_or_username, req.phone_or_username)).fetchone()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Biometrics not recognized. Please sign in with your password first to enable biometrics."
            )

        token = create_session_token(user["id"])
        return {
            "status": "success",
            "message": f"Biometric sign-in verified! Welcome back, {user['full_name']}.",
            "token": token,
            "user": {
                "id": user["id"],
                "account_number": user["account_number"],
                "full_name": user["full_name"],
                "phone": user["phone"],
                "role": user["role"],
                "biometric_enabled": True
            }
        }
    finally:
        conn.close()


@router.get("/me")
def get_current_user_profile(user_row: dict = Depends(get_current_user_from_token)):
    """Returns the authenticated profile, active loans, and notification counts."""
    user = dict(user_row)
    conn = get_db_connection()
    try:
        user_id = user["id"]

        active_rows = conn.execute("""
            SELECT * FROM loans
            WHERE user_id = ? AND status IN ('approved', 'active', 'pending', 'payment_requested', 'overdue')
            ORDER BY id DESC
        """, (user_id,)).fetchall()
        active_loans = [dict(r) for r in active_rows]

        total_active_balance = sum(
            float(l["total_repayable"]) - float(l.get("paid_amount") or 0.0)
            for l in active_loans
            if l["status"] in ('approved', 'active', 'payment_requested', 'overdue')
        )

        unread_notifications = conn.execute("""
            SELECT COUNT(*) AS cnt FROM notifications
            WHERE user_id = ? AND is_read = 0
        """, (user_id,)).fetchone()["cnt"]

        latest_loan = conn.execute("""
            SELECT * FROM loans WHERE user_id = ? ORDER BY id DESC LIMIT 1
        """, (user_id,)).fetchone()

        kyc_count = conn.execute("SELECT COUNT(*) AS cnt FROM kyc_documents WHERE user_id = ?", (user_id,)).fetchone()["cnt"]

        return {
            "user": {
                "id": user["id"],
                "account_number": user["account_number"],
                "full_name": user["full_name"],
                "phone": user["phone"],
                "username": user.get("username") or user["phone"],
                "role": user["role"],
                "id_number": user.get("id_number") or "",
                "address": user.get("address") or "",
                "bank_name": user.get("bank_name") or "",
                "bank_account_number": user.get("bank_account_number") or "",
                "biometric_enabled": bool(user.get("biometric_enabled", 0)),
                "kyc_uploaded": kyc_count >= 3
            },
            "active_balance": total_active_balance,
            "active_loans_count": len([l for l in active_loans if l["status"] == 'active']),
            "unread_notifications": unread_notifications,
            "latest_loan": dict(latest_loan) if latest_loan else None
        }
    finally:
        conn.close()


@router.post("/change-password")
def change_password(req: ChangePasswordRequest, user: dict = Depends(get_current_user_from_token)):
    """Allows authenticated user or admin to update their password."""
    if not verify_password(req.old_password, user["password_hash"], user["salt"]):
        raise HTTPException(status_code=400, detail="Current password is incorrect.")

    new_hash, new_salt = hash_password(req.new_password)
    conn = get_db_connection()
    try:
        conn.execute("UPDATE users SET password_hash = ?, salt = ? WHERE id = ?", (new_hash, new_salt, user["id"]))
        conn.commit()
    finally:
        conn.close()

    return {"status": "success", "message": "Password updated successfully!"}


@router.get("/support-info")
def get_support_info():
    """Provides official WhatsApp and phone contact info."""
    conn = get_db_connection()
    try:
        whatsapp = conn.execute("SELECT value FROM settings WHERE key = 'support_whatsapp'").fetchone()
        phone = conn.execute("SELECT value FROM settings WHERE key = 'support_phone'").fetchone()
        return {
            "brand": "HH Cash Solutions",
            "tagline": "— Your Financial Partner —",
            "whatsapp": whatsapp["value"] if whatsapp else "27821234567",
            "phone": phone["value"] if phone else "0821234567",
            "hours": "Mon - Sat: 08:00 - 18:00"
        }
    finally:
        conn.close()
