"""
Statistics Engine - Transaction Data Aggregation

This service pre-processes transactions into an aggregated summary
to avoid sending 1000s of raw transactions to Gemini API.

Cost Optimization:
- Raw transactions: ~50,000 tokens = $12.50 per insight
- Aggregated summary: ~500 tokens = $0.175 per insight
- Savings: 100x cheaper! (from $12.50 to $0.175)

Algorithm:
1. Calculate overview statistics (total, count, date range)
2. Aggregate by category (top 10 with percentages)
3. Aggregate by merchant (top 10 with frequencies)
4. Detect spending patterns (weekend/weekday, time trends)
5. Identify anomalies (transactions 3x+ category average)
"""

from datetime import datetime, date
from typing import List, Dict, Any, Optional, Tuple
from decimal import Decimal
from collections import defaultdict
import calendar

from app.models.transaction import Transaction


class StatisticsEngine:
    """
    Aggregates transaction data into a compact summary for AI analysis

    Usage:
        engine = StatisticsEngine(transactions, user_id)
        summary = engine.generate_summary()
        # Pass summary to Gemini API instead of raw transactions
    """

    def __init__(self, transactions: List[Transaction], user_id: str):
        """
        Initialize with transaction data

        Args:
            transactions: List of Transaction objects (typically 3-6 months)
            user_id: User UUID for context
        """
        self.transactions = transactions
        self.user_id = user_id

    def generate_summary(self) -> Dict[str, Any]:
        """
        Generate aggregated summary of all transactions

        Returns:
            {
                "overview": {...},       # Total spent, count, date range
                "categories": {...},     # Top 10 categories with percentages
                "top_merchants": [...],  # Top 10 merchants
                "patterns": {...},       # Weekend/weekday, day-of-week, monthly
                "anomalies": [...]       # Transactions 3x+ category average
            }
        """

        if not self.transactions:
            return {
                "overview": {
                    "total_spent": 0,
                    "transaction_count": 0,
                    "date_range": "No data"
                },
                "categories": {},
                "top_merchants": [],
                "patterns": {},
                "anomalies": []
            }

        return {
            "overview": self._calculate_overview(),
            "categories": self._aggregate_categories(),
            "top_merchants": self._aggregate_merchants(),
            "patterns": self._detect_patterns(),
            "anomalies": self._detect_anomalies()
        }

    def _calculate_overview(self) -> Dict[str, Any]:
        """
        Calculate high-level statistics

        Returns:
            {
                "total_spent": 1234.56,
                "transaction_count": 156,
                "date_range": "June 2025 to August 2025",
                "avg_transaction": 7.92,
                "analysis_period_days": 92
            }
        """
        total_spent = sum(float(txn.amount) for txn in self.transactions)
        count = len(self.transactions)

        # Get date range
        dates = [txn.transaction_date for txn in self.transactions]
        earliest = min(dates)
        latest = max(dates)

        # Format date range nicely
        if earliest.year == latest.year:
            if earliest.month == latest.month:
                date_range = f"{earliest.strftime('%B %Y')}"
            else:
                date_range = f"{earliest.strftime('%B')} to {latest.strftime('%B %Y')}"
        else:
            date_range = f"{earliest.strftime('%B %Y')} to {latest.strftime('%B %Y')}"

        # Calculate analysis period
        period_days = (latest - earliest).days + 1

        return {
            "total_spent": round(total_spent, 2),
            "transaction_count": count,
            "date_range": date_range,
            "avg_transaction": round(total_spent / count, 2) if count > 0 else 0,
            "analysis_period_days": period_days
        }

    def _aggregate_categories(self) -> Dict[str, Any]:
        """
        Aggregate transactions by category

        Returns:
            {
                "Dining & Restaurants": {"amount": 450.00, "count": 23, "percentage": 25.3},
                "Groceries": {"amount": 380.00, "count": 12, "percentage": 21.4},
                ...
            }
            Limited to top 10 categories by spending
        """
        category_data = defaultdict(lambda: {"amount": 0, "count": 0})
        total_spent = sum(float(txn.amount) for txn in self.transactions)

        for txn in self.transactions:
            category_name = txn.category.name if txn.category else "Uncategorized"
            category_data[category_name]["amount"] += float(txn.amount)
            category_data[category_name]["count"] += 1

        # Sort by amount (descending) and take top 10
        sorted_categories = sorted(
            category_data.items(),
            key=lambda x: x[1]["amount"],
            reverse=True
        )[:10]

        # Calculate percentages
        result = {}
        for category_name, data in sorted_categories:
            percentage = (data["amount"] / total_spent * 100) if total_spent > 0 else 0
            result[category_name] = {
                "amount": round(data["amount"], 2),
                "count": data["count"],
                "percentage": round(percentage, 1)
            }

        return result

    def _aggregate_merchants(self) -> List[Dict[str, Any]]:
        """
        Aggregate transactions by merchant

        Returns:
            [
                {"merchant": "Starbucks", "amount": 180.00, "count": 24, "avg_transaction": 7.50},
                {"merchant": "Uber", "amount": 156.00, "count": 12, "avg_transaction": 13.00},
                ...
            ]
            Limited to top 10 merchants by total spending
        """
        merchant_data = defaultdict(lambda: {"amount": 0, "count": 0})

        for txn in self.transactions:
            merchant_name = txn.merchant_name or "Unknown Merchant"
            merchant_data[merchant_name]["amount"] += float(txn.amount)
            merchant_data[merchant_name]["count"] += 1

        # Sort by amount (descending) and take top 10
        sorted_merchants = sorted(
            merchant_data.items(),
            key=lambda x: x[1]["amount"],
            reverse=True
        )[:10]

        result = []
        for merchant_name, data in sorted_merchants:
            result.append({
                "merchant": merchant_name,
                "amount": round(data["amount"], 2),
                "count": data["count"],
                "avg_transaction": round(data["amount"] / data["count"], 2)
            })

        return result

    def _detect_patterns(self) -> Dict[str, Any]:
        """
        Detect spending patterns (temporal analysis)

        Returns:
            {
                "weekend_vs_weekday": {
                    "weekend_avg_daily": 85.00,
                    "weekday_avg_daily": 60.00,
                    "difference_percentage": 41.7
                },
                "day_of_week": {
                    "Monday": 234.00,
                    "Tuesday": 189.00,
                    ...
                },
                "monthly_trend": {
                    "June 2025": 1200.00,
                    "July 2025": 1350.00,
                    ...
                }
            }
        """
        # Weekend vs Weekday
        weekend_total = Decimal('0.00')
        weekday_total = Decimal('0.00')
        weekend_days = set()
        weekday_days = set()

        # Day of week analysis
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        day_totals = defaultdict(float)

        # Monthly trend
        monthly_totals = defaultdict(float)

        for txn in self.transactions:
            day_of_week = txn.transaction_date.weekday()

            # Weekend vs weekday
            if day_of_week in [5, 6]:  # Saturday, Sunday
                weekend_total += txn.amount
                weekend_days.add(txn.transaction_date)
            else:
                weekday_total += txn.amount
                weekday_days.add(txn.transaction_date)

            # Day of week totals
            day_totals[day_names[day_of_week]] += float(txn.amount)

            # Monthly totals
            month_year = txn.transaction_date.strftime("%B %Y")
            monthly_totals[month_year] += float(txn.amount)

        # Calculate averages
        weekend_avg = float(weekend_total) / len(weekend_days) if weekend_days else 0
        weekday_avg = float(weekday_total) / len(weekday_days) if weekday_days else 0

        difference_pct = 0
        if weekday_avg > 0:
            difference_pct = ((weekend_avg - weekday_avg) / weekday_avg) * 100

        return {
            "weekend_vs_weekday": {
                "weekend_avg_daily": round(weekend_avg, 2),
                "weekday_avg_daily": round(weekday_avg, 2),
                "difference_percentage": round(difference_pct, 1)
            },
            "day_of_week": {
                day: round(amount, 2)
                for day, amount in sorted(
                    day_totals.items(),
                    key=lambda x: day_names.index(x[0])
                )
            },
            "monthly_trend": {
                month: round(amount, 2)
                for month, amount in sorted(monthly_totals.items())
            }
        }

    def _detect_anomalies(self) -> List[Dict[str, Any]]:
        """
        Detect unusual transactions (3x+ category average)

        Returns:
            [
                {
                    "merchant": "Apple Store",
                    "amount": 1299.00,
                    "category": "Shopping",
                    "date": "2025-07-15",
                    "category_avg": 45.00,
                    "multiplier": 28.9
                },
                ...
            ]
            Limited to top 5 anomalies
        """
        # Calculate average per category
        category_totals = defaultdict(float)
        category_counts = defaultdict(int)

        for txn in self.transactions:
            category_name = txn.category.name if txn.category else "Uncategorized"
            category_totals[category_name] += float(txn.amount)
            category_counts[category_name] += 1

        category_averages = {
            cat: category_totals[cat] / category_counts[cat]
            for cat in category_totals
        }

        # Find anomalies (3x+ category average)
        anomalies = []
        for txn in self.transactions:
            category_name = txn.category.name if txn.category else "Uncategorized"
            category_avg = category_averages.get(category_name, 0)

            if category_avg > 0:
                multiplier = float(txn.amount) / category_avg

                if multiplier >= 3.0:  # 3x or more than average
                    anomalies.append({
                        "merchant": txn.merchant_name or "Unknown",
                        "amount": float(txn.amount),
                        "category": category_name,
                        "date": txn.transaction_date.strftime("%Y-%m-%d"),
                        "category_avg": round(category_avg, 2),
                        "multiplier": round(multiplier, 1)
                    })

        # Sort by multiplier (highest first) and take top 5
        anomalies.sort(key=lambda x: x["multiplier"], reverse=True)
        return anomalies[:5]
