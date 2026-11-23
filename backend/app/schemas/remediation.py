from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field

class RemediationPreviewRequest(BaseModel):
    remediation_id: int
    preview_limit: int = Field(default=10, ge=1, le=100)

class RemediationPreviewOut(BaseModel):
    remediation_id: int
    proposed_action: str
    column_name: Optional[str] = None
    affected_rows_count: int
    before_preview: List[Dict[str, Any]]
    after_preview: List[Dict[str, Any]]
    expected_quality_score_improvement: float

class RemediationActionRequest(BaseModel):
    action: str = Field(..., description="APPROVE, REJECT, or EXECUTE")
    reviewer_notes: Optional[str] = None

class RemediationOut(BaseModel):
    id: int
    dataset_id: int
    version_id: Optional[int] = None
    incident_id: Optional[int] = None
    investigation_id: Optional[int] = None
    problem_type: str
    column_name: Optional[str] = None
    proposed_action: str
    parameters: Optional[Dict[str, Any]] = None
    hypothesis: Optional[str] = None
    expected_impact: str
    risk_level: str
    confidence: float
    supporting_evidence: Optional[str] = None
    status: str
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    execution_result: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

