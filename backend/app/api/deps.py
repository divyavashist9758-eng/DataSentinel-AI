from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
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
    db: Session = Depends(get_db)
) -> User:
    """Dependency to retrieve and authenticate the current user from JWT Bearer token."""
    if not credentials:
        # For development / testing convenience, if no bearer token is supplied,
        # return the default demo admin user or raise 401.
        demo_user = db.query(User).filter(User.username == "admin").first()
        if demo_user:
            return demo_user
        raise AuthenticationException("Authentication required: missing Bearer token")
        
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise AuthenticationException("Could not validate credentials: token invalid or expired")
        
    username: str = payload.get("sub")
    if not username:
        raise AuthenticationException("Token payload missing subject identifier")
        
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise AuthenticationException(f"User '{username}' no longer exists")
        
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user account")
        
    return user

def get_current_active_admin(current_user: User = Depends(get_current_user)) -> User:
    """Ensure current user holds administrator privileges."""
    if current_user.role != "admin":
        raise AuthorizationException("Administrative privileges required for this action")
    return current_user

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
