# Backend Restructuring Plan

## Overview
Migrating from **layer-based** to **feature-based** architecture without breaking functionality.

## Current Structure (Layer-based)
```
app/
├── auth/          # Auth utilities only
├── config/        # Global configs
├── core/          # Shared utilities
├── models/        # All DB models (7 files)
├── routers/       # All API routes (8 files)
├── schemas/       # All Pydantic schemas (7 files)
└── services/      # Business logic
```

## New Structure (Feature-based)
```
app/
├── features/
│   ├── auth/           # User authentication
│   │   ├── __init__.py
│   │   ├── models.py      (from models/user.py)
│   │   ├── router.py      (from routers/auth.py, users.py)
│   │   ├── schemas.py     (from schemas/user.py, token.py, password_reset.py)
│   │   └── services.py    (from auth/*)
│   │
│   ├── cards/          # Credit card management
│   │   ├── __init__.py
│   │   ├── models.py      (from models/credit_card.py)
│   │   ├── router.py      (from routers/credit_cards.py)
│   │   └── schemas.py     (from schemas/credit_card.py)
│   │
│   ├── transactions/   # Transaction tracking
│   │   ├── __init__.py
│   │   ├── models.py      (from models/transaction.py)
│   │   ├── router.py      (from routers/transactions.py)
│   │   └── schemas.py     (from schemas/transaction.py)
│   │
│   ├── statements/     # PDF statement processing
│   │   ├── __init__.py
│   │   ├── models.py      (from models/statement.py)
│   │   ├── router.py      (from routers/statements.py)
│   │   └── schemas.py     (from schemas/statement.py)
│   │
│   ├── categories/     # Spending categories
│   │   ├── __init__.py
│   │   ├── models.py      (from models/category.py)
│   │   ├── router.py      (from routers/categories.py)
│   │   └── schemas.py     (from schemas/category.py)
│   │
│   ├── insights/       # AI insights & analytics
│   │   ├── __init__.py
│   │   ├── models.py      (from models/insight.py, alert.py)
│   │   ├── router.py      (from routers/insights.py)
│   │   ├── schemas.py     (new - insight schemas)
│   │   ├── ai_service.py  (from services/ai_insights.py)
│   │   ├── statistics_engine.py (from services/statistics_engine.py)
│   │   └── generators/
│   │       ├── __init__.py
│   │       ├── recurring_habit.py
│   │       ├── smart_spending_praise.py
│   │       ├── subscription_detection.py
│   │       ├── transport_savings.py
│   │       └── weekend_spending.py
│   │
│   └── analytics/      # Spending analytics
│       ├── __init__.py
│       ├── router.py      (from routers/analytics.py)
│       └── schemas.py     (from schemas/analytics.py)
│
├── core/              # Shared infrastructure (unchanged)
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── email_service.py
│   ├── gemini_service.py
│   └── seed_data.py
│
├── shared/            # Shared configurations
│   ├── __init__.py
│   ├── insights_config.py  (from config/insights_config.py)
│   └── merchant_categories.py (from config/merchant_categories.py)
│
└── main.py

```

## Migration Strategy

### Phase 1: Preparation
1. Verify current app is running
2. Create new folder structure
3. Create git checkpoint

### Phase 2: Feature-by-Feature Migration
Migrate one feature at a time, update imports, test before moving to next.

**Order of migration:**
1. **Auth** (users, authentication)
2. **Cards** (credit cards)
3. **Categories** (spending categories)
4. **Transactions** (transactions)
5. **Statements** (PDF statements)
6. **Analytics** (analytics endpoints)
7. **Insights** (AI insights - most complex)

### Phase 3: Cleanup
1. Move config files to `shared/`
2. Update `main.py` router imports
3. Update `alembic/env.py` model imports
4. Delete old empty folders
5. Test all endpoints
6. Final commit

## Import Updates Required

### Example: Auth Feature
**Before:**
```python
from app.models.user import User
from app.schemas.user import UserCreate
from app.routers.auth import router
```

**After:**
```python
from app.features.auth.models import User
from app.features.auth.schemas import UserCreate
from app.features.auth.router import router
```

## Testing Strategy
After each feature migration:
1. Check backend starts without errors
2. Test relevant API endpoints
3. Verify database operations work
4. Check frontend still functions

## Rollback Plan
If anything breaks:
1. Git stash or reset to last working commit
2. Identify the issue
3. Fix and retry

## Benefits
- ✅ Clear feature boundaries
- ✅ Everything for a feature in one place
- ✅ Easier onboarding for new developers
- ✅ Better testability
- ✅ Follows modern best practices (DDD, Vertical Slice)

## Estimated Time
- Setup: 5 minutes
- Migration per feature: 10-15 minutes
- Testing & cleanup: 15 minutes
- **Total: ~2 hours**

---

**Ready to proceed?** The migration will be done carefully with testing after each step.
