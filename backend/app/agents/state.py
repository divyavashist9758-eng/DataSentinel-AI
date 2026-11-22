from typing import TypedDict, List, Dict, Any, Optional

class AgentTraceData(TypedDict):
    agent_name: str
    role_description: str
    status: str
    execution_time_ms: int
    findings: Dict[str, Any]
    summary_insight: str
    rag_sources: Optional[List[Dict[str, Any]]]

class InvestigationState(TypedDict):
    # Context
    dataset_id: int
    dataset_name: str
    version_num: int
    total_rows: int
    total_columns: int
    
    # Input telemetry
    profiling_data: Dict[str, Any]
    anomaly_data: Dict[str, Any]
    drift_data: Dict[str, Any]
    schema_diff: Dict[str, Any]
    
    # Agent Accumulators
    quality_findings: Dict[str, Any]
    anomaly_findings: Dict[str, Any]
    schema_findings: Dict[str, Any]
    root_cause_findings: Dict[str, Any]
    remediation_proposals: List[Dict[str, Any]]
    final_report: Dict[str, Any]
    
    # Execution traces for each agent
    agent_traces: List[AgentTraceData]
    errors: List[str]
