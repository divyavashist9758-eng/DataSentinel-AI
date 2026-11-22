import time
from typing import Dict, Any
from app.agents.state import InvestigationState, AgentTraceData
from app.agents.llm_factory import LLMFactory

def report_generation_agent(state: InvestigationState) -> InvestigationState:
    """Agent 6: Produces an executive investigation dossier and structured markdown report."""
    start_time = time.time()
    ds_name = state.get("dataset_name", "Dataset")
    v_num = state.get("version_num", 1)
    q_f = state.get("quality_findings", {})
    a_f = state.get("anomaly_findings", {})
    s_f = state.get("schema_findings", {})
    r_f = state.get("root_cause_findings", {})
    rem_p = state.get("remediation_proposals", [])

    def fallback():
        score = q_f.get("overall_score", 100.0)
        status_txt = q_f.get("quality_status", "HEALTHY")
        root_cause = r_f.get("root_cause_hypothesis", "Standard operational baseline.")
        conf = r_f.get("confidence_score", 85)

        markdown_report = f"""# Autonomous Data Investigation Report
**Dataset**: {ds_name} (v{v_num})  
**Quality Status**: {status_txt} ({score}/100)  
**Investigation Confidence**: {conf}%  

## Executive Summary
{q_f.get('summary_insight', '')}

## Machine Learning & Anomaly Findings
{a_f.get('summary_insight', '')}

## Schema & Structural Evolution
{s_f.get('summary_insight', '')}

## Root Cause Analysis
{root_cause}

## Recommended Remediation Actions ({len(rem_p)} Proposals)
"""
        for i, p in enumerate(rem_p, 1):
            markdown_report += f"- **Action {i}**: {p['proposed_action']} on `{p.get('column_name') or 'ALL'}` (Risk: {p['risk_level']}, Confidence: {int(p['confidence']*100)}%)\n  *Impact*: {p['expected_impact']}\n"

        return {
            "title": f"DataSentinel Autonomous Investigation: {ds_name} v{v_num}",
            "status": "COMPLETED",
            "executive_summary": q_f.get('summary_insight', ''),
            "root_cause_hypothesis": root_cause,
            "confidence_score": conf,
            "markdown_content": markdown_report,
            "summary_insight": f"Investigation dossier completed. Identified {len(rem_p)} actionable remediation vectors."
        }

    system_prompt = "You are the Data Sentinel Report Generation Agent. Assemble the investigation report in JSON with keys: title, executive_summary, root_cause_hypothesis, confidence_score, markdown_content, summary_insight."
    user_prompt = f"Dataset: {ds_name} v{v_num}. Quality: {q_f}. Anomalies: {a_f}. Schema: {s_f}. RootCause: {r_f}. Remediations: {len(rem_p)}."

    findings = LLMFactory.generate_completion(system_prompt, user_prompt, fallback)
    elapsed_ms = int((time.time() - start_time) * 1000)

    trace: AgentTraceData = {
        "agent_name": "Report Generation Agent",
        "role_description": "Generates executive audit reports, technical summaries, and remediation roadmaps",
        "status": "SUCCESS",
        "execution_time_ms": elapsed_ms,
        "findings": findings,
        "summary_insight": findings.get("summary_insight", "Investigation report compiled."),
        "rag_sources": []
    }

    state["final_report"] = findings
    state["agent_traces"].append(trace)
    return state

