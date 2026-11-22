import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class DriftResult(Base):
    __tablename__ = "drift_results"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    baseline_version_id = Column(Integer, ForeignKey("dataset_versions.id", ondelete="CASCADE"), nullable=False)
    current_version_id = Column(Integer, ForeignKey("dataset_versions.id", ondelete="CASCADE"), nullable=False)
    overall_drift_detected = Column(Boolean, default=False, nullable=False)
    drift_score = Column(Float, default=0.0, nullable=False)
    drifted_features_count = Column(Integer, default=0, nullable=False)
    total_features_count = Column(Integer, default=0, nullable=False)
    feature_metrics = Column(JSON, nullable=False)  # KS-stat, p-value, PSI, distribution bins
    schema_diff = Column(JSON, nullable=True)  # added, removed, type_changes
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
