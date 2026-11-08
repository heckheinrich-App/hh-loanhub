"""
HH LOANHUB / HH Cash Solutions - Admin Command Center API
Phase 1: Loan Approvals, Borrower Tracking, Repayment Recording & Settings
"""

import secrets
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from core.database import (
    get_db_connection,
    trigger_auto_backup
)
from core.security import require_admin

router = APIRouter(prefix="/api/admin", tags=["Admin Command Center"])


class RecordRepaymentRequest(BaseModel):
    loan_id: int
    amount: float = Field(..., gt=0)
    notes: str = Field("", max_length=200)


class UpdateSettingsRequest(BaseModel):
    default_interest_rate: Optional[float] = None
    min_loan_amount: Optional[float] = None
    max_loan_amount: Optional[float] = None
    support_whatsapp: Optional[str] = None
    support_phone: Optional[str] = None


@router.get("/dashboard")
def get_admin_dashboard(admin: dict = Depends(require_admin)):
    """Provides high-level portfolio metrics for the Master Admin."""
    conn = get_db_connection()
    try:
        total_borrowers = conn.execute("SELECT COUNT(*) AS cnt FROM users WHERE role = 'client'").fetchone()["cnt"]
        pending_count = conn.execute("SELECT COUNT(*) AS cnt FROM loans WHERE status = 'pending'").fetchone()["cnt"]
        active_loans = conn.execute("SELECT COUNT(*) AS cnt, SUM(amount) AS disbursed, SUM(total_repayable) AS outstanding FROM loans WHERE status IN ('approved', 'active')").fetchone()
        overdue_count = conn.execute("SELECT COUNT(*) AS cnt FROM loans WHERE status = 'overdue'").fetchone()["cnt"]
        total_repaid = conn.execute("SELECT SUM(amount) AS sum_repaid FROM repayments WHERE status = 'paid'").fetchone()["sum_repaid"] or 0.0

        return {
            "total_borrowers": total_borrowers,
            "pending_applications": pending_count,
            "active_loans_count": active_loans["cnt"] or 0,
            "total_disbursed": float(active_loans["disbursed"] or 0.0),
            "total_outstanding": float(active_loans["outstanding"] or 0.0),
            "overdue_count": overdue_count,
            "total_repaid": float(total_repaid)
        }
    finally:
        conn.close()


@router.get("/loans")
def list_all_loans(status_filter: Optional[str] = None, admin: dict = Depends(require_admin)):
    """Lists all loans across the platform joined with borrower profiles."""
    conn = get_db_connection()
    try:
        query = """
            SELECT l.*, u.full_name AS borrower_name, u.phone AS borrower_phone, u.account_number
            FROM loans l
            JOIN users u ON l.user_id = u.id
        """
        params = []
        if status_filter and status_filter.lower() != "all":
            query += " WHERE l.status = ?"
            params.append(status_filter.lower())

        query += " ORDER BY l.id DESC"
        rows = conn.execute(query, tuple(params)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


@router.post("/loans/{loan_id}/approve")
def approve_loan(loan_id: int, admin: dict = Depends(require_admin)):
    """Approves a pending loan application and notifies the borrower."""
    conn = get_db_connection()
    try:
        loan = conn.execute("SELECT * FROM loans WHERE id = ?", (loan_id,)).fetchone()
        if not loan:
            raise HTTPException(status_code=404, detail="Loan not found.")

        now_iso = datetime.now(timezone.utc).isoformat()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE loans SET status = 'approved', approved_at = ? WHERE id = ?
        """, (now_iso, loan_id))

        # Notify borrower
        cursor.execute("""
            INSERT INTO notifications (user_id, title, message, type, is_read, created_at)
            VALUES (?, 'Application Approved!', ?, 'approval', 0, ?)
        """, (
            loan["user_id"],
            f"Your loan of R{loan['amount']:,.2f} ({loan['loan_reference']}) has been approved! Funds will reflect shortly.",
            now_iso
        ))
        conn.commit()
    finally:
        conn.close()

    # Trigger auto-backup
    try:
        trigger_auto_backup()
    except Exception as e:
        print(f"[ADMIN APPROVE WARNING] Auto-backup notice: {e}")

    return {"status": "success", "message": f"Loan {loan['loan_reference']} approved successfully."}


@router.post("/loans/{loan_id}/decline")
def decline_loan(loan_id: int, admin: dict = Depends(require_admin)):
    """Declines a loan application and notifies the borrower."""
    conn = get_db_connection()
    try:
        loan = conn.execute("SELECT * FROM loans WHERE id = ?", (loan_id,)).fetchone()
        if not loan:
            raise HTTPException(status_code=404, detail="Loan not found.")

        now_iso = datetime.now(timezone.utc).isoformat()
        cursor = conn.cursor()
        cursor.execute("UPDATE loans SET status = 'declined' WHERE id = ?", (loan_id,))

        cursor.execute("""
            INSERT INTO notifications (user_id, title, message, type, is_read, created_at)
            VALUES (?, 'Application Update', ?, 'alert', 0, ?)
        """, (
            loan["user_id"],
            f"Your application for {loan['loan_reference']} could not be approved at this time. Please contact support for assistance.",
            now_iso
        ))
        conn.commit()
    finally:
        conn.close()

    try:
        trigger_auto_backup()
    except Exception as e:
        print(f"[ADMIN DECLINE WARNING] Auto-backup notice: {e}")

    return {"status": "success", "message": f"Loan {loan['loan_reference']} declined."}


@router.post("/repayments/record")
def record_repayment(req: RecordRepaymentRequest, admin: dict = Depends(require_admin)):
    """Records a borrower repayment, updates loan balance, and marks loan paid if fully settled."""
    conn = get_db_connection()
    try:
        loan = conn.execute("SELECT * FROM loans WHERE id = ?", (req.loan_id,)).fetchone()
        if not loan:
            raise HTTPException(status_code=404, detail="Loan not found.")

        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()
        ref = f"RCPT-{secrets.randbelow(900000) + 100000}"

        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO repayments (loan_id, user_id, amount, payment_date, status, reference, notes)
            VALUES (?, ?, ?, ?, 'paid', ?, ?)
        """, (
            req.loan_id, loan["user_id"], req.amount, now_iso, ref, req.notes
        ))

        # Check total payments against loan total_repayable
        total_paid = conn.execute(
            "SELECT SUM(amount) AS s FROM repayments WHERE loan_id = ? AND status = 'paid'",
            (req.loan_id,)
        ).fetchone()["s"] or 0.0

        if total_paid >= float(loan["total_repayable"]):
            cursor.execute("UPDATE loans SET status = 'paid' WHERE id = ?", (req.loan_id,))

        # Notify borrower
        cursor.execute("""
            INSERT INTO notifications (user_id, title, message, type, is_read, created_at)
            VALUES (?, 'Repayment Received', ?, 'payment', 0, ?)
        """, (
            loan["user_id"],
            f"Payment of R{req.amount:,.2f} recorded (Ref: {ref}). Thank you!",
            now_iso
        ))

        conn.commit()
    finally:
        conn.close()

    try:
        trigger_auto_backup()
    except Exception as e:
        print(f"[REPAYMENT WARNING] Auto-backup notice: {e}")

    return {
        "status": "success",
        "message": f"Repayment of R{req.amount:,.2f} recorded.",
        "receipt_reference": ref,
        "total_paid": total_paid,
        "is_settled": total_paid >= float(loan["total_repayable"])
    }


@router.get("/borrowers")
def list_borrowers(admin: dict = Depends(require_admin)):
    """Returns a directory of all registered borrowers and their active balances."""
    conn = get_db_connection()
    try:
        rows = conn.execute("""
            SELECT u.id, u.account_number, u.full_name, u.phone, u.id_number, u.address,
                   u.guarantor_name, u.guarantor_phone, u.created_at,
                   COUNT(l.id) AS total_loans,
                   SUM(CASE WHEN l.status IN ('approved', 'active') THEN l.total_repayable ELSE 0 END) AS active_balance
            FROM users u
            LEFT JOIN loans l ON u.id = l.user_id
            WHERE u.role = 'client'
            GROUP BY u.id
            ORDER BY u.id DESC
        """).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


@router.post("/trigger-backup")
def manual_backup(admin: dict = Depends(require_admin)):
    """Allows Master Admin to manually trigger an immediate Google Drive sync."""
    result = trigger_auto_backup()
    return result
