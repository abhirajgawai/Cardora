"""
Analytics Router - Spending Analysis Across Cards and Time

THE REAL VALUE OF CARDORA!

This router provides powerful analytics across multiple credit cards:
- Monthly spending analysis (combined across all cards)
- Month-to-month comparisons
- Multi-month trend analysis
- Annual spending breakdown
- Per-card and per-category insights

Compare to .NET: Like AnalyticsController with complex aggregation queries
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Optional
from collections import defaultdict
from calendar import month_name

from app.core.database import get_db
from app.features.auth.models import User
from app.features.cards.models import CreditCard
from app.features.transactions.models import Transaction
from app.features.categories.models import Category
from app.features.analytics.schemas import (
    MonthlyAnalysisResponse,
    ComparisonResponse,
    TrendAnalysisResponse,
    AnnualAnalysisResponse,
    CardsAnalysisResponse,
    CategoryAnalysisResponse
)
from app.features.auth.jwt import get_current_user

# ═══════════════════════════════════════════════════════════════════
# ROUTER SETUP
# ═══════════════════════════════════════════════════════════════════

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


# ═══════════════════════════════════════════════════════════════════
# GET /analytics/monthly - Monthly Analysis (ALL CARDS COMBINED)
# ═══════════════════════════════════════════════════════════════════

@router.get(
    "/monthly",
    response_model=MonthlyAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Monthly spending analysis across all cards",
    description="Get combined spending analysis for a specific month across all credit cards"
)
async def get_monthly_analysis(
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    year: int = Query(..., ge=2020, le=2100, description="Year"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive monthly analysis across ALL user's cards

    Use Case: "How much did I spend in April 2025 across all my cards?"

    Returns:
    - Total spending for the month
    - Per-card breakdown
    - Category breakdown
    - Top merchants
    - Transaction count

    Example:
    GET /analytics/monthly?month=4&year=2025

    Response:
    {
      "month": 4,
      "year": 2025,
      "total_spending": 8750.50,
      "total_transactions": 67,
      "cards_included": [
        {"bank": "CITI", "last_four": "0368", "spending": 4500.00, ...},
        {"bank": "SC Bank", "last_four": "1234", "spending": 4250.50, ...}
      ],
      "category_breakdown": {
        "Dining": 2500.00,
        "Groceries": 1800.00,
        ...
      },
      "top_merchants": [...]
    }
    """

    # Get all transactions for the month across all user's cards
    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.statement_month == month,
        Transaction.statement_year == year
    ).all()

    if not transactions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No transactions found for {month}/{year}"
        )

    # Calculate total spending
    total_spending = sum(t.amount for t in transactions)
    total_transactions = len(transactions)

    # Per-card breakdown
    card_spending = defaultdict(lambda: {"spending": Decimal("0.00"), "count": 0})

    for trans in transactions:
        card = trans.credit_card
        card_key = (card.bank_name, card.last_four_digits, card.card_name)
        card_spending[card_key]["spending"] += trans.amount
        card_spending[card_key]["count"] += 1

    cards_included = []
    for (bank, last_four, card_name), data in card_spending.items():
        percentage = float((data["spending"] / total_spending) * 100) if total_spending > 0 else 0.0
        cards_included.append({
            "bank": bank,
            "card_name": card_name,
            "last_four": last_four,
            "spending": data["spending"],
            "transaction_count": data["count"],
            "percentage": round(percentage, 2)
        })

    # Sort by spending (highest first)
    cards_included.sort(key=lambda x: x["spending"], reverse=True)

    # Category breakdown
    category_breakdown = {}
    for trans in transactions:
        cat_name = trans.category.name if trans.category else "Uncategorized"
        if cat_name not in category_breakdown:
            category_breakdown[cat_name] = Decimal("0.00")
        category_breakdown[cat_name] += trans.amount

    # Top merchants (top 10)
    merchant_spending = defaultdict(Decimal)
    for trans in transactions:
        merchant_spending[trans.merchant_name] += trans.amount

    top_merchants = [
        {"name": merchant, "amount": amount}
        for merchant, amount in sorted(
            merchant_spending.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
    ]

    return {
        "month": month,
        "year": year,
        "total_spending": total_spending,
        "total_transactions": total_transactions,
        "cards_included": cards_included,
        "category_breakdown": category_breakdown,
        "top_merchants": top_merchants
    }


# ═══════════════════════════════════════════════════════════════════
# GET /analytics/compare - Compare Two Months
# ═══════════════════════════════════════════════════════════════════

@router.get(
    "/compare",
    response_model=ComparisonResponse,
    status_code=status.HTTP_200_OK,
    summary="Compare spending between two months",
    description="Compare spending patterns between two different months"
)
async def compare_months(
    current_month: int = Query(..., ge=1, le=12, description="Current month"),
    current_year: int = Query(..., ge=2020, le=2100, description="Current year"),
    compare_month: int = Query(..., ge=1, le=12, description="Month to compare against"),
    compare_year: int = Query(..., ge=2020, le=2100, description="Year to compare against"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Compare spending between two months

    Use Case: "Did I spend more in April than March?"

    Returns:
    - Spending for both months
    - Difference and percentage change
    - Category-by-category comparison

    Example:
    GET /analytics/compare?current_month=4&current_year=2025&compare_month=3&compare_year=2025
    """

    # Get transactions for current month
    current_trans = db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.statement_month == current_month,
        Transaction.statement_year == current_year
    ).all()

    # Get transactions for comparison month
    compare_trans = db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.statement_month == compare_month,
        Transaction.statement_year == compare_year
    ).all()

    if not current_trans or not compare_trans:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insufficient data for comparison"
        )

    # Calculate totals
    current_total = sum(t.amount for t in current_trans)
    compare_total = sum(t.amount for t in compare_trans)

    difference = current_total - compare_total
    percentage_change = float((difference / compare_total) * 100) if compare_total > 0 else 0.0

    # Category-by-category comparison
    current_categories = defaultdict(Decimal)
    compare_categories = defaultdict(Decimal)

    for trans in current_trans:
        cat_name = trans.category.name if trans.category else "Uncategorized"
        current_categories[cat_name] += trans.amount

    for trans in compare_trans:
        cat_name = trans.category.name if trans.category else "Uncategorized"
        compare_categories[cat_name] += trans.amount

    # Combine all categories
    all_categories = set(current_categories.keys()) | set(compare_categories.keys())

    category_changes = {}
    for cat in all_categories:
        current_amt = current_categories.get(cat, Decimal("0.00"))
        compare_amt = compare_categories.get(cat, Decimal("0.00"))
        change = current_amt - compare_amt
        pct_change = float((change / compare_amt) * 100) if compare_amt > 0 else 0.0

        category_changes[cat] = {
            "current": current_amt,
            "previous": compare_amt,
            "change": change,
            "percentage_change": round(pct_change, 2)
        }

    return {
        "current_month": {
            "month": current_month,
            "year": current_year,
            "total": current_total,
            "transaction_count": len(current_trans)
        },
        "previous_month": {
            "month": compare_month,
            "year": compare_year,
            "total": compare_total,
            "transaction_count": len(compare_trans)
        },
        "difference": difference,
        "percentage_change": round(percentage_change, 2),
        "category_changes": category_changes
    }


# ═══════════════════════════════════════════════════════════════════
# GET /analytics/trend - Multi-Month Trend Analysis
# ═══════════════════════════════════════════════════════════════════

@router.get(
    "/trend",
    response_model=TrendAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Multi-month spending trend",
    description="Analyze spending trends over multiple months (e.g., last 6 months)"
)
async def get_trend_analysis(
    months: int = Query(6, ge=1, le=24, description="Number of months to analyze"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze spending trend over multiple months

    Use Case: "What's my spending trend over the last 6 months?"

    Returns:
    - Monthly spending for each month
    - Average monthly spending
    - Highest/lowest months
    - Category trends over time

    Example:
    GET /analytics/trend?months=6

    Response:
    {
      "period": "Last 6 months",
      "monthly_totals": [
        {"month": "Nov 2024", "total": 6500.00, ...},
        {"month": "Dec 2024", "total": 9800.00, ...},
        ...
      ],
      "average_monthly": 7708.42,
      "highest_month": {"month": "Dec 2024", "total": 9800.00},
      "lowest_month": {"month": "Feb 2025", "total": 6900.00}
    }
    """

    # Calculate date range
    today = datetime.now()
    end_month = today.month
    end_year = today.year

    # Get transactions for the last N months
    monthly_data = []

    for i in range(months):
        # Calculate month/year
        target_month = end_month - i
        target_year = end_year

        while target_month <= 0:
            target_month += 12
            target_year -= 1

        # Get transactions for this month
        trans = db.query(Transaction).filter(
            Transaction.user_id == current_user.id,
            Transaction.statement_month == target_month,
            Transaction.statement_year == target_year
        ).all()

        if trans:
            total = sum(t.amount for t in trans)
            monthly_data.append({
                "month": f"{month_name[target_month][:3]} {target_year}",
                "month_num": target_month,
                "year": target_year,
                "total": total,
                "transaction_count": len(trans)
            })

    if not monthly_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No data found for the last {months} months"
        )

    # Reverse to show oldest first
    monthly_data.reverse()

    # Calculate statistics
    totals = [d["total"] for d in monthly_data]
    average_monthly = sum(totals) / len(totals) if totals else Decimal("0.00")

    highest_month = max(monthly_data, key=lambda x: x["total"])
    lowest_month = min(monthly_data, key=lambda x: x["total"])

    # Category trends (simplified - just show top 5 categories)
    category_trends = {}

    # Get all unique categories from these months
    all_trans = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).all()

    top_categories = db.query(
        Category.name,
        func.sum(Transaction.amount).label('total')
    ).join(
        Transaction
    ).filter(
        Transaction.user_id == current_user.id
    ).group_by(
        Category.name
    ).order_by(
        desc('total')
    ).limit(5).all()

    # For each top category, get monthly spending
    for cat_name, _ in top_categories:
        category_trends[cat_name] = []

        for month_data in monthly_data:
            month_trans = db.query(Transaction).join(Category).filter(
                Transaction.user_id == current_user.id,
                Transaction.statement_month == month_data["month_num"],
                Transaction.statement_year == month_data["year"],
                Category.name == cat_name
            ).all()

            month_total = sum(t.amount for t in month_trans) if month_trans else Decimal("0.00")
            category_trends[cat_name].append(month_total)

    # Calculate start and end dates
    start_month_data = monthly_data[0]
    end_month_data = monthly_data[-1]

    start_date = f"{start_month_data['year']}-{start_month_data['month_num']:02d}-01"
    end_date = f"{end_month_data['year']}-{end_month_data['month_num']:02d}-01"

    return {
        "period": f"Last {months} months",
        "start_date": start_date,
        "end_date": end_date,
        "monthly_totals": monthly_data,
        "average_monthly": average_monthly,
        "highest_month": highest_month,
        "lowest_month": lowest_month,
        "category_trends": category_trends
    }


# ═══════════════════════════════════════════════════════════════════
# GET /analytics/annual - Full Year Analysis
# ═══════════════════════════════════════════════════════════════════

@router.get(
    "/annual",
    response_model=AnnualAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Annual spending analysis",
    description="Get complete spending analysis for an entire year"
)
async def get_annual_analysis(
    year: int = Query(..., ge=2020, le=2100, description="Year to analyze"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Full year spending analysis

    Use Case: "How much did I spend in 2025 total?"

    Returns:
    - Total spending for the year
    - Month-by-month breakdown
    - Category totals
    - Average monthly spending

    Example:
    GET /analytics/annual?year=2025
    """

    # Get all transactions for the year
    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.statement_year == year
    ).all()

    if not transactions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No transactions found for year {year}"
        )

    # Calculate total
    total_spending = sum(t.amount for t in transactions)

    # Group by month
    monthly_breakdown = defaultdict(lambda: {"total": Decimal("0.00"), "count": 0})

    for trans in transactions:
        month = trans.statement_month
        monthly_breakdown[month]["total"] += trans.amount
        monthly_breakdown[month]["count"] += 1

    # Convert to list
    monthly_list = []
    for month in range(1, 13):
        if month in monthly_breakdown:
            data = monthly_breakdown[month]
            monthly_list.append({
                "month": month_name[month][:3],
                "month_num": month,
                "year": year,
                "total": data["total"],
                "transaction_count": data["count"]
            })

    months_covered = len(monthly_list)
    average_monthly = total_spending / months_covered if months_covered > 0 else Decimal("0.00")

    # Category totals
    category_totals = defaultdict(Decimal)
    for trans in transactions:
        cat_name = trans.category.name if trans.category else "Uncategorized"
        category_totals[cat_name] += trans.amount

    return {
        "year": year,
        "total_spending": total_spending,
        "months_covered": months_covered,
        "average_monthly": average_monthly,
        "category_totals": dict(category_totals),
        "monthly_breakdown": monthly_list
    }


# ═══════════════════════════════════════════════════════════════════
# USAGE EXAMPLES
# ═══════════════════════════════════════════════════════════════════
"""
# Example 1: Get April 2025 spending across all cards
GET /analytics/monthly?month=4&year=2025
Authorization: Bearer <token>

# Example 2: Compare April vs March
GET /analytics/compare?current_month=4&current_year=2025&compare_month=3&compare_year=2025
Authorization: Bearer <token>

# Example 3: Get 6-month trend
GET /analytics/trend?months=6
Authorization: Bearer <token>

# Example 4: Get 2025 annual report
GET /analytics/annual?year=2025
Authorization: Bearer <token>
"""
