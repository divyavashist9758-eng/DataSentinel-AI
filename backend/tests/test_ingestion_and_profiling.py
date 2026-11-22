import os

def test_dataset_upload_and_profiling(client, auth_headers):
    sample_file_path = "backend/sample_data/customers_clean.csv"
    assert os.path.exists(sample_file_path)

    with open(sample_file_path, "rb") as f:
        response = client.post(
            "/api/v1/datasets/upload",
            files={"file": ("customers_clean.csv", f, "text/csv")},
            data={"name": "Clean Customers Baseline", "description": "Benchmark baseline customer dataset"},
            headers=auth_headers
        )

    assert response.status_code == 201
    dataset = response.json()
    assert dataset["name"] == "Clean Customers Baseline"
    assert dataset["row_count"] == 500
    assert dataset["column_count"] == 6
    assert dataset["file_type"] == "csv"
    assert dataset["latest_quality_score"] is not None
    assert dataset["latest_quality_score"] > 85.0
    dataset_id = dataset["id"]

    # Verify dataset details and sample preview
    detail_resp = client.get(f"/api/v1/datasets/{dataset_id}", headers=auth_headers)
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert len(detail["sample_rows"]) == 10
    assert len(detail["versions"]) == 1

    # Verify profiling results
    prof_resp = client.get(f"/api/v1/profiling/{dataset_id}/latest", headers=auth_headers)
    assert prof_resp.status_code == 200
    prof = prof_resp.json()
    assert prof["total_rows"] == 500
    assert prof["total_columns"] == 6
    assert "quality_breakdown" in prof
    assert prof["quality_breakdown"]["completeness_score"] == 100.0
    assert "age" in prof["column_metrics"]
    assert prof["column_metrics"]["age"]["inferred_type"] == "numeric"

