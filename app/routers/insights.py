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
from uuid import UUID

from app.core.database import get_db
from app.models.user import User
from app.models.insight import Insight, InsightTransaction
from app.models.transaction import Transaction
from app.models.category import Category
from app.auth.jwt import get_current_user
from app.services.insights import WeekendSpendingService
from app.config.insights_config import ANALYSIS_PERIOD, DUPLICATE_PREVENTION_PERIOD


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

    # Get user's transactions from configured analysis period
    analysis_start_date = datetime.now() - ANALYSIS_PERIOD

    print(f"\n{'='*60}")
    print(f"[INSIGHTS ROUTER] Generating insights  ")
    print(f"[INSIGHTS ROUTER] Today's date: {datetime.now().date()}")
    print(f"[INSIGHTS ROUTER] Analysis period: {ANALYSIS_PERIOD.days} days")
    print(f"[INSIGHTS ROUTER] Analysis start date: {analysis_start_date.date()}")
    print(f"{'='*60}\n")

    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_date >= analysis_start_date.date()
    ).all()

    print(f"[INSIGHTS ROUTER] Found {len(transactions)} transactions from last {ANALYSIS_PERIOD.days} days")

    if not transactions:
        print(f"[INSIGHTS ROUTER] NO TRANSACTIONS FOUND - Returning error")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No transactions found. Please upload statements first."
        )

    # Generate insights using rule-based services
    generated_insights = []

    # Check for existing insights to prevent duplicates
    duplicate_check_date = datetime.now() - DUPLICATE_PREVENTION_PERIOD
    existing_insight_types = set(
        insight.insight_type for insight in db.query(Insight).filter(
            Insight.user_id == current_user.id,
            Insight.created_at >= duplicate_check_date,
            Insight.dismissed_at.is_(None)  # Only consider non-dismissed insights
        ).all()
    )

    print(f"[INSIGHTS ROUTER] Existing insight types from last {DUPLICATE_PREVENTION_PERIOD.days} days: {existing_insight_types}")

    # 1. Weekend Spending Insight
    if "weekend_spending" not in existing_insight_types:
        weekend_service = WeekendSpendingService(db)

        # Calculate actual date range from transactions
        if transactions:
            earliest_date = min(txn.transaction_date for txn in transactions)
            latest_date = max(txn.transaction_date for txn in transactions)
        else:
            earliest_date = latest_date = datetime.now().date()

        weekend_insight_data = weekend_service.generate_insight(
            user_id=str(current_user.id),
            transactions=transactions,
            date_range=(earliest_date, latest_date)
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
    else:
        print(f"[INSIGHTS ROUTER] Skipping weekend_spending - already exists within last 7 days")

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


# ═══════════════════════════════════════════════════════════════════
# GET /insights/{insight_id}/transactions - Get Linked Transactions
# ═══════════════════════════════════════════════════════════════════

@router.get(
    "/{insight_id}/transactions",
    status_code=status.HTTP_200_OK,
    summary="Get transactions linked to an insight",
    description="Retrieve all transactions that contributed to a specific insight."
)
async def get_insight_transactions(
    insight_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all transactions linked to a specific insight

    This endpoint returns:
    - The insight details
    - All transactions that contributed to this insight
    - Summary statistics (total amount, count)

    Returns:
        Insight with linked transactions
    """

    try:
        # Convert string to UUID
        insight_uuid = UUID(insight_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid insight ID format"
        )

    print(f"[INSIGHTS] Fetching transactions for insight: {insight_uuid}")
    print(f"[INSIGHTS] Current user ID: {current_user.id} (type: {type(current_user.id)})")

    # Find the insight and verify ownership
    insight = db.query(Insight).filter(
        Insight.id == insight_uuid,
        Insight.user_id == current_user.id  # Both are UUIDs, no conversion needed
    ).first()

    if not insight:
        print(f"[INSIGHTS] Insight not found for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insight not found"
        )

    print(f"[INSIGHTS] Found insight: {insight.title}")

    # Get linked transactions through junction table
    insight_transactions = db.query(InsightTransaction).filter(
        InsightTransaction.insight_id == insight_uuid
    ).all()

    print(f"[INSIGHTS] Found {len(insight_transactions)} linked transaction records")

    # Fetch the actual transaction records
    transaction_ids = [it.transaction_id for it in insight_transactions]

    if not transaction_ids:
        print(f"[INSIGHTS] No transaction IDs found")
        return {
            "insight": {
                "id": str(insight.id),
                "insight_type": insight.insight_type,
                "title": insight.title,
                "description": insight.description,
                "impact_score": insight.impact_score,
                "potential_savings": float(insight.potential_savings) if insight.potential_savings else None,
                "created_at": insight.created_at.isoformat()
            },
            "transactions": [],
            "summary": {
                "total_amount": 0.0,
                "transaction_count": 0
            }
        }

    # Join with Category to get category name
    transactions = db.query(Transaction).join(
        Category, Transaction.category_id == Category.id, isouter=True
    ).filter(
        Transaction.id.in_(transaction_ids)
    ).order_by(desc(Transaction.transaction_date)).all()

    print(f"[INSIGHTS] Found {len(transactions)} actual transactions")

    # Calculate summary statistics
    total_amount = sum(float(txn.amount) for txn in transactions)

    # Format transactions for response
    transactions_data = []
    for txn in transactions:
        # Get category name from relationship (if exists)
        category_name = txn.category.name if txn.category else "Uncategorized"

        transactions_data.append({
            "id": str(txn.id),
            "transaction_date": txn.transaction_date.isoformat(),
            "merchant_name": txn.merchant_name,
            "amount": float(txn.amount),
            "category_name": category_name,
            "description": txn.description
        })

    return {
        "insight": {
            "id": str(insight.id),
            "insight_type": insight.insight_type,
            "title": insight.title,
            "description": insight.description,
            "impact_score": insight.impact_score,
            "potential_savings": float(insight.potential_savings) if insight.potential_savings else None,
            "created_at": insight.created_at.isoformat()
        },
        "transactions": transactions_data,
        "summary": {
            "total_amount": round(total_amount, 2),
            "transaction_count": len(transactions)
        }
    }
