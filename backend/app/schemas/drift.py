from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class DriftDetectionRequest(BaseModel):
    baseline_version_id: int
    current_version_id: int
    p_value_threshold: float = Field(default=0.05, gt=0, lt=1)
    psi_threshold: float = Field(default=0.25, gt=0)

class FeatureDriftMetric(BaseModel):
    column_name: str
    feature_type: str  # numeric, categorical
    is_drifted: bool
    ks_statistic: Optional[float] = None
    p_value: Optional[float] = None
    psi_score: Optional[float] = None
    baseline_distribution: Optional[Dict[str, Any]] = None
    current_distribution: Optional[Dict[str, Any]] = None
    drift_level: str  # NONE, MODERATE, CRITICAL

class SchemaDiffItem(BaseModel):
    added_columns: List[str]
    removed_columns: List[str]
    type_changes: List[Dict[str, str]]
    nullability_changes: List[Dict[str, Any]]
    unexpected_categories: List[Dict[str, Any]]

class DriftOut(BaseModel):
    id: int
    dataset_id: int
    baseline_version_id: int
    current_version_id: int
    overall_drift_detected: bool
    drift_score: float
    drifted_features_count: int
    total_features_count: int
    feature_metrics: Dict[str, FeatureDriftMetric]
    schema_diff: Optional[SchemaDiffItem] = None
    created_at: datetime

    class Config:
        from_attributes = True

