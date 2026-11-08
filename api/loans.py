"""
HH LOANHUB / HH Cash Solutions - Client Loan & Notification API
Phase 2: 30% Interest Loans, Month-End Deductions, Lifecycle Tracking & Notifications
"""

from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from core.database import (
    get_db_connection,
    generate_loan_reference,
    trigger_auto_backup
)
from core.security import get_current_user_from_token
from core.scheduler import calculate_month_end_deduction_date

router = APIRouter(prefix="/api/loans", tags=["Loans"])


class LoanApplyRequest(BaseModel):
    amount: float = Field(..., ge=500, le=20000)
    term_months: int = Field(1, ge=1, le=1)
    purpose: str = Field("Personal Expenses", max_length=150)
    collateral_note: str = Field("", max_length=200)


@router.post("/apply", status_code=status.HTTP_201_CREATED)
def apply_for_loan(req: LoanApplyRequest, user: dict = Depends(get_current_user_from_token)):
    """Submits a new loan application with 30% interest and month-end repayment date."""
    conn = get_db_connection()
    try:
        # Check if borrower already has an active pending or active loan
        existing_active = conn.execute("""
            SELECT id, status FROM loans 
            WHERE user_id = ? AND status IN ('pending', 'approved', 'active', 'payment_requested')
        """, (user["id"],)).fetchone()

        if existing_active:
            raise HTTPException(
                status_code=400,
                detail=f"You already have a loan with status '{existing_active['status']}'. Please settle existing loans before applying for another."
            )

        # 30% Interest Rate
        interest_rate = 30.0
        interest_amount = round(req.amount * (interest_rate / 100.0), 2)
        total_repayable = round(req.amount + interest_amount, 2)

        # Calculate month-end deduction date
        now = datetime.now(timezone.utc)
        iso_deduction, display_deduction = calculate_month_end_deduction_date(now)
        loan_ref = generate_loan_reference()
        now_iso = now.isoformat()

        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO loans (
            loan_reference, user_id, amount, term_months, interest_rate,
            total_repayable, purpose, collateral_note, status,
            first_payment_due, month_end_deduction_date, created_at
        ) VALUES (?, ?, ?, 1, ?, ?, ?, ?, 'pending', ?, ?, ?)
        """, (
            loan_ref, user["id"], req.amount, interest_rate,
            total_repayable, req.purpose, req.collateral_note,
            display_deduction, iso_deduction, now_iso
        ))
        loan_id = cursor.lastrowid

        # Notification to borrower
        cursor.execute("""
        INSERT INTO notifications (user_id, title, message, type, is_read, created_at)
        VALUES (?, ?, ?, 'application', 0, ?)
        """, (
            user["id"],
            "Loan Request Submitted",
            f"Your request for R {req.amount:,.2f} (Total repayable: R {total_repayable:,.2f}) has been submitted to Admin for review.",
            now_iso
        ))

        conn.commit()
    finally:
        conn.close()

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
            "interest_rate": interest_rate,
            "interest_amount": interest_amount,
            "total_repayable": total_repayable,
            "month_end_deduction_date": display_deduction,
            "status": "pending"
        }
    }


@router.get("/my")
def get_my_loans(user: dict = Depends(get_current_user_from_token)):
    """Returns all loans taken by the logged-in borrower."""
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
