import os
import sys
from pathlib import Path

# Disable tracing and external network calls during tests
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGSMITH_TRACING"] = "false"
os.environ["GROQ_API_KEY"] = ""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set backend root in sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.config import settings
TEST_DB_URL = "sqlite:///./test_datasentinel.db"
settings.DATABASE_URL = TEST_DB_URL
settings.GROQ_API_KEY = ""
settings.OPENAI_API_KEY = ""
from app.core.database import Base, get_db, json_dumps_custom, engine as test_engine, SessionLocal as TestingSessionLocal
from app.main import app
from app.core.security import hash_password
from app.models.user import User

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    
    # Create seed admin user
    db = TestingSessionLocal()
    admin = User(
        email="testadmin@datasentinel.ai",
        username="admin",
        full_name="Test Administrator",
        role="admin",
        hashed_password=hash_password("admin123"),
        is_active=True
    )
    db.add(admin)
    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists("./test_datasentinel.db"):
        try:
            os.remove("./test_datasentinel.db")
        except Exception:
            pass

@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app, raise_server_exceptions=True)
    yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def auth_headers(client):
    """Authenticate and return Bearer token headers."""
    resp = client.post("/api/v1/auth/login", json={
        "username_or_email": "admin",
        "password": "admin123"
    })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
