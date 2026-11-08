"""
HH LOANHUB / HH Cash Solutions - Admin Command Center API
Phase 2: Master Admin (Hein/1234), KPI Bar, KYC Document Inspection & Payout Lifecycle
"""

import os
import re
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from core.database import (
    get_db_connection,
    trigger_auto_backup,
    UPLOADS_DIR
)
from core.security import require_admin
from core.scheduler import calculate_month_end_deduction_date

router = APIRouter(prefix="/api/admin", tags=["Admin Command Center"])


class RecordRepaymentRequest(BaseModel):
    loan_id: int
    amount: float = Field(..., gt=0)
    notes: str = Field("", max_length=200)


class PullPaymentRequest(BaseModel):
    loan_id: int
    custom_message: Optional[str] = ""


class OverrideAffordabilityRequest(BaseModel):
    report_id: int
    admin_override_disposable: float
    admin_notes: Optional[str] = ""


def format_sa_whatsapp_link(phone: str, message: str) -> str:
    """Formats South African phone number (e.g. 0821234567 -> 27821234567) into a direct WhatsApp link."""
    clean = re.sub(r"\D", "", phone or "")
    if clean.startswith("0") and len(clean) == 10:
        clean = "27" + clean[1:]
    elif not clean.startswith("27") and len(clean) == 9:
        clean = "27" + clean
    from urllib.parse import quote
    return f"https://wa.me/{clean}?text={quote(message)}"


@router.get("/dashboard")
def get_admin_dashboard(admin: dict = Depends(require_admin)):
    """Provides high-level portfolio metrics for Master Admin (Hein)."""
    conn = get_db_connection()
    try:
        total_borrowers = conn.execute("SELECT COUNT(*) AS cnt FROM users WHERE role = 'client'").fetchone()["cnt"]
        pending_requests = conn.execute("SELECT COUNT(*) AS cnt FROM loans WHERE status = 'pending'").fetchone()["cnt"]
        awaiting_payout = conn.execute("SELECT COUNT(*) AS cnt FROM loans WHERE status = 'approved'").fetchone()["cnt"]

        # Active principal out
        active_loans = conn.execute("""
            SELECT 
                COUNT(*) AS cnt,
                SUM(amount) AS total_principal,
                SUM(total_repayable) AS total_owed,
                SUM(paid_amount) AS total_paid
            FROM loans
            WHERE status IN ('active', 'payment_requested', 'overdue')
        """).fetchone()

        total_principal_out = float(active_loans["total_principal"] or 0.0)
        total_owed_with_interest = max(0.0, float(active_loans["total_owed"] or 0.0) - float(active_loans["total_paid"] or 0.0))

        overdue_count = conn.execute("SELECT COUNT(*) AS cnt FROM loans WHERE status = 'overdue'").fetchone()["cnt"]
        total_repayments_collected = conn.execute("SELECT SUM(amount) AS sm FROM repayments WHERE status = 'paid'").fetchone()["sm"] or 0.0

        return {
            "total_borrowers": total_borrowers,
            "pending_requests": pending_requests,
            "awaiting_payout": awaiting_payout,
            "total_principal_out": total_principal_out,
            "total_owed_with_interest": total_owed_with_interest,
            "overdue_count": overdue_count,
            "total_repayments_collected": float(total_repayments_collected)
        }
    finally:
        conn.close()


@router.get("/pending-queue")
def get_pending_loan_queue(admin: dict = Depends(require_admin)):
    """
    Returns pending loan requests and loans awaiting payout with borrower details,
    uploaded KYC documents, and automated OCR Affordability reports.
    """
    conn = get_db_connection()
    try:
        query = """
            SELECT 
                l.*,
                u.full_name AS borrower_name,
                u.phone AS borrower_phone,
                u.id_number AS borrower_id_number,
                u.bank_name,
                u.bank_account_number,
                u.account_number,
                u.address,
                ar.identity_match_status,
                ar.identity_match_notes,
                ar.estimated_monthly_income,
                ar.estimated_monthly_expenses,
                ar.estimated_disposable_income,
                ar.max_recommended_loan
            FROM loans l
            JOIN users u ON l.user_id = u.id
            LEFT JOIN affordability_reports ar ON l.user_id = ar.user_id
            WHERE l.status IN ('pending', 'approved')
            ORDER BY l.id DESC
        """
        rows = conn.execute(query).fetchall()
        result = []
        for r in rows:
            item = dict(r)
            # Fetch KYC documents for this borrower
            docs = conn.execute("""
                SELECT id, doc_type, filename, file_size, uploaded_at, ocr_status
                FROM kyc_documents
                WHERE user_id = ?
            """, (item["user_id"],)).fetchall()
            item["kyc_documents"] = [dict(d) for d in docs]

            # Generate direct WhatsApp link
            default_wa_msg = f"Hi {item['borrower_name']}, contacting you from HH Cash Solutions regarding your loan application ({item['loan_reference']}) for R {item['amount']:,.2f}."
            item["whatsapp_link"] = format_sa_whatsapp_link(item["borrower_phone"], default_wa_msg)
            result.append(item)

        return result
    finally:
        conn.close()


@router.get("/ledger")
def get_all_users_ledger(admin: dict = Depends(require_admin)):
    """
    Returns complete ledger of all registered borrowers, bank details, KYC status,
    active loan status, amount owed with 30% interest, and direct WhatsApp links.
    """
    conn = get_db_connection()
    try:
        users = conn.execute("""
            SELECT id, account_number, full_name, phone, username, id_number, address,
                   bank_name, bank_account_number, role, created_at
            FROM users
            WHERE role = 'client'
            ORDER BY id DESC
        """).fetchall()

        result = []
        for u in users:
            user_dict = dict(u)
            user_id = user_dict["id"]

            # Active loan or latest loan
            loan = conn.execute("""
                SELECT * FROM loans WHERE user_id = ? ORDER BY id DESC LIMIT 1
            """, (user_id,)).fetchone()

            if loan:
                loan_dict = dict(loan)
                total_repayable = float(loan_dict["total_repayable"])
                paid = float(loan_dict.get("paid_amount") or 0.0)
                loan_dict["remaining_owed"] = max(0.0, total_repayable - paid)
                user_dict["latest_loan"] = loan_dict
            else:
                user_dict["latest_loan"] = None

            # KYC documents count
            docs = conn.execute("SELECT id, doc_type, filename, file_size FROM kyc_documents WHERE user_id = ?", (user_id,)).fetchall()
            user_dict["kyc_docs"] = [dict(d) for d in docs]

            # WhatsApp Link
            amount_owed_str = f"R {user_dict['latest_loan']['remaining_owed']:,.2f}" if user_dict["latest_loan"] else "R0.00"
            wa_msg = f"Hi {user_dict['full_name']}, contacting you from HH Cash Solutions regarding your account {user_dict['account_number']} (Balance: {amount_owed_str})."
            user_dict["whatsapp_link"] = format_sa_whatsapp_link(user_dict["phone"], wa_msg)

            result.append(user_dict)

        return result
    finally:
        conn.close()


@router.post("/loans/{loan_id}/approve")
def approve_loan(loan_id: int, admin: dict = Depends(require_admin)):
    """
    Stage 2: Admin approves loan -> Sets status to 'approved' (APPROVED_AWAITING_PAYOUT).
    Notifies borrower that payout is being prepared to their bank account.
    """
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
            VALUES (?, '🎉 Loan Approved — Payout Pending!', ?, 'approval', 0, ?)
        """, (
            loan["user_id"],
            f"Your loan of R {loan['amount']:,.2f} ({loan['loan_reference']}) has been approved! Payout is being processed to your bank account via EFT.",
            now_iso
        ))

        conn.commit()
    finally:
        conn.close()

    try:
        trigger_auto_backup()
    except Exception as e:
        print(f"[APPROVE WARNING] {e}")

    return {
        "status": "success",
        "message": "Loan approved! Ready for manual EFT payout.",
        "loan_status": "approved"
    }


@router.post("/loans/{loan_id}/decline")
def decline_loan(loan_id: int, admin: dict = Depends(require_admin)):
    """Admin declines loan application."""
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
            VALUES (?, 'Loan Application Update', ?, 'warning', 0, ?)
        """, (
            loan["user_id"],
            f"Your loan request ({loan['loan_reference']}) was declined by underwriter. Please contact support via WhatsApp if you have questions.",
            now_iso
        ))

        conn.commit()
    finally:
        conn.close()

    try:
        trigger_auto_backup()
    except Exception as e:
        print(f"[DECLINE WARNING] {e}")

    return {"status": "success", "message": "Loan declined.", "loan_status": "declined"}


@router.post("/loans/{loan_id}/mark-paid")
def mark_loan_paid_and_disbursed(loan_id: int, admin: dict = Depends(require_admin)):
    """
    Stage 3: Admin clicks 'Mark as Paid (Money Sent)'.
    Activates loan (status = 'active'), sets disbursed timestamp, calculates Month-End Deduction Date.
    """
    conn = get_db_connection()
    try:
        loan = conn.execute("SELECT * FROM loans WHERE id = ?", (loan_id,)).fetchone()
        if not loan:
            raise HTTPException(status_code=404, detail="Loan not found.")

        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()
        iso_deduction, display_deduction = calculate_month_end_deduction_date(now)

        cursor = conn.cursor()
        cursor.execute("""
            UPDATE loans SET
                status = 'active',
                disbursed_at = ?,
                first_payment_due = ?,
                month_end_deduction_date = ?
            WHERE id = ?
        """, (now_iso, display_deduction, iso_deduction, loan_id))

        # Notify borrower
        cursor.execute("""
            INSERT INTO notifications (user_id, title, message, type, is_read, created_at)
            VALUES (?, '💰 Loan Payout Sent & Active!', ?, 'disbursed', 0, ?)
        """, (
            loan["user_id"],
            f"R {loan['amount']:,.2f} has been paid out! Your loan is now active. R {loan['total_repayable']:,.2f} (including 30% interest) is due on {display_deduction}.",
            now_iso
        ))

        conn.commit()
    finally:
        conn.close()

    try:
        trigger_auto_backup()
    except Exception as e:
        print(f"[DISBURSE WARNING] {e}")

    return {
        "status": "success",
        "message": f"Loan marked as paid and active! Month-end deduction set for {display_deduction}.",
        "loan_status": "active",
        "month_end_deduction_date": display_deduction
    }


@router.post("/loans/{loan_id}/pull-payment-request")
def pull_payment_request(loan_id: int, req: PullPaymentRequest = None, admin: dict = Depends(require_admin)):
    """
    Admin triggers 'Pull Payment Request'.
    Flags loan status as 'payment_requested', places urgent banner on client dashboard,
    and returns a pre-filled WhatsApp message.
    """
    conn = get_db_connection()
    try:
        loan = conn.execute("""
            SELECT l.*, u.full_name, u.phone
            FROM loans l
            JOIN users u ON l.user_id = u.id
            WHERE l.id = ?
        """, (loan_id,)).fetchone()

        if not loan:
            raise HTTPException(status_code=404, detail="Loan not found.")

        loan = dict(loan)
        now_iso = datetime.now(timezone.utc).isoformat()
        remaining_owed = float(loan["total_repayable"]) - float(loan.get("paid_amount") or 0.0)

        cursor = conn.cursor()
        cursor.execute("""
            UPDATE loans SET 
                payment_requested = 1,
                payment_requested_at = ?,
                status = 'payment_requested'
            WHERE id = ?
        """, (now_iso, loan_id))

        # Urgent notification to borrower
        cursor.execute("""
            INSERT INTO notifications (user_id, title, message, type, is_read, created_at)
            VALUES (?, '⚠️ Payment Requested Now', ?, 'warning', 0, ?)
        """, (
            loan["user_id"],
            f"Payment of R {remaining_owed:,.2f} has been requested for loan {loan['loan_reference']}. Please transfer via EFT and send payment proof.",
            now_iso
        ))

        conn.commit()

        # WhatsApp Message
        wa_message = f"Hi {loan['full_name']}, this is Hein from HH Cash Solutions regarding your loan {loan['loan_reference']}. Please be advised your payment of R {remaining_owed:,.2f} is now requested. Please settle via EFT and send your proof of payment."
        wa_link = format_sa_whatsapp_link(loan["phone"], wa_message)

        return {
            "status": "success",
            "message": f"Payment request logged for R {remaining_owed:,.2f}.",
            "remaining_owed": remaining_owed,
            "whatsapp_message": wa_message,
            "whatsapp_link": wa_link
        }
    finally:
        conn.close()


@router.post("/repayments/record")
def record_repayment(req: RecordRepaymentRequest, admin: dict = Depends(require_admin)):
    """Records an incoming client repayment, updates loan paid_amount, and checks settlement."""
    conn = get_db_connection()
    try:
        loan = conn.execute("SELECT * FROM loans WHERE id = ?", (req.loan_id,)).fetchone()
        if not loan:
            raise HTTPException(status_code=404, detail="Loan not found.")

        loan = dict(loan)
        now_iso = datetime.now(timezone.utc).isoformat()
        ref = f"PAY-{secrets.randbelow(900000) + 100000}"

        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO repayments (loan_id, user_id, amount, payment_date, status, reference, notes)
            VALUES (?, ?, ?, ?, 'paid', ?, ?)
        """, (req.loan_id, loan["user_id"], req.amount, now_iso, ref, req.notes))

        # Update loan paid_amount
        current_paid = float(loan.get("paid_amount") or 0.0) + req.amount
        total_repayable = float(loan["total_repayable"])

        new_status = loan["status"]
        if current_paid >= total_repayable:
            new_status = "settled"
            # Settlement notification
            cursor.execute("""
                INSERT INTO notifications (user_id, title, message, type, is_read, created_at)
                VALUES (?, '🎉 Loan Settled in Full!', ?, 'settled', 0, ?)
            """, (
                loan["user_id"],
                f"Your loan {loan['loan_reference']} has been settled in full! Thank you for partnering with HH Cash Solutions.",
                now_iso
            ))
        else:
            remaining = total_repayable - current_paid
            cursor.execute("""
                INSERT INTO notifications (user_id, title, message, type, is_read, created_at)
                VALUES (?, 'Payment Received', ?, 'payment', 0, ?)
            """, (
                loan["user_id"],
                f"We received your payment of R {req.amount:,.2f} ({ref}). Remaining balance: R {remaining:,.2f}.",
                now_iso
            ))

        cursor.execute("""
            UPDATE loans SET paid_amount = ?, status = ? WHERE id = ?
        """, (current_paid, new_status, req.loan_id))

        conn.commit()
    finally:
        conn.close()

    try:
        trigger_auto_backup()
    except Exception as e:
        print(f"[REPAYMENT WARNING] {e}")

    return {
        "status": "success",
        "message": f"Repayment of R {req.amount:,.2f} recorded.",
        "receipt_reference": ref,
        "new_paid_total": current_paid,
        "loan_status": new_status,
        "is_settled": new_status == "settled"
    }


@router.get("/documents/{doc_id}/view")
def view_document(doc_id: int, admin: dict = Depends(require_admin)):
    """Serves an uploaded KYC document (bank statement, ID, proof of address) directly to Admin."""
    conn = get_db_connection()
    try:
        doc = conn.execute("SELECT * FROM kyc_documents WHERE id = ?", (doc_id,)).fetchone()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found.")

        file_path = Path(doc["file_path"])
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found on server disk.")

        return FileResponse(
            path=str(file_path),
            filename=doc["filename"],
            media_type=doc["mime_type"]
        )
    finally:
        conn.close()


@router.post("/affordability/{report_id}/override")
def override_affordability(report_id: int, req: OverrideAffordabilityRequest, admin: dict = Depends(require_admin)):
    """Allows Admin to update or override the automated disposable income calculation."""
    conn = get_db_connection()
    try:
        now_iso = datetime.now(timezone.utc).isoformat()
        conn.execute("""
            UPDATE affordability_reports SET
                admin_override_disposable = ?,
                admin_notes = ?,
                updated_at = ?
            WHERE id = ?
        """, (req.admin_override_disposable, req.admin_notes or "", now_iso, report_id))
        conn.commit()
        return {"status": "success", "message": "Affordability figures updated by Admin."}
    finally:
        conn.close()
