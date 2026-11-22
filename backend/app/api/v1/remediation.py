from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.exceptions import EntityNotFoundException, ValidationException
from app.models.remediation import RemediationSuggestion
from app.models.user import User
from app.schemas.remediation import (
    RemediationOut,
    RemediationPreviewOut,
    RemediationPreviewRequest,
    RemediationActionRequest,
)
from app.services.remediation_engine import RemediationEngine
from app.api.deps import get_current_user, require_analyst, record_audit

router = APIRouter(prefix="/remediation", tags=["Remediation Approval Center"])

@router.get("/{dataset_id}/list", response_model=List[RemediationOut])
def list_remediations(
    dataset_id: int,
    status_filter: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all AI-generated remediation suggestions for a dataset."""
    q = db.query(RemediationSuggestion).filter(RemediationSuggestion.dataset_id == dataset_id)
    if status_filter:
        q = q.filter(RemediationSuggestion.status == status_filter.upper())
    return q.order_by(RemediationSuggestion.created_at.desc()).all()

@router.post("/{remediation_id}/preview", response_model=RemediationPreviewOut)
def preview_transformation(
    remediation_id: int,
    preview_limit: int = Query(5, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Preview transformation side-by-side on real sample records without modifying data."""
    return RemediationEngine.preview_remediation(db, remediation_id, preview_limit)

@router.post("/{remediation_id}/action", response_model=RemediationOut)
def review_remediation(
    remediation_id: int,
    req: RemediationActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst)
):
    """Human-in-the-loop review: Approve or Reject a remediation recommendation (Analyst/Admin only)."""
    rem = db.query(RemediationSuggestion).filter(RemediationSuggestion.id == remediation_id).first()
    if not rem:
        raise EntityNotFoundException("Remediation suggestion", remediation_id)

    action_upper = req.action.upper()
    if action_upper not in ["APPROVE", "REJECT"]:
        raise ValidationException("Action must be either 'APPROVE' or 'REJECT'")

    rem.status = "APPROVED" if action_upper == "APPROVE" else "REJECTED"
    rem.reviewed_by = current_user.username
    import datetime
    rem.reviewed_at = datetime.datetime.utcnow()

    record_audit(
        db=db,
        action=f"REMEDIATION_{rem.status}",
        entity_type="remediation",
        entity_id=rem.id,
        user_id=current_user.id,
        details={"notes": req.reviewer_notes}
    )

    db.commit()
    db.refresh(rem)
    return rem

@router.post("/{remediation_id}/execute", response_model=RemediationOut)
def execute_remediation(
    remediation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst)
):
    """Execute approved remediation on a newly created copy of the dataset (Analyst/Admin only). Original is never modified."""
    rem = db.query(RemediationSuggestion).filter(RemediationSuggestion.id == remediation_id).first()
    if not rem:
        raise EntityNotFoundException("Remediation suggestion", remediation_id)

    RemediationEngine.execute_approved_remediation(db, remediation_id, current_user.username)
    db.refresh(rem)
    return rem

