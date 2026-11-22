from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.exceptions import EntityNotFoundException
from app.models.dataset import Dataset
from app.models.profiling import ProfilingResult
from app.models.user import User
from app.schemas.profiling import ProfilingOut
from app.services.profiling_service import ProfilingService
from app.api.deps import get_current_user, record_audit

router = APIRouter(prefix="/profiling", tags=["Data Profiling"])

@router.post("/{dataset_id}/run", response_model=ProfilingOut, status_code=status.HTTP_201_CREATED)
def trigger_profiling(
    dataset_id: int,
    version_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Run automated statistical profiling and calculate transparent 100-point Data Quality Score."""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise EntityNotFoundException("Dataset", dataset_id)

    prof = ProfilingService.run_profiling(db, dataset_id, version_id)

    record_audit(
        db=db,
        action="RUN_PROFILING",
        entity_type="profiling",
        entity_id=prof.id,
        user_id=current_user.id,
        details={"score": prof.overall_score}
    )
    return prof

@router.get("/{dataset_id}/latest", response_model=ProfilingOut)
def get_latest_profiling(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve the most recent profiling results for a dataset."""
    prof = db.query(ProfilingResult).filter(
        ProfilingResult.dataset_id == dataset_id
    ).order_by(ProfilingResult.created_at.desc()).first()

    if not prof:
        raise EntityNotFoundException("Profiling result for dataset", dataset_id)
    return prof

@router.get("/{dataset_id}/history", response_model=List[ProfilingOut])
def get_profiling_history(
    dataset_id: int,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve historical profiling runs for quality score trend analysis."""
    profs = db.query(ProfilingResult).filter(
        ProfilingResult.dataset_id == dataset_id
    ).order_by(ProfilingResult.created_at.desc()).limit(limit).all()
    return profs
