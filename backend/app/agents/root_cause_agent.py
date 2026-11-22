import time
from typing import Dict, Any, List
from app.agents.state import InvestigationState, AgentTraceData
from app.agents.llm_factory import LLMFactory
from app.services.rag_engine import rag_engine

def root_cause_analysis_agent(state: InvestigationState) -> InvestigationState:
    """Agent 4: Correlates quality, anomaly, and schema findings with RAG precedents to deduce root causes."""
    start_time = time.time()
    q_findings = state.get("quality_findings", {})
    a_findings = state.get("anomaly_findings", {})
    s_findings = state.get("schema_findings", {})

    # Construct contextual search query for RAG
    query_parts = []
    if q_findings.get("flagged_columns"):
        query_parts.append("missing null values " + " ".join([c["column"] for c in q_findings["flagged_columns"][:2]]))
    if a_findings.get("primary_driving_features"):
        query_parts.append("outlier anomaly " + " ".join(a_findings["primary_driving_features"][:2]))
    if s_findings.get("added_columns") or s_findings.get("type_changes"):
        query_parts.append("schema change unexpected column type")

    search_query = " ".join(query_parts) if query_parts else "data quality incident root cause"
    rag_sources = rag_engine.retrieve_relevant_knowledge(search_query, top_k=2)

    def fallback():
        hypotheses = []
        if a_findings.get("anomalies_detected") and a_findings.get("primary_driving_features"):
            features = ", ".join(a_findings["primary_driving_features"])
            hypotheses.append(f"Unit scaling discrepancy, currency conversion error, or decimal misplacement affecting [{features}]")
        if q_findings.get("flagged_columns"):
            null_cols = ", ".join([c["column"] for c in q_findings["flagged_columns"][:2]])
            hypotheses.append(f"Upstream ETL pipeline timeout or incomplete payload ingestion in [{null_cols}]")
        if s_findings.get("breaking_changes"):
            hypotheses.append("Uncoordinated upstream microservice release introducing breaking schema contract mutation")
        if not hypotheses:
            hypotheses.append("No critical structural or distributional degradation identified; dataset within acceptable operating tolerances")

        root_cause = " | ".join(hypotheses)
        confidence = 88 if rag_sources and rag_sources[0]["relevance_score"] > 0.2 else 80

        citation_texts = [s.get("citation", "") for s in rag_sources]
        return {
            "root_cause_hypothesis": root_cause,
            "confidence_score": confidence,
            "correlations_identified": len(hypotheses),
            "rag_precedents_matched": len(rag_sources),
            "summary_insight": f"Root Cause: {root_cause}. (Precedents: {', '.join(citation_texts) if citation_texts else 'None'})"
        }

    system_prompt = "You are the Data Sentinel Root Cause Analysis Agent. Correlate data quality, anomaly, and schema issues into a cohesive root cause hypothesis in JSON with keys: root_cause_hypothesis, confidence_score, summary_insight."
    user_prompt = f"Quality: {q_findings}. Anomaly: {a_findings}. Schema: {s_findings}. Precedents: {rag_sources}."

    findings = LLMFactory.generate_completion(system_prompt, user_prompt, fallback)
    elapsed_ms = int((time.time() - start_time) * 1000)

    trace: AgentTraceData = {
        "agent_name": "Root Cause Analysis Agent",
        "role_description": "Correlates multi-source anomalies with historical incident patterns and RAG runbooks",
        "status": "SUCCESS",
        "execution_time_ms": elapsed_ms,
        "findings": findings,
        "summary_insight": findings.get("summary_insight", "Root cause synthesis completed."),
        "rag_sources": rag_sources
    }

    state["root_cause_findings"] = findings
    state["agent_traces"].append(trace)
    return state

