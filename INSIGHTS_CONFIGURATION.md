# Insights Configuration Guide

## Overview

All hardcoded values have been moved to **centralized configuration** in `app/config/insights_config.py`. This allows easy adjustment of insight generation parameters without modifying code.

---

## Configuration File Location

```
app/config/insights_config.py
```

---

## Configurable Parameters

### 1. **Analysis Period**

**What it controls**: How far back to analyze transactions when generating insights

**Default**: 90 days (3 months)

**How to change**:
```python
# In app/config/insights_config.py
ANALYSIS_PERIOD_DAYS = 90  # Change to 30, 60, 180, etc.
```

**Impact**:
- **30 days**: More recent patterns, less data (may miss trends)
- **90 days** (current): Good balance of recent + historical data
- **180 days**: Longer-term patterns, more data required

---

### 2. **Duplicate Prevention Window**

**What it controls**: How long to wait before regenerating the same insight type

**Default**: 7 days (1 week)

**How to change**:
```python
# In app/config/insights_config.py
DUPLICATE_PREVENTION_DAYS = 7  # Change to 1, 3, 14, etc.
```

**Impact**:
- **1 day**: Users can regenerate daily (may show same insights repeatedly)
- **7 days** (current): Weekly refresh allows pattern changes to be detected
- **30 days**: Monthly insights (less frequent updates)

---

### 3. **Weekend Spending Thresholds**

#### 3a. Minimum Percentage Difference

**What it controls**: Weekend spending must be X% higher than weekday to generate insight

**Default**: 4%

**How to change**:
```python
# In app/config/insights_config.py
class WeekendSpendingConfig:
    THRESHOLD_PERCENTAGE = 4  # Change to 5, 10, 15, etc.
```

**Impact**:
- **4%** (current): Sensitive, shows smaller differences
- **10%**: More selective, only significant patterns
- **15%**: Very selective, only major spending differences

#### 3b. Minimum Transactions Required

**What it controls**: Total transactions needed for statistical relevance

**Default**: 10 transactions

**How to change**:
```python
class WeekendSpendingConfig:
    MIN_TRANSACTIONS = 10  # Change to 5, 15, 20, etc.
```

**Impact**:
- **5**: Works with less data (may be less accurate)
- **10** (current): Good balance of accuracy and data requirements
- **20**: More accurate but requires more data

---

## Example Configurations

### Configuration A: Quick Testing
```python
ANALYSIS_PERIOD_DAYS = 30  # 1 month
DUPLICATE_PREVENTION_DAYS = 1  # Daily regeneration
THRESHOLD_PERCENTAGE = 3  # More sensitive
MIN_TRANSACTIONS = 5  # Less data required
```

### Configuration B: Conservative (Current)
```python
ANALYSIS_PERIOD_DAYS = 90  # 3 months
DUPLICATE_PREVENTION_DAYS = 7  # Weekly
THRESHOLD_PERCENTAGE = 4  # Balanced
MIN_TRANSACTIONS = 10  # Moderate
```

### Configuration C: Long-term Analysis
```python
ANALYSIS_PERIOD_DAYS = 180  # 6 months
DUPLICATE_PREVENTION_DAYS = 30  # Monthly
THRESHOLD_PERCENTAGE = 10  # Only significant patterns
MIN_TRANSACTIONS = 30  # High confidence
```

---

## How to Change Configuration

### Method 1: Direct Edit (Development)

1. Open `app/config/insights_config.py`
2. Modify the values
3. Restart the FastAPI server
4. New values take effect immediately

### Method 2: Environment Variables (Production - Future)

**Planned feature**: Allow configuration via environment variables

```bash
# .env file
INSIGHTS_ANALYSIS_PERIOD_DAYS=90
INSIGHTS_DUPLICATE_PREVENTION_DAYS=7
INSIGHTS_THRESHOLD_PERCENTAGE=4
```

---

## Future Insight Types (Pre-configured)

The config file includes placeholders for future insight types:

### Coffee Habit Insights
```python
class CoffeeHabitConfig:
    MIN_MONTHLY_AMOUNT = 50.0  # $50/month on coffee
    MIN_TRANSACTIONS = 5  # At least 5 purchases
```

### Subscription Audit
```python
class SubscriptionConfig:
    MIN_SUBSCRIPTIONS = 3  # Need 3+ subscriptions
    MIN_MONTHLY_COST = 50.0  # Total $50+/month
```

---

## Testing Different Configurations

### Quick Test Script

Create `test_config.py`:

```python
from app.config.insights_config import (
    ANALYSIS_PERIOD_DAYS,
    DUPLICATE_PREVENTION_DAYS,
    WeekendSpendingConfig
)

print(f"Analysis Period: {ANALYSIS_PERIOD_DAYS} days")
print(f"Duplicate Prevention: {DUPLICATE_PREVENTION_DAYS} days")
print(f"Threshold: {WeekendSpendingConfig.THRESHOLD_PERCENTAGE}%")
print(f"Min Transactions: {WeekendSpendingConfig.MIN_TRANSACTIONS}")
```

Run: `python test_config.py`

---

## Benefits of Centralized Configuration

✅ **Easy Adjustments**: Change values in one place
✅ **No Code Changes**: Modify behavior without touching logic
✅ **Testing**: Try different parameters easily
✅ **Documentation**: All settings in one file
✅ **Future-proof**: Ready for environment variables
✅ **Type Safety**: Python classes provide structure

---

## Migration Summary

### Before (Hardcoded)
```python
# Scattered across files
three_months_ago = datetime.now() - timedelta(days=90)
THRESHOLD_PERCENTAGE = 4
MIN_TRANSACTIONS = 10
```

### After (Centralized)
```python
# Single source of truth
from app.config.insights_config import ANALYSIS_PERIOD, WeekendSpendingConfig

analysis_start = datetime.now() - ANALYSIS_PERIOD
if percentage > WeekendSpendingConfig.THRESHOLD_PERCENTAGE:
    # Generate insight
```

---

## Questions?

**Q: Will changing config affect existing insights?**
A: No, existing insights remain unchanged. Only new insights use the new config.

**Q: Can users customize these values?**
A: Not yet. This is a system-wide config. User preferences can be added later.

**Q: How do I reset to defaults?**
A: Re-download `insights_config.py` from the repository or reset values manually.

---

**Last Updated**: October 29, 2025
**Version**: 1.0
