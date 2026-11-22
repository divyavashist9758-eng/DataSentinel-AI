import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(100), nullable=False)  # UPLOAD, PROFILE, DETECT_ANOMALIES, DRIFT_CHECK, INVESTIGATE, APPROVE_REMEDIATION, REJECT_REMEDIATION, EXECUTE_REMEDIATION, CREATE_INCIDENT, RESOLVE_INCIDENT
    entity_type = Column(String(100), nullable=False)  # dataset, version, remediation, incident, investigation
    entity_id = Column(String(100), nullable=False)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="audit_logs")

