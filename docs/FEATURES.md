# Cardora — Feature Roadmap

> Credit card statement analyzer for the Singapore market.  
> Users upload PDF statements; Gemini AI extracts transactions, categorizes spending, and surfaces financial insights.

---

## Current Features

### Authentication & User Management
- Email + password signup and login (JWT-based)
- Password reset via email
- User profile (full name, email)
- Full data export (JSON)
- Account deletion with cascade cleanup

### Credit Card Management
- Add, edit, and delete credit cards
- Stores bank name, card type, credit limit, and last 4 digits
- All cards scoped per user

### PDF Statement Upload & AI Extraction
- Upload PDF credit card statements
- Gemini AI parses the PDF and extracts individual transactions
- Extracts: merchant name, amount, transaction date, description
- Runs as a background task — upload returns immediately
- Statement history with month/year tracking

### Transaction Management
- View all extracted transactions across cards
- Edit transaction details (merchant, amount, category, date)
- Delete transactions
- Transactions linked to the originating card and statement

### Spending Categorization
- 21 built-in system categories (Dining, Transport, Shopping, Groceries, etc.)
- User-created custom categories
- Gemini assigns a category at extraction time
- Users can manually override the category on any transaction

### Analytics
- Total spending across any time range
- Monthly spend trend charts
- Per-card spending breakdowns
- Category-wise spending with donut/bar charts
- Average monthly spend
- AI confidence score (categorization accuracy)
- Filters: time range selector, specific month/year picker, card selector

### Payment Health
- Detects payment status from statement data (paid in full / partial / minimum only)
- Shows monthly interest cost and projected annual interest cost
- Displays APR and revolving balance
- Dismissible per-user alerts
- **Payoff Calculator** — enter balance, APR, and monthly payment to see:
  - Months to pay off
  - Total interest paid
  - Total amount paid
  - Estimated payoff date

---

## Potential Next Features

### High Impact / Build Next

#### Budgets
Set monthly spending limits per category. Get a visual indicator when approaching or exceeding a budget. Simple model: `user_id + category_id + amount + month`.

#### Recurring Transaction Detection
Automatically flag transactions that appear every month at a similar amount (subscriptions, rent, insurance). Let users label them and see a "fixed expenses" total separate from discretionary spend.

#### Due Date Reminders
Store payment due dates per card. Send email reminders 3 days and 1 day before the due date. Prevents missed payments and late fees — directly useful for Singapore users managing multiple cards.

#### Multi-Card Payoff Planner
Extend the existing single-card payoff calculator to handle multiple cards simultaneously. Implement avalanche (highest APR first) and snowball (lowest balance first) strategies and show which saves more interest.

#### Spending Goals
Let users set a monthly spending goal (e.g., "spend under $2,000 this month"). Show progress in the dashboard with a simple progress bar and remaining amount.

---

### Medium Impact / Plan After Above

#### Statement Health Score
A single 0–100 score per statement based on: payment behavior, credit utilization, spend vs. last month, and category diversity. Gives users a quick "how am I doing?" snapshot.

#### Merchant Intelligence
Build a lookup table of common Singapore merchants → category mappings. Reduce reliance on Gemini for well-known merchants (FairPrice, Grab, Lazada) and improve categorization accuracy for free.

#### CSV / Excel Export
Export filtered transactions to CSV or Excel. Useful for users who want to do their own analysis in Google Sheets or report expenses to an employer.

#### Year-in-Review Report
A generated annual summary: total spent, top categories, top merchants, best and worst months, biggest single transaction. Delivered as a shareable PDF or in-app page.

#### Shared Card Support
Allow two users to link the same card (e.g., a couple sharing a supplementary card). Transactions from the same statement can be split-attributed. Requires careful multi-tenancy design.

---

### Longer Term / Explore Later

#### Bank Statement Auto-Fetch (Open Banking)
Integrate with Singapore Open Banking APIs (once available) or screen-scraping solutions to auto-pull statements without manual PDF upload.

#### AI Spending Coach
A conversational interface where users ask natural language questions: "Where did I spend the most last quarter?" or "How much did I spend on food in March?" Powered by Gemini with transaction data as context.

#### Credit Utilization Tracker
Pull credit limit and current balance per card to calculate utilization ratio. Alert users when utilization exceeds 30% (the recommended threshold for credit score health).

#### Tax Category Tagging
Allow users to tag transactions as tax-deductible (business meals, home office supplies, professional development). Generate a filtered export at tax time.

#### Notification Center
In-app notification feed for: new statement processed, budget exceeded, payment due, payoff milestone reached. Upgradeable to push notifications or WhatsApp alerts.

---

## Feature Status Summary

| Feature | Status |
|---|---|
| Auth & user management | Live |
| Credit card CRUD | Live |
| PDF upload & AI extraction | Live |
| Transaction management | Live |
| Spending categorization | Live |
| Analytics dashboard | Live |
| Payment health alerts | Live |
| Payoff calculator | Live |
| Budgets | Planned |
| Recurring transaction detection | Planned |
| Due date reminders | Planned |
| Multi-card payoff planner | Planned |
| Spending goals | Planned |
| Statement health score | Backlog |
| Merchant intelligence | Backlog |
| CSV/Excel export | Backlog |
| Year-in-review report | Backlog |
| Shared card support | Backlog |
| Open banking integration | Future |
| AI spending coach | Future |
| Credit utilization tracker | Future |
| Tax category tagging | Future |
| Notification center | Future |
