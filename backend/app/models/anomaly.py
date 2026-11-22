import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class AnomalyResult(Base):
    __tablename__ = "anomaly_results"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    version_id = Column(Integer, ForeignKey("dataset_versions.id", ondelete="CASCADE"), nullable=True, index=True)
    detector_type = Column(String(100), nullable=False)  # isolation_forest, iqr_fence, z_score
    contamination_rate = Column(Float, default=0.05, nullable=False)
    anomalous_rows_count = Column(Integer, default=0, nullable=False)
    total_evaluated_rows = Column(Integer, default=0, nullable=False)
    anomaly_indices = Column(JSON, nullable=True)  # List of row indices
    feature_importance = Column(JSON, nullable=True)  # Columns contributing most to anomaly
    anomaly_samples = Column(JSON, nullable=True)  # Detailed sampled rows with scores
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Relationships
    dataset = relationship("Dataset", back_populates="anomalies")
