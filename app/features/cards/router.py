"""
Credit Card Router - Manage User's Credit Cards

NOTE: Cards are AUTO-CREATED when uploading statements!
Users don't manually add cards anymore.

Endpoints:
- GET /credit-cards - List all user's cards
- GET /credit-cards/{card_id} - Get specific card
- PATCH /credit-cards/{card_id} - Update card (rename, deactivate)
- DELETE /credit-cards/{card_id} - Delete card

Compare to .NET: Like CreditCardsController
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app.core.database import get_db
from app.features.auth.models import User
from app.features.cards.models import CreditCard
from app.features.cards.schemas import CreditCardResponse, CreditCardUpdate
from app.features.auth.jwt import get_current_user

# ═══════════════════════════════════════════════════════════════════
# ROUTER SETUP
# ═══════════════════════════════════════════════════════════════════

router = APIRouter(
    prefix="/credit-cards",
    tags=["Credit Cards"]
)


# ═══════════════════════════════════════════════════════════════════
# GET /credit-cards - List All User's Cards
# ═══════════════════════════════════════════════════════════════════

@router.get(
    "",
    response_model=List[CreditCardResponse],
    status_code=status.HTTP_200_OK,
    summary="List all credit cards",
    description="Get all credit cards for the current user"
)
async def list_credit_cards(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    include_inactive: bool = False
):
    """
    List all user's credit cards

    - **include_inactive**: Include inactive cards (default: False)
    """

    query = db.query(CreditCard).filter(CreditCard.user_id == current_user.id)

    if not include_inactive:
        query = query.filter(CreditCard.is_active == True)

    cards = query.order_by(CreditCard.created_at.desc()).all()

    return [CreditCardResponse.model_validate(card) for card in cards]


# ═══════════════════════════════════════════════════════════════════
# GET /credit-cards/{card_id} - Get Specific Card
# ═══════════════════════════════════════════════════════════════════

@router.get(
    "/{card_id}",
    response_model=CreditCardResponse,
    status_code=status.HTTP_200_OK,
    summary="Get credit card details",
    description="Get details of a specific credit card"
)
async def get_credit_card(
    card_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific credit card by ID"""

    card = db.query(CreditCard).filter(
        CreditCard.id == card_id,
        CreditCard.user_id == current_user.id
    ).first()

    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Credit card not found"
        )

    return CreditCardResponse.model_validate(card)


# ═══════════════════════════════════════════════════════════════════
# PATCH /credit-cards/{card_id} - Update Card
# ═══════════════════════════════════════════════════════════════════

@router.patch(
    "/{card_id}",
    response_model=CreditCardResponse,
    status_code=status.HTTP_200_OK,
    summary="Update credit card",
    description="Update credit card details"
)
async def update_credit_card(
    card_id: UUID,
    card_update: CreditCardUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update credit card details

    - **card_name**: Update card nickname
    - **card_type**: Update card type
    - **credit_limit**: Update credit limit
    - **is_active**: Activate/deactivate card
    """

    card = db.query(CreditCard).filter(
        CreditCard.id == card_id,
        CreditCard.user_id == current_user.id
    ).first()

    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Credit card not found"
        )

    # Update only provided fields
    if card_update.card_name is not None:
        card.card_name = card_update.card_name

    if card_update.card_type is not None:
        card.card_type = card_update.card_type

    if card_update.credit_limit is not None:
        card.credit_limit = card_update.credit_limit

    if card_update.is_active is not None:
        card.is_active = card_update.is_active

    db.commit()
    db.refresh(card)

    return CreditCardResponse.model_validate(card)


# ═══════════════════════════════════════════════════════════════════
# DELETE /credit-cards/{card_id} - Delete Card
# ═══════════════════════════════════════════════════════════════════

@router.delete(
    "/{card_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete credit card",
    description="Delete a credit card (WARNING: Deletes all associated statements and transactions)"
)
async def delete_credit_card(
    card_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete credit card

    WARNING: This will also delete:
    - All statements for this card
    - All transactions for this card

    Use PATCH to deactivate instead if you want to preserve data.
    """

    card = db.query(CreditCard).filter(
        CreditCard.id == card_id,
        CreditCard.user_id == current_user.id
    ).first()

    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Credit card not found"
        )

    # Delete card (cascade will delete statements and transactions)
    db.delete(card)
    db.commit()

    return None


# ═══════════════════════════════════════════════════════════════════
# USAGE EXAMPLES
# ═══════════════════════════════════════════════════════════════════
"""
# Example 1: Add new card
POST /credit-cards
Authorization: Bearer <token>
Content-Type: application/json

{
    "bank_name": "DBS Bank",
    "card_name": "DBS Altitude Visa",
    "last_four_digits": "1234",
    "card_type": "Visa",
    "credit_limit": 10000.00
}

# Example 2: List all cards
GET /credit-cards
Authorization: Bearer <token>

# Example 3: Update card
PATCH /credit-cards/550e8400-e29b-41d4-a716-446655440000
Authorization: Bearer <token>
Content-Type: application/json

{
    "credit_limit": 15000.00,
    "card_name": "DBS Altitude Visa Signature"
}

# Example 4: Deactivate card (preserve data)
PATCH /credit-cards/550e8400-e29b-41d4-a716-446655440000
Authorization: Bearer <token>
Content-Type: application/json

{
    "is_active": false
}

# Example 5: Delete card (WARNING: Deletes all data)
DELETE /credit-cards/550e8400-e29b-41d4-a716-446655440000
Authorization: Bearer <token>
"""
