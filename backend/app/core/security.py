import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from jose import jwt, JWTError
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError
from app.config import settings

# RFC 9106 recommended Argon2id parameters (64 MiB RAM, 3 iterations, 4 parallelism threads)
_argon2_hasher = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32
)

def hash_password(password: str) -> str:
    """Generate high-security Argon2id cryptographic password hash."""
    if not password:
        raise ValueError("Password cannot be empty")
    return _argon2_hasher.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify plain password against hash.
    Supports primary Argon2id format with constant-time legacy salt$sha256 fallback.
    """
    if not plain_password or not hashed_password:
        return False
    try:
        # Primary: Argon2id verification
        if hashed_password.startswith("$argon2"):
            return _argon2_hasher.verify(hashed_password, plain_password)
        
        # Legacy: Backwards-compatible salted SHA-256 fallback
        if "$" in hashed_password:
            salt, expected_hash = hashed_password.split("$", 1)
            actual_hash = hashlib.sha256((salt + plain_password).encode('utf-8')).hexdigest()
            return secrets.compare_digest(actual_hash, expected_hash)
            
        return False
    except (VerifyMismatchError, InvalidHashError):
        return False
    except Exception:
        return False

def needs_rehash(hashed_password: str) -> bool:
    """Check if hash is legacy or needs upgrade according to current Argon2id parameters."""
    if not hashed_password or not hashed_password.startswith("$argon2"):
        return True
    try:
        return _argon2_hasher.check_needs_rehash(hashed_password)
    except Exception:
        return True

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create signed JWT access token with cryptographic expiry and subject enforcement."""
    to_encode = data.copy()
    now_utc = datetime.now(timezone.utc)
    if expires_delta:
        expire = now_utc + expires_delta
    else:
        expire = now_utc + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": now_utc,
        "nbf": now_utc
    })
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode, cryptographically verify and validate JWT access token.
    Enforces signature verification, algorithm pinning, and expiration.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_iat": True,
                "verify_nbf": True,
                "require_exp": True,
                "require_sub": True
            }
        )
        return payload
    except JWTError:
        return None
    except Exception:
        return None
