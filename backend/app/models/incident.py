import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    version_id = Column(Integer, ForeignKey("dataset_versions.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(50), default="MEDIUM", nullable=False)  # CRITICAL, HIGH, MEDIUM, LOW
    status = Column(String(50), default="OPEN", nullable=False)  # OPEN, INVESTIGATING, REMEDIATED, RESOLVED
    root_cause = Column(Text, nullable=True)
    assigned_to = Column(String(100), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    timeline = Column(JSON, nullable=True)  # List of timestamped events
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    # Relationships
    dataset = relationship("Dataset", back_populates="incidents")
    investigations = relationship("Investigation", back_populates="incident", cascade="all, delete-orphan")
    remediations = relationship("RemediationSuggestion", back_populates="incident")

