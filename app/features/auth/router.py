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
    UserCreate, UserResponse, UserLogin, Token, GoogleLoginRequest,
    PasswordResetRequest, PasswordResetConfirm,
    PasswordResetResponse, PasswordResetSuccess
)
from app.features.auth.google_auth import verify_google_token, get_or_create_google_user
from app.features.auth.password import hash_password, verify_password
from app.features.auth.jwt import create_access_token, get_current_user
from app.features.auth.password_reset import create_password_reset_token, verify_reset_token, clear_reset_token
from app.core.email_service import send_password_reset_email
from fastapi.responses import JSONResponse
import json
from datetime import datetime
from app.features.cards.models import CreditCard
from app.features.transactions.models import Transaction
from app.features.statements.models import Statement


auth_router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

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
    "/google",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="Sign in or register with Google"
)
async def google_login(
    request: GoogleLoginRequest,
    db: Session = Depends(get_db)
):
    """Verify a Google ID token and issue our own JWT for the matching user."""
    try:
        claims = verify_google_token(request.id_token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token",
        )

    if not claims.get("email_verified", False):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google account email not verified",
        )

    user = get_or_create_google_user(db, claims)

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


@users_router.get(
    "/export",
    status_code=status.HTTP_200_OK,
    summary="Export all user data"
)
async def export_user_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export all user data as JSON."""
    try:
        cards = db.query(CreditCard).filter(CreditCard.user_id == current_user.id).all()
        transactions = db.query(Transaction).join(CreditCard).filter(CreditCard.user_id == current_user.id).all()
        statements = db.query(Statement).filter(Statement.user_id == current_user.id).all()

        export_data = {
            "export_date": datetime.utcnow().isoformat(),
            "user": {
                "id": str(current_user.id),
                "email": current_user.email,
                "full_name": current_user.full_name,
                "timezone": current_user.timezone,
                "created_at": current_user.created_at.isoformat() if current_user.created_at else None
            },
            "cards": [
                {
                    "id": str(card.id),
                    "bank_name": card.bank_name,
                    "card_type": card.card_type,
                    "last_four_digits": card.last_four_digits,
                    "credit_limit": float(card.credit_limit) if card.credit_limit else None,
                    "statement_day": card.statement_day,
                    "is_active": card.is_active,
                    "created_at": card.created_at.isoformat() if card.created_at else None
                }
                for card in cards
            ],
            "transactions": [
                {
                    "id": str(txn.id),
                    "card_id": str(txn.card_id),
                    "transaction_date": txn.transaction_date.isoformat() if txn.transaction_date else None,
                    "merchant": txn.merchant,
                    "amount": float(txn.amount),
                    "category": txn.category,
                    "description": txn.description,
                    "is_recurring": txn.is_recurring
                }
                for txn in transactions
            ],
            "statements": [
                {
                    "id": str(stmt.id),
                    "card_id": str(stmt.card_id),
                    "statement_date": stmt.statement_date.isoformat() if stmt.statement_date else None,
                    "due_date": stmt.due_date.isoformat() if stmt.due_date else None,
                    "total_amount": float(stmt.total_amount) if stmt.total_amount else None,
                    "minimum_payment": float(stmt.minimum_payment) if stmt.minimum_payment else None,
                    "uploaded_at": stmt.uploaded_at.isoformat() if stmt.uploaded_at else None,
                    "status": stmt.status
                }
                for stmt in statements
            ],
            "statistics": {
                "total_cards": len(cards),
                "total_transactions": len(transactions),
                "total_statements": len(statements)
            }
        }

        json_data = json.dumps(export_data, indent=2)
        return JSONResponse(
            content=export_data,
            headers={
                "Content-Disposition": f"attachment; filename=cardora-export-{datetime.utcnow().strftime('%Y%m%d')}.json"
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export data: {str(e)}"
        )


@users_router.delete(
    "/data",
    status_code=status.HTTP_200_OK,
    summary="Delete all user data"
)
async def delete_user_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete all user data (transactions, cards, statements) but keep the account."""
    try:
        cards = db.query(CreditCard).filter(CreditCard.user_id == current_user.id).all()
        for card in cards:
            db.query(Transaction).filter(Transaction.card_id == card.id).delete()

        db.query(Statement).filter(Statement.user_id == current_user.id).delete()

        db.query(CreditCard).filter(CreditCard.user_id == current_user.id).delete()

        db.commit()

        return {
            "message": "All user data has been permanently deleted",
            "deleted_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete data: {str(e)}"
        )


@users_router.delete(
    "/account",
    status_code=status.HTTP_200_OK,
    summary="Delete user account"
)
async def delete_user_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Permanently delete user account and all associated data."""
    try:
        cards = db.query(CreditCard).filter(CreditCard.user_id == current_user.id).all()
        for card in cards:
            db.query(Transaction).filter(Transaction.card_id == card.id).delete()

        db.query(Statement).filter(Statement.user_id == current_user.id).delete()
        db.query(CreditCard).filter(CreditCard.user_id == current_user.id).delete()

        db.delete(current_user)
        db.commit()

        return {
            "message": "Account and all associated data has been permanently deleted",
            "deleted_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete account: {str(e)}"
        )
