from typing import Generator, Optional, List
from fastapi import Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_access_token
from app.core.exceptions import AuthenticationException, AuthorizationException
from app.models.user import User
from app.models.audit import AuditLog

security = HTTPBearer(auto_error=False)

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    token_query: Optional[str] = Query(None, alias="token"),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to retrieve and authenticate the current user from JWT Bearer token.
    Enforces strict token validation, expiration, and user active status.
    """
    raw_token = None
    if credentials and credentials.credentials:
        raw_token = credentials.credentials
    elif token_query:
        raw_token = token_query

    if not raw_token:
        raise AuthenticationException("Authentication required: missing Bearer token")
        
    payload = decode_access_token(raw_token)
    if not payload:
        raise AuthenticationException("Could not validate credentials: token invalid or expired")
        
    sub: str = payload.get("sub")
    if not sub:
        raise AuthenticationException("Token payload missing subject identifier")
        
    # Search by username or email
    user = db.query(User).filter((User.username == sub) | (User.email == sub)).first()
    if not user:
        raise AuthenticationException("User account associated with token no longer exists")
        
    if not user.is_active:
        raise AuthorizationException("Inactive or disabled user account")
        
    return user

def require_roles(*allowed_roles: str):
    """Factory dependency to enforce role-based access control (RBAC)."""
    def role_dependency(current_user: User = Depends(get_current_user)) -> User:
        user_role = (current_user.role or "").lower()
        normalized_allowed = [r.lower() for r in allowed_roles]
        if user_role not in normalized_allowed:
            raise AuthorizationException(
                f"Access denied: Requires one of [{', '.join(allowed_roles)}]. User holds role '{current_user.role}'."
            )
        return current_user
    return role_dependency

# Standard Role Dependencies
require_admin = require_roles("admin")
require_analyst = require_roles("admin", "analyst")
require_viewer = require_roles("admin", "analyst", "viewer")
get_current_active_admin = require_admin

def record_audit(
    db: Session,
    action: str,
    entity_type: str,
    entity_id: str | int,
    user_id: Optional[int] = None,
    details: Optional[dict] = None,
    ip_address: Optional[str] = None
) -> AuditLog:
    """Persist an audit log entry for human-in-the-loop and security traceability."""
    audit = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id),
        details=details or {},
        ip_address=ip_address
    )
    db.add(audit)
    db.commit()
    return audit
