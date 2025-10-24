"""
Pydantic Schemas (DTOs)

Compare to .NET: Like having ViewModels, DTOs, or Request/Response models
"""

from .user import UserCreate, UserResponse, UserLogin, UserUpdate
from .token import Token, TokenData
from .password_reset import (
    PasswordResetRequest,
    PasswordResetConfirm,
    PasswordResetResponse,
    PasswordResetSuccess
)
from .category import CategoryResponse, CategoryCreate
from .credit_card import CreditCardResponse, CreditCardUpdate
from .transaction import (
    TransactionCreate,
    TransactionResponse,
    TransactionUpdate,
    TransactionListResponse
)
from .statement import (
    StatementResponse,
    StatementUploadResponse,
    StatementListResponse
)
from .analytics import (
    MonthlyAnalysisResponse,
    ComparisonResponse,
    TrendAnalysisResponse,
    AnnualAnalysisResponse,
    CardsAnalysisResponse,
    CategoryAnalysisResponse
)

__all__ = [
    # User schemas
    "UserCreate",
    "UserResponse",
    "UserLogin",
    "UserUpdate",
    # Token schemas
    "Token",
    "TokenData",
    # Password reset schemas
    "PasswordResetRequest",
    "PasswordResetConfirm",
    "PasswordResetResponse",
    "PasswordResetSuccess",
    # Category schemas
    "CategoryResponse",
    "CategoryCreate",
    # Credit card schemas
    "CreditCardResponse",
    "CreditCardUpdate",
    # Transaction schemas
    "TransactionCreate",
    "TransactionResponse",
    "TransactionUpdate",
    "TransactionListResponse",
    # Statement schemas
    "StatementResponse",
    "StatementUploadResponse",
    "StatementListResponse",
    # Analytics schemas
    "MonthlyAnalysisResponse",
    "ComparisonResponse",
    "TrendAnalysisResponse",
    "AnnualAnalysisResponse",
    "CardsAnalysisResponse",
    "CategoryAnalysisResponse",
]
