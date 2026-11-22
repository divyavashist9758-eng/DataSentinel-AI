import time
from typing import Dict, Any, List
from app.agents.state import InvestigationState, AgentTraceData
from app.agents.llm_factory import LLMFactory

def remediation_agent(state: InvestigationState) -> InvestigationState:
    """Agent 5: Synthesizes safe, non-destructive data remediation proposals for human review."""
    start_time = time.time()
    q_findings = state.get("quality_findings", {})
    a_findings = state.get("anomaly_findings", {})
    s_findings = state.get("schema_findings", {})
    r_findings = state.get("root_cause_findings", {})

    proposals: List[Dict[str, Any]] = []

    # 1. Null handling proposals
    flagged_cols = q_findings.get("flagged_columns", [])
    for col_info in flagged_cols:
        col_name = col_info.get("column")
        col_type = col_info.get("type", "numeric")
        if col_type == "numeric":
            action = "impute_median"
            risk = "LOW"
            impact = f"Impute {col_info.get('null_count')} missing values using robust column median; restores completeness."
        elif col_type == "categorical":
            action = "impute_mode"
            risk = "LOW"
            impact = f"Impute {col_info.get('null_count')} missing values using highest-frequency category."
        else:
            action = "impute_constant"
            risk = "LOW"
            impact = f"Fill {col_info.get('null_count')} missing text values with 'UNKNOWN' fallback token."

        proposals.append({
            "problem_type": "missing_values",
            "column_name": col_name,
            "proposed_action": action,
            "parameters": {"strategy": action},
            "hypothesis": f"Missing values in {col_name} stem from incomplete ingestion; imputation preserves sample size.",
            "expected_impact": impact,
            "risk_level": risk,
            "confidence": 0.92,
            "supporting_evidence": f"Column {col_name} exhibits {col_info.get('null_percentage')}% null rate."
        })

    # 2. Duplicate rows proposal
    dup_count = q_findings.get("duplicate_count", 0)
    if dup_count > 0:
        proposals.append({
            "problem_type": "duplicate_rows",
            "column_name": None,
            "proposed_action": "deduplicate",
            "parameters": {"keep": "first"},
            "hypothesis": "Duplicate records introduced by message re-delivery without idempotent deduplication keys.",
            "expected_impact": f"Remove {dup_count} exact duplicate rows; guarantees primary uniqueness.",
            "risk_level": "LOW",
            "confidence": 0.98,
            "supporting_evidence": f"Identified {dup_count} full-row duplicates."
        })

    # 3. Anomaly / Outlier proposal
    driving_features = a_findings.get("primary_driving_features", [])
    for feat in driving_features[:2]:
        proposals.append({
            "problem_type": "outlier",
            "column_name": feat,
            "proposed_action": "clip_iqr",
            "parameters": {"factor": 1.5},
            "hypothesis": f"Extreme values in {feat} skew downstream statistical estimators.",
            "expected_impact": f"Winsorize/clip values in {feat} to 1.5x IQR boundaries without dropping rows.",
            "risk_level": "MEDIUM",
            "confidence": 0.85,
            "supporting_evidence": f"Isolation Forest flagged {feat} as a primary anomaly driver."
        })

    def fallback():
        return {
            "proposals": proposals,
            "total_proposals": len(proposals),
            "summary_insight": f"Formulated {len(proposals)} non-destructive remediation proposals awaiting human review."
        }

    system_prompt = "You are the Data Sentinel Remediation Agent. Review proposed remediation actions into JSON with key 'summary_insight'."
    user_prompt = f"Proposals: {proposals}. Root Cause: {r_findings.get('root_cause_hypothesis')}."

    findings = LLMFactory.generate_completion(system_prompt, user_prompt, fallback)
    elapsed_ms = int((time.time() - start_time) * 1000)

    trace: AgentTraceData = {
        "agent_name": "Remediation Agent",
        "role_description": "Generates actionable non-destructive data correction proposals and risk assessments",
        "status": "SUCCESS",
        "execution_time_ms": elapsed_ms,
        "findings": {
            "proposals": proposals,
            "total_proposals": len(proposals),
            "summary_insight": findings.get("summary_insight", fallback()["summary_insight"])
        },
        "summary_insight": findings.get("summary_insight", fallback()["summary_insight"]),
        "rag_sources": []
    }

    state["remediation_proposals"] = proposals
    state["agent_traces"].append(trace)
    return state
