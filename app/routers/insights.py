"""
Insights Router - AI and Rule-Based Financial Insights

Endpoints for generating and retrieving financial insights.
All endpoints require authentication.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.user import User
from app.models.insight import Insight
from app.models.transaction import Transaction
from app.auth.jwt import get_current_user
from app.services.insights import WeekendSpendingService


# ═══════════════════════════════════════════════════════════════════
# ROUTER SETUP
# ═══════════════════════════════════════════════════════════════════

router = APIRouter(
    prefix="/insights",
    tags=["Insights"]
)


# ═══════════════════════════════════════════════════════════════════
# GET /insights - Get All Insights for Current User
# ═══════════════════════════════════════════════════════════════════

@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="Get all insights for current user",
    description="Retrieve all financial insights for the authenticated user. Includes both active and dismissed insights."
)
async def get_insights(
    include_dismissed: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all insights for the current user

    Query Parameters:
        - include_dismissed: If True, includes dismissed insights. Default: False

    Returns:
        List of insights ordered by created_at (newest first)
    """

    # Base query: get user's insights
    query = db.query(Insight).filter(Insight.user_id == current_user.id)

    # Filter out dismissed insights unless explicitly requested
    if not include_dismissed:
        query = query.filter(Insight.dismissed_at.is_(None))

    # Order by created date (newest first)
    insights = query.order_by(desc(Insight.created_at)).all()

    # Convert to dict for response
    result = []
    for insight in insights:
        result.append({
            "id": str(insight.id),
            "insight_type": insight.insight_type,
            "title": insight.title,
            "description": insight.description,
            "impact_score": insight.impact_score,
            "potential_savings": float(insight.potential_savings) if insight.potential_savings else None,
            "created_at": insight.created_at.isoformat(),
            "dismissed_at": insight.dismissed_at.isoformat() if insight.dismissed_at else None
        })

    return {
        "insights": result,
        "count": len(result)
    }


# ═══════════════════════════════════════════════════════════════════
# POST /insights/generate - Generate Insights for Current User
# ═══════════════════════════════════════════════════════════════════

@router.post(
    "/generate",
    status_code=status.HTTP_200_OK,
    summary="Generate new insights for current user",
    description="Analyze user transactions and generate new financial insights using rule-based algorithms."
)
async def generate_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate new insights for the current user

    Process:
    1. Fetch last 3 months of transactions
    2. Run rule-based insight algorithms (Weekend Spending, etc.)
    3. Save generated insights to database
    4. Return newly created insights

    Returns:
        List of newly generated insights
    """

    # Get user's transactions from last 3 months
    three_months_ago = datetime.now() - timedelta(days=90)

    print(f"\n{'='*60}")
    print(f"[INSIGHTS ROUTER] Generating insights  ")
    print(f"[INSIGHTS ROUTER] Today's date: {datetime.now().date()}")
    print(f"[INSIGHTS ROUTER] 3 months ago: {three_months_ago.date()}")
    print(f"{'='*60}\n")

    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_date >= three_months_ago.date()
    ).all()

    print(f"[INSIGHTS ROUTER] Found {len(transactions)} transactions from last 90 days")

    if not transactions:
        print(f"[INSIGHTS ROUTER] NO TRANSACTIONS FOUND - Returning error")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No transactions found. Please upload statements first."
        )

    # Generate insights using rule-based services
    generated_insights = []

    # 1. Weekend Spending Insight
    weekend_service = WeekendSpendingService(db)
    weekend_insight_data = weekend_service.generate_insight(
        user_id=str(current_user.id),
        transactions=transactions
    )

    if weekend_insight_data:
        insight = weekend_service.save_insight(
            user_id=str(current_user.id),
            insight_data=weekend_insight_data
        )
        generated_insights.append({
            "id": str(insight.id),
            "insight_type": insight.insight_type,
            "title": insight.title,
            "description": insight.description,
            "impact_score": insight.impact_score,
            "potential_savings": float(insight.potential_savings) if insight.potential_savings else None,
            "created_at": insight.created_at.isoformat()
        })

    # TODO: Add more insight types here (Coffee Habit, Subscription Audit, etc.)

    return {
        "generated": len(generated_insights),
        "insights": generated_insights,
        "message": f"Generated {len(generated_insights)} new insight(s)" if generated_insights else "No new insights generated based on your spending patterns."
    }


# ═══════════════════════════════════════════════════════════════════
# PATCH /insights/{insight_id}/dismiss - Dismiss an Insight
# ═══════════════════════════════════════════════════════════════════

@router.patch(
    "/{insight_id}/dismiss",
    status_code=status.HTTP_200_OK,
    summary="Dismiss an insight",
    description="Mark an insight as dismissed. Dismissed insights won't show up in the default list."
)
async def dismiss_insight(
    insight_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Dismiss an insight

    The insight remains in the database but is marked as dismissed.
    """

    # Find the insight
    insight = db.query(Insight).filter(
        Insight.id == insight_id,
        Insight.user_id == current_user.id
    ).first()

    if not insight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insight not found"
        )

    # Mark as dismissed
    insight.dismissed_at = datetime.now()
    db.commit()

    return {
        "message": "Insight dismissed successfully",
        "id": str(insight.id)
    }
