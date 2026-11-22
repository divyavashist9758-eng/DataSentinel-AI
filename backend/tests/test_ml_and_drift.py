import os

def test_anomaly_detection_isolation_forest(client, auth_headers):
    # Upload anomalous json dataset
    anom_file = "backend/sample_data/transactions_anomalous.json"
    assert os.path.exists(anom_file)

    with open(anom_file, "rb") as f:
        upload_resp = client.post(
            "/api/v1/datasets/upload",
            files={"file": ("transactions_anomalous.json", f, "application/json")},
            data={"name": "Anomalous Transactions", "description": "Synthetic transactions with 100x currency errors"},
            headers=auth_headers
        )
    assert upload_resp.status_code == 201
    dataset_id = upload_resp.json()["id"]

    # Trigger Isolation Forest
    ml_resp = client.post(
        f"/api/v1/ml/{dataset_id}/anomalies",
        json={"detector_type": "isolation_forest", "contamination_rate": 0.05},
        headers=auth_headers
    )
    assert ml_resp.status_code == 201
    res = ml_resp.json()
    assert res["anomalous_rows_count"] > 0
    assert len(res["anomaly_samples"]) > 0
    assert "amount" in res["feature_importance"]
    assert res["detector_type"] == "isolation_forest"

def test_data_and_schema_drift(client, auth_headers):
    # Upload baseline
    with open("backend/sample_data/customers_clean.csv", "rb") as f:
        base_resp = client.post(
            "/api/v1/datasets/upload",
            files={"file": ("customers_clean.csv", f, "text/csv")},
            data={"name": "Customer Evolution Baseline", "description": "Baseline for drift test"},
            headers=auth_headers
        )
    dataset_id = base_resp.json()["id"]

    # Upload drifted version
    with open("backend/sample_data/customers_drifted.csv", "rb") as f:
        drift_upload = client.post(
            "/api/v1/datasets/upload",
            files={"file": ("customers_drifted.csv", f, "text/csv")},
            data={"name": "Customer Evolution Drifted", "description": "Younger cohort with added column"},
            headers=auth_headers
        )
    drift_ds_id = drift_upload.json()["id"]

    # Fetch version IDs
    v_base_id = client.get(f"/api/v1/datasets/{dataset_id}", headers=auth_headers).json()["versions"][0]["id"]
    v_curr_id = client.get(f"/api/v1/datasets/{drift_ds_id}", headers=auth_headers).json()["versions"][0]["id"]

    # Trigger drift analysis
    drift_resp = client.post(
        f"/api/v1/drift/{dataset_id}/analyze",
        json={
            "baseline_version_id": v_base_id,
            "current_version_id": v_curr_id,
            "p_value_threshold": 0.05,
            "psi_threshold": 0.25
        },
        headers=auth_headers
    )
    assert drift_resp.status_code == 201
    drift_res = drift_resp.json()
    assert drift_res["overall_drift_detected"] is True
    # Age feature must have drifted significantly (42 vs 26 average)
    assert "age" in drift_res["feature_metrics"]
    assert drift_res["feature_metrics"]["age"]["is_drifted"] is True
    # Schema diff must reflect added column 'loyalty_tier'
    assert "loyalty_tier" in drift_res["schema_diff"]["added_columns"]

