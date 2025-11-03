"""
Category Router - Manage Transaction Categories

Endpoints:
- GET /categories - List all categories (system + user's custom)

Future endpoints (not implemented yet):
- POST /categories - Create custom category
- PATCH /categories/{category_id} - Update custom category
- DELETE /categories/{category_id} - Delete custom category

Compare to .NET: Like CategoriesController
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.features.auth.models import User
from app.features.categories.models import Category
from app.features.auth.schemas import CategoryResponse
from app.features.auth.jwt import get_current_user

# ═══════════════════════════════════════════════════════════════════
# ROUTER SETUP
# ═══════════════════════════════════════════════════════════════════

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


# ═══════════════════════════════════════════════════════════════════
# GET /categories - List All Categories
# ═══════════════════════════════════════════════════════════════════

@router.get(
    "",
    response_model=List[CategoryResponse],
    status_code=status.HTTP_200_OK,
    summary="List all categories",
    description="Get all available categories (system + user's custom categories)"
)
async def list_categories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all available categories

    Returns:
    - System categories (user_id = NULL) - Available to all users
    - User's custom categories (user_id = current_user.id)

    Categories are ordered by:
    1. System categories first (is_custom = False)
    2. Then custom categories
    3. Alphabetically by name
    """

    # Get system categories (user_id = NULL) + user's custom categories
    categories = db.query(Category).filter(
        (Category.user_id == None) |  # System categories
        (Category.user_id == current_user.id)  # User's custom categories
    ).order_by(
        Category.is_custom.asc(),  # System categories first
        Category.name.asc()  # Then alphabetically
    ).all()

    return [CategoryResponse.model_validate(cat) for cat in categories]


# ═══════════════════════════════════════════════════════════════════
# USAGE EXAMPLES
# ═══════════════════════════════════════════════════════════════════
"""
# Example 1: List all categories
GET /categories
Authorization: Bearer <token>

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
        "name": "Dining",
        "icon": "🍽️",
        "color": "#FF9800",
        "is_custom": false,
        "created_at": "2024-10-22T10:30:00Z"
    },
    {
        "id": "770e8400-e29b-41d4-a716-446655440002",
        "name": "Coffee Shops",
        "icon": "☕",
        "color": "#8B4513",
        "is_custom": true,
        "created_at": "2024-10-23T14:00:00Z"
    }
]

Note: System categories (is_custom=false) are available to all users.
      Custom categories (is_custom=true) are private to the user who created them.
"""
