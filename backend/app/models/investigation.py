import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class Investigation(Base):
    __tablename__ = "investigations"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    version_id = Column(Integer, ForeignKey("dataset_versions.id", ondelete="SET NULL"), nullable=True)
    incident_id = Column(Integer, ForeignKey("incidents.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), nullable=False)
    status = Column(String(50), default="completed", nullable=False)  # pending, running, completed, failed
    summary = Column(Text, nullable=True)
    root_cause_hypothesis = Column(Text, nullable=True)
    confidence_score = Column(Integer, default=85, nullable=False)  # 0 to 100
    state_data = Column(JSON, nullable=True)  # LangGraph state snapshot
    agent_traces = Column(JSON, nullable=False)  # traces for the 6 agents
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    # Relationships
    dataset = relationship("Dataset", back_populates="investigations")
    incident = relationship("Incident", back_populates="investigations")
    remediations = relationship("RemediationSuggestion", back_populates="investigation")
