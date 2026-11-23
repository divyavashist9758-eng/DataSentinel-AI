"""
Comprehensive Local Live Smoke Test for DataSentinel AI
Tests against running FastAPI backend on http://127.0.0.1:8000

NOTICE: This script performs end-to-end integration data-writing operations:
- User registration (if admin account missing)
- Dataset file upload and table insertion
- Profiling and anomaly result record insertion
- Drift result analysis insertion
- LangGraph investigation and agent trace insertion
- Incident creation and timeline updates
- Remediation approval and non-destructive cloned version creation

FOR NON-DESTRUCTIVE VERIFICATION: Use 'safe_readonly_check.py' (zero data writes).
FOR ISOLATED TESTING: Use 'python backend/tests/verify_all.py' (runs in isolated temporary SQLite test DB).
"""
import sys
import time
from pathlib import Path
import requests

BASE_URL = "http://127.0.0.1:8000"
ROOT_DIR = Path(__file__).resolve().parent
if ROOT_DIR.name == "tests":
    SAMPLE_DATA_DIR = ROOT_DIR.parent / "sample_data"
else:
    SAMPLE_DATA_DIR = ROOT_DIR / "backend" / "sample_data"

def run_smoke_test():
    print(f"=== Starting DataSentinel AI Live Smoke Test on {BASE_URL} ===")
    session = requests.Session()

    # 1. Health check
    print("\n1. Testing Health Endpoint (/health)...")
    r = session.get(f"{BASE_URL}/health")
    assert r.status_code == 200, f"Health check failed: {r.status_code} {r.text}"
    health_data = r.json()
    print(f"   -> PASS: {health_data}")

    # 2. Auth Health check
    print("\n2. Testing Auth Health Endpoint (/api/v1/auth/health)...")
    r = session.get(f"{BASE_URL}/api/v1/auth/health")
    assert r.status_code == 200, f"Auth health failed: {r.status_code} {r.text}"
    print(f"   -> PASS: {r.json()}")

    # 3. Authentication (Login with admin)
    print("\n3. Testing Authentication (Admin Login)...")
    r = session.post(f"{BASE_URL}/api/v1/auth/login", json={
        "username_or_email": "admin",
        "password": "admin123"
    })
    if r.status_code != 200:
        print("   Admin user not found. Registering test analyst...")
        r_reg = session.post(f"{BASE_URL}/api/v1/auth/register", json={
            "username": "smoke_tester",
            "email": "smoke_tester@datasentinel.ai",
            "password": "SmokeTestPassword123!",
            "full_name": "Smoke Test Auditor",
            "role": "admin"
        })
        assert r_reg.status_code in [201, 422], f"Registration failed: {r_reg.text}"
        r = session.post(f"{BASE_URL}/api/v1/auth/login", json={
            "username_or_email": "smoke_tester",
            "password": "SmokeTestPassword123!"
        })
    assert r.status_code == 200, f"Login failed: {r.status_code} {r.text}"
    token_data = r.json()
    token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"   -> PASS: Logged in successfully. Token type: {token_data['token_type']}")

    # 4. Profile /auth/me
    print("\n4. Testing Profile Retrieval (/api/v1/auth/me)...")
    r = session.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
    assert r.status_code == 200, f"Profile failed: {r.status_code} {r.text}"
    profile = r.json()
    print(f"   -> PASS: User '{profile['username']}' with role '{profile['role']}' verified.")

    # 5. Dataset Upload (Clean Baseline)
    print("\n5. Testing Dataset Upload & Ingestion (/api/v1/datasets/upload)...")
    clean_csv_path = SAMPLE_DATA_DIR / "customers_clean.csv"
    with open(clean_csv_path, "rb") as f:
        r = session.post(
            f"{BASE_URL}/api/v1/datasets/upload",
            headers=headers,
            data={"name": "Smoke Benchmark Baseline", "description": "Local smoke test clean dataset"},
            files={"file": ("customers_clean.csv", f, "text/csv")}
        )
    assert r.status_code == 201, f"Upload failed: {r.status_code} {r.text}"
    clean_ds = r.json()
    clean_id = clean_ds["id"]
    print(f"   -> PASS: Uploaded dataset ID {clean_id}: {clean_ds['row_count']} rows, {clean_ds['column_count']} cols.")

    # 6. Profiling & Quality Score
    print("\n6. Testing Automated Profiling & Quality Scoring (/api/v1/profiling/{id}/latest)...")
    r = session.get(f"{BASE_URL}/api/v1/profiling/{clean_id}/latest", headers=headers)
    assert r.status_code == 200, f"Profiling failed: {r.status_code} {r.text}"
    prof = r.json()
    print(f"   -> PASS: Quality Score {prof['overall_score']}/100. Columns profiled: {len(prof['column_metrics'])}.")

    # 7. ML Anomaly Detection (Isolation Forest)
    print("\n7. Testing ML Anomaly Detection (/api/v1/ml/{id}/anomalies)...")
    r = session.post(
        f"{BASE_URL}/api/v1/ml/{clean_id}/anomalies",
        headers=headers,
        json={"detector_type": "isolation_forest", "contamination_rate": 0.05}
    )
    assert r.status_code in [200, 201], f"Anomaly detection failed: {r.status_code} {r.text}"
    anom = r.json()
    print(f"   -> PASS: Evaluated {anom['total_evaluated_rows']} rows. Anomalies detected: {anom['anomalous_rows_count']}.")

    # 8. Upload Drifted Dataset & Run Drift Analysis
    print("\n8. Testing Data & Schema Drift Detection (/api/v1/drift/{id}/analyze)...")
    drift_csv_path = SAMPLE_DATA_DIR / "customers_drifted.csv"
    with open(drift_csv_path, "rb") as f:
        r = session.post(
            f"{BASE_URL}/api/v1/datasets/upload",
            headers=headers,
            data={"name": "Smoke Drifted Current", "description": "Local smoke test drifted dataset"},
            files={"file": ("customers_drifted.csv", f, "text/csv")}
        )
    assert r.status_code == 201, f"Drifted upload failed: {r.status_code} {r.text}"
    drift_ds = r.json()
    drift_id = drift_ds["id"]

    clean_detail = session.get(f"{BASE_URL}/api/v1/datasets/{clean_id}", headers=headers).json()
    drift_detail = session.get(f"{BASE_URL}/api/v1/datasets/{drift_id}", headers=headers).json()
    clean_ver_id = clean_detail["versions"][0]["id"]
    drift_ver_id = drift_detail["versions"][0]["id"]

    r = session.post(
        f"{BASE_URL}/api/v1/drift/{drift_id}/analyze",
        headers=headers,
        json={
            "baseline_version_id": clean_ver_id,
            "current_version_id": drift_ver_id,
            "p_value_threshold": 0.05,
            "psi_threshold": 0.25
        }
    )
    assert r.status_code in [200, 201], f"Drift analysis failed: {r.status_code} {r.text}"
    drift_res = r.json()
    print(f"   -> PASS: Drift detected={drift_res['overall_drift_detected']}. Drifted features: {drift_res['drifted_features_count']}/{drift_res['total_features_count']}.")

    # 9. LangGraph Multi-Agent Autonomous Investigation & RAG
    print("\n9. Testing LangGraph 6-Agent Investigation & RAG (/api/v1/investigations/{id}/start)...")
    r = session.post(
        f"{BASE_URL}/api/v1/investigations/{drift_id}/start",
        headers=headers,
        json={"version_id": drift_ver_id, "focus_areas": ["quality", "anomalies", "schema", "drift"]}
    )
    assert r.status_code == 201, f"Investigation failed: {r.status_code} {r.text}"
    inv = r.json()
    inv_id = inv["id"]
    traces = inv.get("agent_traces", [])
    print(f"   -> PASS: Investigation #{inv_id} completed. Traces generated: {len(traces)}. Status: {inv['status']}")
    for t in traces:
        print(f"      - Agent [{t['agent_name']}]: {t['status']} in {t['execution_time_ms']}ms")

    # 10. Incident Lifecycle
    print("\n10. Testing Incident Lifecycle (/api/v1/incidents/)...")
    r = session.post(
        f"{BASE_URL}/api/v1/incidents/",
        headers=headers,
        json={
            "dataset_id": drift_id,
            "version_id": drift_ver_id,
            "title": "Smoke Test Distribution Drift Alert",
            "description": "Critical drift detected in customer tenure and account balances",
            "severity": "CRITICAL"
        }
    )
    assert r.status_code == 201, f"Incident creation failed: {r.status_code} {r.text}"
    inc = r.json()
    inc_id = inc["id"]
    print(f"   -> PASS: Incident #{inc_id} created with status '{inc['status']}'.")

    # Update incident status
    r = session.patch(
        f"{BASE_URL}/api/v1/incidents/{inc_id}",
        headers=headers,
        json={"status": "INVESTIGATING", "root_cause": "Verified upstream schema evolution and missing data"}
    )
    assert r.status_code == 200, f"Incident update failed: {r.status_code} {r.text}"
    updated_inc = r.json()
    print(f"   -> PASS: Incident #{inc_id} transitioned to '{updated_inc['status']}'. Timeline events: {len(updated_inc.get('timeline', []))}")

    # 11. HITL Remediation Workflow
    print("\n11. Testing HITL Remediation (Preview -> Approve -> Execute)...")
    r = session.get(f"{BASE_URL}/api/v1/remediation/{drift_id}/list", headers=headers)
    assert r.status_code == 200, f"Remediation retrieval failed: {r.status_code} {r.text}"
    remediations = r.json()
    assert len(remediations) > 0, "No remediation suggestions generated"
    rem = remediations[0]
    rem_id = rem["id"]
    print(f"   -> Found remediation #{rem_id}: proposed action '{rem['proposed_action']}' on column '{rem.get('column_name')}'.")

    # Preview diff
    r = session.post(
        f"{BASE_URL}/api/v1/remediation/{rem_id}/preview?preview_limit=5",
        headers=headers
    )
    assert r.status_code == 200, f"Preview failed: {r.status_code} {r.text}"
    prev = r.json()
    print(f"   -> PASS: Preview diff generated. Affected rows: {prev['affected_rows_count']}, before/after rows previewed.")

    # Approve
    r = session.post(
        f"{BASE_URL}/api/v1/remediation/{rem_id}/action",
        headers=headers,
        json={"action": "APPROVE", "reviewer_notes": "Smoke test automated sign-off"}
    )
    assert r.status_code == 200, f"Approval failed: {r.status_code} {r.text}"
    print(f"   -> PASS: Remediation #{rem_id} approved.")

    # Execute non-destructively
    r = session.post(
        f"{BASE_URL}/api/v1/remediation/{rem_id}/execute",
        headers=headers
    )
    assert r.status_code == 200, f"Execution failed: {r.status_code} {r.text}"
    exec_res = r.json()
    print(f"   -> PASS: Remediation #{rem_id} executed. Cloned to new version: {exec_res['execution_result']['new_version_num']}. Original raw data preserved.")

    # 12. PDF & CSV Report Exports
    print("\n12. Testing PDF and CSV Dossier Generation (/api/v1/reports/export/investigation/{id}/...)...")
    r_pdf = session.get(f"{BASE_URL}/api/v1/reports/export/investigation/{inv_id}/pdf", headers=headers)
    assert r_pdf.status_code == 200, f"PDF export failed: {r_pdf.status_code} {r_pdf.text}"
    assert r_pdf.content.startswith(b"%PDF"), "Response is not a valid PDF document"
    print(f"   -> PASS: Exported valid PDF document ({len(r_pdf.content)} bytes).")

    r_csv = session.get(f"{BASE_URL}/api/v1/reports/export/investigation/{inv_id}/csv", headers=headers)
    assert r_csv.status_code == 200, f"CSV export failed: {r_csv.status_code} {r_csv.text}"
    assert "investigation_id" in r_csv.text.lower() or "agent" in r_csv.text.lower() or "dataset" in r_csv.text.lower(), "CSV header mismatch"
    print(f"   -> PASS: Exported valid CSV dossier ({len(r_csv.content)} bytes).")

    print("\n" + "=" * 70)
    print("ALL 12 APPLICATION SMOKE TESTS PASSED ON LIVE RUNNING INSTANCE!")
    print("=" * 70)

if __name__ == "__main__":
    try:
        run_smoke_test()
    except Exception as e:
        print(f"\nFATAL SMOKE TEST FAILURE: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
