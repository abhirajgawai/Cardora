"""
Authentication Schemas (DTOs)

Consolidated schemas for:
- User management (registration, profile, updates)
- Authentication (login, tokens)
- Password reset
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from uuid import UUID
from datetime import datetime
from typing import Optional


# ═══════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════

class UserCreate(BaseModel):
    """Schema for user registration (input)."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, max_length=100, description="User's password")
    full_name: Optional[str] = Field(None, max_length=255, description="User's full name")
    timezone: str = Field(default="Asia/Singapore", max_length=50, description="User's timezone")

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not any(c.isalpha() for c in v) or not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one letter and one digit")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "john.doe@example.com",
                "password": "MySecurePassword123!",
                "full_name": "John Doe",
                "timezone": "Asia/Singapore"
            }
        }
    )


class UserResponse(BaseModel):
    """Schema for user data response (output)."""
    id: UUID
    email: EmailStr
    full_name: Optional[str]
    timezone: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    """Schema for user login (input)."""
    email: EmailStr
    password: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "john.doe@example.com",
                "password": "MySecurePassword123!"
            }
        }
    )


class GoogleLoginRequest(BaseModel):
    """Schema for Google Sign-In (input)."""
    id_token: str = Field(..., description="Google ID token from the frontend Sign-In button")


class UserUpdate(BaseModel):
    """Schema for updating user profile (input)."""
    full_name: Optional[str] = Field(None, max_length=255)
    timezone: Optional[str] = Field(None, max_length=50)


# ═══════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════

class Token(BaseModel):
    """Schema for JWT token response (output)."""
    access_token: str
    token_type: str = "bearer"

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }
    )


class TokenData(BaseModel):
    """Schema for data stored inside JWT token (claims)."""
    user_id: Optional[UUID] = None
    email: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════

class PasswordResetRequest(BaseModel):
    """Request schema for forgot password endpoint."""
    email: EmailStr = Field(..., description="Email address")


class PasswordResetConfirm(BaseModel):
    """Request schema for password reset confirmation."""
    token: str = Field(..., min_length=1, description="Reset token from email")
    new_password: str = Field(..., min_length=8, max_length=100, description="New password")


class PasswordResetResponse(BaseModel):
    """Response schema for password reset request."""
    message: str


class PasswordResetSuccess(BaseModel):
    """Response schema for successful password reset."""
    message: str
