"""
Category Pydantic Schemas (DTOs)

    - CategoryResponse → CategoryDto (output)
    - CategoryCreate → POST /categories input
    - CategoryUpdate → PATCH /categories/{id} input

Categories in Cardora:
- System categories: user_id = NULL (available to all users)
- Custom categories: user_id = specific UUID (private to that user)

Examples:
    System: Groceries, Dining, Transport, Shopping, etc.
    Custom: User creates "Coffee Shops", "Pet Supplies", etc.
"""

from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional


# ═══════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════

class CategoryResponse(BaseModel):
    """
    Schema for category data response (output)

        public class CategoryDto
        {
            public Guid Id { get; set; }
            public string Name { get; set; }
            public string Icon { get; set; }
            public string Color { get; set; }
            public bool IsCustom { get; set; }
            public DateTime CreatedAt { get; set; }
        }

    Used for:
    - Listing all categories (system + user's custom)
    - Displaying category in transaction details
    - Category selection dropdown
    """
    id: UUID = Field(
        ...,
        description="Category's unique identifier",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )

    name: str = Field(
        ...,
        description="Category name",
        examples=["Groceries", "Dining", "Transport"]
    )

    icon: Optional[str] = Field(
        None,
        description="Category icon (emoji)",
        examples=["🛒", "🍽️", "🚗"]
    )

    color: Optional[str] = Field(
        None,
        description="Category color (hex code)",
    )

    is_custom: bool = Field(
        ...,
        description="Whether this is a custom user category (False = system category)",
        examples=[False, True]
    )

    created_at: datetime = Field(
        ...,
        description="When the category was created",
        examples=["2024-10-22T10:30:00Z"]
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Groceries",
                "icon": "🛒",
                "is_custom": False,
                "created_at": "2024-10-22T10:30:00Z"
            }
        }
    )


# ═══════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════

class CategoryCreate(BaseModel):
    """
    Schema for creating custom category (input)

        public class CreateCategoryRequest
        {
            [Required]
            public string Name { get; set; }

            public string Icon { get; set; }
            public string Color { get; set; }
        }

    Used for:
    - POST /categories
    - User creates custom category
    """
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Category name",
        examples=["Coffee Shops", "Pet Supplies"]
    )

    icon: Optional[str] = Field(
        None,
        max_length=10,
        description="Category icon (emoji)",
        examples=["☕", "🐾"]
    )

    color: Optional[str] = Field(
        None,
        max_length=7,
        description="Category color (hex code)",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Coffee Shops",
                "icon": "☕",
                "color": "#8B4513"
            }
        }
    )


# ═══════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════

class CategoryUpdate(BaseModel):
    """
    Schema for updating custom category (input)

    All fields optional — only provided fields are updated (PATCH semantics).

    Used for:
    - PATCH /categories/{category_id}
    - User updates their own custom category
    """
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Category name",
        examples=["Coffee Shops", "Pet Supplies"]
    )

    icon: Optional[str] = Field(
        None,
        max_length=10,
        description="Category icon (emoji)",
        examples=["☕", "🐾"]
    )

    color: Optional[str] = Field(
        None,
        max_length=7,
        description="Category color (hex code)",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Coffee Shops",
                "icon": "☕",
                "color": "#8B4513"
            }
        }
    )


# ═══════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════
"""
GET /categories

[
    {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "Groceries",
        "icon": "🛒",
        "is_custom": false,
        "created_at": "2024-10-22T10:30:00Z"
    },
    {
        "id": "660e8400-e29b-41d4-a716-446655440001",
        "name": "Coffee Shops",
        "icon": "☕",
        "color": "#8B4513",
        "is_custom": true,
        "created_at": "2024-10-23T14:00:00Z"
    }
]


POST /categories
Content-Type: application/json
Authorization: Bearer ***

{
    "name": "Coffee Shops",
    "icon": "☕",
    "color": "#8B4513"
}

{
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "name": "Coffee Shops",
    "icon": "☕",
    "color": "#8B4513",
    "is_custom": true,
    "created_at": "2024-10-23T14:00:00Z"
}


{
    "id": "770e8400-e29b-41d4-a716-446655440002",
    "merchant_name": "Starbucks",
    "amount": 6.50,
    "transaction_date": "2024-10-15",
    "category": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "Dining",
        "icon": "🍽️",
        "is_custom": false
    }
}
"""
