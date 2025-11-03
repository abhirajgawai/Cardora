"""
Transaction Pydantic Schemas (DTOs)

Compare to .NET: Like having DTOs for Transactions
    - TransactionCreate → CreateTransactionRequest DTO
    - TransactionResponse → TransactionDto (output)
    - TransactionUpdate → UpdateTransactionRequest DTO

Transactions in Cardora:
- Extracted from PDF statements using Gemini AI
- Can also be manually entered/edited by user
- Each transaction has a category (for analytics)
- Includes confidence score from AI extraction
"""

from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import date, datetime
from typing import Optional
from decimal import Decimal

# Import CategoryResponse for nested response
from app.features.categories.schemas import CategoryResponse


# ═══════════════════════════════════════════════════════════════════
# TRANSACTION CREATE (Input - Manual Entry)
# ═══════════════════════════════════════════════════════════════════

class TransactionCreate(BaseModel):
    """
    Schema for creating a transaction manually (input)

    Compare to .NET:
        public class CreateTransactionRequest
        {
            [Required]
            public Guid CardId { get; set; }

            [Required]
            public string MerchantName { get; set; }

            [Required]
            public decimal Amount { get; set; }

            [Required]
            public DateTime TransactionDate { get; set; }

            public Guid? CategoryId { get; set; }
            public string Description { get; set; }
        }

    Used for:
    - POST /transactions (manual transaction entry)
    - User adds a transaction that wasn't in statement
    """
    card_id: UUID = Field(
        ...,
        description="Credit card ID",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )

    merchant_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Merchant/store name",
        examples=["Starbucks", "NTUC FairPrice", "Grab"]
    )

    amount: Decimal = Field(
        ...,
        gt=0,  # Greater than 0
        decimal_places=2,
        description="Transaction amount in dollars",
        examples=[6.50, 125.00]
    )

    transaction_date: date = Field(
        ...,
        description="Transaction date (YYYY-MM-DD)",
        examples=["2024-10-15"]
    )

    category_id: Optional[UUID] = Field(
        None,
        description="Category ID (optional)",
        examples=["660e8400-e29b-41d4-a716-446655440001"]
    )

    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Additional notes/description",
        examples=["Coffee with friends"]
    )

    # Configuration
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "card_id": "550e8400-e29b-41d4-a716-446655440000",
                "merchant_name": "Starbucks",
                "amount": 6.50,
                "transaction_date": "2024-10-15",
                "category_id": "660e8400-e29b-41d4-a716-446655440001",
                "description": "Coffee with friends"
            }
        }
    )


# ═══════════════════════════════════════════════════════════════════
# TRANSACTION RESPONSE (Output)
# ═══════════════════════════════════════════════════════════════════

class TransactionResponse(BaseModel):
    """
    Schema for transaction data response (output)

    Compare to .NET:
        public class TransactionDto
        {
            public Guid Id { get; set; }
            public Guid UserId { get; set; }
            public Guid CardId { get; set; }
            public Guid? StatementId { get; set; }
            public string MerchantName { get; set; }
            public decimal Amount { get; set; }
            public DateTime TransactionDate { get; set; }
            public string Description { get; set; }
            public int StatementMonth { get; set; }
            public int StatementYear { get; set; }
            public bool IsRecurring { get; set; }
            public decimal? ConfidenceScore { get; set; }
            public CategoryDto Category { get; set; }  // Nested
            public DateTime CreatedAt { get; set; }
            public DateTime UpdatedAt { get; set; }
        }

    Used for:
    - Listing transactions
    - Displaying transaction details
    - Monthly analytics
    """
    id: UUID = Field(
        ...,
        description="Transaction's unique identifier",
        examples=["770e8400-e29b-41d4-a716-446655440002"]
    )

    user_id: UUID = Field(
        ...,
        description="Owner's user ID",
        examples=["660e8400-e29b-41d4-a716-446655440001"]
    )

    card_id: UUID = Field(
        ...,
        description="Credit card ID",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )

    statement_id: Optional[UUID] = Field(
        None,
        description="Statement ID (if from PDF upload)",
        examples=["880e8400-e29b-41d4-a716-446655440003"]
    )

    merchant_name: str = Field(
        ...,
        description="Merchant/store name",
        examples=["Starbucks", "NTUC FairPrice"]
    )

    amount: Decimal = Field(
        ...,
        description="Transaction amount in dollars",
        examples=[6.50, 125.00]
    )

    transaction_date: date = Field(
        ...,
        description="Transaction date",
        examples=["2024-10-15"]
    )

    description: Optional[str] = Field(
        None,
        description="Additional notes/description",
        examples=["Coffee with friends"]
    )

    statement_month: int = Field(
        ...,
        ge=1,
        le=12,
        description="Statement month (1-12)",
        examples=[10]
    )

    statement_year: int = Field(
        ...,
        ge=2020,
        le=2100,
        description="Statement year",
        examples=[2024]
    )

    is_recurring: bool = Field(
        ...,
        description="Whether transaction is recurring (detected by AI)",
        examples=[False, True]
    )

    confidence_score: Optional[Decimal] = Field(
        None,
        ge=0,
        le=1,
        description="AI confidence score (0.00-1.00)",
        examples=[0.95, 0.87]
    )

    # Nested category data
    category: Optional[CategoryResponse] = Field(
        None,
        description="Transaction category (nested object)"
    )

    created_at: datetime = Field(
        ...,
        description="When the transaction was created",
        examples=["2024-10-22T10:30:00Z"]
    )

    updated_at: datetime = Field(
        ...,
        description="When the transaction was last updated",
        examples=["2024-10-22T10:30:00Z"]
    )

    # Configuration
    model_config = ConfigDict(
        from_attributes=True,  # Allows creation from ORM models
        json_schema_extra={
            "example": {
                "id": "770e8400-e29b-41d4-a716-446655440002",
                "user_id": "660e8400-e29b-41d4-a716-446655440001",
                "card_id": "550e8400-e29b-41d4-a716-446655440000",
                "statement_id": "880e8400-e29b-41d4-a716-446655440003",
                "merchant_name": "Starbucks",
                "amount": 6.50,
                "transaction_date": "2024-10-15",
                "description": "Coffee with friends",
                "statement_month": 10,
                "statement_year": 2024,
                "is_recurring": False,
                "confidence_score": 0.95,
                "category": {
                    "id": "990e8400-e29b-41d4-a716-446655440004",
                    "name": "Dining",
                    "icon": "🍽️",
                    "color": "#FF9800",
                    "is_custom": False,
                    "created_at": "2024-10-22T10:30:00Z"
                },
                "created_at": "2024-10-22T10:30:00Z",
                "updated_at": "2024-10-22T10:30:00Z"
            }
        }
    )


# ═══════════════════════════════════════════════════════════════════
# TRANSACTION UPDATE (Input)
# ═══════════════════════════════════════════════════════════════════

class TransactionUpdate(BaseModel):
    """
    Schema for updating transaction (input)

    Compare to .NET:
        public class UpdateTransactionRequest
        {
            public Guid? CategoryId { get; set; }
            public string? Description { get; set; }
            public string? MerchantName { get; set; }
            public decimal? Amount { get; set; }
        }

    All fields are optional (partial update)

    Used for:
    - PATCH /transactions/{transaction_id}
    - User corrects AI-extracted transaction
    - User updates category
    """
    category_id: Optional[UUID] = Field(
        None,
        description="Category ID",
        examples=["660e8400-e29b-41d4-a716-446655440001"]
    )

    merchant_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Merchant/store name",
        examples=["Starbucks Orchard"]
    )

    amount: Optional[Decimal] = Field(
        None,
        gt=0,
        decimal_places=2,
        description="Transaction amount in dollars",
        examples=[7.00]
    )

    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Additional notes/description",
        examples=["Updated: Coffee and pastry"]
    )

    # Configuration
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "category_id": "660e8400-e29b-41d4-a716-446655440001",
                "description": "Updated: Coffee and pastry"
            }
        }
    )


# ═══════════════════════════════════════════════════════════════════
# TRANSACTION LIST RESPONSE (for pagination)
# ═══════════════════════════════════════════════════════════════════

class TransactionListResponse(BaseModel):
    """
    Schema for paginated transaction list

    Compare to .NET:
        public class PagedResult<T>
        {
            public List<T> Items { get; set; }
            public int Total { get; set; }
            public int Page { get; set; }
            public int PageSize { get; set; }
        }

    Used for:
    - GET /transactions?page=1&limit=20
    - Paginated transaction listing
    """
    transactions: list[TransactionResponse] = Field(
        ...,
        description="List of transactions"
    )

    total: int = Field(
        ...,
        description="Total number of transactions",
        examples=[150]
    )

    page: int = Field(
        ...,
        description="Current page number",
        examples=[1]
    )

    page_size: int = Field(
        ...,
        description="Number of items per page",
        examples=[20]
    )

    # Configuration
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "transactions": [
                    {
                        "id": "770e8400-e29b-41d4-a716-446655440002",
                        "merchant_name": "Starbucks",
                        "amount": 6.50,
                        "transaction_date": "2024-10-15",
                        "category": {
                            "name": "Dining",
                            "icon": "🍽️",
                            "color": "#FF9800"
                        }
                    }
                ],
                "total": 150,
                "page": 1,
                "page_size": 20
            }
        }
    )


# ═══════════════════════════════════════════════════════════════════
# USAGE EXAMPLES
# ═══════════════════════════════════════════════════════════════════
"""
# Example 1: List transactions with filters
GET /transactions?month=10&year=2024&category_id=660e8400-e29b-41d4-a716-446655440001&page=1&limit=20
Authorization: Bearer <token>

# Response 200 OK:
{
    "transactions": [
        {
            "id": "770e8400-e29b-41d4-a716-446655440002",
            "user_id": "660e8400-e29b-41d4-a716-446655440001",
            "card_id": "550e8400-e29b-41d4-a716-446655440000",
            "statement_id": "880e8400-e29b-41d4-a716-446655440003",
            "merchant_name": "Starbucks",
            "amount": 6.50,
            "transaction_date": "2024-10-15",
            "description": "Coffee with friends",
            "statement_month": 10,
            "statement_year": 2024,
            "is_recurring": false,
            "confidence_score": 0.95,
            "category": {
                "id": "660e8400-e29b-41d4-a716-446655440001",
                "name": "Dining",
                "icon": "🍽️",
                "color": "#FF9800",
                "is_custom": false
            },
            "created_at": "2024-10-22T10:30:00Z",
            "updated_at": "2024-10-22T10:30:00Z"
        }
    ],
    "total": 45,
    "page": 1,
    "page_size": 20
}


# Example 2: Create manual transaction
POST /transactions
Content-Type: application/json
Authorization: Bearer <token>

{
    "card_id": "550e8400-e29b-41d4-a716-446655440000",
    "merchant_name": "7-Eleven",
    "amount": 3.50,
    "transaction_date": "2024-10-20",
    "category_id": "660e8400-e29b-41d4-a716-446655440001",
    "description": "Snacks"
}

# Response 201 Created:
{
    "id": "990e8400-e29b-41d4-a716-446655440004",
    "user_id": "660e8400-e29b-41d4-a716-446655440001",
    "card_id": "550e8400-e29b-41d4-a716-446655440000",
    "statement_id": null,
    "merchant_name": "7-Eleven",
    "amount": 3.50,
    "transaction_date": "2024-10-20",
    "description": "Snacks",
    "statement_month": 10,
    "statement_year": 2024,
    "is_recurring": false,
    "confidence_score": null,
    "category": {
        "id": "660e8400-e29b-41d4-a716-446655440001",
        "name": "Shopping",
        "icon": "🛍️",
        "color": "#E91E63",
        "is_custom": false
    },
    "created_at": "2024-10-23T16:00:00Z",
    "updated_at": "2024-10-23T16:00:00Z"
}


# Example 3: Update transaction category
PATCH /transactions/770e8400-e29b-41d4-a716-446655440002
Content-Type: application/json
Authorization: Bearer <token>

{
    "category_id": "110e8400-e29b-41d4-a716-446655440005",
    "description": "Updated: Coffee and pastry"
}

# Response 200 OK:
{
    "id": "770e8400-e29b-41d4-a716-446655440002",
    "merchant_name": "Starbucks",
    "amount": 6.50,
    "transaction_date": "2024-10-15",
    "description": "Updated: Coffee and pastry",
    "category": {
        "id": "110e8400-e29b-41d4-a716-446655440005",
        "name": "Entertainment",
        "icon": "🎬",
        "color": "#9C27B0",
        "is_custom": false
    },
    "updated_at": "2024-10-23T16:30:00Z"
}
"""
