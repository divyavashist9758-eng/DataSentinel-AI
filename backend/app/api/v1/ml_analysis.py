from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.exceptions import EntityNotFoundException
from app.models.dataset import Dataset
from app.models.anomaly import AnomalyResult
from app.models.user import User
from app.schemas.anomaly import AnomalyDetectionRequest, AnomalyOut
from app.services.ml_engine import MLEngine
from app.api.deps import get_current_user, record_audit

router = APIRouter(prefix="/ml", tags=["Machine Learning Engine"])

@router.post("/{dataset_id}/anomalies", response_model=AnomalyOut, status_code=status.HTTP_201_CREATED)
def trigger_anomaly_detection(
    dataset_id: int,
    req: AnomalyDetectionRequest,
    version_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Run real Isolation Forest or statistical outlier detection on dataset."""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise EntityNotFoundException("Dataset", dataset_id)

    res = MLEngine.run_anomaly_analysis(
        db=db,
        dataset_id=dataset_id,
        version_id=version_id,
        detector_type=req.detector_type,
        contamination=req.contamination_rate,
        selected_columns=req.selected_columns
    )

    record_audit(
        db=db,
        action="RUN_ANOMALY_DETECTION",
        entity_type="anomaly_result",
        entity_id=res.id,
        user_id=current_user.id,
        details={"detector": req.detector_type, "anomalies": res.anomalous_rows_count}
    )
    return res

@router.get("/{dataset_id}/anomalies/latest", response_model=AnomalyOut)
def get_latest_anomalies(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve the latest ML anomaly results for a dataset."""
    res = db.query(AnomalyResult).filter(
        AnomalyResult.dataset_id == dataset_id
    ).order_by(AnomalyResult.created_at.desc()).first()

    if not res:
        # Run automatically if none exists yet
        res = MLEngine.run_anomaly_analysis(db=db, dataset_id=dataset_id)
    return res

