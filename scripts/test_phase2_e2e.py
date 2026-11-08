"""
Automated End-to-End Verification for Phase 2:
- Master Admin (Hein/1234)
- KYC Multipart Registration with OCR Affordability Engine
- Loan Lifecycle: Pending -> Approved -> Active (Mark Paid) -> Pull Payment Request -> Repayment
- Document Inspection Endpoint
"""

import sys
import io
import requests

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000"

def test_pipeline():
    print("--- 1. Testing Health Endpoint ---")
    r = requests.get(f"{BASE_URL}/api/health")
    assert r.status_code == 200, f"Health check failed: {r.text}"
    print(f"✓ Local API Health OK: {r.json()}")

    print("\n--- 2. Testing Master Admin Login (Hein / 1234) ---")
    r = requests.post(f"{BASE_URL}/api/auth/login", json={"phone": "Hein", "password": "1234"})
    assert r.status_code == 200, f"Admin login failed: {r.text}"
    admin_data = r.json()
    admin_token = admin_data["token"]
    assert admin_data["user"]["role"] == "admin"
    print(f"✓ Master Admin Login OK: {admin_data['user']['full_name']} (Role: {admin_data['user']['role']})")

    headers_admin = {"Authorization": f"Bearer {admin_token}"}

    print("\n--- 3. Testing Admin Dashboard KPI Stats ---")
    r = requests.get(f"{BASE_URL}/api/admin/dashboard", headers=headers_admin)
    assert r.status_code == 200, f"Dashboard failed: {r.text}"
    print(f"✓ Admin KPIs: {r.json()}")

    print("\n--- 4. Testing KYC Registration & OCR Affordability Engine ---")
    # Create sample files
    dummy_pdf = b"%PDF-1.4\n1 0 obj\n<< /Title (Bank Statement - John Doe) >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF"
    dummy_id = b"%PDF-1.4\n1 0 obj\n<< /Title (National ID - John Doe 8801015009087) >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF"
    dummy_proof = b"%PDF-1.4\n1 0 obj\n<< /Title (Proof of Residence - 123 Main St) >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF"

    test_phone = f"082{secrets_randint(1000000, 9999999)}"
    files = {
        "bank_statement": ("bank_statement.pdf", io.BytesIO(dummy_pdf), "application/pdf"),
        "id_document": ("id_document.pdf", io.BytesIO(dummy_id), "application/pdf"),
        "proof_of_residence": ("proof_residence.pdf", io.BytesIO(dummy_proof), "application/pdf"),
    }
    data = {
        "full_name": "Sipho Dlamini",
        "phone": test_phone,
        "id_number": "9005125800085",
        "address": "45 Commissioner St, Johannesburg, 2001",
        "bank_name": "Capitec Bank",
        "bank_account_number": "1458963254",
        "password": "pass1234Secure!",
        "initial_loan_amount": "4000.0"
    }

    r = requests.post(f"{BASE_URL}/api/auth/register-with-kyc", data=data, files=files)
    assert r.status_code == 201, f"KYC registration failed: {r.text}"
    reg_data = r.json()
    user_token = reg_data["token"]
    user_id = reg_data["user"]["id"]
    loan_info = reg_data["initial_loan"]
    print(f"✓ Registration & KYC Uploaded OK! Client: {reg_data['user']['full_name']} (Acc: {reg_data['user']['account_number']})")
    print(f"✓ Initial Loan Created: R {loan_info['amount']} Principal | 30% Total Repayable: R {loan_info['total_repayable']} (Status: {loan_info['status']})")

    headers_user = {"Authorization": f"Bearer {user_token}"}

    print("\n--- 5. Testing Client /api/auth/me Lifecycle Info ---")
    r = requests.get(f"{BASE_URL}/api/auth/me", headers=headers_user)
    assert r.status_code == 200, f"User profile failed: {r.text}"
    user_profile = r.json()
    assert user_profile["latest_loan"]["status"] == "pending"
    loan_id = user_profile["latest_loan"]["id"]
    print(f"✓ Client Profile returned latest loan with status: '{user_profile['latest_loan']['status']}'")

    print("\n--- 6. Testing Admin Pending Queue Inspection ---")
    r = requests.get(f"{BASE_URL}/api/admin/pending-queue", headers=headers_admin)
    assert r.status_code == 200
    queue = r.json()
    target_loan = next((l for l in queue if l["id"] == loan_id), None)
    assert target_loan is not None, "Newly registered loan not found in pending queue!"
    print(f"✓ Loan found in Pending Queue! Bank: {target_loan['bank_name']} Acc: {target_loan['bank_account_number']}")
    print(f"✓ OCR Affordability Report: Match Status: {target_loan['identity_match_status']} | Max Recommended Loan: R {target_loan['max_recommended_loan']}")
    print(f"✓ Attached KYC Docs: {len(target_loan['kyc_documents'])} files")
    assert len(target_loan["kyc_documents"]) == 3, "Missing KYC documents!"

    doc_id = target_loan["kyc_documents"][0]["id"]
    print(f"\n--- 7. Testing Admin Document Viewer (/api/admin/documents/{doc_id}/view) ---")
    r = requests.get(f"{BASE_URL}/api/admin/documents/{doc_id}/view", headers=headers_admin)
    assert r.status_code == 200, f"Doc view failed: {r.status_code}"
    print(f"✓ Document View Success! Content-Type: {r.headers.get('content-type')} Length: {len(r.content)} bytes")

    print(f"\n--- 8. Testing Admin Loan Approval (/api/admin/loans/{loan_id}/approve) ---")
    r = requests.post(f"{BASE_URL}/api/admin/loans/{loan_id}/approve", headers=headers_admin)
    assert r.status_code == 200, f"Approval failed: {r.text}"
    print(f"✓ Approval Result: {r.json()['message']}")

    # Verify client profile reflects approved
    r = requests.get(f"{BASE_URL}/api/auth/me", headers=headers_user)
    assert r.json()["latest_loan"]["status"] == "approved"
    print(f"✓ Client Profile dynamically updated to: '{r.json()['latest_loan']['status']}' (Awaiting Payout)")

    print(f"\n--- 9. Testing Admin 'Mark as Paid (Money Sent via EFT)' ---")
    r = requests.post(f"{BASE_URL}/api/admin/loans/{loan_id}/mark-paid", headers=headers_admin)
    assert r.status_code == 200, f"Mark paid failed: {r.text}"
    paid_res = r.json()
    print(f"✓ Mark Paid Result: {paid_res['message']} (Status: {paid_res['status']})")
    print(f"✓ Month-End Deduction Date: {paid_res['month_end_deduction_date']}")

    # Verify client profile reflects active
    r = requests.get(f"{BASE_URL}/api/auth/me", headers=headers_user)
    assert r.json()["latest_loan"]["status"] == "active"
    print(f"✓ Client Profile dynamically updated to: '{r.json()['latest_loan']['status']}'")

    print(f"\n--- 10. Testing Admin Pull Payment Request ---")
    r = requests.post(f"{BASE_URL}/api/admin/loans/{loan_id}/pull-payment-request", headers=headers_admin, json={"loan_id": loan_id})
    assert r.status_code == 200, f"Pull payment failed: {r.text}"
    print(f"✓ Pull Payment Request OK: {r.json()['message']}")

    # Verify client profile reflects payment_requested
    r = requests.get(f"{BASE_URL}/api/auth/me", headers=headers_user)
    assert r.json()["latest_loan"]["status"] == "payment_requested"
    print(f"✓ Client Profile dynamically updated to: '{r.json()['latest_loan']['status']}' (Urgent Banner Active)")

    print(f"\n--- 11. Testing Admin Record Repayment ---")
    r = requests.post(f"{BASE_URL}/api/admin/repayments/record", headers=headers_admin, json={
        "loan_id": loan_id,
        "amount": 5200.0,
        "notes": "Full settlement EFT Ref Capitec 9021"
    })
    assert r.status_code == 200, f"Repayment failed: {r.text}"
    repay_res = r.json()
    print(f"✓ Repayment Recorded: {repay_res['message']} | Settled: {repay_res['is_settled']}")

    print(f"\n--- 12. Testing Biometric Enrollment & Login ---")
    r = requests.post(f"{BASE_URL}/api/auth/biometric/register", headers=headers_user, json={"credential_id": "bio-cred-test-999"})
    assert r.status_code == 200, f"Bio register failed: {r.text}"
    print(f"✓ Biometric Registered: {r.json()['message']}")

    r = requests.post(f"{BASE_URL}/api/auth/biometric/login", json={"credential_id": "bio-cred-test-999", "phone_or_username": test_phone})
    assert r.status_code == 200, f"Bio login failed: {r.text}"
    print(f"✓ Biometric Login Successful: {r.json()['message']}")

    print("\n=======================================================")
    print("ALL 12 END-TO-END VERIFICATION CHECKS PASSED PERFECTLY!")
    print("=======================================================")

def secrets_randint(a, b):
    import random
    return random.randint(a, b)

if __name__ == "__main__":
    test_pipeline()
