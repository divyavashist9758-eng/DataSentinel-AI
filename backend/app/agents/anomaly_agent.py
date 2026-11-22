import time
from typing import Dict, Any
from app.agents.state import InvestigationState, AgentTraceData
from app.agents.llm_factory import LLMFactory

def anomaly_investigation_agent(state: InvestigationState) -> InvestigationState:
    """Agent 2: Investigates multi-dimensional anomalies, outliers, and feature oddities."""
    start_time = time.time()
    anomaly_data = state.get("anomaly_data", {})
    anom_count = anomaly_data.get("anomalous_rows_count", 0)
    total_eval = anomaly_data.get("total_evaluated_rows", 1)
    feature_imp = anomaly_data.get("feature_importance", {})
    samples = anomaly_data.get("anomaly_samples", [])

    def fallback():
        top_features = sorted(feature_imp.items(), key=lambda x: x[1], reverse=True)[:3]
        rate = round((anom_count / max(1, total_eval)) * 100, 2)
        insight = (
            f"Isolation Forest flagged {anom_count} anomalous rows ({rate}% contamination). "
            f"Key driving features: {', '.join([f'{k} ({round(v*100, 1)}% contribution)' for k, v in top_features])}."
            if anom_count > 0 else "No anomalous record clusters detected by Isolation Forest."
        )
        return {
            "anomalies_detected": anom_count > 0,
            "anomalous_count": anom_count,
            "anomaly_rate_percent": rate,
            "primary_driving_features": [k for k, _ in top_features],
            "severity": "HIGH" if rate > 5.0 else ("MEDIUM" if rate > 1.0 else "LOW"),
            "summary_insight": insight
        }

    system_prompt = "You are the Data Sentinel Anomaly Investigation Agent. Synthesize Isolation Forest and outlier detections into JSON with keys: anomalies_detected, severity, primary_driving_features, summary_insight."
    user_prompt = f"Anomalies: {anom_count} of {total_eval} rows. Feature Importance: {feature_imp}. Samples: {len(samples)}."

    findings = LLMFactory.generate_completion(system_prompt, user_prompt, fallback)
    elapsed_ms = int((time.time() - start_time) * 1000)

    trace: AgentTraceData = {
        "agent_name": "Anomaly Investigation Agent",
        "role_description": "Investigates multivariate Isolation Forest outliers and extreme deviation clusters",
        "status": "SUCCESS",
        "execution_time_ms": elapsed_ms,
        "findings": findings,
        "summary_insight": findings.get("summary_insight", "Anomaly investigation completed."),
        "rag_sources": []
    }

    state["anomaly_findings"] = findings
    state["agent_traces"].append(trace)
    return state
