import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class RemediationSuggestion(Base):
    __tablename__ = "remediation_suggestions"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    version_id = Column(Integer, ForeignKey("dataset_versions.id", ondelete="SET NULL"), nullable=True)
    incident_id = Column(Integer, ForeignKey("incidents.id", ondelete="SET NULL"), nullable=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id", ondelete="SET NULL"), nullable=True)
    
    problem_type = Column(String(100), nullable=False)  # missing_values, duplicate_rows, invalid_type, outlier, schema_mismatch
    column_name = Column(String(255), nullable=True)
    proposed_action = Column(String(100), nullable=False)  # impute_mean, impute_median, impute_mode, drop_nulls, deduplicate, clip_iqr, cast_type
    parameters = Column(JSON, nullable=True)  # Strategy parameters
    
    hypothesis = Column(Text, nullable=True)
    expected_impact = Column(Text, nullable=False)
    risk_level = Column(String(50), default="LOW", nullable=False)  # LOW, MEDIUM, HIGH
    confidence = Column(Float, default=0.90, nullable=False)
    supporting_evidence = Column(Text, nullable=True)
    
    status = Column(String(50), default="PENDING", nullable=False)  # PENDING, APPROVED, REJECTED, EXECUTED
    reviewed_by = Column(String(100), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    execution_result = Column(JSON, nullable=True)  # new_version_id, rows_affected, before_stats, after_stats
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Relationships
    dataset = relationship("Dataset", back_populates="remediations")
    incident = relationship("Incident", back_populates="remediations")
    investigation = relationship("Investigation", back_populates="remediations")

