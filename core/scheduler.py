"""
HH Cash Solutions / HH LOANHUB - Loan Lifecycle & Month-End Deduction Scheduler
Phase 2: End-of-Month Deduction Calculation & Active Loan Status Monitor
"""

import calendar
import asyncio
from datetime import datetime, timezone, timedelta
from core.database import get_db_connection


def calculate_month_end_deduction_date(from_dt: datetime = None) -> tuple[str, str]:
    """
    Calculates the exact month-end deduction date.
    If loan is disbursed on or before the 24th, deduction is the final day of current month.
    If disbursed on or after the 25th, deduction is the final day of next month.
    Returns (iso_date, formatted_display_date e.g. '30 Nov 2026').
    """
    if not from_dt:
        from_dt = datetime.now(timezone.utc)

    year = from_dt.year
    month = from_dt.month
    day = from_dt.day

    if day >= 25:
        # Move to next month
        if month == 12:
            month = 1
            year += 1
        else:
            month += 1

    last_day = calendar.monthrange(year, month)[1]
    deduction_dt = datetime(year, month, last_day, 23, 59, 59, tzinfo=timezone.utc)

    iso_date = deduction_dt.date().isoformat()
    formatted_display = deduction_dt.strftime("%d %b %Y")
    return iso_date, formatted_display


async def loan_lifecycle_monitor_worker():
    """
    Background worker that runs every hour to check active loans,
    detect overdue accounts, and notify borrowers.
    """
    while True:
        try:
            conn = get_db_connection()
            now = datetime.now(timezone.utc)
            now_iso_date = now.date().isoformat()

            # Find active loans that have passed their deduction date
            loans = conn.execute("""
            SELECT id, user_id, loan_reference, total_repayable, paid_amount, month_end_deduction_date, status
            FROM loans
            WHERE status IN ('active', 'approved')
            """).fetchall()

            for loan in loans:
                deduction_date = loan["month_end_deduction_date"]
                if deduction_date and deduction_date < now_iso_date:
                    owed = float(loan["total_repayable"]) - float(loan["paid_amount"] or 0.0)
                    if owed > 0 and loan["status"] != "overdue":
                        conn.execute("UPDATE loans SET status = 'overdue' WHERE id = ?", (loan["id"],))
                        # Create overdue notification
                        conn.execute("""
                        INSERT INTO notifications (user_id, title, message, type, is_read, created_at)
                        VALUES (?, ?, ?, 'warning', 0, ?)
                        """, (
                            loan["user_id"],
                            "Payment Overdue Reminder",
                            f"Your loan {loan['loan_reference']} was due on {deduction_date}. Outstanding: R {owed:,.2f}. Please settle via EFT.",
                            now.isoformat()
                        ))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[SCHEDULER NOTICE] {e}")

        await asyncio.sleep(3600)  # Check every hour
