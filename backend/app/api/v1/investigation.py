from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.exceptions import EntityNotFoundException
from app.models.dataset import Dataset, DatasetVersion
from app.models.profiling import ProfilingResult
from app.models.anomaly import AnomalyResult
from app.models.drift import DriftResult
from app.models.investigation import Investigation
from app.models.remediation import RemediationSuggestion
from app.models.user import User
from app.schemas.investigation import InvestigationRequest, InvestigationOut
from app.agents.state import InvestigationState
from app.agents.workflow import run_investigation
from app.services.profiling_service import ProfilingService
from app.services.ml_engine import MLEngine
from app.services.drift_engine import DriftEngine
from app.api.deps import get_current_user, record_audit

router = APIRouter(prefix="/investigations", tags=["AI Investigation Center"])

@router.post("/{dataset_id}/start", response_model=InvestigationOut, status_code=status.HTTP_201_CREATED)
def start_investigation(
    dataset_id: int,
    req: InvestigationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Trigger the autonomous multi-agent LangGraph investigation workflow."""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise EntityNotFoundException("Dataset", dataset_id)

    target_ver = None
    if req.version_id:
        target_ver = db.query(DatasetVersion).filter(DatasetVersion.id == req.version_id).first()
    if not target_ver:
        target_ver = dataset.versions[0] if dataset.versions else None

    # Fetch or auto-run telemetry required for investigation
    prof = db.query(ProfilingResult).filter(ProfilingResult.dataset_id == dataset.id).order_by(ProfilingResult.created_at.desc()).first()
    if not prof:
        prof = ProfilingService.run_profiling(db, dataset.id, target_ver.id if target_ver else None)

    anom = db.query(AnomalyResult).filter(AnomalyResult.dataset_id == dataset.id).order_by(AnomalyResult.created_at.desc()).first()
    if not anom:
        anom = MLEngine.run_anomaly_analysis(db, dataset.id, target_ver.id if target_ver else None)

    drift = db.query(DriftResult).filter(DriftResult.dataset_id == dataset.id).order_by(DriftResult.created_at.desc()).first()

    # Build initial LangGraph InvestigationState
    initial_state: InvestigationState = {
        "dataset_id": dataset.id,
        "dataset_name": dataset.name,
        "version_num": target_ver.version_num if target_ver else 1,
        "total_rows": dataset.row_count,
        "total_columns": dataset.column_count,
        "profiling_data": {
            "overall_score": prof.overall_score,
            "total_rows": prof.total_rows,
            "missing_cells_count": prof.missing_cells_count,
            "duplicate_rows_count": prof.duplicate_rows_count,
            "column_metrics": prof.column_metrics
        },
        "anomaly_data": {
            "anomalous_rows_count": anom.anomalous_rows_count,
            "total_evaluated_rows": anom.total_evaluated_rows,
            "feature_importance": anom.feature_importance,
            "anomaly_samples": anom.anomaly_samples
        },
        "drift_data": {
            "overall_drift_detected": drift.overall_drift_detected if drift else False,
            "drift_score": drift.drift_score if drift else 0.0,
            "feature_metrics": drift.feature_metrics if drift else {}
        },
        "schema_diff": drift.schema_diff if drift and drift.schema_diff else {
            "added_columns": [], "removed_columns": [], "type_changes": [], "nullability_changes": [], "unexpected_categories": []
        },
        "quality_findings": {},
        "anomaly_findings": {},
        "schema_findings": {},
        "root_cause_findings": {},
        "remediation_proposals": [],
        "final_report": {},
        "agent_traces": [],
        "errors": []
    }

    # Execute LangGraph workflow
    final_state = run_investigation(initial_state)

    # Persist Investigation record
    investigation = Investigation(
        dataset_id=dataset.id,
        version_id=target_ver.id if target_ver else None,
        incident_id=req.incident_id,
        title=final_state.get("final_report", {}).get("title", f"Autonomous Investigation: {dataset.name}"),
        status="completed" if not final_state.get("errors") else "completed_with_warnings",
        summary=final_state.get("final_report", {}).get("executive_summary", ""),
        root_cause_hypothesis=final_state.get("final_report", {}).get("root_cause_hypothesis", ""),
        confidence_score=final_state.get("final_report", {}).get("confidence_score", 85),
        state_data={
            "quality_findings": final_state.get("quality_findings"),
            "anomaly_findings": final_state.get("anomaly_findings"),
            "schema_findings": final_state.get("schema_findings"),
            "root_cause_findings": final_state.get("root_cause_findings"),
            "errors": final_state.get("errors")
        },
        agent_traces=final_state.get("agent_traces", [])
    )
    db.add(investigation)
    db.flush()

    # Persist remediation suggestions generated by the workflow
    for prop in final_state.get("remediation_proposals", []):
        suggestion = RemediationSuggestion(
            dataset_id=dataset.id,
            version_id=target_ver.id if target_ver else None,
            incident_id=req.incident_id,
            investigation_id=investigation.id,
            problem_type=prop.get("problem_type", "data_quality"),
            column_name=prop.get("column_name"),
            proposed_action=prop.get("proposed_action", "impute_median"),
            parameters=prop.get("parameters", {}),
            hypothesis=prop.get("hypothesis"),
            expected_impact=prop.get("expected_impact", ""),
            risk_level=prop.get("risk_level", "LOW"),
            confidence=prop.get("confidence", 0.9),
            supporting_evidence=prop.get("supporting_evidence"),
            status="PENDING"
        )
        db.add(suggestion)

    record_audit(
        db=db,
        action="RUN_INVESTIGATION",
        entity_type="investigation",
        entity_id=investigation.id,
        user_id=current_user.id,
        details={"traces": len(investigation.agent_traces), "confidence": investigation.confidence_score}
    )

    db.commit()
    db.refresh(investigation)
    return investigation

@router.get("/{investigation_id}", response_model=InvestigationOut)
def get_investigation_detail(
    investigation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve full investigation report with all 6 agent traces."""
    inv = db.query(Investigation).filter(Investigation.id == investigation_id).first()
    if not inv:
        raise EntityNotFoundException("Investigation", investigation_id)
    return inv

@router.get("/dataset/{dataset_id}", response_model=List[InvestigationOut])
def list_dataset_investigations(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all completed investigations for a dataset."""
    return db.query(Investigation).filter(
        Investigation.dataset_id == dataset_id
    ).order_by(Investigation.created_at.desc()).all()

