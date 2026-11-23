from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None
    role: str = Field(default="analyst")

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    username_or_email: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    password: str

    @model_validator(mode="before")
    @classmethod
    def normalize_login_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            ident = data.get("username_or_email") or data.get("username") or data.get("email")
            if ident:
                data["username_or_email"] = str(ident).strip()
        return data

    @model_validator(mode="after")
    def validate_identifier(self) -> "UserLogin":
        if not self.username_or_email:
            raise ValueError("Username or email is required")
        return self

class UserOut(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None

