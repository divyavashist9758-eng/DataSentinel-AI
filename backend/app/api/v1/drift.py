from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.exceptions import EntityNotFoundException, ValidationException
from app.models.dataset import Dataset, DatasetVersion
from app.models.drift import DriftResult
from app.models.user import User
from app.schemas.drift import DriftDetectionRequest, DriftOut
from app.services.drift_engine import DriftEngine
from app.api.deps import get_current_user, record_audit

router = APIRouter(prefix="/drift", tags=["Data & Schema Drift"])

@router.post("/{dataset_id}/analyze", response_model=DriftOut, status_code=status.HTTP_201_CREATED)
def trigger_drift_analysis(
    dataset_id: int,
    req: DriftDetectionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Run Kolmogorov-Smirnov (KS) test, PSI, and schema mutation analysis between two versions."""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise EntityNotFoundException("Dataset", dataset_id)

    res = DriftEngine.run_drift_analysis(
        db=db,
        dataset_id=dataset_id,
        baseline_version_id=req.baseline_version_id,
        current_version_id=req.current_version_id,
        p_val_threshold=req.p_value_threshold,
        psi_threshold=req.psi_threshold
    )

    record_audit(
        db=db,
        action="RUN_DRIFT_ANALYSIS",
        entity_type="drift_result",
        entity_id=res.id,
        user_id=current_user.id,
        details={"drift_detected": res.overall_drift_detected, "score": res.drift_score}
    )
    return res

@router.get("/{dataset_id}/latest", response_model=DriftOut)
def get_latest_drift(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve the latest drift analysis results for a dataset."""
    res = db.query(DriftResult).filter(
        DriftResult.dataset_id == dataset_id
    ).order_by(DriftResult.created_at.desc()).first()

    if not res:
        dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            raise EntityNotFoundException("Dataset", dataset_id)
        if len(dataset.versions) >= 2:
            # Auto-run between v1 and v2
            v_base = dataset.versions[-1]
            v_curr = dataset.versions[0]
            res = DriftEngine.run_drift_analysis(db, dataset.id, v_base.id, v_curr.id)
        else:
            raise ValidationException("At least two dataset versions are required to compute drift")

    return res

@router.get("/{dataset_id}/history", response_model=List[DriftOut])
def get_drift_history(
    dataset_id: int,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List historical drift events for a dataset."""
    return db.query(DriftResult).filter(
        DriftResult.dataset_id == dataset_id
    ).order_by(DriftResult.created_at.desc()).limit(limit).all()
