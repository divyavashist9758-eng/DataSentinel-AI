"""
Safe Read-Only Live Verification Script for DataSentinel AI
Performs strictly read-only inspection against running instance on http://127.0.0.1:8000.
Does NOT create, update, or delete any datasets, versions, users, or incidents.
"""
import sys
import requests

BASE_URL = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://127.0.0.1:8000"

def run_safe_readonly_check():
    print("=" * 70)
    print("DATASENTINEL AI: SAFE READ-ONLY VERIFICATION")
    print(f"Target: {BASE_URL}")
    print("Mode: Strictly Non-Destructive / Zero Database Writes")
    print("=" * 70)

    session = requests.Session()
    results = {}

    # 1. Health check
    print("\n1. Verifying /health endpoint...")
    try:
        r = session.get(f"{BASE_URL}/health", timeout=30)
        assert r.status_code == 200, f"HTTP {r.status_code}"
        data = r.json()
        assert data.get("status") == "healthy"
        results["Health Check"] = "PASS"
        print(f"   -> PASS: {data}")
    except Exception as e:
        results["Health Check"] = f"FAIL: {e}"
        print(f"   -> FAIL: {e}")

    # 2. Auth Health check
    print("\n2. Verifying /api/v1/auth/health endpoint...")
    try:
        r = session.get(f"{BASE_URL}/api/v1/auth/health", timeout=30)
        assert r.status_code == 200, f"HTTP {r.status_code}"
        data = r.json()
        assert data.get("status") == "healthy"
        results["Auth Health"] = "PASS"
        print(f"   -> PASS: {data}")
    except Exception as e:
        results["Auth Health"] = f"FAIL: {e}"
        print(f"   -> FAIL: {e}")

    # 3. Read-Only Authentication verification
    print("\n3. Verifying Authentication & Token Acquisition...")
    token = None
    try:
        r = session.post(f"{BASE_URL}/api/v1/auth/login", json={
            "username_or_email": "admin",
            "password": "admin123"
        }, timeout=30)
        assert r.status_code == 200, f"Login failed: HTTP {r.status_code}"
        token = r.json().get("access_token")
        assert token, "No access_token returned"
        results["Authentication (Login)"] = "PASS"
        print("   -> PASS: Valid JWT bearer token acquired using existing credentials.")
    except Exception as e:
        results["Authentication (Login)"] = f"FAIL: {e}"
        print(f"   -> FAIL: {e}")

    if not token:
        print("\nAborting authenticated read checks due to login failure.")
        return results

    headers = {"Authorization": f"Bearer {token}"}

    # 4. User Profile Read-Only Check
    print("\n4. Verifying User Profile Retrieval (/api/v1/auth/me)...")
    try:
        r = session.get(f"{BASE_URL}/api/v1/auth/me", headers=headers, timeout=30)
        assert r.status_code == 200, f"HTTP {r.status_code}"
        user_info = r.json()
        assert "username" in user_info and "role" in user_info
        results["Profile Inspection"] = "PASS"
        print(f"   -> PASS: Authenticated user '{user_info['username']}' (role: {user_info['role']}).")
    except Exception as e:
        results["Profile Inspection"] = f"FAIL: {e}"
        print(f"   -> FAIL: {e}")

    # 5. Dataset List (Read-Only)
    print("\n5. Verifying Dataset Query (/api/v1/datasets/)...")
    try:
        r = session.get(f"{BASE_URL}/api/v1/datasets/", headers=headers, timeout=30)
        assert r.status_code == 200, f"HTTP {r.status_code}"
        datasets = r.json()
        results["Dataset List (Read)"] = "PASS"
        print(f"   -> PASS: Retrieved dataset catalog ({len(datasets)} dataset(s) present).")
    except Exception as e:
        results["Dataset List (Read)"] = f"FAIL: {e}"
        print(f"   -> FAIL: {e}")

    # 6. Dashboard Telemetry Metrics (Read-Only)
    print("\n6. Verifying Dashboard Metrics (/api/v1/reports/dashboard/metrics)...")
    try:
        r = session.get(f"{BASE_URL}/api/v1/reports/dashboard/metrics", headers=headers, timeout=30)
        assert r.status_code == 200, f"HTTP {r.status_code}"
        metrics = r.json()
        assert "overall_health_score" in metrics
        results["Dashboard Metrics (Read)"] = "PASS"
        print(f"   -> PASS: Health score={metrics['overall_health_score']}, Total datasets={metrics['total_datasets']}.")
    except Exception as e:
        results["Dashboard Metrics (Read)"] = f"FAIL: {e}"
        print(f"   -> FAIL: {e}")

    # 7. Incident Queries (Read-Only)
    print("\n7. Verifying Incident Registry (/api/v1/incidents/)...")
    try:
        r = session.get(f"{BASE_URL}/api/v1/incidents/", headers=headers, timeout=30)
        assert r.status_code == 200, f"HTTP {r.status_code}"
        incidents = r.json()
        results["Incident Registry (Read)"] = "PASS"
        print(f"   -> PASS: Queried incidents table ({len(incidents)} record(s)).")
    except Exception as e:
        results["Incident Registry (Read)"] = f"FAIL: {e}"
        print(f"   -> FAIL: {e}")

    # 8. RAG Knowledge Base (Read-Only)
    print("\n8. Verifying RAG Knowledge Base (/api/v1/rag/all)...")
    try:
        r = session.get(f"{BASE_URL}/api/v1/rag/all", headers=headers, timeout=30)
        assert r.status_code == 200, f"HTTP {r.status_code}"
        kb = r.json()
        results["RAG Knowledge (Read)"] = "PASS"
        print(f"   -> PASS: RAG knowledge base loaded ({len(kb)} domain playbook(s)).")
    except Exception as e:
        results["RAG Knowledge (Read)"] = f"FAIL: {e}"
        print(f"   -> FAIL: {e}")

    print("\n" + "=" * 70)
    print("READ-ONLY VERIFICATION SCORECARD")
    print("=" * 70)
    all_pass = True
    for test, res in results.items():
        print(f"  {test:<35}: {res}")
        if res != "PASS":
            all_pass = False
    print("=" * 70)
    if all_pass:
        print("OVERALL: ALL READ-ONLY CHECKS PASSED (Zero data mutations)")
    else:
        print("OVERALL: SOME CHECKS FAILED")
    print("=" * 70)
    return results

if __name__ == "__main__":
    run_safe_readonly_check()
