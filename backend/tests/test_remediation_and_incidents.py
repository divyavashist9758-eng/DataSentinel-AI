import os

def test_incident_lifecycle_and_remediation_workflow(client, auth_headers):
    # Upload anomalous json dataset with duplicates and outliers
    with open("backend/sample_data/transactions_anomalous.json", "rb") as f:
        ds_resp = client.post(
            "/api/v1/datasets/upload",
            files={"file": ("transactions_anomalous.json", f, "application/json")},
            data={"name": "Incident Target Transactions", "description": "For incident test"},
            headers=auth_headers
        )
    dataset_id = ds_resp.json()["id"]

    # 1. Create Incident
    inc_resp = client.post(
        "/api/v1/incidents/",
        json={
            "dataset_id": dataset_id,
            "title": "Severe Outlier Spike Detected in Amount",
            "description": "Isolation Forest flagged abnormal transaction amounts exceeding $4000",
            "severity": "CRITICAL",
            "assigned_to": "admin"
        },
        headers=auth_headers
    )
    assert inc_resp.status_code == 201
    incident = inc_resp.json()
    assert incident["status"] == "OPEN"
    assert incident["severity"] == "CRITICAL"
    inc_id = incident["id"]

    # 2. Update Incident status to INVESTIGATING
    patch_resp = client.patch(
        f"/api/v1/incidents/{inc_id}",
        json={"status": "INVESTIGATING", "root_cause": "Suspected currency scaling decimal shift"},
        headers=auth_headers
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["status"] == "INVESTIGATING"

    # 3. Run Investigation which generates remediation proposals
    inv_resp = client.post(
        f"/api/v1/investigations/{dataset_id}/start",
        json={"incident_id": inc_id},
        headers=auth_headers
    )
    assert inv_resp.status_code == 201

    # 4. List Remediation proposals for this dataset
    rem_resp = client.get(f"/api/v1/remediation/{dataset_id}/list", headers=auth_headers)
    assert rem_resp.status_code == 200
    proposals = rem_resp.json()
    assert len(proposals) > 0
    prop = proposals[0]
    rem_id = prop["id"]

    # 5. Preview remediation transformation
    prev_resp = client.post(f"/api/v1/remediation/{rem_id}/preview", headers=auth_headers)
    assert prev_resp.status_code == 200
    prev_data = prev_resp.json()
    assert "before_preview" in prev_data
    assert "after_preview" in prev_data

    # 6. Human Approval
    action_resp = client.post(
        f"/api/v1/remediation/{rem_id}/action",
        json={"action": "APPROVE", "reviewer_notes": "Approved by lead data engineer"},
        headers=auth_headers
    )
    assert action_resp.status_code == 200
    assert action_resp.json()["status"] == "APPROVED"

    # 7. Safe Execution on non-destructive copy
    exec_resp = client.post(f"/api/v1/remediation/{rem_id}/execute", headers=auth_headers)
    assert exec_resp.status_code == 200
    assert exec_resp.json()["status"] == "EXECUTED"

    # Verify new version was generated
    detail_resp = client.get(f"/api/v1/datasets/{dataset_id}", headers=auth_headers)
    versions = detail_resp.json()["versions"]
    assert len(versions) >= 2  # v1 (original raw) and v2 (remediated copy)

    # 8. Test Export Reports (PDF & CSV)
    inv_id = inv_resp.json()["id"]
    pdf_resp = client.get(f"/api/v1/reports/export/investigation/{inv_id}/pdf", headers=auth_headers)
    assert pdf_resp.status_code == 200
    assert pdf_resp.headers["content-type"] == "application/pdf"
    assert len(pdf_resp.content) > 500  # Generated valid PDF bytes

    csv_resp = client.get(f"/api/v1/reports/export/investigation/{inv_id}/csv", headers=auth_headers)
    assert csv_resp.status_code == 200
    assert "Investigation ID" in csv_resp.text
