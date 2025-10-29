"""
Insights Configuration

Centralized configuration for AI insights generation.
Adjust these values to fine-tune insight generation behavior.
"""

from datetime import timedelta


# ═══════════════════════════════════════════════════════════════════
# ANALYSIS PERIOD SETTINGS
# ═══════════════════════════════════════════════════════════════════

# How far back to analyze transactions when generating insights
ANALYSIS_PERIOD_DAYS = 90  # 3 months
# Alternative: Use timedelta for clarity
ANALYSIS_PERIOD = timedelta(days=ANALYSIS_PERIOD_DAYS)


# ═══════════════════════════════════════════════════════════════════
# DUPLICATE PREVENTION SETTINGS
# ═══════════════════════════════════════════════════════════════════

# Don't regenerate the same insight type within this window
DUPLICATE_PREVENTION_DAYS = 7  # 1 week
DUPLICATE_PREVENTION_PERIOD = timedelta(days=DUPLICATE_PREVENTION_DAYS)


# ═══════════════════════════════════════════════════════════════════
# WEEKEND SPENDING INSIGHT SETTINGS
# ═══════════════════════════════════════════════════════════════════

class WeekendSpendingConfig:
    """Configuration for weekend spending insights"""

    # Minimum percentage difference to generate insight
    # E.g., 4 = weekend spending must be 4%+ higher than weekday
    THRESHOLD_PERCENTAGE = 4

    # Minimum number of transactions required for analysis
    # Ensures statistical relevance
    MIN_TRANSACTIONS = 10

    # Minimum weekend transactions required
    # Need enough weekend data to make meaningful comparison
    MIN_WEEKEND_TRANSACTIONS = 3

    # Minimum weekday transactions required
    MIN_WEEKDAY_TRANSACTIONS = 5


# ═══════════════════════════════════════════════════════════════════
# FUTURE INSIGHT TYPE SETTINGS
# ═══════════════════════════════════════════════════════════════════

class CoffeeHabitConfig:
    """Configuration for coffee/small purchases insights (future)"""

    # Minimum monthly spending on coffee to generate insight
    MIN_MONTHLY_AMOUNT = 50.0

    # Minimum transactions to detect pattern
    MIN_TRANSACTIONS = 5


class SubscriptionConfig:
    """Configuration for subscription audit insights (future)"""

    # Minimum number of subscriptions to trigger audit
    MIN_SUBSCRIPTIONS = 3

    # Minimum total monthly subscription cost
    MIN_MONTHLY_COST = 50.0


# ═══════════════════════════════════════════════════════════════════
# IMPACT SCORE SETTINGS
# ═══════════════════════════════════════════════════════════════════

class ImpactScoreConfig:
    """Configuration for impact score calculation"""

    # Impact score thresholds (1-10 scale)
    HIGH_IMPACT_MIN = 8      # 8-10 = High priority
    MEDIUM_IMPACT_MIN = 5    # 5-7 = Medium priority
    LOW_IMPACT_MAX = 4       # 1-4 = Low priority

    # Potential savings thresholds for bonus points
    HIGH_SAVINGS_MIN = 100.0   # $100+ monthly savings
    MEDIUM_SAVINGS_MIN = 50.0  # $50-99 monthly savings
