import os
from pathlib import Path
from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "DataSentinel AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Authentication & Security
    SECRET_KEY: str = "datasentinel-dev-secret-key-must-be-changed-in-production-123456"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # Database (PostgreSQL for production/docker, SQLite for lightweight zero-config local run)
    DATABASE_URL: str = "sqlite:///./datasentinel.db"
    
    # File Storage
    UPLOAD_DIR: str = str(BASE_DIR / "data" / "uploads")
    REMEDIATED_DIR: str = str(BASE_DIR / "data" / "remediated")
    RAG_STORE_DIR: str = str(BASE_DIR / "data" / "rag_store")
    MAX_UPLOAD_SIZE_MB: int = 100  # 100 Megabytes
    
    # LLM Settings (Groq API primary, local deterministic fallback)
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    # Redis / Celery (Optional)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "*"
    ]

    model_config = {
        "env_file": ".env",
        "extra": "ignore",
        "case_sensitive": True
    }

settings = Settings()

# Ensure directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.REMEDIATED_DIR, exist_ok=True)
os.makedirs(settings.RAG_STORE_DIR, exist_ok=True)
