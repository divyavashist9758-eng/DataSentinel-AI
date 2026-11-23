import json
import datetime
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings
from app.core.logging import logger

def default_json_serializer(obj):
    """Serialize numpy, pandas, and datetime types automatically for JSON columns."""
    if isinstance(obj, (np.integer, int)):
        return int(obj)
    if isinstance(obj, (np.floating, float)):
        return float(obj)
    if isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, (pd.Timestamp, datetime.date, datetime.datetime)):
        return obj.isoformat()
    return str(obj)

def json_dumps_custom(obj):
    return json.dumps(obj, default=default_json_serializer)

connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

database_url = settings.DATABASE_URL

if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+psycopg2://", 1)

engine = create_engine(
    database_url,
    connect_args=connect_args,
    json_serializer=json_dumps_custom,
    echo=False,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """FastAPI database session dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Create all tables in database if they do not exist."""
    import app.models  # Ensure all models are registered
    logger.info("Initializing database schemas...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database schemas initialized successfully.")


