# Payment Notification System - Implementation Plan

**Status**: Planned (Not Yet Implemented)
**Priority**: High
**Last Updated**: 2025-11-03

## Overview

This document outlines the comprehensive plan for implementing a payment notification system that alerts users when they haven't paid their full credit card balance, calculates interest costs, warns about credit card debt dangers, and provides actionable advice.

## Current Implementation Status

### What's Already Built ✓

1. **Interest Calculations** - Fully working
   - `estimated_monthly_interest` = `revolving_balance * (apr / 12 / 100)`
   - `estimated_annual_cost` = `estimated_monthly_interest * 12`
   - Location: `app/features/statements/models.py:339-355`

2. **Payment Status Tracking** - Data model ready
   - Fields: `payment_status`, `amount_paid`, `minimum_payment_due`, `statement_balance`
   - APR, interest charged, fees all tracked
   - Location: `app/features/statements/models.py:264-365`

3. **Payment Alert Framework** - Built but disabled
   - Alert types: "paid_full", "partial_paid", "below_minimum", "no_payment"
   - Severity levels and recommendations field exists
   - Currently commented out in: `app/features/statements/router.py:434-488`

### What's Missing ✗

1. **Payment Detection Module** - Not implemented
   - The code references `app/services/payment_detection.py` but this file doesn't exist
   - This would compare statements to detect if user paid full/partial/minimum

2. **Active Notifications** - Disabled
   - The alert generation code is commented out with note: "Disabled for now - payment_detection module not yet implemented"

3. **Debt Education Content** - Not generated
   - No warnings about credit card debt dangers
   - No advice on how to fix debt situation

4. **Frontend UI** - Not connected
   - Alert display components exist but aren't receiving payment alerts

---

## Notification Flow Architecture

### 1. Trigger Point: New Statement Upload

```
User uploads PDF → AI extracts data → Statement saved to DB → Payment Detection triggered
```

**Location**: `app/features/statements/router.py:119` (after statement creation)

### 2. Payment Detection Logic

When a new statement is created, the system:

1. **Fetches previous statement** for the same credit card
2. **Compares key fields**:
   - Previous statement's `statement_balance` vs Current statement's `payments_credits`
   - Determines if user paid: Full / Partial / Minimum / Nothing

3. **Calculates financial impact**:
   - Interest accrued this cycle (`interest_charged`)
   - Projected monthly interest if balance continues (`estimated_monthly_interest`)
   - Annual cost (`estimated_annual_cost`)

**Location**: New file `app/features/payments/services.py`

### 3. Alert Generation

Based on payment behavior, create alerts with different severity:

| Payment Behavior | Alert Type | Severity | Content |
|-----------------|------------|----------|---------|
| Paid Full | Success notification | Low | "Great job! No interest charged" |
| Paid > Minimum | Warning | Medium | Shows interest cost + yearly projection |
| Paid = Minimum | Warning | High | Shows debt trap danger + suggestions |
| Paid < Minimum | Critical | Critical | Late fee warning + urgent action needed |
| No Payment | Critical | Critical | Account status at risk + immediate steps |

**Location**: `app/features/insights/services.py` (create payment alerts)

### 4. Notification Storage

Alerts stored in `payment_alerts` table with:
- Type (payment_warning, debt_education, etc.)
- Title & Description
- Amount owed
- Interest calculations
- Due date
- Actionable recommendations
- `is_dismissed` flag

**Location**: Database via `app/features/insights/models.py:314` (PaymentAlert model)

### 5. Frontend Display

**Multiple touchpoints**:

#### A. Dashboard Alert Banner (Top priority)
```
Location: Dashboard page
Shows: Active payment alerts for cards with upcoming due dates
Style: Color-coded by severity (yellow/orange/red)
Action: Click to see full details
```

#### B. Statement Detail Page
```
Location: When viewing a specific statement
Shows: Payment status for that statement
      Interest calculation breakdown
      Comparison: "If you paid full vs minimum"
```

#### C. Insights/Notifications Center
```
Location: Dedicated notifications page
Shows: All payment alerts (active + dismissed)
        Educational content about debt management
Filter: By card, by severity, by date
```

#### D. Card Overview Page
```
Location: Credit card list view
Shows: Badge/indicator on cards with unpaid balances
       Quick stats: Current debt, monthly interest cost
```

### 6. Educational Content Delivery

When alert severity is Medium/High/Critical, include:

**Debt Education Module**:
- 📊 Visual breakdown: Principal vs Interest over time
- ⚠️ Warning: "At current minimum payment, you'll pay $X in interest"
- 💡 Recommendation: "Pay $Y extra to save $Z in interest"
- 🎯 Payoff calculator: "Pay off in X months by paying $Y/month"
- 📚 Resources: Links to debt management strategies

**Location**: Frontend component + Backend generates personalized content

---

## Detailed Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. USER UPLOADS STATEMENT PDF                                   │
└───────────────────────────┬─────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. AI EXTRACTION (Gemini)                                       │
│    - statement_balance: $2,500                                  │
│    - minimum_payment: $50                                       │
│    - interest_charged: $35                                      │
│    - apr: 18.99%                                                │
│    - due_date: 2025-01-15                                       │
└───────────────────────────┬─────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. SAVE TO DATABASE                                             │
│    Statement created with all fields                            │
└───────────────────────────┬─────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. PAYMENT DETECTION SERVICE (Async Task)                       │
│                                                                  │
│    A. Fetch previous statement for same card                    │
│       Previous balance: $2,000                                  │
│                                                                  │
│    B. Check current statement's "payments_credits"              │
│       Amount paid: $50                                          │
│                                                                  │
│    C. Calculate payment behavior:                               │
│       $50 paid = Minimum only                                   │
│       $1,950 balance carried forward                            │
│       $35 interest charged THIS cycle                           │
│                                                                  │
│    D. Calculate future costs:                                   │
│       Monthly interest: $2,500 × (18.99% / 12) = $39.56       │
│       Annual cost: $39.56 × 12 = $474.72                       │
│       Payoff time at min payment: 94 months                    │
│       Total interest over payoff: $2,200                       │
└───────────────────────────┬─────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. GENERATE PAYMENT ALERT                                       │
│                                                                  │
│    alert_type: "payment_warning"                                │
│    severity: "high"                                             │
│    title: "⚠️ Minimum Payment Only - Interest Adding Up"       │
│    description: "You paid $50 (minimum) on your $2,500        │
│                  balance. Interest charged: $35 this cycle."   │
│                                                                  │
│    financial_breakdown: {                                       │
│      "current_balance": 2500,                                   │
│      "interest_this_cycle": 35,                                 │
│      "monthly_interest_projection": 39.56,                      │
│      "annual_cost": 474.72,                                     │
│      "months_to_payoff_at_minimum": 94,                        │
│      "total_interest_if_minimum": 2200                         │
│    }                                                            │
│                                                                  │
│    recommendations: [                                           │
│      "Pay $200/month to pay off in 15 months (save $1,800)",  │
│      "Pay $300/month to pay off in 9 months (save $2,000)",   │
│      "Consider balance transfer to 0% APR card"                │
│    ]                                                            │
│                                                                  │
│    education_content: {                                         │
│      "debt_warning": "Credit card debt compounds daily...",    │
│      "minimum_trap": "Minimum payments barely cover interest", │
│      "action_steps": ["Create budget", "Pay more than min"]   │
│    }                                                            │
└───────────────────────────┬─────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. SAVE ALERT TO DATABASE                                       │
│    payment_alerts table                                         │
│    linked to: statement_id, credit_card_id, user_id            │
└───────────────────────────┬─────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. FRONTEND NOTIFICATION                                        │
│                                                                  │
│    ┌──────────────────────────────────────────────────────┐   │
│    │ 🔔 Dashboard Banner (Top)                            │   │
│    │ ⚠️ You have 1 payment alert for Chase Sapphire      │   │
│    │ Due: Jan 15 | Balance: $2,500 | Click to view       │   │
│    └──────────────────────────────────────────────────────┘   │
│                                                                  │
│    ┌──────────────────────────────────────────────────────┐   │
│    │ 📊 Statement Detail Page                             │   │
│    │                                                        │   │
│    │ ⚠️ Payment Analysis                                  │   │
│    │ You paid: $50 (Minimum only)                         │   │
│    │                                                        │   │
│    │ 💰 Interest Breakdown:                               │   │
│    │ • This cycle: $35                                    │   │
│    │ • Next month (projected): $39.56                     │   │
│    │ • Annual cost: $474.72                               │   │
│    │                                                        │   │
│    │ ⏰ At this rate:                                     │   │
│    │ • Payoff time: 94 months (7.8 years)                │   │
│    │ • Total interest: $2,200                             │   │
│    │                                                        │   │
│    │ 💡 Better Options:                                   │   │
│    │ [View Recommendations] [Create Payment Plan]        │   │
│    └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## API Endpoints

### Existing (to modify)
- `POST /api/statements/` → Add payment detection trigger after save

### New Endpoints
- `GET /api/insights/payment-alerts` → Get active alerts for user
- `GET /api/insights/payment-alerts/{card_id}` → Get alerts for specific card
- `PUT /api/insights/payment-alerts/{alert_id}/dismiss` → Dismiss alert
- `POST /api/insights/calculate-payoff` → Calculate custom payoff scenarios

---

## User Experience Examples

### Scenario 1: User Paid Full Balance
```
✓ Great Job! Statement paid in full
Balance: $0 | Interest: $0
Keep it up to avoid interest charges!
[Dismiss]
```

### Scenario 2: User Paid Only Minimum
```
⚠️ Minimum Payment Only - Interest Is Adding Up

Balance: $2,500
Interest this month: $35
Annual cost at this rate: $474.72

⚠️ Debt Warning:
At minimum payments only, it will take 94 months to pay off
and you'll pay $2,200 in interest.

💡 How to Fix It:
• Pay $200/month → Pay off in 15 months, save $1,800
• Pay $300/month → Pay off in 9 months, save $2,000
• Consider a balance transfer to 0% APR

[Create Payment Plan] [Learn More] [Dismiss]
```

### Scenario 3: No Payment Made
```
🚨 CRITICAL: No Payment Detected

Your Chase Sapphire statement is overdue!
Due Date: Jan 15, 2025 (3 days ago)
Amount Due: $50 (minimum)
Total Balance: $2,500

⚠️ Consequences:
• Late fee: $39 (likely charged next cycle)
• Credit score impact
• Possible APR increase

🎯 Take Action Now:
[Pay Online] [Set Up Autopay] [Contact Support]
```

---

## Technical Implementation Order

### Phase 1: Backend Core (Payment Detection)
1. Create `app/features/payments/services.py`
   - `detect_payment_behavior(statement_id)` function
   - `get_previous_statement(card_id, statement_date)` function
   - Payment comparison logic

2. Create `app/features/payments/calculations.py`
   - `calculate_payoff_schedule(balance, apr, monthly_payment)` function
   - `calculate_interest_savings(balance, apr, extra_payment)` function
   - `generate_payment_recommendations(statement)` function

### Phase 2: Backend Alert System
3. Modify `app/features/statements/router.py`
   - Uncomment alert generation code (lines 434-488)
   - Add call to payment detection service after statement creation
   - Integrate alert creation with payment detection

4. Create `app/features/insights/alert_service.py`
   - `create_payment_alert(statement, payment_behavior)` function
   - Alert content generation based on severity
   - Educational content integration

### Phase 3: Backend API
5. Add endpoints to `app/features/insights/router.py`
   - `GET /api/insights/payment-alerts`
   - `GET /api/insights/payment-alerts/{card_id}`
   - `PUT /api/insights/payment-alerts/{alert_id}/dismiss`
   - `POST /api/insights/calculate-payoff`

### Phase 4: Frontend Components
6. Create alert components
   - `PaymentAlertBanner.tsx` (dashboard top banner)
   - `PaymentAnalysisCard.tsx` (statement detail)
   - `PayoffCalculator.tsx` (interactive calculator)
   - `DebtEducationModule.tsx` (educational content)

7. Create notification center
   - `NotificationCenter.tsx` (dedicated page)
   - Alert filtering and sorting
   - Dismiss functionality

### Phase 5: Frontend Integration
8. Integrate into existing pages
   - Dashboard: Add alert banner
   - Statement detail: Add payment analysis card
   - Card overview: Add debt indicators
   - Navigation: Add notification badge

### Phase 6: Testing & Polish
9. End-to-end testing
   - Test all payment scenarios
   - Verify calculations
   - Test notification display
   - Test dismissal and persistence

10. UI/UX polish
    - Visual design refinement
    - Responsive design
    - Accessibility improvements
    - Performance optimization

---

## Data Models

### Payment Alert (Existing)
```python
# app/features/insights/models.py:314-421
class PaymentAlert(Base):
    id: UUID
    user_id: UUID
    credit_card_id: UUID
    statement_id: UUID
    alert_type: str  # payment_due, subscription_renewal, unusual_charge
    title: str
    description: str
    due_date: datetime
    amount: Decimal
    dismissed_at: datetime | None
    created_at: datetime
```

### Statement (Existing - Payment Fields)
```python
# app/features/statements/models.py:198-365
class Statement(Base):
    # Balance fields
    statement_balance: Decimal
    minimum_payment_due: Decimal
    previous_balance: Decimal
    new_charges: Decimal
    payments_credits: Decimal

    # Interest & fees
    interest_charged: Decimal
    fees_charged: Decimal
    apr: Decimal

    # Payment tracking
    payment_status: str  # pending/paid_full/partial_paid/minimum_paid/late/unknown
    amount_paid: Decimal | None

    # Calculations
    revolving_balance: Decimal
    estimated_monthly_interest: Decimal
    estimated_annual_cost: Decimal

    # Dates
    statement_date: datetime
    due_date: datetime
    days_until_due: int
```

---

## Educational Content Structure

### Debt Warning Messages

**Level 1: Informational (Paid > Minimum)**
- "You're paying more than the minimum - good progress!"
- Interest cost breakdown
- Savings projection if paid more

**Level 2: Warning (Paid = Minimum)**
- "Minimum payments keep you in debt longer"
- Real cost example: "$2,500 debt at 18.99% APR takes 94 months to pay off at minimum"
- "You'll pay $2,200 in interest - nearly doubling your debt"

**Level 3: Critical (Paid < Minimum or No Payment)**
- "Immediate action required to avoid penalties"
- Late fee amounts
- Credit score impact warning
- "Contact your card issuer if you're struggling to make payments"

### Action Steps by Scenario

**For High Balance Carriers:**
1. Create a budget to identify extra payment capacity
2. Consider the debt avalanche method (highest APR first)
3. Explore balance transfer options to 0% APR cards
4. Calculate your debt-free date with increased payments

**For Late Payers:**
1. Set up autopay for at least minimum payment
2. Schedule payment reminders 5 days before due date
3. Contact card issuer to discuss hardship programs
4. Review spending to ensure payment capacity

**For Partial Payers:**
1. Review budget to find extra $X per month
2. Calculate interest savings with increased payment
3. Set payment goals: "Be debt-free by [date]"
4. Track progress monthly

---

## Metrics to Track

### System Metrics
- Alerts generated per day/week
- Alert types distribution
- Alert dismissal rate
- Time to dismiss

### User Behavior Metrics
- Payment behavior changes after alerts
- Full payment rate before/after implementation
- Average balance reduction
- User engagement with educational content

### Financial Impact
- Total interest saved by users
- Average payoff time improvement
- Percentage of users paying more than minimum

---

## Future Enhancements

1. **Predictive Alerts**
   - Predict when user might miss payment based on spending patterns
   - Alert before due date if balance is growing

2. **Automated Payment Plans**
   - Generate custom payment schedules
   - Track progress toward payoff goals
   - Celebrate milestones

3. **Integration with Payment Systems**
   - Direct payment from Cardora interface
   - Scheduled payments
   - Split payments across pay periods

4. **Social Features**
   - Anonymous debt payoff success stories
   - Community challenges
   - Accountability partners

5. **Advanced Analytics**
   - Debt-to-income ratio tracking
   - Credit utilization impact
   - Net worth impact of debt reduction

---

## Security Considerations

1. **Data Privacy**
   - Payment alerts contain sensitive financial data
   - Ensure proper access controls
   - Encrypt alert content in database

2. **Alert Fatigue**
   - Don't over-alert users
   - Allow customization of alert frequency
   - Smart dismissal (don't repeat same alert for same cycle)

3. **Accuracy**
   - Verify payment detection logic thoroughly
   - Handle edge cases (refunds, credits, disputes)
   - Clearly label estimates vs actual amounts

---

## Success Criteria

1. **Technical Success**
   - Payment detection accuracy > 95%
   - Alert generation within 1 minute of statement upload
   - Zero false positives on "no payment" alerts

2. **User Success**
   - 70%+ of users engage with alerts (don't dismiss immediately)
   - 30%+ of users click through to educational content
   - Measurable increase in full payment rate

3. **Business Success**
   - Positive user feedback on feature
   - Increased user retention (users find value)
   - Positions Cardora as financial wellness tool

---

## References

- Statement Model: `app/features/statements/models.py:198-365`
- Payment Alert Model: `app/features/insights/models.py:314-421`
- Disabled Alert Code: `app/features/statements/router.py:434-488`
- AI Extraction: `app/core/gemini_service.py:316-452`
