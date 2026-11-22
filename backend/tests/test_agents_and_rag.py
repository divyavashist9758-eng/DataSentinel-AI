def test_rag_knowledge_retrieval(client, auth_headers):
    # Query for currency and outlier incidents
    resp = client.get("/api/v1/rag/search?query=currency%20outlier%20amount", headers=auth_headers)
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) > 0
    top_result = results[0]
    assert "citation" in top_result
    assert "relevance_score" in top_result

def test_langgraph_multi_agent_investigation(client, auth_headers):
    # Upload drifted customer dataset
    with open("backend/sample_data/customers_drifted.csv", "rb") as f:
        ds_resp = client.post(
            "/api/v1/datasets/upload",
            files={"file": ("customers_drifted.csv", f, "text/csv")},
            data={"name": "Investigation Target Dataset", "description": "Drifted dataset with missing values"},
            headers=auth_headers
        )
    dataset_id = ds_resp.json()["id"]

    # Start multi-agent LangGraph investigation
    inv_resp = client.post(
        f"/api/v1/investigations/{dataset_id}/start",
        json={"focus_areas": ["quality", "anomalies", "schema", "drift"]},
        headers=auth_headers
    )
    assert inv_resp.status_code == 201
    inv = inv_resp.json()
    assert inv["dataset_id"] == dataset_id
    assert inv["status"] in ["completed", "completed_with_warnings"]
    assert inv["confidence_score"] >= 75
    assert len(inv["agent_traces"]) == 6  # All 6 specialized agents executed!

    # Check that each agent produced its dedicated trace
    agent_names = [t["agent_name"] for t in inv["agent_traces"]]
    assert "Data Quality Agent" in agent_names
    assert "Anomaly Investigation Agent" in agent_names
    assert "Schema Analysis Agent" in agent_names
    assert "Root Cause Analysis Agent" in agent_names
    assert "Remediation Agent" in agent_names
    assert "Report Generation Agent" in agent_names

