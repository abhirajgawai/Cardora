"""
Subscription Detection Insight

Identifies recurring monthly subscriptions (Netflix, Spotify, gym, etc.)
Helps users track and evaluate their subscriptions.
"""

from typing import List, Optional, Dict, Tuple
from datetime import date, datetime
from decimal import Decimal
from collections import defaultdict
import re

from app.features.transactions.models import Transaction
from app.features.insights.models import Insight, InsightTransaction
from app.core.database import get_db
from app.shared.merchant_categories import normalize_merchant_name


class SubscriptionDetectionService:
    """
    Detect recurring monthly subscriptions

    A subscription is identified as:
    - Same merchant charged multiple times
    - Similar amount each time (within 10% tolerance)
    - Roughly monthly frequency (25-35 days apart)
    - At least 2 occurrences in the analysis period
    - NOT in excluded categories (Dining, Groceries, etc.)
    """

    # Categories to exclude from subscription detection
    # These represent one-time purchases or variable spending that shouldn't be subscriptions
    EXCLUDED_CATEGORIES = {
        # Food & Dining (variable spending)
        'Dining',
        'Dining & Restaurants',
        'Restaurants',
        'Food & Dining',
        'Groceries',
        'Groceries & Food',

        # Shopping (one-time purchases)
        'Shopping',
        'General Shopping',
        'Retail',
        'Online Shopping',
        'Clothing & Accessories',
        'Electronics',

        # Travel (trip-based, not subscriptions)
        'Flights & Travel Bookings',
        'Hotels & Accommodation',

        # Home & Lifestyle (variable purchases)
        'Home & Garden',
        'Beauty & Personal Care',

        # Transport & Fuel (variable usage)
        'Gas & Fuel',
        'Transportation',
        'Transport',

        # Healthcare (variable, not subscriptions)
        'Medical',
        'Healthcare',

        # Other variable categories
        'Entertainment',  # Movies, events are one-time
        'Pets',  # Pet supplies are variable
        'Education & Learning'  # Courses/books can be one-time
    }

    def __init__(self, db):
        self.db = db

    def generate_insights(
        self,
        user_id: str,
        transactions: List[Transaction],
        date_range: Optional[Tuple[date, date]] = None,
        statement_periods: Optional[List[Tuple[int, int]]] = None
    ) -> List[Dict]:
        """
        Detect all subscriptions in transaction history

        Args:
            user_id: User UUID
            transactions: List of user transactions
            date_range: (start_date, end_date) for the analysis period

        Returns:
            List of insight data dicts (one per detected subscription)
        """
        if not transactions or not date_range:
            return []

        start_date, end_date = date_range

        # Group transactions by normalized merchant
        # Filter out excluded categories (Dining, Groceries, etc.)
        merchant_groups = defaultdict(list)
        for txn in transactions:
            # Skip transactions in excluded categories
            if txn.category and txn.category.name in self.EXCLUDED_CATEGORIES:
                continue

            normalized = normalize_merchant_name(txn.merchant_name)
            merchant_groups[normalized].append(txn)

        print(f"[SUBSCRIPTION DETECTION] Filtered transactions: {sum(len(txns) for txns in merchant_groups.values())} eligible (excluded Dining, Groceries, etc.)")

        detected_subscriptions = []

        # Analyze each merchant for subscription patterns
        for merchant, txns in merchant_groups.items():
            # Need at least 2 transactions
            if len(txns) < 2:
                continue

            # Sort by date
            sorted_txns = sorted(txns, key=lambda t: t.transaction_date)

            # Check if amounts are similar (within 10% tolerance)
            amounts = [float(txn.amount) for txn in sorted_txns]
            avg_amount = sum(amounts) / len(amounts)

            # Check if all amounts are within 10% of average
            similar_amounts = all(
                abs(amount - avg_amount) / avg_amount <= 0.1
                for amount in amounts
            )

            if not similar_amounts:
                continue

            # Check if transactions are roughly monthly (25-35 days apart on average)
            intervals = []
            for i in range(1, len(sorted_txns)):
                days_apart = (sorted_txns[i].transaction_date - sorted_txns[i-1].transaction_date).days
                intervals.append(days_apart)

            if not intervals:
                continue

            avg_interval = sum(intervals) / len(intervals)

            # Is it roughly monthly? (20-40 days)
            is_monthly = 20 <= avg_interval <= 40

            if not is_monthly:
                continue

            # We found a subscription!
            subscription = self._create_subscription_insight(
                merchant=merchant,
                transactions=sorted_txns,
                avg_amount=avg_amount,
                start_date=start_date,
                end_date=end_date,
                statement_periods=statement_periods
            )

            if subscription:
                detected_subscriptions.append(subscription)

        # Sort by monthly cost (highest first)
        detected_subscriptions.sort(key=lambda x: x.get("monthly_cost", 0), reverse=True)

        return detected_subscriptions

    def _create_subscription_insight(
        self,
        merchant: str,
        transactions: List[Transaction],
        avg_amount: float,
        start_date: date,
        end_date: date,
        statement_periods: Optional[List[Tuple[int, int]]] = None
    ) -> Optional[Dict]:
        """Create insight data for a detected subscription"""

        count = len(transactions)
        total_spent = sum(float(txn.amount) for txn in transactions)
        monthly_cost = avg_amount  # Average monthly cost

        # Calculate annual cost
        annual_cost = monthly_cost * 12

        # Format date range
        months = self._format_date_range(start_date, end_date, statement_periods)

        # Format merchant name for display
        display_merchant = merchant.title()

        # Determine category/type for better advice
        subscription_type = self._categorize_subscription(merchant)

        # Build insight based on subscription type
        if subscription_type == "streaming":
            title = f"Subscription: {display_merchant} (${monthly_cost:.2f}/month)"
            description = (
                f"From {months}, you've been charged ${monthly_cost:.2f} per month by {display_merchant} "
                f"({count} payments totaling ${total_spent:.2f}).\n\n"
                f"💡 That's ${annual_cost:.2f} per year. Are you using this subscription enough to justify the cost? "
                f"Consider sharing with family/friends to split the cost, or review if you're still actively using it."
            )
            impact_score = 6

        elif subscription_type == "fitness":
            title = f"Subscription: {display_merchant} (${monthly_cost:.2f}/month)"
            description = (
                f"From {months}, you've been paying ${monthly_cost:.2f} per month for {display_merchant} "
                f"({count} payments totaling ${total_spent:.2f}).\n\n"
                f"💪 That's ${annual_cost:.2f} per year. Are you going regularly? If not, consider canceling "
                f"and using free alternatives (outdoor running, home workouts, YouTube fitness channels)."
            )
            impact_score = 7

        elif subscription_type == "software":
            title = f"Subscription: {display_merchant} (${monthly_cost:.2f}/month)"
            description = (
                f"From {months}, you've been charged ${monthly_cost:.2f} per month by {display_merchant} "
                f"({count} payments totaling ${total_spent:.2f}).\n\n"
                f"💻 That's ${annual_cost:.2f} per year. Review if you're using all features. "
                f"Sometimes annual billing is cheaper than monthly, or there might be free alternatives."
            )
            impact_score = 6

        else:  # General subscription
            title = f"Subscription: {display_merchant} (${monthly_cost:.2f}/month)"
            description = (
                f"From {months}, you've been paying ${monthly_cost:.2f} per month to {display_merchant} "
                f"({count} payments totaling ${total_spent:.2f}).\n\n"
                f"📊 That's ${annual_cost:.2f} per year. Review this subscription:\n"
                f"• Are you still using it regularly?\n"
                f"• Could you downgrade to a cheaper plan?\n"
                f"• Is there a free alternative?\n\n"
                f"Even small subscriptions add up over time!"
            )
            impact_score = 7

        # Potential savings: suggest they could save 50% by evaluating/canceling if not needed
        potential_savings = monthly_cost * 6  # 6 months of savings if canceled

        insight_data = {
            "insight_type": "subscription_detection",
            "title": title,
            "description": description,
            "impact_score": impact_score,
            "potential_savings": potential_savings,
            "monthly_cost": monthly_cost,  # Used for sorting
            "transaction_ids": [str(txn.id) for txn in transactions]
        }

        return insight_data

    def _categorize_subscription(self, merchant: str) -> str:
        """Categorize subscription for better advice"""
        merchant_lower = merchant.lower()

        streaming_keywords = ["netflix", "spotify", "disney", "hbo", "youtube", "prime", "apple music"]
        fitness_keywords = ["gym", "fitness", "yoga", "anytime", "activesg"]
        software_keywords = ["adobe", "microsoft", "google", "dropbox", "storage", "cloud"]

        for keyword in streaming_keywords:
            if keyword in merchant_lower:
                return "streaming"

        for keyword in fitness_keywords:
            if keyword in merchant_lower:
                return "fitness"

        for keyword in software_keywords:
            if keyword in merchant_lower:
                return "software"

        return "general"

    def save_insight(self, user_id: str, insight_data: Dict) -> Insight:
        """
        Save the subscription detection insight to database

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
