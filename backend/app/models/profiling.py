import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class ProfilingResult(Base):
    __tablename__ = "profiling_results"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    version_id = Column(Integer, ForeignKey("dataset_versions.id", ondelete="CASCADE"), nullable=True, index=True)
    overall_score = Column(Float, nullable=False)  # 0 to 100
    total_rows = Column(Integer, nullable=False)
    total_columns = Column(Integer, nullable=False)
    missing_cells_count = Column(Integer, default=0, nullable=False)
    duplicate_rows_count = Column(Integer, default=0, nullable=False)
    column_metrics = Column(JSON, nullable=False)  # Detailed stats per column
    quality_breakdown = Column(JSON, nullable=False)  # Completeness, Uniqueness, Consistency, Validity scores
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Relationships
    dataset = relationship("Dataset", back_populates="profiling_results")
