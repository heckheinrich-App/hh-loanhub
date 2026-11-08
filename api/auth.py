"""
HH LOANHUB / HH Cash Solutions - Authentication API
Phase 1: Registration, Login, Session Management & Password Controls
"""

import re
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from core.database import (
    get_db_connection,
    hash_password,
    verify_password,
    generate_account_number,
    trigger_auto_backup
)
from core.security import create_session_token, get_current_user_from_token

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# ------------------------------------------------------------------------------
# Request & Response Schemas
# ------------------------------------------------------------------------------
class RegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., min_length=8, max_length=20)
    id_number: str = Field("", max_length=30)
    address: str = Field("", max_length=200)
    guarantor_name: str = Field("", max_length=100)
    guarantor_phone: str = Field("", max_length=20)
    password: str = Field(..., min_length=4)


class LoginRequest(BaseModel):
    phone: str
    password: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=4)


def clean_phone(phone: str) -> str:
    """Normalizes phone string by stripping spaces, hyphens, and parentheses."""
    return re.sub(r"[^\d+]", "", phone.strip())


# ------------------------------------------------------------------------------
# Endpoints
# ------------------------------------------------------------------------------
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(req: RegisterRequest):
    """Registers a new borrower, assigns an account number, and triggers auto-backup."""
    phone = clean_phone(req.phone)
    if not phone:
        raise HTTPException(status_code=400, detail="Valid phone number is required.")

    conn = get_db_connection()
    try:
        # Check if phone already registered
        existing = conn.execute("SELECT id FROM users WHERE phone = ?", (phone,)).fetchone()
        if existing:
            raise HTTPException(status_code=400, detail="This phone number is already registered. Please log in.")

        account_number = generate_account_number()
        pw_hash, salt = hash_password(req.password)
        now_iso = datetime.now(timezone.utc).isoformat()

        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO users (
            account_number, full_name, phone, id_number, address,
            guarantor_name, guarantor_phone, password_hash, salt, role, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            account_number, req.full_name.strip(), phone, req.id_number.strip(),
            req.address.strip(), req.guarantor_name.strip(), clean_phone(req.guarantor_phone),
            pw_hash, salt, "client", now_iso
        ))
        user_id = cursor.lastrowid

        # Insert welcome notification
        cursor.execute("""
        INSERT INTO notifications (user_id, title, message, type, is_read, created_at)
        VALUES (?, ?, ?, 'info', 0, ?)
        """, (
            user_id,
            "Welcome to HH Cash Solutions!",
            f"Your account {account_number} is now active. You can now apply for loans up to R20,000.",
            now_iso
        ))

        conn.commit()
    finally:
        conn.close()

    # Trigger automated Google Drive backup on new user registration
    try:
        trigger_auto_backup()
    except Exception as e:
        print(f"[REGISTER WARNING] Auto-backup notice: {e}")

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
    """Authenticates borrower or admin, returning a session bearer token."""
    phone = clean_phone(req.phone)
    conn = get_db_connection()
    try:
        user = conn.execute("SELECT * FROM users WHERE phone = ?", (phone,)).fetchone()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect phone number or password."
            )

        if not verify_password(req.password, user["password_hash"], user["salt"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect phone number or password."
            )

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
                "role": user["role"],
                "id_number": user["id_number"] or "",
                "address": user["address"] or ""
            }
        }
    finally:
        conn.close()


@router.get("/me")
def get_current_user_profile(user: dict = Depends(get_current_user_from_token)):
    """Returns the authenticated profile, active loan status, and notification counts."""
    conn = get_db_connection()
    try:
        user_id = user["id"]

        # Calculate active loan balance
        active_loans = conn.execute("""
            SELECT * FROM loans
            WHERE user_id = ? AND status IN ('approved', 'active')
            ORDER BY id DESC
        """, (user_id,)).fetchall()

        total_active_balance = sum(float(l["total_repayable"]) for l in active_loans)
        unread_notifications = conn.execute("""
            SELECT COUNT(*) AS cnt FROM notifications
            WHERE user_id = ? AND is_read = 0
        """, (user_id,)).fetchone()["cnt"]

        # Latest loan
        latest_loan = conn.execute("""
            SELECT * FROM loans WHERE user_id = ? ORDER BY id DESC LIMIT 1
        """, (user_id,)).fetchone()

        return {
            "user": {
                "id": user["id"],
                "account_number": user["account_number"],
                "full_name": user["full_name"],
                "phone": user["phone"],
                "role": user["role"],
                "id_number": user.get("id_number") or "",
                "address": user.get("address") or "",
                "guarantor_name": user.get("guarantor_name") or "",
                "guarantor_phone": user.get("guarantor_phone") or ""
            },
            "active_balance": total_active_balance,
            "active_loans_count": len(active_loans),
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
        conn.execute("""
            UPDATE users SET password_hash = ?, salt = ? WHERE id = ?
        """, (new_hash, new_salt, user["id"]))
        conn.commit()
    finally:
        conn.close()

    return {"status": "success", "message": "Password updated successfully!"}


@router.get("/support-info")
def get_support_info():
    """Provides official WhatsApp and phone contact info for support and password resets."""
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
