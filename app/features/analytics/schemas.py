"""
Analytics Schemas - Response Models for Analytics Endpoints

These schemas define the structure of analytics data returned to users.
They provide insights across multiple credit cards and time periods.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from decimal import Decimal
from datetime import datetime


# ═══════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════

class CardSpending(BaseModel):
    """Spending breakdown per card"""
    bank: str = Field(..., description="Bank name")
    card_name: str = Field(..., description="Card name/type")
    last_four: str = Field(..., description="Last 4 digits")
    spending: Decimal = Field(..., description="Total spending on this card")
    transaction_count: int = Field(..., description="Number of transactions")
    percentage: float = Field(..., description="Percentage of total spending")

    class Config:
        from_attributes = True


class MonthlyAnalysisResponse(BaseModel):
    """Combined analysis for a specific month across all cards"""
    month: int = Field(..., ge=1, le=12, description="Month (1-12)")
    year: int = Field(..., ge=2020, description="Year")
    total_spending: Decimal = Field(..., description="Total spending across all cards")
    total_transactions: int = Field(..., description="Total number of transactions")
    cards_included: List[CardSpending] = Field(..., description="Per-card breakdown")
    category_breakdown: Dict[str, Decimal] = Field(..., description="Spending by category")
    top_merchants: List[Dict[str, Any]] = Field(..., description="Top merchants by spending")

    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════

class MonthData(BaseModel):
    """Data for a single month"""
    month: int
    year: int
    total: Decimal
    transaction_count: int


class CategoryChange(BaseModel):
    """Change in spending for a category"""
    current: Decimal
    previous: Decimal
    change: Decimal
    percentage_change: float


class ComparisonResponse(BaseModel):
    """Comparison between two months"""
    current_month: MonthData
    previous_month: MonthData
    difference: Decimal = Field(..., description="Spending difference")
    percentage_change: float = Field(..., description="Percentage change")
    category_changes: Dict[str, CategoryChange] = Field(..., description="Per-category changes")

    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════

class MonthlyTotal(BaseModel):
    """Monthly total for trend analysis"""
    month: str = Field(..., description="Month name (e.g., 'Apr 2025')")
    month_num: int = Field(..., description="Month number (1-12)")
    year: int
    total: Decimal
    transaction_count: int


class TrendAnalysisResponse(BaseModel):
    """Multi-month trend analysis"""
    period: str = Field(..., description="Period description (e.g., 'Last 6 months')")
    start_date: str
    end_date: str
    monthly_totals: List[MonthlyTotal] = Field(..., description="Monthly spending breakdown")
    average_monthly: Decimal = Field(..., description="Average monthly spending")
    highest_month: MonthlyTotal
    lowest_month: MonthlyTotal
    category_trends: Dict[str, List[Decimal]] = Field(..., description="Category spending over time")

    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════

class AnnualAnalysisResponse(BaseModel):
    """Full year analysis"""
    year: int
    total_spending: Decimal = Field(..., description="Total spending for the year")
    months_covered: int = Field(..., description="Number of months with data")
    average_monthly: Decimal = Field(..., description="Average monthly spending")
    category_totals: Dict[str, Decimal] = Field(..., description="Total spending by category")
    monthly_breakdown: List[MonthlyTotal] = Field(..., description="Month-by-month breakdown")

    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════

class CardAnalysis(BaseModel):
    """Detailed analysis for a single card"""
    bank: str
    card_name: str
    last_four: str
    total_spending: Decimal
    transaction_count: int
    average_transaction: Decimal
    top_category: str
    top_category_amount: Decimal

    class Config:
        from_attributes = True


class CardsAnalysisResponse(BaseModel):
    """Per-card analysis for a specific period"""
    month: int
    year: int
    cards: List[CardAnalysis] = Field(..., description="Analysis for each card")

    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════

class MerchantSpending(BaseModel):
    """Merchant spending details"""
    name: str
    amount: Decimal
    transaction_count: int


class CardUsage(BaseModel):
    """Card usage for a category"""
    bank: str
    amount: Decimal
    transaction_count: int


class CategoryDetail(BaseModel):
    """Detailed category analysis"""
    name: str
    total: Decimal
    percentage: float
    transaction_count: int
    top_merchants: List[MerchantSpending]
    cards_used: List[CardUsage]

    class Config:
        from_attributes = True


class CategoryAnalysisResponse(BaseModel):
    """Deep dive into categories"""
    month: int
    year: int
    categories: List[CategoryDetail] = Field(..., description="Detailed category breakdown")

    class Config:
        from_attributes = True
