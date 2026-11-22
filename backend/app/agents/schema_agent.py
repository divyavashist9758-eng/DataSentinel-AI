import time
from typing import Dict, Any
from app.agents.state import InvestigationState, AgentTraceData
from app.agents.llm_factory import LLMFactory

def schema_analysis_agent(state: InvestigationState) -> InvestigationState:
    """Agent 3: Explains structural mutations, added/removed columns, and schema drift."""
    start_time = time.time()
    schema_diff = state.get("schema_diff", {})
    drift_data = state.get("drift_data", {})

    added = schema_diff.get("added_columns", [])
    removed = schema_diff.get("removed_columns", [])
    type_changes = schema_diff.get("type_changes", [])
    nullability = schema_diff.get("nullability_changes", [])
    unexp_cats = schema_diff.get("unexpected_categories", [])

    def fallback():
        changes = []
        if added:
            changes.append(f"Added columns: {', '.join(added)}")
        if removed:
            changes.append(f"Removed columns: {', '.join(removed)}")
        if type_changes:
            changes.append(f"Type conversions: {', '.join([f'{tc['column']} ({tc['baseline_type']} -> {tc['current_type']})' for tc in type_changes])}")
        if nullability:
            changes.append(f"Nullability breaches: {', '.join([nc['column'] for nc in nullability])}")
        if unexp_cats:
            changes.append(f"New categorical values: {', '.join([f'{uc['column']}: {uc['new_categories']}' for uc in unexp_cats])}")

        has_drift = bool(added or removed or type_changes or nullability or unexp_cats)
        insight = (
            f"Structural schema mutations detected: {'; '.join(changes)}."
            if has_drift else "Schema structure is stable and identical to historical baseline."
        )
        return {
            "schema_mutations_detected": has_drift,
            "breaking_changes": bool(removed or type_changes),
            "added_columns": added,
            "removed_columns": removed,
            "type_changes": type_changes,
            "nullability_changes": nullability,
            "unexpected_categories": unexp_cats,
            "summary_insight": insight
        }

    system_prompt = "You are the Data Sentinel Schema Analysis Agent. Analyze schema mutations against historical baselines into JSON with keys: schema_mutations_detected, breaking_changes, summary_insight."
    user_prompt = f"Added: {added}, Removed: {removed}, TypeChanges: {type_changes}, Nullability: {nullability}, Categories: {unexp_cats}."

    findings = LLMFactory.generate_completion(system_prompt, user_prompt, fallback)
    elapsed_ms = int((time.time() - start_time) * 1000)

    trace: AgentTraceData = {
        "agent_name": "Schema Analysis Agent",
        "role_description": "Analyzes structural mutations, added/removed columns, and datatype casting drift",
        "status": "SUCCESS",
        "execution_time_ms": elapsed_ms,
        "findings": findings,
        "summary_insight": findings.get("summary_insight", "Schema analysis completed."),
        "rag_sources": []
    }

    state["schema_findings"] = findings
    state["agent_traces"].append(trace)
    return state

