from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.datasets import router as datasets_router
from app.api.v1.profiling import router as profiling_router
from app.api.v1.ml_analysis import router as ml_router
from app.api.v1.drift import router as drift_router
from app.api.v1.investigation import router as investigation_router
from app.api.v1.rag import router as rag_router
from app.api.v1.remediation import router as remediation_router
from app.api.v1.incidents import router as incidents_router
from app.api.v1.reports import router as reports_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(datasets_router)
api_router.include_router(profiling_router)
api_router.include_router(ml_router)
api_router.include_router(drift_router)
api_router.include_router(investigation_router)
api_router.include_router(rag_router)
api_router.include_router(remediation_router)
api_router.include_router(incidents_router)
api_router.include_router(reports_router)

__all__ = ["api_router"]

