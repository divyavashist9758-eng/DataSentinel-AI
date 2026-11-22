from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class AnomalyDetectionRequest(BaseModel):
    detector_type: str = Field(default="isolation_forest")  # isolation_forest, iqr_fence, z_score
    contamination_rate: float = Field(default=0.05, ge=0.01, le=0.5)
    selected_columns: Optional[List[str]] = None

class AnomalySample(BaseModel):
    row_index: int
    anomaly_score: float
    values: Dict[str, Any]
    flagged_reasons: List[str]

class AnomalyOut(BaseModel):
    id: int
    dataset_id: int
    version_id: Optional[int] = None
    detector_type: str
    contamination_rate: float
    anomalous_rows_count: int
    total_evaluated_rows: int
    anomaly_indices: List[int]
    feature_importance: Dict[str, float]
    anomaly_samples: List[AnomalySample]
    created_at: datetime

    class Config:
        from_attributes = True

