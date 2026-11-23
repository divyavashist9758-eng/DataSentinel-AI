from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field

class IncidentCreate(BaseModel):
    dataset_id: int
    version_id: Optional[int] = None
    title: str = Field(..., min_length=3, max_length=255)
    description: str
    severity: str = Field(default="MEDIUM")  # CRITICAL, HIGH, MEDIUM, LOW
    assigned_to: Optional[str] = None

class IncidentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None  # OPEN, INVESTIGATING, REMEDIATED, RESOLVED
    assigned_to: Optional[str] = None
    root_cause: Optional[str] = None
    resolution_notes: Optional[str] = None

class IncidentTimelineEvent(BaseModel):
    timestamp: str
    event: str
    actor: str
    details: Optional[str] = None

class IncidentOut(BaseModel):
    id: int
    dataset_id: int
    dataset_name: Optional[str] = None
    version_id: Optional[int] = None
    title: str
    description: str
    severity: str
    status: str
    root_cause: Optional[str] = None
    assigned_to: Optional[str] = None
    resolution_notes: Optional[str] = None
    timeline: Optional[List[IncidentTimelineEvent]] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

