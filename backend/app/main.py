from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.core.database import init_db, SessionLocal
from app.core.logging import logger
from app.core.exceptions import DataSentinelException
from app.core.security import hash_password
from app.models.user import User
from app.api.v1 import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB and seed demo admin user
    logger.info("Initializing DataSentinel AI Backend...")
    init_db()

    db = SessionLocal()
    try:
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            admin_user = User(
                email="admin@datasentinel.ai",
                username="admin",
                full_name="System Administrator",
                role="admin",
                hashed_password=hash_password("admin123"),
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            logger.info("Created default system administrator account (admin / admin123).")
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
    finally:
        db.close()

    yield
    logger.info("Shutting down DataSentinel AI Backend...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Autonomous AI-Powered Data Quality, Observability & Intelligence Platform",
    lifespan=lifespan
)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Centralized exception handling
@app.exception_handler(DataSentinelException)
async def datasentinel_exception_handler(request: Request, exc: DataSentinelException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error_type": exc.__class__.__name__}
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected server error occurred. Please consult system logs.", "error": str(exc)}
    )

@app.get("/health", tags=["Health"])
def health_check():
    """System health inspection endpoint."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }

# Mount API V1 routes
app.include_router(api_router, prefix=settings.API_V1_STR)
