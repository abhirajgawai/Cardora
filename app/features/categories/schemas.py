"""
Category Pydantic Schemas (DTOs)

Compare to .NET: Like having DTOs for Categories
    - CategoryResponse → CategoryDto (output)

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
# CATEGORY RESPONSE (Output)
# ═══════════════════════════════════════════════════════════════════

class CategoryResponse(BaseModel):
    """
    Schema for category data response (output)

    Compare to .NET:
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
        examples=["#4CAF50", "#FF9800", "#2196F3"]
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

    # Configuration
    model_config = ConfigDict(
        from_attributes=True,  # Allows creation from ORM models
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Groceries",
                "icon": "🛒",
                "color": "#4CAF50",
                "is_custom": False,
                "created_at": "2024-10-22T10:30:00Z"
            }
        }
    )


# ═══════════════════════════════════════════════════════════════════
# CATEGORY CREATE (Future feature - custom categories)
# ═══════════════════════════════════════════════════════════════════

class CategoryCreate(BaseModel):
    """
    Schema for creating custom category (input)

    Compare to .NET:
        public class CreateCategoryRequest
        {
            [Required]
            public string Name { get; set; }

            public string Icon { get; set; }
            public string Color { get; set; }
        }

    Used for:
    - POST /categories (future endpoint)
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
        pattern="^#[0-9A-Fa-f]{6}$",  # Validates hex color format
        description="Category color (hex code)",
        examples=["#8B4513", "#FF1493"]
    )

    # Configuration
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
# USAGE EXAMPLES
# ═══════════════════════════════════════════════════════════════════
"""
# Example 1: List all categories (system + user's custom)
GET /categories

# Response 200 OK:
[
    {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "Groceries",
        "icon": "🛒",
        "color": "#4CAF50",
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


# Example 2: Create custom category (future feature)
POST /categories
Content-Type: application/json
Authorization: Bearer <token>

{
    "name": "Coffee Shops",
    "icon": "☕",
    "color": "#8B4513"
}

# Response 201 Created:
{
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "name": "Coffee Shops",
    "icon": "☕",
    "color": "#8B4513",
    "is_custom": true,
    "created_at": "2024-10-23T14:00:00Z"
}


# Example 3: Category in transaction response
{
    "id": "770e8400-e29b-41d4-a716-446655440002",
    "merchant_name": "Starbucks",
    "amount": 6.50,
    "transaction_date": "2024-10-15",
    "category": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "Dining",
        "icon": "🍽️",
        "color": "#FF9800",
        "is_custom": false
    }
}
"""
