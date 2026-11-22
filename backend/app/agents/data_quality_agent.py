import time
from typing import Dict, Any
from app.agents.state import InvestigationState, AgentTraceData
from app.agents.llm_factory import LLMFactory

def data_quality_agent(state: InvestigationState) -> InvestigationState:
    """Agent 1: Evaluates quality metrics, completeness, uniqueness, and SLA compliance."""
    start_time = time.time()
    profiling = state.get("profiling_data", {})
    score = profiling.get("overall_score", 100.0)
    col_metrics = profiling.get("column_metrics", {})
    
    # Identify high-null and duplicate issues
    flagged_columns = []
    for col, m in col_metrics.items():
        if m.get("null_percentage", 0) > 5.0:
            flagged_columns.append({
                "column": col,
                "null_count": m.get("null_count", 0),
                "null_percentage": m.get("null_percentage", 0),
                "type": m.get("inferred_type", "unknown")
            })

    duplicate_rows = profiling.get("duplicate_rows_count", 0)
    total_rows = profiling.get("total_rows", 1)

    def fallback():
        issues = []
        if flagged_columns:
            issues.append(f"{len(flagged_columns)} columns exceed the 5% null threshold ({', '.join([c['column'] for c in flagged_columns[:3]])})")
        if duplicate_rows > 0:
            issues.append(f"{duplicate_rows} duplicate rows detected ({round(duplicate_rows/total_rows*100, 2)}% of dataset)")
        if score < 80.0:
            issues.append(f"Overall Data Quality Score ({score}/100) is below enterprise SLA baseline of 80/100")
        
        status_eval = "DEGRADED" if score < 75.0 else ("WARNING" if score < 90.0 else "HEALTHY")
        return {
            "quality_status": status_eval,
            "overall_score": score,
            "flagged_columns": flagged_columns,
            "duplicate_count": duplicate_rows,
            "summary_insight": f"Data quality is {status_eval}. " + ("; ".join(issues) if issues else "All quality thresholds met.")
        }

    system_prompt = "You are the Data Sentinel Quality Agent. Analyze dataset profiling metrics and summarize quality health in JSON with keys: quality_status, overall_score, summary_insight."
    user_prompt = f"Dataset: {state.get('dataset_name')}, Score: {score}, Null Columns: {flagged_columns}, Duplicates: {duplicate_rows}."

    findings = LLMFactory.generate_completion(system_prompt, user_prompt, fallback)
    elapsed_ms = int((time.time() - start_time) * 1000)

    trace: AgentTraceData = {
        "agent_name": "Data Quality Agent",
        "role_description": "Evaluates quality scores, missing values, duplicates, and column SLA thresholds",
        "status": "SUCCESS",
        "execution_time_ms": elapsed_ms,
        "findings": findings,
        "summary_insight": findings.get("summary_insight", "Quality inspection completed."),
        "rag_sources": []
    }

    state["quality_findings"] = findings
    state["agent_traces"].append(trace)
    return state

