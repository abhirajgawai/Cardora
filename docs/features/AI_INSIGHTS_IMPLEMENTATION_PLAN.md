# 🎯 AI Insights - 4 Week Implementation Plan

**Project:** Cardora AI Insights Feature
**Timeline:** 4 Weeks (Complete Version)
**Approach:** Vertical Slices (Build each insight end-to-end)
**Status:** Ready to Start

---

## 📊 Overview

### Goal
Ship production-ready AI Insights feature with:
- ✅ 6 types of insights (Subscription, Coffee Habit, Weekend Spending, Category Trend, Merchant Concentration, Anomaly Detection)
- ✅ Full transaction linking (show exact transactions behind each insight)
- ✅ Dashboard hero card + dedicated /insights page
- ✅ Async processing with Celery + Redis
- ✅ AI-powered insights using Gemini API
- ✅ Polished UI with animations

### Architecture

```
User uploads PDF
    ↓
Statement processed (existing)
    ↓
Trigger async Celery job → generate_insights_task()
    ↓
StatisticsEngine: Pre-process transactions → aggregated summary
    ↓
Generate 6 insights in parallel:
    1. Subscription Audit (rule-based)
    2. Coffee/Recurring Habit (rule-based)
    3. Weekend Spending (pattern-based)
    4. Category Trend (comparison-based)
    5. Merchant Concentration (aggregation-based)
    6. AI-Generated Insight (Gemini API)
    ↓
Save insights + link to transactions
    ↓
Update statement.insights_status = "completed"
    ↓
Frontend polls status → displays insights
```

### Tech Stack
- **Backend:** FastAPI, Celery, Redis, PostgreSQL, Alembic
- **AI:** Google Gemini API (gemini-1.5-flash)
- **Frontend:** Next.js, React, Framer Motion, TailwindCSS
- **Deployment:** Existing infrastructure + Redis container

---

## 🗄️ Database Schema

### New Tables

**insights**
```sql
id: UUID (PK)
user_id: INT (FK users.id)
statement_id: UUID (FK statements.id, nullable)
insight_type: VARCHAR(50)  -- 'subscription_audit', 'coffee_habit', etc.
title: VARCHAR(200)
description: TEXT
data: JSON  -- Summary metrics
priority: VARCHAR(20)  -- 'high', 'medium', 'low'
status: VARCHAR(20)  -- 'active', 'dismissed', 'completed'
transaction_count: INT
created_at: TIMESTAMP
updated_at: TIMESTAMP
```

**insight_transactions** (junction table)
```sql
id: UUID (PK)
insight_id: UUID (FK insights.id, ON DELETE CASCADE)
transaction_id: UUID (FK transactions.id, ON DELETE CASCADE)
relevance_score: DECIMAL(3,2)  -- 0.0 to 1.0
created_at: TIMESTAMP
UNIQUE(insight_id, transaction_id)
```

**payment_alerts** (for subscription tracking)
```sql
id: UUID (PK)
user_id: INT (FK users.id)
insight_id: UUID (FK insights.id)
merchant_name: VARCHAR(200)
amount: DECIMAL(10,2)
frequency: VARCHAR(20)  -- 'monthly', 'yearly'
next_charge_date: DATE
is_active: BOOLEAN
created_at: TIMESTAMP
```

### Update Existing Table

**statements**
```sql
-- Add columns:
insights_status: VARCHAR(20) DEFAULT 'pending'  -- 'pending', 'processing', 'completed', 'failed'
insights_generated_at: TIMESTAMP (nullable)
```

---

## 📅 Week-by-Week Breakdown

### **WEEK 1: Foundation & Infrastructure**
**Goal:** Database ready + Async jobs working + First insight live

#### Day 1-2: Database Setup
- [ ] Create models: `Insight`, `InsightTransaction`, `PaymentAlert`
- [ ] Create Alembic migration
- [ ] Run migration: `alembic upgrade head`
- [ ] Verify schema in PostgreSQL

#### Day 3-4: Async Infrastructure
- [ ] Install: `celery==5.3.4`, `redis==5.0.1`
- [ ] Set up `app/core/celery_app.py`
- [ ] Start Redis container: `docker run -d -p 6379:6379 redis`
- [ ] Start Celery worker: `celery -A app.core.celery_app worker --loglevel=info`
- [ ] Test async task execution

#### Day 5-7: Core Services + First Insight
- [ ] Build `StatisticsEngine` service (data aggregation)
- [ ] Build `PaymentDetectionService` (subscription finder)
- [ ] Build `RuleBasedInsights.generate_subscription_insight()`
- [ ] Create API router: `app/routers/insights.py`
- [ ] Create endpoints: `GET /insights/hero`, `GET /insights`, `GET /insights/{id}/transactions`
- [ ] Test Subscription Audit insight end-to-end

**Deliverable:** Upload statement → Subscription insight appears on dashboard

---

### **WEEK 2: Core Rule-Based Insights**
**Goal:** 4 rule-based insights working + /insights page

#### Day 8-9: Coffee/Recurring Habit Insight
- [ ] Build merchant frequency analyzer
- [ ] Generate insight for merchants visited 10+ times/month
- [ ] Link transactions to insight
- [ ] Test with Starbucks/coffee shop data

#### Day 10-11: Weekend Spending & Category Trend
- [ ] Build weekend vs weekday analyzer
- [ ] Build category trend analyzer (compare month-over-month)
- [ ] Generate insights with transaction links
- [ ] Test with real data

#### Day 12-14: Frontend - /insights Page
- [ ] Build `InsightsList` component
- [ ] Build transaction detail view (expandable)
- [ ] Create `/insights` page route
- [ ] Add expand/collapse for transaction lists
- [ ] Integrate hero card into `/dashboard`
- [ ] Test all 4 insights displaying correctly

**Deliverable:** /insights page showing 4 insights with expandable transaction details

---

### **WEEK 3: AI Integration & Advanced Insights**
**Goal:** Gemini AI working + All 6 insights complete

#### Day 15-16: Gemini API Setup
- [ ] Get Gemini API key from Google AI Studio
- [ ] Add to `.env`: `GEMINI_API_KEY=your_key`
- [ ] Install: `google-generativeai`
- [ ] Build `app/services/ai_insights.py`
- [ ] Test AI insight generation with sample summary

#### Day 17-18: AI Insight Integration
- [ ] Build prompt engineering for financial analysis
- [ ] Use `StatisticsEngine` summary (not raw transactions)
- [ ] Generate ONE personalized insight per statement
- [ ] Link relevant transactions to AI insight
- [ ] Test AI quality with 3+ real statements

#### Day 19-21: Remaining Insights + Integration
- [ ] Build Merchant Concentration insight
- [ ] Build Anomaly Detection insight
- [ ] Update `/statements/upload` to trigger async insights job
- [ ] Add polling mechanism on frontend (check every 3s)
- [ ] Add toast notifications for new insights
- [ ] Test all 6 insights working together

**Deliverable:** Full insights system with AI generation after every upload

---

### **WEEK 4: Polish, Testing & Deployment**
**Goal:** Production-ready feature with monitoring

#### Day 22-24: Testing & Tuning
- [ ] Upload 3 real statements, verify all insights generate
- [ ] Tune thresholds (what's "high" priority vs "medium"?)
- [ ] Test edge cases: no data, single transaction, etc.
- [ ] Test with 1000+ transactions (performance)
- [ ] Add error handling for Gemini API failures

#### Day 25-26: UI Polish
- [ ] Add Framer Motion animations to insight cards
- [ ] Add loading states and skeleton loaders
- [ ] Add export CSV functionality for transactions
- [ ] Add filters on /insights page (type, priority, date)
- [ ] Add "Mark as Reviewed" functionality
- [ ] Improve mobile responsiveness

#### Day 27-28: Documentation & Deployment
- [ ] Write API documentation for insights endpoints
- [ ] Create user guide: "Understanding Your Insights"
- [ ] Add monitoring for Celery jobs (failure alerts)
- [ ] Add monitoring for Gemini API usage (cost tracking)
- [ ] Deploy to production
- [ ] Gather initial user feedback

**Deliverable:** Production deployment with monitoring + user guide

---

## 🏗️ Critical Implementation Details

### 1. StatisticsEngine Service

**Purpose:** Pre-process transactions into aggregated summary (avoid sending 1000s of transactions to Gemini)

**Key Methods:**
```python
class StatisticsEngine:
    def generate_summary() -> dict:
        return {
            "overview": {...},          # Total spent, count, date range
            "categories": {...},        # Top 10 categories with percentages
            "top_merchants": [...],     # Top 10 merchants
            "patterns": {...},          # Weekend/weekday, day-of-week, monthly
            "anomalies": [...]          # Transactions 3x+ category average
        }
```

**Why:** Reduces Gemini API cost from $12.50 to $0.12 per insight (100x cheaper!)

---

### 2. Payment Detection Algorithm

**Logic:**
1. Group transactions by normalized merchant name
2. Calculate day intervals between transactions
3. Check if intervals are consistent (~30 days = monthly, ~365 = yearly)
4. Check if amounts are consistent (within 10% variance)
5. Minimum 2 occurrences to consider it recurring

**Thresholds:**
- Monthly: 25-35 day intervals
- Yearly: 350-380 day intervals
- Amount variance: ≤10% of average

---

### 3. Insight Priority Ranking

**Rules:**
- `HIGH`: Subscriptions, Anomalies, AI insights, Category trends >50%
- `MEDIUM`: Merchant concentration, Weekend spending
- `LOW`: Informational insights

**Hero Card Selection:**
1. Get all "active" insights for user
2. Sort by priority (HIGH first)
3. Sort by created_at (newest first)
4. Return first result

---

### 4. Celery Task Flow

```python
# app/tasks/insights_tasks.py

@celery_app.task(name="generate_insights")
def generate_insights_task(statement_id: str, user_id: int):
    """
    Async task to generate all insights
    """
    try:
        # Update status
        update_statement_status(statement_id, "processing")

        # Get transactions
        transactions = get_user_transactions(user_id, months=12)

        # Generate aggregated summary
        stats_engine = StatisticsEngine(transactions, user_id)
        summary = stats_engine.generate_summary()

        # Generate rule-based insights (fast)
        rule_insights = RuleBasedInsights(db, user_id)
        insights = [
            rule_insights.generate_subscription_insight(),
            rule_insights.generate_coffee_habit_insight(),
            rule_insights.generate_weekend_spending_insight(),
            rule_insights.generate_category_trend_insight(),
            rule_insights.generate_merchant_concentration_insight(),
            rule_insights.generate_anomaly_insight()
        ]

        # Generate AI insight (slower, costs money)
        ai_insight = AIInsightsService(db, user_id).generate_insight(summary)
        insights.append(ai_insight)

        # Save all insights
        save_insights([i for i in insights if i is not None])

        # Update status
        update_statement_status(statement_id, "completed")

    except Exception as e:
        update_statement_status(statement_id, "failed")
        raise
```

**Trigger:**
```python
# In app/routers/statements.py after PDF processing

@router.post("/upload")
async def upload_statement(...):
    # ... existing PDF processing ...

    # Trigger async insights generation
    from app.tasks.insights_tasks import generate_insights_task
    generate_insights_task.delay(str(statement.id), current_user.id)

    return {"message": "Processing...", "statement_id": statement.id}
```

---

### 5. AI Insight Prompt Engineering

```python
# app/services/ai_insights.py

INSIGHT_PROMPT = """
You are a financial advisor analyzing spending patterns.

SPENDING SUMMARY:
{summary_json}

Generate ONE interesting, actionable insight that:
1. Reveals something the user likely hasn't noticed
2. Is specific with actual numbers from the data
3. Suggests a clear action to save money or improve finances
4. Is friendly and non-judgmental in tone

Focus areas:
- Small recurring expenses that add up (coffee, food delivery, etc.)
- Day-of-week or weekend spending patterns
- Category trends (increasing/decreasing)
- Merchant concentration (shopping at same places)
- Budget optimization opportunities

Return ONLY valid JSON (no markdown):
{
    "title": "Short catchy title (max 60 chars)",
    "description": "2-3 sentences explaining the insight and suggesting action",
    "data": {
        "key_metric_1": value,
        "key_metric_2": value,
        "potential_savings": amount (if applicable)
    }
}
"""
```

**Cost Control:**
- Summary ~500 tokens input
- Response ~200 tokens output
- Total: ~700 tokens × $0.00025 = **$0.175 per insight**
- With 100 users uploading monthly: **$17.50/month**

---

### 6. API Endpoints

```python
# app/routers/insights.py

# Get hero insight for dashboard
GET /insights/hero
Response: Single insight object (highest priority, newest)

# List all insights
GET /insights?show_dismissed=false&limit=20
Response: Array of insight objects

# Get single insight with details
GET /insights/{insight_id}
Response: Insight object with full data

# Get transactions linked to insight
GET /insights/{insight_id}/transactions
Response: {insight, transactions: [...], total_amount}

# Dismiss insight
POST /insights/{insight_id}/dismiss
Response: {message: "Dismissed"}

# Check statement insights status (for polling)
GET /statements/{statement_id}/status
Response: {insights_status, insights_generated_at}
```

---

### 7. Frontend Polling Pattern

```typescript
// frontend/src/app/upload/page.tsx

const pollInsightsStatus = async (statementId: string) => {
    const maxAttempts = 20;  // Poll for up to 1 minute
    let attempts = 0;

    const interval = setInterval(async () => {
        attempts++;

        const status = await getStatementStatus(statementId);

        if (status.insights_status === "completed") {
            clearInterval(interval);
            toast.success("Insights ready!");
            router.push("/dashboard");
        } else if (status.insights_status === "failed" || attempts >= maxAttempts) {
            clearInterval(interval);
            toast.error("Insights generation failed");
        }
    }, 3000);  // Check every 3 seconds
};
```

---

## 🧪 Testing Checklist

### Backend Tests
- [ ] Subscription detection with 2, 3, 6, 12 monthly charges
- [ ] Coffee habit detection with 10, 20, 45 visits
- [ ] Weekend spending with mixed weekday/weekend data
- [ ] Category trend with increasing/decreasing patterns
- [ ] Anomaly detection with 3x, 5x, 10x unusual transactions
- [ ] AI insight generation with valid summary
- [ ] Celery task execution and retry logic
- [ ] Transaction linking (correct IDs, no duplicates)

### Frontend Tests
- [ ] Dashboard hero card displays correctly
- [ ] /insights page loads all insights
- [ ] Transaction expand/collapse works
- [ ] Export CSV functionality
- [ ] Filters work (type, priority, date)
- [ ] Dismiss insight updates status
- [ ] Polling shows loading state
- [ ] Mobile responsiveness

### Edge Cases
- [ ] No transactions (handle gracefully)
- [ ] Single transaction (no insights)
- [ ] 1000+ transactions (performance test)
- [ ] Gemini API failure (retry + fallback)
- [ ] Celery worker down (queue pending)
- [ ] Multiple statements uploaded quickly (parallelization)

---

## 📊 Monitoring & Metrics

### Key Metrics to Track

1. **Insight Generation Rate**
   - Statements processed per day
   - Insights generated per statement (should be ~4-6)
   - Generation time (target: <30 seconds)

2. **Gemini API Usage**
   - API calls per day
   - Token usage per call
   - Monthly cost (target: <$20 for 100 users)
   - Error rate

3. **Celery Queue Health**
   - Pending tasks count
   - Failed tasks count
   - Average task duration
   - Worker uptime

4. **User Engagement**
   - % of users viewing insights
   - Insights dismissed vs acted upon
   - Time spent on /insights page
   - Most valuable insight types

### Monitoring Setup

```python
# Add to app/core/celery_app.py
from celery.signals import task_success, task_failure

@task_success.connect
def log_success(sender=None, **kwargs):
    logger.info(f"Task {sender.name} succeeded")

@task_failure.connect
def log_failure(sender=None, **kwargs):
    logger.error(f"Task {sender.name} failed: {kwargs.get('exception')}")
    # Send alert (email, Slack, etc.)
```

---

## 🚀 Deployment Checklist

### Pre-Deployment
- [ ] All migrations tested locally
- [ ] Celery worker running on server
- [ ] Redis container running
- [ ] Environment variables set (`GEMINI_API_KEY`, `REDIS_URL`)
- [ ] Database backup created
- [ ] API endpoints tested in Postman/Swagger

### Deployment Steps
1. **Backend:**
   ```bash
   git pull origin main
   alembic upgrade head
   pip install -r requirements.txt
   celery -A app.core.celery_app worker --loglevel=info --detach
   systemctl restart uvicorn
   ```

2. **Frontend:**
   ```bash
   cd frontend
   npm install
   npm run build
   systemctl restart next-app
   ```

3. **Verify:**
   - [ ] Upload test statement
   - [ ] Check Celery logs
   - [ ] Verify insights appear on dashboard
   - [ ] Check Gemini API usage in console

### Post-Deployment
- [ ] Monitor Celery worker logs for first 24 hours
- [ ] Check Gemini API costs daily for first week
- [ ] Gather user feedback
- [ ] Monitor error rates
- [ ] Adjust thresholds if needed

---

## 💰 Cost Estimates

### Infrastructure
- **Redis:** Free (Docker container on existing server)
- **Celery:** Free (open source)
- **Database:** No additional cost (existing PostgreSQL)

### AI API Costs
- **Gemini API:** $0.175 per insight
- **Expected Usage:**
  - 100 users × 1 statement/month = 100 insights/month
  - 100 × $0.175 = **$17.50/month**
  - Annual: **$210/year**

### Scaling Considerations
- At 1,000 users: $175/month
- At 10,000 users: $1,750/month
- Optimization: Cache insights, batch API calls, use cheaper models for simple insights

---

## 📚 Reference Links

### Documentation
- [Celery Documentation](https://docs.celeryq.dev/)
- [Gemini API Docs](https://ai.google.dev/docs)
- [Alembic Migrations](https://alembic.sqlalchemy.org/)
- [Framer Motion](https://www.framer.com/motion/)

### Internal Files
- Database Models: `app/models/insight.py`
- Services: `app/services/insights_orchestrator.py`
- API Router: `app/routers/insights.py`
- Frontend Components: `frontend/src/components/insights/`
- Frontend Page: `frontend/src/app/insights/page.tsx`

---

## 🎯 Success Criteria

**Week 1:** ✅ 1 insight working end-to-end
**Week 2:** ✅ 4 insights + /insights page live
**Week 3:** ✅ All 6 insights + AI integration
**Week 4:** ✅ Production deployment + monitoring

**Final Deliverable:**
- 6 insight types generating automatically
- Transaction linking working
- Dashboard + /insights page polished
- Async processing stable
- Cost under $20/month for 100 users
- User guide published

---

**Last Updated:** 2025-01-28
**Version:** 1.0
**Status:** Ready to Start Week 1
