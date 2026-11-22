from typing import Dict, Any, List
from fastapi import APIRouter, Depends, Response, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.core.exceptions import EntityNotFoundException
from app.models.dataset import Dataset
from app.models.profiling import ProfilingResult
from app.models.anomaly import AnomalyResult
from app.models.drift import DriftResult
from app.models.incident import Incident
from app.models.investigation import Investigation
from app.models.remediation import RemediationSuggestion
from app.models.audit import AuditLog
from app.models.user import User
from app.services.report_generator import ReportGenerator
from app.api.deps import get_current_user

router = APIRouter(prefix="/reports", tags=["Analytics & Reporting"])

@router.get("/dashboard/metrics")
def get_dashboard_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Provide real aggregated telemetry metrics across all datasets, pipelines, and incidents."""
    total_datasets = db.query(Dataset).filter(Dataset.is_active == True).count()
    
    # Calculate average quality score across latest profiling runs
    latest_profiles = (
        db.query(ProfilingResult.overall_score)
        .order_by(ProfilingResult.created_at.desc())
        .limit(20)
        .all()
    )
    avg_quality = round(sum([p[0] for p in latest_profiles]) / len(latest_profiles), 1) if latest_profiles else 100.0

    # Total anomalies
    total_anomalies = db.query(func.sum(AnomalyResult.anomalous_rows_count)).scalar() or 0

    # Total drift events
    total_drift_events = db.query(DriftResult).filter(DriftResult.overall_drift_detected == True).count()

    # Incident counts by severity
    incidents = db.query(Incident).all()
    severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    status_counts = {"OPEN": 0, "INVESTIGATING": 0, "REMEDIATED": 0, "RESOLVED": 0}

    for inc in incidents:
        sev = inc.severity.upper()
        if sev in severity_counts:
            severity_counts[sev] += 1
        st = inc.status.upper()
        if st in status_counts:
            status_counts[st] += 1

    # Pending remediations
    pending_remediations = db.query(RemediationSuggestion).filter(RemediationSuggestion.status == "PENDING").count()

    # Recent historical score trend
    recent_runs = (
        db.query(ProfilingResult.created_at, ProfilingResult.overall_score, Dataset.name)
        .join(Dataset, ProfilingResult.dataset_id == Dataset.id)
        .order_by(ProfilingResult.created_at.desc())
        .limit(10)
        .all()
    )
    score_trends = [
        {
            "timestamp": r[0].strftime("%b %d, %H:%M"),
            "score": round(float(r[1]), 1),
            "dataset": r[2]
        }
        for r in reversed(recent_runs)
    ]

    # Recent audit logs
    recent_audits = (
        db.query(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .limit(8)
        .all()
    )
    audit_list = [
        {
            "id": a.id,
            "action": a.action,
            "entity_type": a.entity_type,
            "entity_id": a.entity_id,
            "timestamp": a.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
        for a in recent_audits
    ]

    return {
        "overall_health_score": avg_quality,
        "total_datasets": total_datasets,
        "total_anomalies_detected": int(total_anomalies),
        "total_drift_events": total_drift_events,
        "pending_remediations": pending_remediations,
        "incident_severity_distribution": severity_counts,
        "incident_status_distribution": status_counts,
        "quality_score_trends": score_trends,
        "recent_audit_trail": audit_list
    }

@router.get("/export/investigation/{investigation_id}/pdf")
def export_investigation_pdf(
    investigation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate and download a PDF investigation dossier."""
    inv = db.query(Investigation).filter(Investigation.id == investigation_id).first()
    if not inv:
        raise EntityNotFoundException("Investigation", investigation_id)

    pdf_bytes = ReportGenerator.generate_investigation_pdf(inv, inv.dataset)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=investigation_report_{inv.id}.pdf"}
    )

@router.get("/export/investigation/{investigation_id}/csv")
def export_investigation_csv(
    investigation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export investigation agent traces and findings as CSV."""
    inv = db.query(Investigation).filter(Investigation.id == investigation_id).first()
    if not inv:
        raise EntityNotFoundException("Investigation", investigation_id)

    csv_str = ReportGenerator.generate_investigation_csv(inv, inv.dataset)
    return Response(
        content=csv_str,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=investigation_traces_{inv.id}.csv"}
    )
