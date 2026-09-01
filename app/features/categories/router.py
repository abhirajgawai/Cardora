"""
Category Router - Manage Transaction Categories

Endpoints:
- GET /categories - List all categories (system + user's custom)
- POST /categories - Create custom category (201)
- PATCH /categories/{category_id} - Update user's custom category
- DELETE /categories/{category_id} - Delete user's custom category (204)

System categories (is_custom=False, user_id=NULL) are read-only for everyone.
Cross-user access to custom categories returns 404 (never leaks existence).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.features.auth.models import User
from app.features.categories.models import Category
from app.features.categories.schemas import CategoryCreate, CategoryUpdate, CategoryResponse
from app.features.auth.jwt import get_current_user

# ═══════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


# ═══════════════════════════════════════════════════════════════════
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

    categories = db.query(Category).filter(
        (Category.user_id == current_user.id) | (Category.user_id.is_(None))
    ).order_by(
        Category.is_custom.asc(),
        Category.name.asc()
    ).all()

    return [CategoryResponse.model_validate(cat) for cat in categories]


# ═══════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════

@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a custom category",
    description="Create a new user-defined category owned by the authenticated user"
)
async def create_category(
    payload: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trimmed_name = payload.name.strip()
    if not trimmed_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category name cannot be empty"
        )

    duplicate = db.query(Category).filter(
        func.lower(Category.name) == trimmed_name.lower(),
        ((Category.user_id == current_user.id) | (Category.user_id.is_(None)))
    ).first()
    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A category with this name already exists"
        )

    category = Category(
        user_id=current_user.id,
        name=trimmed_name,
        icon=payload.icon,
        color=payload.color,
        is_custom=True,
    )
    db.add(category)
    db.commit()
    db.refresh(category)

    return CategoryResponse.model_validate(category)


# ═══════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════

def _get_owned_custom_category_or_404(
    category_id,
    current_user: User,
    db: Session
) -> Category:
    """
    Shared lookup for PATCH/DELETE.

    404 when: the id doesn't exist, or it belongs to another user
    (never reveal another user's resource).

    403 when: it's a system category (read-only for everyone).
    """
    category = db.query(Category).filter(
        Category.id == category_id
    ).first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    if category.user_id is None or not category.is_custom:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="System categories cannot be modified"
        )

    if category.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    return category


# ═══════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════

@router.patch(
    "/{category_id}",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a custom category",
    description="Update name/icon/color of a category owned by the authenticated user"
)
async def update_category(
    category_id,
    payload: CategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    category = _get_owned_custom_category_or_404(category_id, current_user, db)

    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )

    if "name" in updates:
        if updates["name"] is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category name cannot be empty"
            )
        trimmed_name = updates["name"].strip()
        if not trimmed_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category name cannot be empty"
            )
        updates["name"] = trimmed_name

    if "name" in updates and updates["name"].lower() != category.name.lower():
        duplicate = db.query(Category).filter(
            func.lower(Category.name) == updates["name"].lower(),
            ((Category.user_id == current_user.id) | (Category.user_id.is_(None)))
        ).first()
        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A category with this name already exists"
            )

    for field, value in updates.items():
        setattr(category, field, value)

    db.commit()
    db.refresh(category)

    return CategoryResponse.model_validate(category)


# ═══════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════

@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a custom category",
    description="Delete a category owned by the authenticated user"
)
async def delete_category(
    category_id,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    category = _get_owned_custom_category_or_404(category_id, current_user, db)

    db.delete(category)
    db.commit()

    return None


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
