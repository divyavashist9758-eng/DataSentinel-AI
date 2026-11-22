from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class InvestigationRequest(BaseModel):
    version_id: Optional[int] = None
    incident_id: Optional[int] = None
    focus_areas: Optional[List[str]] = Field(default_factory=lambda: ["quality", "anomalies", "schema", "drift"])

class AgentTrace(BaseModel):
    agent_name: str
    role_description: str
    status: str  # SUCCESS, WARNING, FAILED
    execution_time_ms: int
    findings: Dict[str, Any]
    summary_insight: str
    rag_sources: Optional[List[Dict[str, Any]]] = None

class InvestigationOut(BaseModel):
    id: int
    dataset_id: int
    version_id: Optional[int] = None
    incident_id: Optional[int] = None
    title: str
    status: str
    summary: Optional[str] = None
    root_cause_hypothesis: Optional[str] = None
    confidence_score: int
    agent_traces: List[AgentTrace]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
