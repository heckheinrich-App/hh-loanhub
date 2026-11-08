"""
HH LOANHUB / HH Cash Solutions - Client Loan & Notification API
Phase 1: Loan Application Wizard, Repayment Schedules & Status
"""

from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from core.database import (
    get_db_connection,
    generate_loan_reference,
    trigger_auto_backup
)
from core.security import get_current_user_from_token

router = APIRouter(prefix="/api/loans", tags=["Loans"])


class LoanApplyRequest(BaseModel):
    amount: float = Field(..., ge=500, le=20000)
    term_months: int = Field(1, ge=1, le=12)
    purpose: str = Field("Personal", max_length=150)
    collateral_note: str = Field("", max_length=200)


@router.post("/apply", status_code=status.HTTP_201_CREATED)
def apply_for_loan(req: LoanApplyRequest, user: dict = Depends(get_current_user_from_token)):
    """Submits a new loan application, calculates interest, creates notification, and auto-backs up."""
    conn = get_db_connection()
    try:
        # Check if borrower already has an active pending or overdue loan
        existing_pending = conn.execute("""
            SELECT id FROM loans WHERE user_id = ? AND status = 'pending'
        """, (user["id"],)).fetchone()
        if existing_pending:
            raise HTTPException(
                status_code=400,
                detail="You already have a loan application pending approval. Please wait for our team to review."
            )

        # Get system default interest rate
        setting = conn.execute("SELECT value FROM settings WHERE key = 'default_interest_rate'").fetchone()
        rate = float(setting["value"]) if setting else 15.0

        # Calculation (flat interest per month)
        interest_amount = req.amount * (rate / 100.0) * req.term_months
        total_repayable = round(req.amount + interest_amount, 2)

        # First payment due date: exactly 30 days from now
        now = datetime.now(timezone.utc)
        due_date = (now + timedelta(days=30)).strftime("%d %b %Y")
        loan_ref = generate_loan_reference()
        now_iso = now.isoformat()

        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO loans (
            loan_reference, user_id, amount, term_months, interest_rate,
            total_repayable, purpose, collateral_note, status, first_payment_due, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?, ?)
        """, (
            loan_ref, user["id"], req.amount, req.term_months, rate,
            total_repayable, req.purpose, req.collateral_note, due_date, now_iso
        ))
        loan_id = cursor.lastrowid

        # Notification to borrower
        cursor.execute("""
        INSERT INTO notifications (user_id, title, message, type, is_read, created_at)
        VALUES (?, ?, ?, 'application', 0, ?)
        """, (
            user["id"],
            "Loan Application Received",
            f"Your application for R{req.amount:,.2f} ({loan_ref}) is being reviewed by our underwriting team.",
            now_iso
        ))

        conn.commit()
    finally:
        conn.close()

    # Trigger auto-backup hook
    try:
        trigger_auto_backup()
    except Exception as e:
        print(f"[LOAN APPLY WARNING] Auto-backup notice: {e}")

    return {
        "status": "success",
        "message": "Loan application submitted successfully!",
        "loan": {
            "id": loan_id,
            "reference": loan_ref,
            "amount": req.amount,
            "term_months": req.term_months,
            "interest_rate": rate,
            "interest_amount": interest_amount,
            "total_repayable": total_repayable,
            "first_payment_due": due_date,
            "status": "pending"
        }
    }


@router.get("/my")
def get_my_loans(user: dict = Depends(get_current_user_from_token)):
    """Returns all loans applied for or taken by the logged-in borrower."""
    conn = get_db_connection()
    try:
        loans = conn.execute("""
            SELECT * FROM loans WHERE user_id = ? ORDER BY id DESC
        """, (user["id"],)).fetchall()
        return [dict(l) for l in loans]
    finally:
        conn.close()


@router.get("/{loan_id}")
def get_loan_details(loan_id: int, user: dict = Depends(get_current_user_from_token)):
    """Returns loan details and associated repayment records."""
    conn = get_db_connection()
    try:
        # Client can only see their own loans; admin can see any
        if user.get("role") == "admin":
            loan = conn.execute("SELECT * FROM loans WHERE id = ?", (loan_id,)).fetchone()
        else:
            loan = conn.execute("SELECT * FROM loans WHERE id = ? AND user_id = ?", (loan_id, user["id"])).fetchone()

        if not loan:
            raise HTTPException(status_code=404, detail="Loan not found.")

        repayments = conn.execute("""
            SELECT * FROM repayments WHERE loan_id = ? ORDER BY id ASC
        """, (loan_id,)).fetchall()

        return {
            "loan": dict(loan),
            "repayments": [dict(r) for r in repayments]
        }
    finally:
        conn.close()


@router.get("/notifications/list")
def get_notifications(user: dict = Depends(get_current_user_from_token)):
    """Returns recent alerts and notifications for the borrower."""
    conn = get_db_connection()
    try:
        notes = conn.execute("""
            SELECT * FROM notifications WHERE user_id = ? ORDER BY id DESC LIMIT 20
        """, (user["id"],)).fetchall()
        return [dict(n) for n in notes]
    finally:
        conn.close()


@router.post("/notifications/mark-read")
def mark_notifications_read(user: dict = Depends(get_current_user_from_token)):
    """Marks all unread notifications as read."""
    conn = get_db_connection()
    try:
        conn.execute("UPDATE notifications SET is_read = 1 WHERE user_id = ?", (user["id"],))
        conn.commit()
        return {"status": "success"}
    finally:
        conn.close()
