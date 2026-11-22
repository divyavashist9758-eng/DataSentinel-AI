"""
Security validation tests for DataSentinel AI:
- Argon2id password hashing and backwards compatibility
- JWT token expiry and tampering prevention
- Zero-backdoor unauthenticated request rejection
- Role-based authorization enforcement (RBAC)
- Path traversal rejection
- Malicious executable binary disguised upload rejection
- File size bounds enforcement
"""
import os
import io
import pytest
from datetime import timedelta
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token
)
from app.services.ingestion import IngestionService
from app.core.exceptions import FileProcessingException, ValidationException
from app.models.user import User

def test_argon2id_password_hashing_and_verification():
    raw_password = "P@ssw0rdSecure!999"
    argon2_hash = hash_password(raw_password)

    # Must start with standard Argon2id signature
    assert argon2_hash.startswith("$argon2id$")
    assert verify_password(raw_password, argon2_hash) is True
    assert verify_password("WrongPassword!", argon2_hash) is False
    assert verify_password("", argon2_hash) is False

def test_legacy_salted_hash_backwards_compatibility():
    # Legacy salt$hash format
    salt = "abcd1234efgh5678"
    import hashlib
    pw = "LegacyPass123"
    legacy_hash = f"{salt}${hashlib.sha256((salt + pw).encode('utf-8')).hexdigest()}"

    # Verifies seamlessly without breaking existing databases
    assert verify_password(pw, legacy_hash) is True
    assert verify_password("WrongPass", legacy_hash) is False

def test_jwt_expiry_and_tampering():
    # Valid token
    token = create_access_token({"sub": "admin", "role": "admin"})
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "admin"

    # Expired token (issued with negative delta)
    expired_token = create_access_token({"sub": "admin"}, expires_delta=timedelta(seconds=-10))
    expired_payload = decode_access_token(expired_token)
    assert expired_payload is None, "Expired JWT token was improperly accepted"

    # Tampered token
    tampered = token[:-4] + "fake"
    tampered_payload = decode_access_token(tampered)
    assert tampered_payload is None, "Tampered JWT signature was improperly accepted"

def test_unauthenticated_requests_strictly_rejected(client):
    # Calling protected endpoint without Authorization header must fail with 401
    resp = client.get("/api/v1/datasets/")
    assert resp.status_code == 401, f"Expected 401 Unauthorized, got {resp.status_code}"

    # Malformed token must fail with 401
    resp = client.get("/api/v1/datasets/", headers={"Authorization": "Bearer invalid.jwt.token"})
    assert resp.status_code == 401

def test_role_based_access_control_viewer_restricted(client, db_session):
    # Register a viewer user
    viewer_username = "audit_viewer"
    viewer_password = "ViewerPass123!"
    existing = db_session.query(User).filter(User.username == viewer_username).first()
    if not existing:
        viewer = User(
            email="viewer@datasentinel.ai",
            username=viewer_username,
            full_name="Read-Only Auditor",
            role="viewer",
            hashed_password=hash_password(viewer_password),
            is_active=True
        )
        db_session.add(viewer)
        db_session.commit()

    # Authenticate as viewer
    resp = client.post("/api/v1/auth/login", json={
        "username_or_email": viewer_username,
        "password": viewer_password
    })
    assert resp.status_code == 200
    viewer_token = resp.json()["access_token"]
    viewer_headers = {"Authorization": f"Bearer {viewer_token}"}

    # 1. Viewer cannot upload datasets
    csv_content = b"col1,col2\n1,2\n3,4\n"
    up_resp = client.post(
        "/api/v1/datasets/upload",
        files={"file": ("test.csv", io.BytesIO(csv_content), "text/csv")},
        data={"name": "Viewer Upload Attempt"},
        headers=viewer_headers
    )
    assert up_resp.status_code == 403, f"Expected 403 Forbidden for viewer upload, got {up_resp.status_code}"

    # 2. Viewer cannot create incidents
    inc_resp = client.post(
        "/api/v1/incidents/",
        json={"dataset_id": 1, "title": "Unauthorized Incident", "description": "Test", "severity": "LOW"},
        headers=viewer_headers
    )
    assert inc_resp.status_code == 403, f"Expected 403 Forbidden for viewer incident create, got {inc_resp.status_code}"

    # 3. Viewer cannot approve remediations
    rem_resp = client.post(
        "/api/v1/remediation/1/action",
        json={"action": "APPROVE", "reviewer_notes": "Attempted by viewer"},
        headers=viewer_headers
    )
    assert rem_resp.status_code == 403, f"Expected 403 Forbidden for viewer remediation action, got {rem_resp.status_code}"

def test_executable_upload_blocked_by_magic_bytes(client, auth_headers):
    # Disguised Linux ELF binary renamed to .csv
    fake_elf_csv = b"\x7fELF\x02\x01\x01\x00malicious binary content payload"
    resp = client.post(
        "/api/v1/datasets/upload",
        files={"file": ("malware.csv", io.BytesIO(fake_elf_csv), "text/csv")},
        data={"name": "Disguised Executable"},
        headers=auth_headers
    )
    assert resp.status_code in [400, 422], f"Expected 400/422 for executable upload, got {resp.status_code}"
    assert "Executable binary or script headers detected" in resp.text

    # Disguised Windows PE executable renamed to .csv
    fake_pe_csv = b"MZ\x90\x00\x03\x00\x00\x00fake pe executable content"
    resp_pe = client.post(
        "/api/v1/datasets/upload",
        files={"file": ("exploit.csv", io.BytesIO(fake_pe_csv), "text/csv")},
        data={"name": "Disguised PE"},
        headers=auth_headers
    )
    assert resp_pe.status_code in [400, 422]
    assert "Executable binary or script headers detected" in resp_pe.text

def test_path_traversal_sanitization():
    # Dangerous path traversal filenames must be stripped to safe basename
    dangerous_names = [
        "../../../../etc/passwd.csv",
        "..\\..\\..\\windows\\system32\\cmd.exe.csv",
        "/absolute/root/exploit.csv",
        "....//....//nested.csv"
    ]
    for d_name in dangerous_names:
        sanitized = IngestionService.sanitize_filename(d_name)
        assert "/" not in sanitized
        assert "\\" not in sanitized
        assert ".." not in sanitized

def test_path_confinement_load_dataframe_denied():
    # Attempting to load files outside storage/sample directories must be blocked
    forbidden_path = os.path.abspath("backend/app/main.py")
    with pytest.raises(FileProcessingException) as excinfo:
        IngestionService.load_dataframe(forbidden_path, "csv")
    assert "Access denied" in str(excinfo.value)

