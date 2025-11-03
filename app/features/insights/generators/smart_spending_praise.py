"""
Smart Spending Praise Insight

Praises users for making smart financial choices like using public transport.
Positive reinforcement encourages continued good behavior.
"""

from typing import List, Optional, Dict, Tuple
from datetime import date, datetime
from decimal import Decimal
from collections import defaultdict

from app.features.transactions.models import Transaction
from app.features.insights.models import Insight, InsightTransaction
from app.core.database import get_db
from app.shared.merchant_categories import (
    categorize_merchant,
    MerchantCategory,
    SpendingType,
    get_spending_type,
    normalize_merchant_name
)


class SmartSpendingPraiseService:
    """
    Generate insights that praise smart spending decisions

    Currently focuses on:
    - Public transport usage (vs ride-sharing)
    """

    def __init__(self, db):
        self.db = db

    def generate_insight(
        self,
        user_id: str,
        transactions: List[Transaction],
        date_range: Optional[Tuple[date, date]] = None,
        statement_periods: Optional[List[Tuple[int, int]]] = None
    ) -> Optional[Dict]:
        """
        Generate smart spending praise insight

        Praises user for using public transport and shows savings vs ride-sharing

        Args:
            user_id: User UUID
            transactions: List of user transactions
            date_range: (start_date, end_date) for the analysis period

        Returns:
            Insight data dict or None if no praise-worthy behavior found
        """
        if not transactions or not date_range:
            return None

        start_date, end_date = date_range

        # Group transactions by category
        transport_spending = {
            MerchantCategory.PUBLIC_TRANSPORT: [],
            MerchantCategory.RIDE_SHARING: []
        }

        for txn in transactions:
            # Use pre-categorized data from PDF extraction if available
            if txn.category_auto:
                try:
                    category = MerchantCategory(txn.category_auto)
                except ValueError:
                    category = categorize_merchant(txn.merchant_name)
            else:
                category = categorize_merchant(txn.merchant_name)

            if category in transport_spending:
                transport_spending[category].append(txn)

        public_transport_txns = transport_spending[MerchantCategory.PUBLIC_TRANSPORT]
        ride_sharing_txns = transport_spending[MerchantCategory.RIDE_SHARING]

        # Only generate if they use public transport
        if not public_transport_txns:
            return None

        public_transport_amount = sum(float(txn.amount) for txn in public_transport_txns)
        public_transport_count = len(public_transport_txns)

        # Calculate potential savings
        # Average Grab ride in Singapore: ~$10-15
        # Average public transport trip: ~$1.50
        avg_public_transport = public_transport_amount / public_transport_count if public_transport_count > 0 else 1.5

        # Estimate how much they would have spent on ride-sharing
        estimated_ride_sharing_cost = public_transport_count * 12  # Assuming avg $12 per Grab ride
        actual_savings = estimated_ride_sharing_cost - public_transport_amount

        # Also calculate if they DO use ride-sharing
        ride_sharing_amount = sum(float(txn.amount) for txn in ride_sharing_txns) if ride_sharing_txns else 0
        ride_sharing_count = len(ride_sharing_txns)

        # Format date range for display
        months = self._format_date_range(start_date, end_date, statement_periods)

        # Generate appropriate message based on usage pattern
        if ride_sharing_count == 0:
            # Pure public transport user - maximum praise!
            title = "Excellent! You're saving money with public transport"
            description = (
                f"From {months}, you made {public_transport_count} trips using public transport, "
                f"spending just ${public_transport_amount:,.2f} (avg ${avg_public_transport:.2f} per trip).\n\n"
                f"💰 Smart choice! If you had used ride-sharing instead, you would have spent approximately "
                f"${estimated_ride_sharing_cost:,.2f}. You've saved around ${actual_savings:,.2f}!\n\n"
                f"Keep it up! Public transport is not only economical but also environmentally friendly. 🌱"
            )
            impact_score = 9  # High positive impact
            potential_savings = None  # No savings to suggest - they're already optimal!

        else:
            # Mixed user - only praise if genuinely doing well
            public_transport_ratio = public_transport_count / (public_transport_count + ride_sharing_count)

            # ONLY SHOW PRAISE if public transport usage is 60%+
            # Below 60%, let the "transport_savings" insight handle it (it's not praise-worthy yet)
            if public_transport_ratio >= 0.6:  # 60%+ public transport - genuinely good!
                title = f"Great job! You used public transport {int(public_transport_ratio * 100)}% of the time"
                description = (
                    f"From {months}, you wisely chose public transport for {public_transport_count} trips "
                    f"(${public_transport_amount:,.2f}), compared to just {ride_sharing_count} ride-sharing trips "
                    f"(${ride_sharing_amount:,.2f}).\n\n"
                    f"💰 You've already saved approximately ${actual_savings:,.2f} by choosing public transport!\n\n"
                    f"🌟 Keep up the smart spending! You're making excellent financial choices while being "
                    f"environmentally friendly."
                )
                impact_score = 8
                # No potential savings - they're already doing great!
                potential_savings = None

            else:
                # Less than 60% public transport - NOT praise-worthy yet
                # The transport_savings insight will handle suggestions
                return None

        # Build insight data
        insight_data = {
            "insight_type": "smart_spending_praise",
            "title": title,
            "description": description,
            "impact_score": impact_score,
            "potential_savings": float(potential_savings) if potential_savings else None,
            "transaction_ids": [str(txn.id) for txn in public_transport_txns]  # Link public transport transactions
        }

        return insight_data

    def save_insight(self, user_id: str, insight_data: Dict) -> Insight:
        """
        Save the smart spending praise insight to database

        Args:
            user_id: User UUID string
            insight_data: Insight data dictionary

        Returns:
            Created Insight model instance
        """
        # Create insight record
        insight = Insight(
            user_id=user_id,
            insight_type=insight_data["insight_type"],
            title=insight_data["title"],
            description=insight_data["description"],
            impact_score=insight_data["impact_score"],
            potential_savings=insight_data.get("potential_savings"),
            created_at=datetime.now()
        )

        self.db.add(insight)
        self.db.flush()  # Get the insight ID

        # Link transactions
        for txn_id in insight_data.get("transaction_ids", []):
            link = InsightTransaction(
                insight_id=insight.id,
                transaction_id=txn_id
            )
            self.db.add(link)

        self.db.commit()
        self.db.refresh(insight)

        return insight

    def _format_date_range(
        self,
        start_date: date,
        end_date: date,
        statement_periods: Optional[List[Tuple[int, int]]] = None
    ) -> str:
        """
        Format date range intelligently based on uploaded statement periods

        Examples:
        - Consecutive months: "June to September 2025"
        - 2 non-consecutive months: "July and September 2025"
        - 3+ non-consecutive months: "July, August, and October 2025"
        """
        from calendar import month_name

        if not statement_periods:
            # Fallback to old behavior if no statement periods provided
            if start_date.year == end_date.year:
                if start_date.month == end_date.month:
                    return start_date.strftime("%B %Y")
                return f"{start_date.strftime('%B')} to {end_date.strftime('%B %Y')}"
            return f"{start_date.strftime('%B %Y')} to {end_date.strftime('%B %Y')}"

        # Sort statement periods by year, then month
        sorted_periods = sorted(statement_periods, key=lambda x: (x[1], x[0]))

        if len(sorted_periods) == 1:
            month, year = sorted_periods[0]
            return f"{month_name[month]} {year}"

        # Check if all periods are in the same year
        years = set(year for _, year in sorted_periods)
        same_year = len(years) == 1
        year = sorted_periods[0][1] if same_year else None

        # Check if months are consecutive
        months_only = [month for month, _ in sorted_periods]
        is_consecutive = all(
            months_only[i] + 1 == months_only[i + 1]
            for i in range(len(months_only) - 1)
        ) if same_year else False

        if is_consecutive and same_year:
            # Use "to" for consecutive months
            first_month = month_name[sorted_periods[0][0]]
            last_month = month_name[sorted_periods[-1][0]]
            return f"{first_month} to {last_month} {year}"

        # Non-consecutive months
        if len(sorted_periods) == 2:
            # Use "and" for exactly 2 months
            month1, year1 = sorted_periods[0]
            month2, year2 = sorted_periods[1]
            if same_year:
                return f"{month_name[month1]} and {month_name[month2]} {year}"
            return f"{month_name[month1]} {year1} and {month_name[month2]} {year2}"

        # 3+ non-consecutive months: use comma-separated list
        if same_year:
            month_names = [month_name[month] for month, _ in sorted_periods[:-1]]
            last_month = month_name[sorted_periods[-1][0]]
            return f"{', '.join(month_names)}, and {last_month} {year}"
        else:
            # Different years - show year for each
            parts = [f"{month_name[month]} {year}" for month, year in sorted_periods[:-1]]
            last = f"{month_name[sorted_periods[-1][0]]} {sorted_periods[-1][1]}"
            return f"{', '.join(parts)}, and {last}"
