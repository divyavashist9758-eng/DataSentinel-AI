import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from jose import jwt, JWTError
from app.config import settings

def hash_password(password: str) -> str:
    """Secure salted SHA-256 hash with cryptographic salt."""
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode('utf-8')).hexdigest()
    return f"{salt}${hashed}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against salt$hash string."""
    try:
        if "$" not in hashed_password:
            return False
        salt, expected_hash = hashed_password.split("$", 1)
        actual_hash = hashlib.sha256((salt + plain_password).encode('utf-8')).hexdigest()
        return secrets.compare_digest(actual_hash, expected_hash)
    except Exception:
        return False

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create signed JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate JWT access token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
