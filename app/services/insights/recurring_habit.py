"""
Recurring Habit Insight Service

Analyzes frequent merchant visits for DISCRETIONARY spending only.
(Coffee shops, dining, entertainment, etc.)

Algorithm:
1. Group transactions by normalized merchant name
2. Filter OUT essential categories (groceries, utilities, public transport)
3. Count visits per merchant
4. Calculate total spending per merchant
5. If any merchant has 10+ visits in analysis period → Generate insight
6. Provide context-aware advice based on merchant category

Performance: O(n) where n = number of transactions
"""

from datetime import datetime, date
from typing import List, Optional, Dict, Any, Tuple
from decimal import Decimal
from sqlalchemy.orm import Session
from collections import defaultdict
import re

from app.models.transaction import Transaction
from app.models.insight import Insight, InsightTransaction
from app.config.insights_config import WeekendSpendingConfig
from app.config.merchant_categories import (
    normalize_merchant_name,
    categorize_merchant,
    should_generate_recurring_insight,
    MerchantCategory,
    SpendingType,
    get_spending_type
)


class RecurringHabitService:
    """
    Detects frequent merchant visits for DISCRETIONARY spending

    ONLY generates insights for:
    - Coffee shops (high savings potential)
    - Restaurants & fast food (dining out)
    - Food delivery services
    - Entertainment (movies, games)
    - Shopping (retail)
    - Lifestyle (gym, beauty)

    SKIPS essential spending:
    - Groceries (people need food!)
    - Public transport (this is SMART spending, praised separately)
    - Utilities (necessary)
    - Healthcare (necessary)
    """

    # Thresholds
    MIN_VISITS = 10  # Minimum visits to consider it a "habit"
    MIN_TRANSACTIONS_OVERALL = 20  # Need enough total data

    def __init__(self, db: Session):
        self.db = db

    def generate_insights(
        self,
        user_id: str,
        transactions: List[Transaction],
        date_range: Optional[Tuple[date, date]] = None,
        statement_periods: Optional[List[Tuple[int, int]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate recurring habit insights from transactions
        Returns MULTIPLE insights (one per frequent merchant)

        Args:
            user_id: UUID of the user
            transactions: List of user transactions
            date_range: Optional tuple of (earliest_date, latest_date)

        Returns:
            List of insight dicts (one per frequent merchant)
        """

        print(f"\n{'='*60}")
        print(f"[RECURRING HABIT] Starting analysis")
        print(f"[RECURRING HABIT] Total transactions: {len(transactions)}")
        print(f"[RECURRING HABIT] Minimum visits required: {self.MIN_VISITS}")
        print(f"{'='*60}\n")

        # Need enough data
        if len(transactions) < self.MIN_TRANSACTIONS_OVERALL:
            print(f"[RECURRING HABIT] NOT ENOUGH TRANSACTIONS - Need {self.MIN_TRANSACTIONS_OVERALL}, got {len(transactions)}")
            return []

        # Group transactions by normalized merchant name
        merchant_groups = defaultdict(list)

        for txn in transactions:
            normalized_name = normalize_merchant_name(txn.merchant_name)
            merchant_groups[normalized_name].append(txn)

        print(f"[RECURRING HABIT] Found {len(merchant_groups)} unique merchants (before filtering)")

        # Find merchants with frequent visits (FILTER OUT ESSENTIAL CATEGORIES)
        frequent_merchants = []

        for merchant_name, merchant_txns in merchant_groups.items():
            visit_count = len(merchant_txns)

            if visit_count >= self.MIN_VISITS:
                # Get category from first transaction (all should have same merchant category)
                # Priority: Use pre-categorized data from PDF extraction (category_auto)
                first_txn = merchant_txns[0]
                if first_txn.category_auto:
                    try:
                        category = MerchantCategory(first_txn.category_auto)
                        print(f"[RECURRING HABIT] Using pre-categorized data: {merchant_name} -> {category.value}")
                    except ValueError:
                        # Fallback if invalid category value
                        category = categorize_merchant(merchant_name)
                        print(f"[RECURRING HABIT] Invalid category_auto, using pattern match: {merchant_name} -> {category.value}")
                else:
                    # Fallback to pattern matching if category_auto not set
                    category = categorize_merchant(merchant_name)
                    print(f"[RECURRING HABIT] No category_auto, using pattern match: {merchant_name} -> {category.value}")

                # Skip if it's essential spending (groceries, public transport, etc.)
                if not should_generate_recurring_insight(category):
                    print(f"[RECURRING HABIT] Skipping {merchant_name} ({category.value}) - essential/smart spending")
                    continue

                # ALSO skip ride-sharing - the transport_savings insight handles this better
                # It compares ride-sharing vs public transport in a more comprehensive way
                if category == MerchantCategory.RIDE_SHARING:
                    print(f"[RECURRING HABIT] Skipping {merchant_name} (ride_sharing) - handled by transport_savings insight")
                    continue

                total_spent = sum(txn.amount for txn in merchant_txns)
                avg_per_visit = total_spent / visit_count

                frequent_merchants.append({
                    'name': merchant_name,
                    'category': category,
                    'original_names': list(set(txn.merchant_name for txn in merchant_txns)),
                    'visits': visit_count,
                    'total': total_spent,
                    'average': avg_per_visit,
                    'transactions': merchant_txns
                })

        if not frequent_merchants:
            print(f"[RECURRING HABIT] No merchants with {self.MIN_VISITS}+ visits found")
            print(f"[RECURRING HABIT] Generating POSITIVE insight for good spending habits!")

            # Generate positive insight - praise for NOT having recurring wasteful habits
            positive_insight = self._generate_positive_insight(
                date_range=date_range,
                statement_periods=statement_periods
            )
            return [positive_insight]

        # Sort by visit count (most frequent first)
        frequent_merchants.sort(key=lambda x: x['visits'], reverse=True)

        print(f"[RECURRING HABIT] Found {len(frequent_merchants)} frequent merchants")

        # Generate insight for EACH frequent merchant (up to top 5)
        insights = []
        max_insights = min(5, len(frequent_merchants))  # Limit to top 5 to avoid overwhelming

        for merchant in frequent_merchants[:max_insights]:
            print(f"[RECURRING HABIT] Generating insight for: {merchant['name']}")
            print(f"[RECURRING HABIT]   Visits: {merchant['visits']}")
            print(f"[RECURRING HABIT]   Total: ${merchant['total']}")
            print(f"[RECURRING HABIT]   Average: ${merchant['average']:.2f}")

            # Calculate impact score (higher for more visits and higher total)
            impact_score = self._calculate_impact_score(
                merchant['visits'],
                float(merchant['total'])
            )

            # Calculate potential savings (if reduced visits by 50%)
            monthly_cost = self._estimate_monthly_cost(
                float(merchant['total']),
                date_range
            )
            potential_savings = monthly_cost * Decimal('0.5')  # 50% reduction

            # Generate insight with category-aware advice
            insight = {
                "insight_type": "recurring_habit",
                "title": f"You visited {merchant['name']} {merchant['visits']} times",
                "description": self._generate_description(
                    merchant_name=merchant['name'],
                    category=merchant['category'],
                    visits=merchant['visits'],
                    total=merchant['total'],
                    average=merchant['average'],
                    monthly_cost=monthly_cost,
                    date_range=date_range,
                    statement_periods=statement_periods
                ),
                "impact_score": impact_score,
                "potential_savings": float(potential_savings),
                "transaction_ids": [str(txn.id) for txn in merchant['transactions']],
                "metadata": {
                    "merchant_name": merchant['name'],
                    "category": merchant['category'].value,
                    "visit_count": merchant['visits'],
                    "total_spent": float(merchant['total']),
                    "average_per_visit": float(merchant['average'])
                }
            }

            insights.append(insight)

        print(f"[RECURRING HABIT] Generated {len(insights)} insights total")
        return insights

    def _estimate_monthly_cost(
        self,
        total_spent: float,
        date_range: Optional[Tuple[date, date]]
    ) -> Decimal:
        """
        Estimate monthly cost based on actual date range
        """
        if not date_range:
            # Assume 3 months if no range provided
            return Decimal(str(total_spent)) / Decimal('3')

        start_date, end_date = date_range
        days_in_period = (end_date - start_date).days + 1

        if days_in_period <= 0:
            days_in_period = 30

        # Calculate daily average and multiply by 30
        daily_avg = Decimal(str(total_spent)) / Decimal(str(days_in_period))
        monthly_cost = daily_avg * Decimal('30')

        return monthly_cost

    def _generate_description(
        self,
        merchant_name: str,
        category: MerchantCategory,
        visits: int,
        total: Decimal,
        average: Decimal,
        monthly_cost: Decimal,
        date_range: Optional[Tuple[date, date]] = None,
        statement_periods: Optional[List[Tuple[int, int]]] = None
    ) -> str:
        """Generate human-friendly, category-aware description"""

        # Format date range based on statement periods
        if date_range:
            start_date, end_date = date_range
            months_str = self._format_date_range(start_date, end_date, statement_periods)
            time_period = f"From {months_str}"
        else:
            time_period = "Over the past few months"

        # Calculate yearly projection
        yearly_cost = monthly_cost * Decimal('12')

        # Generate category-aware suggestion
        suggestion = self._generate_category_suggestion(category, merchant_name, monthly_cost)

        return (
            f"{time_period}, you visited {merchant_name.title()} {visits} times, "
            f"spending ${total:,.2f} (avg ${average:.2f} per visit). "
            f"That's approximately ${monthly_cost:.2f}/month or ${yearly_cost:.2f}/year.\n\n"
            f"{suggestion}"
        )

    def _generate_category_suggestion(
        self,
        category: MerchantCategory,
        merchant_name: str,
        monthly_cost: Decimal
    ) -> str:
        """Generate contextual suggestion based on merchant category"""

        # Coffee shops - high savings potential!
        if category == MerchantCategory.COFFEE_SHOP:
            return (
                "☕ Coffee adds up fast! Consider:\n"
                "• Brew at home (costs ~$0.50 vs $5-7 per cup)\n"
                "• Reduce to 2-3 times per week as a treat\n"
                "• Use a refillable cup for discounts\n\n"
                "Cutting visits by 50% could save you hundreds per year!"
            )

        # Fast food
        elif category == MerchantCategory.FAST_FOOD:
            return (
                "🍔 Fast food convenience comes at a cost. Try:\n"
                "• Meal prep on Sundays (cheaper, healthier)\n"
                "• Pack lunch 2-3 days per week\n"
                "• Cook simple meals at home (fried rice, pasta, sandwiches)\n\n"
                "Even small changes can save $100+/month while improving your health!"
            )

        # Dining out
        elif category == MerchantCategory.DINING_OUT:
            return (
                "🍽️ Dining out is fun but expensive! Balance it:\n"
                "• Cook at home during weekdays\n"
                "• Save dining out for special occasions or weekends\n"
                "• Try cooking your favorite restaurant dishes at home\n\n"
                "Reducing by 30-40% could free up budget for other goals while still enjoying meals out!"
            )

        # Food delivery
        elif category == MerchantCategory.FOOD_DELIVERY:
            return (
                "📦 Food delivery fees and surcharges add up! Consider:\n"
                "• Delivery fees, service charges, and tips cost 20-30% extra\n"
                "• Cook simple meals or pick up takeout yourself\n"
                "• Batch order once instead of multiple times per week\n\n"
                "Switching to self-pickup or cooking could save ${:.0f}/month!".format(float(monthly_cost) * 0.5)
            )

        # Entertainment
        elif category == MerchantCategory.ENTERTAINMENT:
            return (
                "🎮 Entertainment is important for balance! Optimize it:\n"
                "• Look for free/cheaper alternatives (YouTube, free games)\n"
                "• Share subscriptions with family/friends\n"
                "• Take advantage of promos and discounts\n\n"
                "Budget wisely so you can enjoy entertainment without overspending!"
            )

        # Shopping
        elif category == MerchantCategory.SHOPPING:
            return (
                "🛍️ Frequent shopping can strain your budget. Try:\n"
                "• Wait 24-48 hours before buying (reduces impulse purchases)\n"
                "• Make a shopping list and stick to it\n"
                "• Ask yourself: 'Do I need this or want this?'\n\n"
                "Being mindful can save hundreds while you still get what you truly need!"
            )

        # Ride-sharing (shouldn't appear often since transport_savings handles this)
        elif category == MerchantCategory.RIDE_SHARING:
            return (
                "🚗 Ride-sharing is convenient but costly. Consider:\n"
                "• Use public transport for routine trips (~$1.50 vs $10-15)\n"
                "• Save ride-sharing for late nights, bad weather, or heavy items\n"
                "• Carpool with friends to split costs\n\n"
                "Switching most trips to MRT/bus could save ${:.0f}/month!".format(float(monthly_cost) * 0.8)
            )

        # Lifestyle (gym, beauty, etc.)
        elif category == MerchantCategory.LIFESTYLE:
            return (
                "💆 Lifestyle expenses should align with your usage:\n"
                "• Gym: Are you going regularly? Consider home workouts if not\n"
                "• Beauty: Can you space out appointments or do some at home?\n"
                "• Wellness: Balance luxury with budget-friendly self-care\n\n"
                "Evaluate if you're getting value for money!"
            )

        # Default for unknown categories
        else:
            return (
                "💡 This is a recurring expense. Consider:\n"
                "• Is this adding value to your life?\n"
                "• Can you reduce frequency by 25-50%?\n"
                "• Are there cheaper alternatives?\n\n"
                "Even small reductions in recurring expenses add up over time!"
            )

    def _calculate_impact_score(self, visits: int, total_spent: float) -> int:
        """
        Calculate impact score (1-10)

        Based on:
        - Number of visits (more visits = higher score)
        - Total amount spent
        """
        score = 5  # Base score

        # Add points for visit frequency
        if visits >= 30:
            score += 3
        elif visits >= 20:
            score += 2
        elif visits >= 15:
            score += 1

        # Add points for total spending
        if total_spent >= 200:
            score += 2
        elif total_spent >= 100:
            score += 1

        return min(10, score)

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

    def _generate_positive_insight(
        self,
        date_range: Optional[Tuple[date, date]] = None,
        statement_periods: Optional[List[Tuple[int, int]]] = None
    ) -> Dict[str, Any]:
        """
        Generate a positive insight when NO recurring wasteful habits are detected

        This celebrates users who show good financial discipline by not developing
        expensive recurring discretionary spending patterns.

        Args:
            date_range: Optional date range for context
            statement_periods: List of (month, year) tuples

        Returns:
            Insight dict with positive reinforcement message
        """
        # Format time period
        if date_range:
            start_date, end_date = date_range
            months_str = self._format_date_range(start_date, end_date, statement_periods)
            time_period = f"From {months_str}"
        else:
            time_period = "Over the analyzed period"

        title = "Great self-control! No recurring spending habits detected"

        description = (
            f"{time_period}, you haven't developed any recurring discretionary spending patterns "
            f"like daily coffee runs or frequent fast food visits.\n\n"
            f"This shows excellent financial discipline! Many people develop expensive habits without realizing:\n"
            f"• Daily $5 coffee = $1,825/year\n"
            f"• Weekly $15 fast food = $780/year\n"
            f"• Frequent food delivery = Easily $2,000+/year\n\n"
            f"By avoiding these patterns, you're saving hundreds or even thousands annually. "
            f"This makes a huge difference in reaching your financial goals!\n\n"
            f"Keep up the smart spending! Your future self will thank you."
        )

        return {
            "insight_type": "recurring_habit",
            "title": title,
            "description": description,
            "impact_score": 3,  # Lower score - informational/positive, not urgent
            "potential_savings": 0.0,  # No specific savings since it's a positive insight
            "transaction_ids": [],  # No specific transactions to link
            "metadata": {
                "is_positive_insight": True,
                "pattern_type": "no_recurring_habits"
            }
        }

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
