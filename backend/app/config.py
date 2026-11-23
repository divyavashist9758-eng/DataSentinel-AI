import os
import json
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
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # Standard enterprise session expiry (60 mins)
    
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
    
    # CORS (Strict whitelist; wildcard '*' is prohibited when credentials are used)
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "https://datasentinel-frontend.onrender.com"
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            v_stripped = v.strip()
            if v_stripped.startswith("[") and v_stripped.endswith("]"):
                try:
                    return json.loads(v_stripped)
                except Exception:
                    pass
            # Split comma separated origins
            origins = [origin.strip() for origin in v_stripped.split(",") if origin.strip()]
            # Filter out dangerous wildcard if credentials allowed
            return [o for o in origins if o != "*"]
        elif isinstance(v, list):
            return [o for o in v if o != "*"]
        return v

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str, info) -> str:
        env = os.environ.get("ENVIRONMENT", "development").lower()
        if env == "production":
            if len(v) < 32 or "dev-secret" in v.lower() or "change-in-production" in v.lower():
                raise ValueError("CRITICAL SECURITY ERROR: Production deployment requires a secure, random SECRET_KEY >= 32 characters!")
        return v

    model_config = {
        "env_file": ".env",
        "extra": "ignore",
        "case_sensitive": True
    }

settings = Settings()

# Ensure directories exist and are absolute
settings.UPLOAD_DIR = str(Path(settings.UPLOAD_DIR).resolve())
settings.REMEDIATED_DIR = str(Path(settings.REMEDIATED_DIR).resolve())
settings.RAG_STORE_DIR = str(Path(settings.RAG_STORE_DIR).resolve())

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.REMEDIATED_DIR, exist_ok=True)
os.makedirs(settings.RAG_STORE_DIR, exist_ok=True)


