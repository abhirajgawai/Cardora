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
from app.features.auth.models import User
from app.features.insights.models import Insight, InsightTransaction
from app.features.transactions.models import Transaction
from app.features.statements.models import Statement
from app.features.categories.models import Category
from app.features.auth.jwt import get_current_user
from app.services.insights import (
    WeekendSpendingService,
    RecurringHabitService,
    SmartSpendingPraiseService,
    SubscriptionDetectionService,
    TransportSavingsService
)
from app.features.insights.ai_insights import AIInsightsService
from app.shared.insights_config import ANALYSIS_PERIOD, DUPLICATE_PREVENTION_PERIOD


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

    try:
        # Get user's most recent statements (last 6 months or 2-6 available)
        print(f"\n{'='*60}", flush=True)
        print(f"[INSIGHTS ROUTER] Generating insights for user {current_user.email}", flush=True)
        print(f"[INSIGHTS ROUTER] Today's date: {datetime.now().date()}", flush=True)
        print(f"{'='*60}\n", flush=True)

        # Query recent statements (ordered by year/month descending)
        recent_statements = db.query(Statement).filter(
            Statement.user_id == current_user.id,
            Statement.processing_status == "completed"
        ).order_by(
            Statement.statement_year.desc(),
            Statement.statement_month.desc()
        ).limit(6).all()  # Get last 6 months of statements
        print(f"[INSIGHTS ROUTER] Found {len(recent_statements)} recent statements")
        if len(recent_statements) < 2:
            print(f"[INSIGHTS ROUTER] NOT ENOUGH STATEMENTS - Need at least 2, got {len(recent_statements)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not enough data for insights. Please upload at least 2 months of statements."
            )
        # Get statement IDs
        statement_ids = [stmt.id for stmt in recent_statements]
        # Log the statement periods being analyzed
        for stmt in recent_statements:
            print(f"[INSIGHTS ROUTER]   - {stmt.statement_month}/{stmt.statement_year}")
        # Get transactions from these statements only
        transactions = db.query(Transaction).filter(
            Transaction.user_id == current_user.id,
            Transaction.statement_id.in_(statement_ids)
        ).all()
        print(f"[INSIGHTS ROUTER] Found {len(transactions)} transactions from {len(recent_statements)} recent statements", flush=True)
        # Log transaction date range
        if transactions:
            dates = [txn.transaction_date for txn in transactions]
            print(f"[INSIGHTS ROUTER] Transaction date range: {min(dates)} to {max(dates)}", flush=True)
            print(f"[INSIGHTS ROUTER] Statement IDs being analyzed: {statement_ids}", flush=True)
        if not transactions:
            print(f"[INSIGHTS ROUTER] NO TRANSACTIONS FOUND - Returning error")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No transactions found in recent statements. Statements may be processing or empty."
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
        # Calculate date range from UPLOADED STATEMENT PERIODS (not transaction dates)
        # This ensures insights say "July and September 2025" when only those months are uploaded
        # rather than showing "June to September 2025" based on transaction dates
        if recent_statements:
            from datetime import date
            # Get earliest and latest statement periods
            earliest_stmt = min(recent_statements, key=lambda s: (s.statement_year, s.statement_month))
            latest_stmt = max(recent_statements, key=lambda s: (s.statement_year, s.statement_month))

            # Create dates for first day of earliest month and last day of latest month
            earliest_date = date(earliest_stmt.statement_year, earliest_stmt.statement_month, 1)

            # Get last day of the month
            if latest_stmt.statement_month == 12:
                latest_date = date(latest_stmt.statement_year, 12, 31)
            else:
                # First day of next month minus 1 day
                from calendar import monthrange
                last_day = monthrange(latest_stmt.statement_year, latest_stmt.statement_month)[1]
                latest_date = date(latest_stmt.statement_year, latest_stmt.statement_month, last_day)
        else:
            earliest_date = latest_date = datetime.now().date()

        # Create list of uploaded statement periods for better date formatting
        statement_periods = [(s.statement_month, s.statement_year) for s in recent_statements]
        print(f"[INSIGHTS ROUTER] Statement period range: {earliest_date} to {latest_date}")
        print(f"[INSIGHTS ROUTER] Uploaded statement periods: {statement_periods}")

        # 1. Weekend Spending Insight
        if "weekend_spending" not in existing_insight_types:
            weekend_service = WeekendSpendingService(db)
            weekend_insight_data = weekend_service.generate_insight(
                user_id=str(current_user.id),
                transactions=transactions,
                date_range=(earliest_date, latest_date),
                statement_periods=statement_periods
            )
            if weekend_insight_data:
                insight = weekend_service.save_insight(
                    user_id=str(current_user.id),
                    insight_data=weekend_insight_data
                )
                # Update the set so AI knows this insight was just generated
                existing_insight_types.add("weekend_spending")
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
            print(f"[INSIGHTS ROUTER] Skipping weekend_spending - already exists within last {DUPLICATE_PREVENTION_PERIOD.days} days")
        # 2. Recurring Habit Insights (Coffee, Fast Food, etc.) - MULTIPLE INSIGHTS
        # Note: Unlike other insight types, recurring_habit can have multiple instances (one per merchant)
        habit_service = RecurringHabitService(db)
        # Use same date range as weekend spending
        habit_insights_data = habit_service.generate_insights(  # Returns LIST of insights
            user_id=str(current_user.id),
            transactions=transactions,
            date_range=(earliest_date, latest_date) if transactions else None,
            statement_periods=statement_periods
        )
        # Get existing recurring habit insight titles to avoid merchant duplicates
        existing_recurring_titles = set(
            insight.title for insight in db.query(Insight).filter(
                Insight.user_id == current_user.id,
                Insight.insight_type == "recurring_habit",
                Insight.created_at >= duplicate_check_date,
                Insight.dismissed_at.is_(None)
            ).all()
        )
        print(f"[INSIGHTS ROUTER] Found {len(habit_insights_data)} potential recurring habit insights")
        print(f"[INSIGHTS ROUTER] Existing recurring habit titles: {existing_recurring_titles}")
        # Save each recurring habit insight separately (skip duplicates by title)
        new_habits_count = 0
        for habit_insight_data in habit_insights_data:
            # Check if this specific merchant insight already exists
            if habit_insight_data["title"] not in existing_recurring_titles:
                insight = habit_service.save_insight(
                    user_id=str(current_user.id),
                    insight_data=habit_insight_data
                )
                # Update the set so AI knows this insight was just generated
                existing_insight_types.add("recurring_habit")
                generated_insights.append({
                    "id": str(insight.id),
                    "insight_type": insight.insight_type,
                    "title": insight.title,
                    "description": insight.description,
                    "impact_score": insight.impact_score,
                    "potential_savings": float(insight.potential_savings) if insight.potential_savings else None,
                    "created_at": insight.created_at.isoformat()
                })
                new_habits_count += 1
            else:
                print(f"[INSIGHTS ROUTER] Skipping duplicate recurring habit: {habit_insight_data['title']}")
        print(f"[INSIGHTS ROUTER] Generated {new_habits_count} new recurring habit insights")
        # 3. Smart Spending Praise (Public Transport Usage)
        # Track if this insight is generated to prevent overlap with transport_savings
        smart_spending_generated = False

        if "smart_spending_praise" not in existing_insight_types:
            print(f"[INSIGHTS ROUTER] Generating smart spending praise insight")
            praise_service = SmartSpendingPraiseService(db)
            praise_insight_data = praise_service.generate_insight(
                user_id=str(current_user.id),
                transactions=transactions,
                date_range=(earliest_date, latest_date),
                statement_periods=statement_periods
            )
            if praise_insight_data:
                insight = praise_service.save_insight(
                    user_id=str(current_user.id),
                    insight_data=praise_insight_data
                )
                # Update the set so AI knows this insight was just generated
                existing_insight_types.add("smart_spending_praise")
                generated_insights.append({
                    "id": str(insight.id),
                    "insight_type": insight.insight_type,
                    "title": insight.title,
                    "description": insight.description,
                    "impact_score": insight.impact_score,
                    "potential_savings": float(insight.potential_savings) if insight.potential_savings else None,
                    "created_at": insight.created_at.isoformat()
                })
                print(f"[INSIGHTS ROUTER] Generated smart spending praise insight")
                smart_spending_generated = True
            else:
                print(f"[INSIGHTS ROUTER] No smart spending praise insight generated")
        else:
            print(f"[INSIGHTS ROUTER] Skipping smart_spending_praise - already exists")
            smart_spending_generated = True  # Assume it exists, so skip transport_savings

        # 4. Transport Savings (Ride-sharing vs Public Transport)
        # Skip if smart_spending_praise was generated (they overlap - both about transport)
        if "transport_savings" not in existing_insight_types and not smart_spending_generated:
            print(f"[INSIGHTS ROUTER] Generating transport savings insight")
            transport_service = TransportSavingsService(db)
            transport_insight_data = transport_service.generate_insight(
                user_id=str(current_user.id),
                transactions=transactions,
                date_range=(earliest_date, latest_date),
                statement_periods=statement_periods
            )
            if transport_insight_data:
                insight = transport_service.save_insight(
                    user_id=str(current_user.id),
                    insight_data=transport_insight_data
                )
                # Update the set so AI knows this insight was just generated
                existing_insight_types.add("transport_savings")
                generated_insights.append({
                    "id": str(insight.id),
                    "insight_type": insight.insight_type,
                    "title": insight.title,
                    "description": insight.description,
                    "impact_score": insight.impact_score,
                    "potential_savings": float(insight.potential_savings) if insight.potential_savings else None,
                    "created_at": insight.created_at.isoformat()
                })
                print(f"[INSIGHTS ROUTER] Generated transport savings insight")
            else:
                print(f"[INSIGHTS ROUTER] No transport savings insight generated")
        elif smart_spending_generated:
            print(f"[INSIGHTS ROUTER] Skipping transport_savings - smart_spending_praise already generated (prevents overlap)")
        else:
            print(f"[INSIGHTS ROUTER] Skipping transport_savings - already exists")

        # 5. Subscription Detection (Netflix, Spotify, Gym, etc.)
        # Note: Like recurring_habit, this can have multiple instances (one per subscription)
        subscription_service = SubscriptionDetectionService(db)
        subscription_insights_data = subscription_service.generate_insights(
            user_id=str(current_user.id),
            transactions=transactions,
            date_range=(earliest_date, latest_date) if transactions else None,
            statement_periods=statement_periods
        )
        # Get existing subscription titles to avoid duplicates
        existing_subscription_titles = set(
            insight.title for insight in db.query(Insight).filter(
                Insight.user_id == current_user.id,
                Insight.insight_type == "subscription_detection",
                Insight.created_at >= duplicate_check_date,
                Insight.dismissed_at.is_(None)
            ).all()
        )
        print(f"[INSIGHTS ROUTER] Found {len(subscription_insights_data)} potential subscription insights")
        print(f"[INSIGHTS ROUTER] Existing subscription titles: {existing_subscription_titles}")
        # Save each subscription insight separately (skip duplicates by title)
        new_subscriptions_count = 0
        for subscription_data in subscription_insights_data:
            if subscription_data["title"] not in existing_subscription_titles:
                insight = subscription_service.save_insight(
                    user_id=str(current_user.id),
                    insight_data=subscription_data
                )
                # Update the set so AI knows this insight was just generated
                existing_insight_types.add("subscription_detection")
                generated_insights.append({
                    "id": str(insight.id),
                    "insight_type": insight.insight_type,
                    "title": insight.title,
                    "description": insight.description,
                    "impact_score": insight.impact_score,
                    "potential_savings": float(insight.potential_savings) if insight.potential_savings else None,
                    "created_at": insight.created_at.isoformat()
                })
                new_subscriptions_count += 1
            else:
                print(f"[INSIGHTS ROUTER] Skipping duplicate subscription: {subscription_data['title']}")
        print(f"[INSIGHTS ROUTER] Generated {new_subscriptions_count} new subscription insights")

        # 6. AI-Powered Personalized Insight (Gemini API)
        # Only generate if we don't have one recently (expensive API call)
        print(f"[INSIGHTS ROUTER] *** CHECKING IF AI INSIGHTS SHOULD BE GENERATED ***")
        print(f"[INSIGHTS ROUTER] Existing types (including just-generated): {existing_insight_types}")
        if "ai_personalized" not in existing_insight_types:
            print(f"[INSIGHTS ROUTER] Generating AI-powered personalized insight")
            try:
                ai_service = AIInsightsService(db)
                ai_insight_data = ai_service.generate_insight(
                    user_id=str(current_user.id),
                    transactions=transactions,
                    date_range=(earliest_date, latest_date),
                    statement_periods=statement_periods,
                    existing_insight_types=existing_insight_types
                )
                if ai_insight_data:
                    insight = ai_service.save_insight(
                        user_id=str(current_user.id),
                        insight_data=ai_insight_data
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
                    print(f"[INSIGHTS ROUTER] Generated AI-powered insight successfully")
                else:
                    print(f"[INSIGHTS ROUTER] AI insight generation returned None")
            except Exception as ai_error:
                # Don't fail the entire insights generation if AI fails
                # (e.g., API key not configured, API rate limit, etc.)
                print(f"[INSIGHTS ROUTER] AI insight generation failed: {str(ai_error)}")
                print(f"[INSIGHTS ROUTER] Continuing with rule-based insights only...")
        else:
            print(f"[INSIGHTS ROUTER] Skipping ai_personalized - already exists within last {DUPLICATE_PREVENTION_PERIOD.days} days")

        # Sort insights by impact score (highest first) for better UX
        generated_insights.sort(key=lambda x: x.get("impact_score", 0), reverse=True)
        print(f"\n[INSIGHTS ROUTER] Successfully generated {len(generated_insights)} insights", flush=True)
        return {
            "generated": len(generated_insights),
            "insights": generated_insights,
            "message": f"Generated {len(generated_insights)} new insight(s)" if generated_insights else "No new insights generated based on your spending patterns."
        }

    except HTTPException:
        # Re-raise HTTP exceptions (like 400 Bad Request)
        raise
    except Exception as e:
        # Catch any unexpected errors and return detailed information
        import traceback
        error_details = traceback.format_exc()

        print(f"\n{'='*60}", flush=True)
        print(f"[INSIGHTS ROUTER] FATAL ERROR!", flush=True)
        print(f"{'='*60}", flush=True)
        print(f"Error Type: {type(e).__name__}", flush=True)
        print(f"Error Message: {str(e)}", flush=True)
        print(f"\nFull Traceback:", flush=True)
        print(error_details, flush=True)
        print(f"{'='*60}\n", flush=True)

        # Return detailed error to client
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": str(e),
                "error_type": type(e).__name__,
                "message": "An unexpected error occurred while generating insights. Check the error details below.",
                "hint": "Check server logs for full traceback."
            }
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

