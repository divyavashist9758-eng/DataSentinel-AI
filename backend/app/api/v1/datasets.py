import os
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.exceptions import EntityNotFoundException, AuthorizationException
from app.models.dataset import Dataset, DatasetVersion
from app.models.profiling import ProfilingResult
from app.models.user import User
from app.schemas.dataset import DatasetOut, DatasetDetailOut
from app.services.ingestion import IngestionService
from app.services.profiling_service import ProfilingService
from app.api.deps import get_current_user, record_audit

router = APIRouter(prefix="/datasets", tags=["Datasets"])

@router.post("/upload", response_model=DatasetOut, status_code=status.HTTP_201_CREATED)
def upload_dataset(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload and ingest a new CSV, Excel, or JSON dataset."""
    dataset_name = name or file.filename or "uploaded_dataset"
    dataset = IngestionService.ingest_uploaded_dataset(
        db=db,
        upload_file=file,
        dataset_name=dataset_name,
        description=description or "",
        owner=current_user
    )

    # Automatically run initial profiling on version 1
    v1 = dataset.versions[0]
    prof = ProfilingService.run_profiling(db, dataset.id, v1.id)

    record_audit(
        db=db,
        action="DATASET_UPLOAD",
        entity_type="dataset",
        entity_id=dataset.id,
        user_id=current_user.id,
        details={"name": dataset.name, "rows": dataset.row_count, "cols": dataset.column_count}
    )

    # Attach latest score for response
    dataset_dict = DatasetOut.model_validate(dataset).model_dump()
    dataset_dict["latest_quality_score"] = prof.overall_score
    dataset_dict["versions_count"] = 1
    return dataset_dict

@router.get("/", response_model=List[DatasetOut])
def list_datasets(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all available datasets with their latest quality scores."""
    datasets = db.query(Dataset).filter(Dataset.is_active == True).order_by(Dataset.created_at.desc()).offset(skip).limit(limit).all()

    results = []
    for d in datasets:
        d_out = DatasetOut.model_validate(d).model_dump()
        latest_prof = db.query(ProfilingResult).filter(ProfilingResult.dataset_id == d.id).order_by(ProfilingResult.created_at.desc()).first()
        d_out["latest_quality_score"] = latest_prof.overall_score if latest_prof else None
        d_out["versions_count"] = len(d.versions)
        results.append(d_out)
    return results

@router.get("/{dataset_id}", response_model=DatasetDetailOut)
def get_dataset_detail(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dataset details, versions, schemas, and a 10-row sample preview."""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id, Dataset.is_active == True).first()
    if not dataset:
        raise EntityNotFoundException("Dataset", dataset_id)

    latest_prof = db.query(ProfilingResult).filter(ProfilingResult.dataset_id == dataset.id).order_by(ProfilingResult.created_at.desc()).first()
    d_out = DatasetDetailOut.model_validate(dataset).model_dump()
    d_out["latest_quality_score"] = latest_prof.overall_score if latest_prof else None
    d_out["versions_count"] = len(dataset.versions)

    # Load 10 sample preview rows
    try:
        df = IngestionService.load_dataframe(dataset.file_path, dataset.file_type)
        sample_rows = df.head(10).fillna("").to_dict(orient="records")
        d_out["sample_rows"] = sample_rows
    except Exception:
        d_out["sample_rows"] = []

    return d_out

@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dataset(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Soft-delete or delete a dataset with permission validation."""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise EntityNotFoundException("Dataset", dataset_id)

    if dataset.owner_id != current_user.id and current_user.role != "admin":
        raise AuthorizationException("You do not have permission to delete this dataset")

    dataset.is_active = False
    db.commit()

    record_audit(
        db=db,
        action="DATASET_DELETE",
        entity_type="dataset",
        entity_id=dataset.id,
        user_id=current_user.id
    )
    return None
