"""
Authentication and User Management Router

Consolidated router combining:
- Authentication endpoints (register, login, password reset)
- User profile endpoints (get current user)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.features.auth.models import User
from app.features.auth.schemas import (
    UserCreate, UserResponse, UserLogin, Token,
    PasswordResetRequest, PasswordResetConfirm,
    PasswordResetResponse, PasswordResetSuccess
)
from app.features.auth.password import hash_password, verify_password
from app.features.auth.jwt import create_access_token, get_current_user
from app.features.auth.password_reset import create_password_reset_token, verify_reset_token, clear_reset_token
from app.core.email_service import send_password_reset_email


# Router for /auth endpoints
auth_router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

# Router for /users endpoints
users_router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# ═══════════════════════════════════════════════════════════════════
# AUTHENTICATION ENDPOINTS
# ═══════════════════════════════════════════════════════════════════

@auth_router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user"
)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Register a new user account."""
    existing_user = db.query(User).filter(User.email == user_data.email).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    try:
        new_user = User(
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
            full_name=user_data.full_name,
            timezone=user_data.timezone,
            is_active=True,
            is_verified=False
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return UserResponse.model_validate(new_user)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@auth_router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="Login user"
)
async def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """Authenticate user and return JWT token."""
    user = db.query(User).filter(User.email == credentials.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )

    return Token(access_token=access_token, token_type="bearer")


@auth_router.post(
    "/forgot-password",
    response_model=PasswordResetResponse,
    status_code=status.HTTP_200_OK,
    summary="Request password reset"
)
async def forgot_password(
    request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """Request password reset - sends email with reset link."""
    user = db.query(User).filter(User.email == request.email).first()

    if user and user.is_active:
        reset_token = create_password_reset_token(db, user)
        await send_password_reset_email(
            email=user.email,
            reset_token=reset_token,
            user_name=user.full_name or "User"
        )

    return PasswordResetResponse(
        message="If your email exists in our system, you will receive a password reset link"
    )


@auth_router.post(
    "/reset-password",
    response_model=PasswordResetSuccess,
    status_code=status.HTTP_200_OK,
    summary="Reset password with token"
)
async def reset_password(
    request: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """Reset password using token from email."""
    user = verify_reset_token(db, request.token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    user.hashed_password = hash_password(request.new_password)
    clear_reset_token(db, user)
    db.commit()

    return PasswordResetSuccess(
        message="Password has been reset successfully"
    )


# ═══════════════════════════════════════════════════════════════════
# USER PROFILE ENDPOINTS
# ═══════════════════════════════════════════════════════════════════

@users_router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile"
)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current authenticated user's profile."""
    return UserResponse.model_validate(current_user)
