"""
Insights Services

Rule-based and AI-powered financial insights generation.

Available insights:
- WeekendSpendingService: Analyzes weekend vs weekday spending patterns
- RecurringHabitService: Detects frequent discretionary spending (coffee, dining, etc.)
- SmartSpendingPraiseService: Praises users for using public transport
- SubscriptionDetectionService: Identifies recurring monthly subscriptions
- TransportSavingsService: Shows savings potential by switching to public transport
"""

from app.services.insights.weekend_spending import WeekendSpendingService
from app.services.insights.recurring_habit import RecurringHabitService
from app.services.insights.smart_spending_praise import SmartSpendingPraiseService
from app.services.insights.subscription_detection import SubscriptionDetectionService
from app.services.insights.transport_savings import TransportSavingsService

__all__ = [
    "WeekendSpendingService",
    "RecurringHabitService",
    "SmartSpendingPraiseService",
    "SubscriptionDetectionService",
    "TransportSavingsService"
]
