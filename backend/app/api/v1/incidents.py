import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.exceptions import EntityNotFoundException
from app.models.incident import Incident
from app.models.dataset import Dataset
from app.models.user import User
from app.schemas.incident import IncidentCreate, IncidentUpdate, IncidentOut
from app.api.deps import get_current_user, require_analyst, record_audit

router = APIRouter(prefix="/incidents", tags=["Incident Management"])

@router.post("/", response_model=IncidentOut, status_code=status.HTTP_201_CREATED)
def create_incident(
    req: IncidentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst)
):
    """Create a new data quality or schema degradation incident."""
    dataset = db.query(Dataset).filter(Dataset.id == req.dataset_id).first()
    if not dataset:
        raise EntityNotFoundException("Dataset", req.dataset_id)

    now_iso = datetime.datetime.utcnow().isoformat()
    timeline = [{
        "timestamp": now_iso,
        "event": "INCIDENT_CREATED",
        "actor": current_user.username,
        "details": f"Incident logged with {req.severity} severity"
    }]

    incident = Incident(
        dataset_id=req.dataset_id,
        version_id=req.version_id,
        title=req.title,
        description=req.description,
        severity=req.severity.upper(),
        status="OPEN",
        assigned_to=req.assigned_to or current_user.username,
        timeline=timeline
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)

    record_audit(
        db=db,
        action="CREATE_INCIDENT",
        entity_type="incident",
        entity_id=incident.id,
        user_id=current_user.id,
        details={"title": incident.title, "severity": incident.severity}
    )

    inc_dict = IncidentOut.model_validate(incident).model_dump()
    inc_dict["dataset_name"] = dataset.name
    return inc_dict

@router.get("/", response_model=List[IncidentOut])
def list_incidents(
    status_filter: Optional[str] = Query(None),
    severity_filter: Optional[str] = Query(None),
    dataset_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List data quality incidents with optional status, severity, and dataset filters."""
    q = db.query(Incident)
    if status_filter:
        q = q.filter(Incident.status == status_filter.upper())
    if severity_filter:
        q = q.filter(Incident.severity == severity_filter.upper())
    if dataset_id:
        q = q.filter(Incident.dataset_id == dataset_id)

    incidents = q.order_by(Incident.created_at.desc()).all()
    results = []
    for inc in incidents:
        d = IncidentOut.model_validate(inc).model_dump()
        d["dataset_name"] = inc.dataset.name if inc.dataset else None
        results.append(d)
    return results

@router.get("/{incident_id}", response_model=IncidentOut)
def get_incident_detail(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve detailed incident record with full chronological timeline."""
    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    if not inc:
        raise EntityNotFoundException("Incident", incident_id)

    d = IncidentOut.model_validate(inc).model_dump()
    d["dataset_name"] = inc.dataset.name if inc.dataset else None
    return d

@router.patch("/{incident_id}", response_model=IncidentOut)
def update_incident(
    incident_id: int,
    req: IncidentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst)
):
    """Update incident status, severity, root cause, or resolution notes."""
    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    if not inc:
        raise EntityNotFoundException("Incident", incident_id)

    timeline = list(inc.timeline or [])
    now_iso = datetime.datetime.utcnow().isoformat()

    if req.status and req.status.upper() != inc.status:
        old_status = inc.status
        inc.status = req.status.upper()
        timeline.append({
            "timestamp": now_iso,
            "event": f"STATUS_CHANGED_{inc.status}",
            "actor": current_user.username,
            "details": f"Status updated from {old_status} to {inc.status}"
        })

    if req.severity:
        inc.severity = req.severity.upper()
    if req.title:
        inc.title = req.title
    if req.description:
        inc.description = req.description
    if req.assigned_to:
        inc.assigned_to = req.assigned_to
    if req.root_cause:
        inc.root_cause = req.root_cause
    if req.resolution_notes:
        inc.resolution_notes = req.resolution_notes

    inc.timeline = timeline
    db.commit()
    db.refresh(inc)

    record_audit(
        db=db,
        action="UPDATE_INCIDENT",
        entity_type="incident",
        entity_id=inc.id,
        user_id=current_user.id,
        details={"status": inc.status, "severity": inc.severity}
    )

    d = IncidentOut.model_validate(inc).model_dump()
    d["dataset_name"] = inc.dataset.name if inc.dataset else None
    return d

