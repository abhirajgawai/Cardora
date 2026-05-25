"""
Credit Card Pydantic Schemas (DTOs)

    - CreditCardResponse → CardDto (output)
    - CreditCardUpdate → UpdateCardRequest DTO

Credit cards in Cardora:
- Cards are AUTO-CREATED from PDF statements (users don't manually add them)
- Each card can have multiple statements
- Cards link to transactions for analytics
"""

from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional
from decimal import Decimal


# ═══════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════

class CreditCardResponse(BaseModel):
    """
    Schema for credit card data response (output)

        public class CardDto
        {
            public Guid Id { get; set; }
            public Guid UserId { get; set; }
            public string BankName { get; set; }
            public string CardName { get; set; }
            public string LastFourDigits { get; set; }
            public string CardType { get; set; }
            public decimal? CreditLimit { get; set; }
            public bool IsActive { get; set; }
            public DateTime CreatedAt { get; set; }
            public DateTime UpdatedAt { get; set; }
        }

    Used for:
    - Listing user's credit cards
    - Displaying card details
    - Card selection dropdown
    """
    id: UUID = Field(
        ...,
        description="Card's unique identifier",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )

    user_id: UUID = Field(
        ...,
        description="Owner's user ID",
        examples=["660e8400-e29b-41d4-a716-446655440001"]
    )

    bank_name: str = Field(
        ...,
        description="Bank name",
        examples=["DBS Bank", "OCBC Bank"]
    )

    card_name: Optional[str] = Field(
        None,
        description="Card name/nickname",
        examples=["DBS Altitude Visa"]
    )

    last_four_digits: str = Field(
        ...,
        description="Last 4 digits of card number",
        examples=["1234"]
    )

    card_type: Optional[str] = Field(
        None,
        description="Card type",
        examples=["Visa", "Mastercard"]
    )

    credit_limit: Optional[Decimal] = Field(
        None,
        description="Credit limit in dollars",
        examples=[10000.00]
    )

    statement_day: Optional[str] = Field(
        None,
        description="Day of month when statement is generated (1-31)",
        examples=["15", "16", "1"]
    )

    is_active: bool = Field(
        ...,
        description="Whether the card is active",
        examples=[True]
    )

    created_at: datetime = Field(
        ...,
        description="When the card was added",
        examples=["2024-10-22T10:30:00Z"]
    )

    updated_at: datetime = Field(
        ...,
        description="When the card was last updated",
        examples=["2024-10-22T10:30:00Z"]
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "660e8400-e29b-41d4-a716-446655440001",
                "bank_name": "DBS Bank",
                "card_name": "DBS Altitude Visa",
                "last_four_digits": "1234",
                "card_type": "Visa",
                "credit_limit": 10000.00,
                "statement_day": "15",
                "is_active": True,
                "created_at": "2024-10-22T10:30:00Z",
                "updated_at": "2024-10-22T10:30:00Z"
            }
        }
    )


# ═══════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════

class CreditCardUpdate(BaseModel):
    """
    Schema for updating credit card (input)

        public class UpdateCardRequest
        {
            public string? CardName { get; set; }
            public string? CardType { get; set; }
            public decimal? CreditLimit { get; set; }
            public bool? IsActive { get; set; }
        }

    All fields are optional (partial update)

    Used for:
    - PATCH /credit-cards/{card_id}
    - User updates card details
    """
    card_name: Optional[str] = Field(
        None,
        max_length=100,
        description="Card name/nickname",
        examples=["DBS Altitude Visa Signature"]
    )

    card_type: Optional[str] = Field(
        None,
        max_length=50,
        description="Card type",
        examples=["Visa Signature"]
    )

    credit_limit: Optional[Decimal] = Field(
        None,
        ge=0,
        decimal_places=2,
        description="Credit limit in dollars",
        examples=[15000.00]
    )

    is_active: Optional[bool] = Field(
        None,
        description="Whether the card is active",
        examples=[False]
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "card_name": "DBS Altitude Visa Signature",
                "credit_limit": 15000.00,
                "is_active": True
            }
        }
    )


# ═══════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════
"""
NOTE: Credit cards are AUTO-CREATED when uploading PDF statements.
Users don't manually add cards anymore.

GET /credit-cards
Authorization: Bearer <token>

[
    {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "user_id": "660e8400-e29b-41d4-a716-446655440001",
        "bank_name": "DBS Bank",
        "card_name": "DBS Altitude Visa",
        "last_four_digits": "1234",
        "card_type": "Visa",
        "credit_limit": 10000.00,
        "statement_day": "15",
        "is_active": true,
        "created_at": "2024-10-22T10:30:00Z",
        "updated_at": "2024-10-22T10:30:00Z"
    },
    {
        "id": "770e8400-e29b-41d4-a716-446655440002",
        "user_id": "660e8400-e29b-41d4-a716-446655440001",
        "bank_name": "OCBC Bank",
        "card_name": "OCBC 365 Credit Card",
        "last_four_digits": "5678",
        "card_type": "Mastercard",
        "credit_limit": 5000.00,
        "statement_day": "16",
        "is_active": true,
        "created_at": "2024-10-23T14:00:00Z",
        "updated_at": "2024-10-23T14:00:00Z"
    }
]


PATCH /credit-cards/550e8400-e29b-41d4-a716-446655440000
Content-Type: application/json
Authorization: Bearer <token>

{
    "credit_limit": 15000.00,
    "card_name": "DBS Altitude Visa Signature"
}

{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "660e8400-e29b-41d4-a716-446655440001",
    "bank_name": "DBS Bank",
    "card_name": "DBS Altitude Visa Signature",
    "last_four_digits": "1234",
    "card_type": "Visa",
    "credit_limit": 15000.00,
    "statement_day": "15",
    "is_active": true,
    "created_at": "2024-10-22T10:30:00Z",
    "updated_at": "2024-10-23T15:30:00Z"
}
"""
