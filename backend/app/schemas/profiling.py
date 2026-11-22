from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class ColumnMetric(BaseModel):
    name: str
    data_type: str
    inferred_type: str
    total_count: int
    null_count: int
    null_percentage: float
    unique_count: int
    unique_percentage: float
    min_value: Optional[Any] = None
    max_value: Optional[Any] = None
    mean_value: Optional[float] = None
    std_value: Optional[float] = None
    median_value: Optional[float] = None
    q25: Optional[float] = None
    q75: Optional[float] = None
    outliers_iqr_count: Optional[int] = 0
    top_frequent_values: Optional[List[Dict[str, Any]]] = None
    histogram: Optional[Dict[str, Any]] = None

class QualityScoreBreakdown(BaseModel):
    overall_score: float
    completeness_score: float
    uniqueness_score: float
    validity_score: float
    consistency_score: float
    penalties: Dict[str, float]

class ProfilingOut(BaseModel):
    id: int
    dataset_id: int
    version_id: Optional[int] = None
    overall_score: float
    total_rows: int
    total_columns: int
    missing_cells_count: int
    duplicate_rows_count: int
    column_metrics: Dict[str, ColumnMetric]
    quality_breakdown: QualityScoreBreakdown
    created_at: datetime

    class Config:
        from_attributes = True

