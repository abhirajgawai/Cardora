"""
Transaction Router - View and Manage Transactions

NOTE: Transactions come from uploaded statements and cannot be individually deleted.
To remove transactions, delete the entire statement.

Endpoints:
- GET /transactions - List transactions with filters
- GET /transactions/{transaction_id} - Get transaction details
- PATCH /transactions/{transaction_id} - Update transaction (category, etc.)

"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional

from app.core.database import get_db
from app.features.auth.models import User
from app.features.transactions.models import Transaction
from app.features.transactions.schemas import TransactionResponse, TransactionUpdate, TransactionListResponse
from app.features.auth.jwt import get_current_user

# ═══════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)


# ═══════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════

@router.get(
    "",
    response_model=TransactionListResponse,
    status_code=status.HTTP_200_OK,
    summary="List transactions",
    description="Get transactions with filtering and pagination"
)
async def list_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    month: Optional[int] = Query(None, ge=1, le=12, description="Filter by month (1-12)"),
    year: Optional[int] = Query(None, ge=2020, le=2100, description="Filter by year"),
    card_id: Optional[UUID] = Query(None, description="Filter by credit card"),
    category_id: Optional[UUID] = Query(None, description="Filter by category"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=10000, description="Items per page (max 10000)")
):
    """
    List transactions with filtering

    Query Parameters:
    - **month**: Filter by statement month (1-12)
    - **year**: Filter by statement year
    - **card_id**: Filter by credit card
    - **category_id**: Filter by category
    - **page**: Page number (default: 1)
    - **limit**: Items per page (default: 20, max: 10000)

    Returns:
    - Paginated list of transactions
    - Total count
    - Page info
    """

    query = db.query(Transaction).filter(Transaction.user_id == current_user.id)

    if month:
        query = query.filter(Transaction.statement_month == month)

    if year:
        query = query.filter(Transaction.statement_year == year)

    if card_id:
        query = query.filter(Transaction.card_id == card_id)

    if category_id:
        query = query.filter(Transaction.category_id == category_id)

    total = query.count()

    offset = (page - 1) * limit
    transactions = query.order_by(
        Transaction.transaction_date.desc()
    ).offset(offset).limit(limit).all()

    return TransactionListResponse(
        transactions=[TransactionResponse.model_validate(trans) for trans in transactions],
        total=total,
        page=page,
        page_size=limit
    )


# ═══════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════

@router.get(
    "/{transaction_id}",
    response_model=TransactionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get transaction details",
    description="Get details of a specific transaction"
)
async def get_transaction(
    transaction_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific transaction by ID"""

    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ).first()

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )

    return TransactionResponse.model_validate(transaction)


# ═══════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════

@router.patch(
    "/{transaction_id}",
    response_model=TransactionResponse,
    status_code=status.HTTP_200_OK,
    summary="Update transaction",
    description="Update transaction details (e.g., change category)"
)
async def update_transaction(
    transaction_id: UUID,
    trans_update: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update transaction

    Typical use cases:
    - Change transaction category
    - Add/update description
    - Correct merchant name
    - Adjust amount
    """

    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ).first()

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )

    if trans_update.category_id is not None:
        transaction.category_id = trans_update.category_id

    if trans_update.merchant_name is not None:
        transaction.merchant_name = trans_update.merchant_name

    if trans_update.amount is not None:
        transaction.amount = trans_update.amount

    if trans_update.description is not None:
        transaction.description = trans_update.description

    db.commit()
    db.refresh(transaction)

    return TransactionResponse.model_validate(transaction)


# ═══════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════
"""
GET /transactions?month=10&year=2024&page=1&limit=20
Authorization: Bearer <token>

GET /transactions?card_id=550e8400-e29b-41d4-a716-446655440000&category_id=660e8400-e29b-41d4-a716-446655440001
Authorization: Bearer <token>

PATCH /transactions/770e8400-e29b-41d4-a716-446655440002
Authorization: Bearer <token>
Content-Type: application/json

{
    "category_id": "880e8400-e29b-41d4-a716-446655440003",
    "description": "Updated category"
}

NOTE: Individual transaction deletion is not supported.
Transactions come from uploaded statements. To remove transactions, delete the entire statement.
"""
