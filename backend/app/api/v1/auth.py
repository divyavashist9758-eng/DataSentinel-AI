from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.config import settings
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.core.exceptions import AuthenticationException, ValidationException
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserOut, Token
from app.api.deps import get_current_user, record_audit

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """Register a new user account."""
    existing_email = db.query(User).filter(User.email == user_in.email).first()
    if existing_email:
        raise ValidationException("Email is already registered")

    existing_username = db.query(User).filter(User.username == user_in.username).first()
    if existing_username:
        raise ValidationException("Username is already taken")

    user = User(
        email=user_in.email,
        username=user_in.username,
        full_name=user_in.full_name,
        role=user_in.role if user_in.role in ["admin", "analyst", "viewer"] else "analyst",
        hashed_password=hash_password(user_in.password),
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    record_audit(db, action="USER_REGISTER", entity_type="user", entity_id=user.id, user_id=user.id)
    return user

@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """Authenticate credentials and generate JWT token."""
    user = db.query(User).filter(
        (User.username == login_data.username_or_email) | (User.email == login_data.username_or_email)
    ).first()

    if not user or not verify_password(login_data.password, user.hashed_password):
        raise AuthenticationException("Invalid username or password")

    if not user.is_active:
        raise HTTPException(status_code=400, detail="User account is deactivated")

    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    record_audit(db, action="USER_LOGIN", entity_type="user", entity_id=user.id, user_id=user.id)
    return {"access_token": access_token, "token_type": "bearer", "user": user}

@router.get("/me", response_model=UserOut)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Retrieve authenticated user's profile."""
    return current_user

