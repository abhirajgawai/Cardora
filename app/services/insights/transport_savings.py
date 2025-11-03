"""
Transport Savings Insight

Analyzes ride-sharing usage and shows potential savings by switching to public transport.
Helps users make smarter transport choices.
"""

from typing import List, Optional, Dict, Tuple
from datetime import date, datetime
from decimal import Decimal
from collections import defaultdict

from app.models.transaction import Transaction
from app.models.insight import Insight, InsightTransaction
from app.core.database import get_db
from app.config.merchant_categories import (
    categorize_merchant,
    MerchantCategory,
    normalize_merchant_name
)


class TransportSavingsService:
    """
    Generate insights about transport spending

    Focuses on users who use ride-sharing (Grab, Gojek) and shows them
    potential savings by switching to public transport.
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
        Generate transport savings insight

        Args:
            user_id: User UUID
            transactions: List of user transactions
            date_range: (start_date, end_date) for the analysis period

        Returns:
            Insight data dict or None if no savings opportunity found
        """
        if not transactions or not date_range:
            return None

        start_date, end_date = date_range

        # Group transport transactions
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

        ride_sharing_txns = transport_spending[MerchantCategory.RIDE_SHARING]
        public_transport_txns = transport_spending[MerchantCategory.PUBLIC_TRANSPORT]

        # Only generate if they use ride-sharing significantly
        if not ride_sharing_txns or len(ride_sharing_txns) < 5:
            return None

        ride_sharing_amount = sum(float(txn.amount) for txn in ride_sharing_txns)
        ride_sharing_count = len(ride_sharing_txns)
        avg_ride_cost = ride_sharing_amount / ride_sharing_count

        # Calculate public transport usage
        public_transport_amount = sum(float(txn.amount) for txn in public_transport_txns) if public_transport_txns else 0
        public_transport_count = len(public_transport_txns)

        # Average Singapore public transport trip cost: ~$1.50
        avg_public_transport_cost = 1.50

        # Calculate potential savings
        # Assume they could switch 50-70% of ride-sharing trips to public transport
        switchable_percentage = 0.6  # Conservative 60%
        switchable_trips = int(ride_sharing_count * switchable_percentage)

        # Current cost of those switchable trips
        current_cost_switchable = switchable_trips * avg_ride_cost

        # What those trips would cost on public transport
        public_transport_cost_switchable = switchable_trips * avg_public_transport_cost

        # Potential monthly and annual savings
        potential_savings = current_cost_switchable - public_transport_cost_switchable

        # Only generate if savings is significant (>$50 in the period)
        if potential_savings < 50:
            return None

        # Calculate monthly/annual projections
        months_in_period = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month) + 1
        monthly_savings = potential_savings / months_in_period if months_in_period > 0 else potential_savings
        annual_savings = monthly_savings * 12

        # Format date range using uploaded statement periods
        months = self._format_date_range(start_date, end_date, statement_periods)

        # Determine transport usage ratio
        total_transport_trips = ride_sharing_count + public_transport_count
        ride_sharing_ratio = ride_sharing_count / total_transport_trips if total_transport_trips > 0 else 1

        # Generate insight based on usage pattern
        if public_transport_count == 0:
            # Pure ride-sharing user - biggest opportunity!
            title = f"You could save ${monthly_savings:.0f}/month by using public transport"
            description = (
                f"From {months}, you spent ${ride_sharing_amount:,.2f} on {ride_sharing_count} ride-sharing trips "
                f"(avg ${avg_ride_cost:.2f} per trip).\n\n"
                f"💰 Big savings opportunity! If you switched just {int(switchable_percentage * 100)}% of these trips "
                f"to public transport (MRT/bus at ~${avg_public_transport_cost:.2f} per trip), you could save:\n"
                f"• ${monthly_savings:.2f} per month\n"
                f"• ${annual_savings:.2f} per year\n\n"
                f"💡 Try this: Use ride-sharing for late nights, urgent trips, or heavy groceries. "
                f"Use public transport for routine trips like commuting to work, meeting friends in town, or weekend outings.\n\n"
                f"Singapore's MRT system is efficient, air-conditioned, and much cheaper!"
            )
            impact_score = 10  # Highest - big savings opportunity

        else:
            # Mixed user
            if ride_sharing_ratio >= 0.7:  # 70%+ ride-sharing
                title = f"Switch more trips to public transport - save ${monthly_savings:.0f}/month"
                description = (
                    f"From {months}, you used ride-sharing for {ride_sharing_count} trips (${ride_sharing_amount:,.2f}) "
                    f"and public transport for {public_transport_count} trips (${public_transport_amount:,.2f}).\n\n"
                    f"💰 You're already using public transport sometimes! If you could increase that by switching "
                    f"more ride-sharing trips to MRT/bus, you could save:\n"
                    f"• ${monthly_savings:.2f} per month\n"
                    f"• ${annual_savings:.2f} per year\n\n"
                    f"Each ride-sharing trip costs ${avg_ride_cost:.2f} vs ${avg_public_transport_cost:.2f} for public transport. "
                    f"That's a ${avg_ride_cost - avg_public_transport_cost:.2f} saving per trip! 💵"
                )
                impact_score = 9

            elif ride_sharing_ratio >= 0.5:  # 50-70% ride-sharing
                title = f"Balance ride-sharing with public transport - save ${monthly_savings:.0f}/month"
                description = (
                    f"From {months}, you split transport fairly evenly: {ride_sharing_count} ride-sharing trips "
                    f"(${ride_sharing_amount:,.2f}) and {public_transport_count} public transport trips (${public_transport_amount:,.2f}).\n\n"
                    f"💰 Great balance! If you could shift a bit more towards public transport for routine trips, "
                    f"you could save approximately:\n"
                    f"• ${monthly_savings:.2f} per month\n"
                    f"• ${annual_savings:.2f} per year\n\n"
                    f"🎯 Target: Use ride-sharing for convenience (late nights, heavy items, bad weather). "
                    f"Use public transport as default for routine trips."
                )
                impact_score = 7

            else:
                # They already use mostly public transport - no need for this insight
                return None

        insight_data = {
            "insight_type": "transport_savings",
            "title": title,
            "description": description,
            "impact_score": impact_score,
            "potential_savings": float(monthly_savings),  # Return MONTHLY savings for consistency
            "transaction_ids": [str(txn.id) for txn in ride_sharing_txns]  # Link ride-sharing transactions
        }

        return insight_data

    def save_insight(self, user_id: str, insight_data: Dict) -> Insight:
        """
        Save the transport savings insight to database

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
