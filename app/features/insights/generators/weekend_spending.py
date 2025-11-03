"""
Weekend Spending Insight Service

Analyzes if user spends significantly more on weekends vs weekdays.

Algorithm:
1. Separate transactions into weekend (Sat/Sun) and weekday (Mon-Fri)
2. Calculate average daily spending for each
3. If weekend spending is >30% higher, generate insight
4. Return linked transactions that contributed to the insight

Performance: O(n) where n = number of transactions
"""

from datetime import datetime, date
from typing import List, Optional, Dict, Any, Tuple
from decimal import Decimal
from sqlalchemy.orm import Session

from app.features.transactions.models import Transaction
from app.features.insights.models import Insight, InsightTransaction
from app.shared.insights_config import WeekendSpendingConfig


class WeekendSpendingService:
    """
    Detects if user has higher spending on weekends

    Example Insight:
        "You spend 45% more on weekends - $180 vs $124 on weekdays"
    """

    def __init__(self, db: Session):
        self.db = db
        self.config = WeekendSpendingConfig

    def generate_insight(
        self,
        user_id: str,
        transactions: List[Transaction],
        date_range: Optional[Tuple[date, date]] = None,
        statement_periods: Optional[List[Tuple[int, int]]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Generate weekend spending insight from transactions

        Args:
            user_id: UUID of the user
            transactions: List of user transactions (typically last 3-6 months)
            date_range: Optional tuple of (earliest_date, latest_date) for the analysis period

        Returns:
            Dict with insight data or None if no significant pattern detected
            {
                "insight_type": "weekend_spending",
                "title": "You spend 45% more on weekends",
                "description": "From June 2025 to August 2025, your weekend spending...",
                "impact_score": 7,
                "potential_savings": 50.00,
                "transaction_ids": [list of transaction UUIDs]
            }
        """

        print(f"\n{'='*60}")
        print(f"[WEEKEND INSIGHTS] Starting analysis")
        print(f"[WEEKEND INSIGHTS] Total transactions received: {len(transactions)}")
        print(f"[WEEKEND INSIGHTS] Minimum required: {self.config.MIN_TRANSACTIONS}")
        print(f"{'='*60}\n")

        # Need enough data to make meaningful analysis
        if len(transactions) < self.config.MIN_TRANSACTIONS:
            print(f"[WEEKEND INSIGHTS] NOT ENOUGH TRANSACTIONS - Need {self.config.MIN_TRANSACTIONS}, got {len(transactions)}")
            return None

        # Separate weekend vs weekday transactions
        weekend_transactions = []
        weekday_transactions = []
        weekend_total = Decimal('0.00')
        weekday_total = Decimal('0.00')

        for txn in transactions:
            # Get day of week (0=Monday, 6=Sunday)
            day_of_week = txn.transaction_date.weekday()

            if day_of_week in [5, 6]:  # Saturday (5) or Sunday (6)
                weekend_transactions.append(txn)
                weekend_total += txn.amount
            else:  # Monday-Friday
                weekday_transactions.append(txn)
                weekday_total += txn.amount

        print(f"[WEEKEND INSIGHTS] Separated transactions:")
        print(f"[WEEKEND INSIGHTS]   Weekend transactions: {len(weekend_transactions)}")
        print(f"[WEEKEND INSIGHTS]   Weekday transactions: {len(weekday_transactions)}")

        # Need data from both weekend and weekdays
        if not weekend_transactions or not weekday_transactions:
            print(f"[WEEKEND INSIGHTS] INSUFFICIENT DATA - Need both weekend AND weekday transactions")
            print(f"[WEEKEND INSIGHTS]   Has weekend txns: {len(weekend_transactions) > 0}")
            print(f"[WEEKEND INSIGHTS]   Has weekday txns: {len(weekday_transactions) > 0}")
            return None

        # Calculate average daily spending
        # Note: This is a simplified calculation
        # More accurate would be: total_spending / actual_number_of_days
        weekend_avg = weekend_total / len(weekend_transactions)
        weekday_avg = weekday_total / len(weekday_transactions)

        print(f"[WEEKEND INSIGHTS] Calculated averages:")
        print(f"[WEEKEND INSIGHTS]   Weekend total: ${weekend_total}")
        print(f"[WEEKEND INSIGHTS]   Weekend count: {len(weekend_transactions)}")
        print(f"[WEEKEND INSIGHTS]   Weekend avg: ${weekend_avg}")
        print(f"[WEEKEND INSIGHTS]   Weekday total: ${weekday_total}")
        print(f"[WEEKEND INSIGHTS]   Weekday count: {len(weekday_transactions)}")
        print(f"[WEEKEND INSIGHTS]   Weekday avg: ${weekday_avg}")

        # Calculate percentage difference
        # Formula: ((weekend - weekday) / weekday) * 100
        if weekday_avg == 0:
            print(f"[WEEKEND INSIGHTS] ERROR: Weekday average is zero! Cannot calculate percentage.")
            return None

        print(f"[WEEKEND INSIGHTS] About to calculate percentage...")
        percentage_higher = ((weekend_avg - weekday_avg) / weekday_avg) * 100
        print(f"[WEEKEND INSIGHTS] Percentage calculated: {percentage_higher:.2f}%")

        # Debug logging
        print(f"[WEEKEND INSIGHTS DEBUG]")
        print(f"  Total transactions: {len(transactions)}")
        print(f"  Weekend transactions: {len(weekend_transactions)}")
        print(f"  Weekday transactions: {len(weekday_transactions)}")
        print(f"  Weekend avg per transaction: ${weekend_avg:.2f}")
        print(f"  Weekday avg per transaction: ${weekday_avg:.2f}")
        print(f"  Percentage higher: {percentage_higher:.2f}%")
        print(f"  Threshold: {self.config.THRESHOLD_PERCENTAGE}%")

        # Only generate insight if weekend spending is significantly higher
        if percentage_higher < self.config.THRESHOLD_PERCENTAGE:
            print(f"  Result: NO INSIGHT (below threshold)")
            return None

        print(f"  Result: INSIGHT GENERATED!")

        # Calculate potential monthly savings
        # If user reduced weekend spending to match weekday average
        excess_per_weekend_txn = weekend_avg - weekday_avg
        # Assume ~8 weekend days per month, estimate transactions
        weekend_txns_per_month = len(weekend_transactions) / (len(transactions) / 30) * 8
        potential_monthly_savings = excess_per_weekend_txn * Decimal(weekend_txns_per_month)

        # Generate insight
        return {
            "insight_type": "weekend_spending",
            "title": f"You spend {int(percentage_higher)}% more on weekends",
            "description": self._generate_description(
                weekend_total=weekend_total,
                weekday_total=weekday_total,
                weekend_count=len(weekend_transactions),
                weekday_count=len(weekday_transactions),
                percentage_higher=int(percentage_higher),
                date_range=date_range,
                statement_periods=statement_periods
            ),
            "impact_score": self._calculate_impact_score(percentage_higher, potential_monthly_savings),
            "potential_savings": float(potential_monthly_savings),
            "transaction_ids": [str(txn.id) for txn in weekend_transactions]
        }

    def _generate_description(
        self,
        weekend_total: Decimal,
        weekday_total: Decimal,
        weekend_count: int,
        weekday_count: int,
        percentage_higher: int,
        date_range: Optional[Tuple[date, date]] = None,
        statement_periods: Optional[List[Tuple[int, int]]] = None
    ) -> str:
        """Generate human-friendly description with specific date range"""

        weekend_avg = weekend_total / weekend_count
        weekday_avg = weekday_total / weekday_count

        # Format date range based on statement periods
        if date_range:
            start_date, end_date = date_range
            months_str = self._format_date_range(start_date, end_date, statement_periods)
            time_period = f"From {months_str}"
        else:
            time_period = "Over the past few months"

        return (
            f"{time_period}, you've spent ${weekend_total:,.2f} across {weekend_count} "
            f"weekend transactions (avg ${weekend_avg:.2f} per transaction), compared to "
            f"${weekday_total:,.2f} across {weekday_count} weekday transactions "
            f"(avg ${weekday_avg:.2f} per transaction). That's {percentage_higher}% more on weekends! "
            f"\n\nConsider being more mindful of weekend spending - perhaps plan activities in advance "
            f"or set a weekend budget to avoid impulse purchases."
        )

    def _calculate_impact_score(self, percentage_higher: Decimal, potential_savings: Decimal) -> int:
        """
        Calculate impact score (1-10)

        Based on:
        - How much higher the percentage is (30% = 5, 50% = 7, 100%+ = 10)
        - Potential monthly savings ($0-50 = +0, $50-100 = +1, $100+ = +2)
        """
        # Base score from percentage
        if percentage_higher >= 100:
            score = 10
        elif percentage_higher >= 70:
            score = 8
        elif percentage_higher >= 50:
            score = 7
        elif percentage_higher >= 40:
            score = 6
        else:  # 30-40%
            score = 5

        # Bonus for high savings potential
        if potential_savings >= 100:
            score = min(10, score + 2)
        elif potential_savings >= 50:
            score = min(10, score + 1)

        return score

    def save_insight(self, user_id: str, insight_data: Dict[str, Any]) -> Insight:
        """
        Save insight to database with linked transactions

        Args:
            user_id: UUID of the user
            insight_data: Dict returned by generate_insight()

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
            potential_savings=Decimal(str(insight_data["potential_savings"]))
        )

        self.db.add(insight)
        self.db.flush()  # Get insight.id without committing

        # Link transactions to insight
        for txn_id in insight_data["transaction_ids"]:
            insight_txn = InsightTransaction(
                insight_id=insight.id,
                transaction_id=txn_id
            )
            self.db.add(insight_txn)

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
