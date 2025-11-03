# Cardora Frontend Development Roadmap

**Next.js 14+ App Router | shadcn/ui | TypeScript | Framer Motion**

---

## 📋 Table of Contents
1. [Backend API Reference](#backend-api-reference)
2. [Frontend Pages & Components](#frontend-pages--components)
3. [Implementation Phases](#implementation-phases)
4. [API Integration Map](#api-integration-map)
5. [Component Library](#component-library)
6. [State Management](#state-management)

---

## 🔌 Backend API Reference

### Base URL
```
Development: http://localhost:8000
Production: TBD
```

### Authentication Endpoints

#### 1. User Registration
```http
POST /auth/register
Content-Type: application/json

Request:
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe"
}

Response (201):
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "created_at": "2025-10-24T10:00:00Z"
}
```

#### 2. User Login
```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

Request:
username=user@example.com&password=SecurePass123!

Response (200):
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### 3. Get Current User
```http
GET /auth/me
Authorization: Bearer {access_token}

Response (200):
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "created_at": "2025-10-24T10:00:00Z"
}
```

---

### Credit Card Endpoints

#### 4. List All Cards
```http
GET /cards
Authorization: Bearer {access_token}

Response (200):
[
  {
    "id": 1,
    "user_id": 1,
    "card_name": "CITI Credit Card",
    "last_four_digits": "1234",
    "card_type": "credit",
    "bank_name": "Citibank",
    "credit_limit": 50000.00,
    "current_balance": 12345.67,
    "statement_date": 15,
    "due_date": 25,
    "created_at": "2025-10-24T10:00:00Z"
  }
]
```

#### 5. Get Single Card
```http
GET /cards/{card_id}
Authorization: Bearer {access_token}

Response (200):
{
  "id": 1,
  "user_id": 1,
  "card_name": "CITI Credit Card",
  "last_four_digits": "1234",
  "card_type": "credit",
  "bank_name": "Citibank",
  "credit_limit": 50000.00,
  "current_balance": 12345.67,
  "statement_date": 15,
  "due_date": 25,
  "created_at": "2025-10-24T10:00:00Z"
}
```

#### 6. Create Card
```http
POST /cards
Authorization: Bearer {access_token}
Content-Type: application/json

Request:
{
  "card_name": "HDFC Credit Card",
  "last_four_digits": "5678",
  "card_type": "credit",
  "bank_name": "HDFC Bank",
  "credit_limit": 100000.00,
  "statement_date": 10,
  "due_date": 20
}

Response (201):
{
  "id": 2,
  "user_id": 1,
  "card_name": "HDFC Credit Card",
  ...
}
```

#### 7. Update Card
```http
PUT /cards/{card_id}
Authorization: Bearer {access_token}
Content-Type: application/json

Request:
{
  "card_name": "HDFC Regalia",
  "credit_limit": 150000.00
}

Response (200):
{
  "id": 2,
  "card_name": "HDFC Regalia",
  "credit_limit": 150000.00,
  ...
}
```

#### 8. Delete Card
```http
DELETE /cards/{card_id}
Authorization: Bearer {access_token}

Response (200):
{
  "message": "Credit card deleted successfully"
}
```

---

### Transaction Endpoints

#### 9. List All Transactions
```http
GET /transactions
Authorization: Bearer {access_token}
Query Params:
  - skip: int (default: 0)
  - limit: int (default: 100)
  - card_id: int (optional)
  - category: str (optional)
  - start_date: date (optional)
  - end_date: date (optional)

Response (200):
[
  {
    "id": 1,
    "card_id": 1,
    "transaction_date": "2025-10-20",
    "description": "Amazon Purchase",
    "amount": 1234.56,
    "category": "Shopping",
    "merchant_name": "Amazon",
    "ai_confidence_score": 0.95,
    "created_at": "2025-10-24T10:00:00Z"
  }
]
```

#### 10. Get Single Transaction
```http
GET /transactions/{transaction_id}
Authorization: Bearer {access_token}

Response (200):
{
  "id": 1,
  "card_id": 1,
  "transaction_date": "2025-10-20",
  "description": "Amazon Purchase",
  "amount": 1234.56,
  "category": "Shopping",
  "merchant_name": "Amazon",
  "ai_confidence_score": 0.95,
  "created_at": "2025-10-24T10:00:00Z"
}
```

#### 11. Create Transaction (Manual)
```http
POST /transactions
Authorization: Bearer {access_token}
Content-Type: application/json

Request:
{
  "card_id": 1,
  "transaction_date": "2025-10-24",
  "description": "Coffee Shop",
  "amount": 450.00,
  "category": "Dining",
  "merchant_name": "Starbucks"
}

Response (201):
{
  "id": 67,
  "card_id": 1,
  "transaction_date": "2025-10-24",
  ...
}
```

#### 12. Update Transaction
```http
PUT /transactions/{transaction_id}
Authorization: Bearer {access_token}
Content-Type: application/json

Request:
{
  "category": "Entertainment",
  "description": "Updated description"
}

Response (200):
{
  "id": 67,
  "category": "Entertainment",
  ...
}
```

#### 13. Delete Transaction
```http
DELETE /transactions/{transaction_id}
Authorization: Bearer {access_token}

Response (200):
{
  "message": "Transaction deleted successfully"
}
```

---

### PDF Upload & AI Extraction

#### 14. Upload PDF Statement
```http
POST /upload
Authorization: Bearer {access_token}
Content-Type: multipart/form-data

Request:
{
  "file": <PDF file>,
  "card_id": 1  (optional - will auto-create if not provided)
}

Response (200):
{
  "message": "Statement processed successfully",
  "card_id": 1,
  "transactions_created": 66,
  "total_amount": 2087.62,
  "ai_confidence": 0.93,
  "categories_found": {
    "Groceries": 8,
    "Dining": 12,
    "Shopping": 15,
    "Transport": 10,
    ...
  },
  "card_details": {
    "id": 1,
    "card_name": "CITI Credit Card",
    "last_four_digits": "1234",
    ...
  }
}
```

---

### Analytics Endpoints (Future)

#### 15. Get Spending Summary
```http
GET /analytics/summary
Authorization: Bearer {access_token}
Query Params:
  - start_date: date
  - end_date: date
  - card_id: int (optional)

Response (200):
{
  "total_spending": 2087.62,
  "transaction_count": 66,
  "average_transaction": 31.63,
  "top_category": "Dining",
  "category_breakdown": {
    "Groceries": 450.00,
    "Dining": 680.50,
    ...
  },
  "monthly_trend": [
    { "month": "2025-10", "amount": 2087.62 }
  ]
}
```

#### 16. Get Category Insights
```http
GET /analytics/categories
Authorization: Bearer {access_token}

Response (200):
{
  "categories": [
    {
      "name": "Dining",
      "total": 680.50,
      "count": 12,
      "percentage": 32.6,
      "trend": "up",
      "avg_transaction": 56.71
    }
  ]
}
```

---

## 🎨 Frontend Pages & Components

### 1. Authentication Pages

#### `/login` - Login Page
**Purpose:** User authentication entry point

**Components:**
- `LoginForm` - Email/password form with validation
- `SocialLoginButtons` - Google/GitHub OAuth (future)
- `FeatureHighlight` - Split-screen feature showcase

**API Calls:**
- `POST /auth/login` - User authentication

**Features:**
- Form validation (email format, password strength)
- Error handling (invalid credentials, server errors)
- Loading states (button spinner)
- Redirect to dashboard on success
- "Remember me" functionality
- Forgot password link (future)

**Animations:**
- Split-screen parallax effect
- Gradient background animation (slow, ambient)
- Input focus transitions
- Button ripple effect on click
- Error message slide-in from top

---

#### `/register` - Sign Up Page
**Purpose:** New user registration

**Components:**
- `RegisterForm` - Full name, email, password fields
- `PasswordStrengthIndicator` - Real-time password validation
- `TermsCheckbox` - Accept terms and conditions

**API Calls:**
- `POST /auth/register` - Create new user account
- `POST /auth/login` - Auto-login after registration

**Features:**
- Real-time validation (email exists, password strength)
- Confirm password field
- Terms acceptance required
- Auto-login after successful registration
- Redirect to onboarding/dashboard

**Animations:**
- Stagger fade-in for form fields
- Password strength bar animation
- Success checkmark animation
- Smooth transition to dashboard

---

### 2. Dashboard Pages

#### `/dashboard` - Main Dashboard
**Purpose:** Overview of all financial activity

**Components:**
- `DashboardHeader` - Welcome message, search bar
- `StatCards` - 4 key metrics (Total Spending, Transactions, Cards, AI Accuracy)
- `SpendingTrendChart` - Line chart showing 6-month spending trend
- `CategoryBreakdownChart` - Doughnut chart of category distribution
- `RecentTransactionsList` - Last 10 transactions
- `CreditCardPreview` - Featured card with utilization bar

**API Calls:**
- `GET /auth/me` - User info for welcome message
- `GET /cards` - List all cards
- `GET /transactions?limit=10` - Recent transactions
- `GET /analytics/summary` - Dashboard stats (future)

**Features:**
- Real-time data updates
- Interactive charts (hover tooltips)
- Quick action buttons (Upload, Add Transaction)
- Card switching dropdown
- Date range selector (Last 7/30/90 days)
- Empty state for new users

**Animations:**
- Stat cards: Stagger fade-in from top (100ms delay each)
- Charts: Draw animation on load
- Transaction list: Slide in from right
- Card hover: Lift with shadow increase
- Number counters: Animate from 0 to final value

---

#### `/upload` - PDF Upload Page
**Purpose:** Upload and process credit card statements

**Components:**
- `UploadDropzone` - Drag & drop area with file validation
- `UploadProgressBar` - Multi-stage progress indicator
- `ExtractionResults` - Success summary with stats
- `AutoCreatedCard` - Display of newly created card
- `CategoryDistribution` - Visual breakdown of categories
- `ActionButtons` - View transactions, Upload another

**API Calls:**
- `POST /upload` - Upload PDF and extract transactions

**Features:**
- Drag & drop file upload
- File type validation (PDF only)
- File size validation (< 10MB)
- Multi-stage progress (Upload → Extract → AI Process)
- Real-time progress updates
- Detailed success summary
- Error handling (invalid PDF, extraction failures)
- Auto-navigation to transactions after success

**Animations:**
- Drag zone: Pulsing border when file is over
- Upload progress: Smooth width animation + color shift (blue → green)
- Success state: Confetti animation + scale bounce
- Results: Fade in with stagger for each stat
- Category bars: Width animation from 0 to percentage

---

#### `/cards` - Credit Cards List
**Purpose:** Manage all credit cards

**Components:**
- `CardGrid` - Grid layout of credit cards
- `CreditCardComponent` - Individual card with details
- `CardUtilizationBar` - Visual spending/limit ratio
- `AddCardButton` - Create new card modal trigger
- `CardStats` - Quick stats per card
- `CardActionsMenu` - Edit, Delete, View transactions

**API Calls:**
- `GET /cards` - List all cards
- `POST /cards` - Create new card
- `PUT /cards/{id}` - Update card
- `DELETE /cards/{id}` - Delete card

**Features:**
- Grid/list view toggle
- Sort by (Name, Balance, Limit)
- Filter by bank/type
- Search cards
- Add new card modal
- Edit card inline or modal
- Delete with confirmation
- View transactions per card

**Animations:**
- Card grid: Stagger fade-in (masonry layout)
- Card hover: Lift + shadow + subtle rotate
- Add card: Modal slide up from bottom
- Delete: Card fade out + collapse
- Utilization bar: Animate width on load

---

#### `/cards/[id]` - Single Card Detail
**Purpose:** Deep dive into one credit card

**Components:**
- `CardHero` - Large card visual with details
- `CardInsights` - Spending patterns, avg transaction
- `MonthlySpendingChart` - Line chart of spending over time
- `TransactionsList` - All transactions for this card
- `PaymentReminder` - Days until due date
- `CardSettings` - Edit limits, dates, etc.

**API Calls:**
- `GET /cards/{id}` - Card details
- `GET /transactions?card_id={id}` - Card transactions
- `PUT /cards/{id}` - Update card settings

**Features:**
- Visual card representation
- Spending insights (avg, peak, low)
- Monthly breakdown
- Transaction filtering
- Payment reminders
- Quick actions (Pay bill, Report lost)

**Animations:**
- Card 3D tilt on mouse move
- Chart: Line draw animation
- Insights: Count-up animations for numbers
- Transaction list: Virtualized scrolling

---

#### `/transactions` - All Transactions
**Purpose:** View and manage all transactions

**Components:**
- `TransactionsTable` - Sortable, filterable table
- `TransactionFilters` - Date range, category, card, amount
- `TransactionRow` - Individual transaction with actions
- `BulkActions` - Select multiple, categorize, delete
- `ExportButton` - Download CSV/Excel
- `TransactionDetails` - Expandable row with full details

**API Calls:**
- `GET /transactions` - List with filters
- `PUT /transactions/{id}` - Update transaction
- `DELETE /transactions/{id}` - Delete transaction

**Features:**
- Advanced filtering (multi-select, date ranges)
- Search by description/merchant
- Sort by date, amount, category
- Pagination or infinite scroll
- Bulk select and actions
- Edit category/description inline
- Delete with undo (5 second toast)
- Export to CSV/Excel

**Animations:**
- Table rows: Fade in on scroll (virtualized)
- Filters: Slide in from left
- Row hover: Background color transition
- Expandable details: Smooth height animation
- Bulk select: Checkbox bounce

---

#### `/transactions/[id]` - Single Transaction
**Purpose:** Edit and view transaction details

**Components:**
- `TransactionHeader` - Amount, date, merchant
- `TransactionForm` - Edit all fields
- `AIConfidenceIndicator` - Show AI extraction confidence
- `RelatedTransactions` - Similar transactions by merchant/category
- `ReceiptUpload` - Attach receipt image (future)

**API Calls:**
- `GET /transactions/{id}` - Transaction details
- `PUT /transactions/{id}` - Update transaction

**Features:**
- Edit all transaction fields
- AI confidence visualization
- Suggest similar categories
- Receipt attachment (future)
- Delete transaction
- View card details

**Animations:**
- Form: Slide in from right
- Save button: Success checkmark animation
- AI confidence: Progress bar animation
- Related items: Stagger fade-in

---

#### `/analytics` - Analytics Dashboard
**Purpose:** Financial insights and trends

**Components:**
- `SpendingOverview` - Total, avg, peak spending
- `CategoryInsights` - Breakdown by category with trends
- `MonthlyComparison` - Bar chart comparing months
- `TopMerchants` - Most frequent/expensive merchants
- `SavingsGoals` - Track spending vs goals (future)
- `ExportReports` - Generate PDF/Excel reports

**API Calls:**
- `GET /analytics/summary` - Overall stats
- `GET /analytics/categories` - Category insights
- `GET /transactions` - For custom charts

**Features:**
- Date range selector (custom, presets)
- Category deep-dive
- Merchant analysis
- Spending trends (up/down)
- Budget tracking (future)
- Export reports

**Animations:**
- Charts: Draw animations on load
- Stats: Count-up animations
- Trend arrows: Bounce in
- Category cards: Stagger fade-in

---

#### `/settings` - User Settings
**Purpose:** Manage account and preferences

**Components:**
- `ProfileSettings` - Name, email, password
- `NotificationSettings` - Email, push preferences
- `CategorySettings` - Customize categories, colors
- `ThemeToggle` - Light/dark mode
- `DataExport` - Download all data
- `DeleteAccount` - Permanent account deletion

**API Calls:**
- `GET /auth/me` - User profile
- `PUT /auth/profile` - Update profile (future)
- `PUT /auth/password` - Change password (future)

**Features:**
- Profile editing
- Password change with validation
- Email preferences
- Custom categories
- Theme switching
- Export user data
- Delete account with confirmation

**Animations:**
- Settings cards: Fade in on scroll
- Toggle switches: Smooth slide
- Save button: Success checkmark
- Delete confirmation: Modal shake effect

---

### 3. Utility Pages

#### `/404` - Not Found
**Components:**
- `ErrorMessage` - Friendly 404 message
- `NavigationLinks` - Quick links to main pages
- `SearchBar` - Search for what you're looking for

**Features:**
- Helpful error message
- Navigation suggestions
- Auto-redirect after 10 seconds

**Animations:**
- 404 number: Glitch effect
- Links: Fade in with stagger

---

#### `/500` - Server Error
**Components:**
- `ErrorMessage` - Server error explanation
- `RetryButton` - Retry the failed action
- `ContactSupport` - Link to support

**Features:**
- Clear error explanation
- Retry mechanism
- Contact support option

---

## 🏗️ Implementation Phases

### Phase 1: Foundation (Week 1)
**Goal:** Set up project structure, design system, authentication

**Tasks:**
- [x] Create Next.js 14 project with App Router
- [ ] Install dependencies (shadcn/ui, Framer Motion, Recharts)
- [ ] Configure Tailwind with custom theme
- [ ] Set up folder structure
- [ ] Create layout components (Header, Sidebar, Footer)
- [ ] Build design system components (Button, Input, Card, Badge)
- [ ] Implement authentication pages (Login, Register)
- [ ] Set up API client with Axios/fetch
- [ ] JWT token management (localStorage, auto-refresh)
- [ ] Protected route wrapper
- [ ] CORS configuration in FastAPI backend

**Deliverables:**
- Working login/register flow
- Protected routes
- Basic layout structure
- Design system components

---

### Phase 2: Core Features (Week 2)
**Goal:** Dashboard, PDF upload, cards management

**Tasks:**
- [ ] Build dashboard page with stat cards
- [ ] Integrate Recharts for spending trends
- [ ] Build doughnut chart for categories
- [ ] Fetch and display recent transactions
- [ ] Build upload page with drag-drop
- [ ] Implement file upload to `/upload` endpoint
- [ ] Show multi-stage progress bar
- [ ] Display extraction results
- [ ] Build cards list page
- [ ] Create card component with utilization
- [ ] Add/edit/delete card functionality
- [ ] Card detail page with insights

**Deliverables:**
- Functional dashboard with real data
- Working PDF upload with AI extraction
- Full card management

---

### Phase 3: Transactions & Analytics (Week 3)
**Goal:** Transaction management, analytics dashboard

**Tasks:**
- [ ] Build transactions table with filters
- [ ] Implement sorting, pagination
- [ ] Bulk actions (select, categorize, delete)
- [ ] Transaction detail page
- [ ] Edit transaction inline
- [ ] Build analytics dashboard
- [ ] Category insights with charts
- [ ] Monthly comparison bar chart
- [ ] Top merchants analysis
- [ ] Export to CSV/Excel functionality

**Deliverables:**
- Full transaction management
- Analytics dashboard with insights
- Export functionality

---

### Phase 4: Polish & PWA (Week 4)
**Goal:** Animations, dark mode, PWA, optimizations

**Tasks:**
- [ ] Add Framer Motion animations to all pages
- [ ] Implement dark mode toggle
- [ ] Create skeleton loaders for all pages
- [ ] Build empty states with illustrations
- [ ] Error boundary components
- [ ] Toast notifications system
- [ ] PWA setup (service worker, manifest)
- [ ] Offline fallback page
- [ ] Image optimization
- [ ] Code splitting and lazy loading
- [ ] Lighthouse optimization (95+ score)
- [ ] Accessibility audit (WCAG AA)

**Deliverables:**
- Fully animated, smooth UI
- Dark mode support
- PWA-ready application
- Lighthouse score 95+

---

## 🔗 API Integration Map

### Page → API Mapping

| Page | API Endpoints Used | Purpose |
|------|-------------------|---------|
| `/login` | `POST /auth/login` | User authentication |
| `/register` | `POST /auth/register` | Create account |
| `/dashboard` | `GET /auth/me`, `GET /cards`, `GET /transactions?limit=10` | Overview data |
| `/upload` | `POST /upload` | PDF statement processing |
| `/cards` | `GET /cards`, `POST /cards`, `PUT /cards/{id}`, `DELETE /cards/{id}` | Card CRUD |
| `/cards/[id]` | `GET /cards/{id}`, `GET /transactions?card_id={id}` | Card details |
| `/transactions` | `GET /transactions`, `PUT /transactions/{id}`, `DELETE /transactions/{id}` | Transaction CRUD |
| `/transactions/[id]` | `GET /transactions/{id}`, `PUT /transactions/{id}` | Transaction detail |
| `/analytics` | `GET /analytics/summary`, `GET /analytics/categories` | Insights (future) |
| `/settings` | `GET /auth/me` | User profile |

---

## 🧩 Component Library

### Core Components (shadcn/ui based)

#### Buttons
- `Button` - Primary, Secondary, Outline, Danger, Success, Ghost
- `IconButton` - Icon-only button
- `LoadingButton` - Button with loading spinner

#### Forms
- `Input` - Text, email, password, number
- `TextArea` - Multi-line text
- `Select` - Dropdown select
- `Checkbox` - Single checkbox
- `Radio` - Radio button group
- `Switch` - Toggle switch
- `DatePicker` - Date selection
- `FileUpload` - File input with drag-drop

#### Display
- `Card` - Base card container
- `StatCard` - Dashboard stat display
- `Badge` - Category, status badges
- `Avatar` - User profile image
- `Tooltip` - Hover info
- `Progress` - Progress bar
- `Skeleton` - Loading placeholder

#### Navigation
- `Header` - Top navigation bar
- `Sidebar` - Side navigation menu
- `Breadcrumb` - Page navigation trail
- `Tabs` - Tab navigation
- `Pagination` - Page navigation

#### Feedback
- `Toast` - Notification popup
- `Alert` - Inline message
- `Dialog` - Modal dialog
- `Popover` - Floating content
- `ConfirmDialog` - Confirmation prompt

#### Data Display
- `Table` - Data table
- `List` - Simple list
- `EmptyState` - No data placeholder
- `ErrorState` - Error display

#### Charts (Recharts)
- `LineChart` - Spending trends
- `BarChart` - Monthly comparison
- `DoughnutChart` - Category breakdown
- `AreaChart` - Filled trend chart

---

## 🗂️ State Management

### Approach: React Server Components + Client State

#### Server Components (Default)
- Dashboard data fetching
- Transaction lists
- Card lists
- Analytics data

#### Client Components (Interactive)
- Forms (Login, Register, Add Card)
- Drag-drop upload
- Charts with interactions
- Modals and dialogs
- Filters and search

#### State Libraries
- **React Context** - User auth state, theme
- **Zustand** (optional) - Global UI state (sidebar open, filters)
- **TanStack Query** (React Query) - Server state caching, auto-refetch

#### Data Flow
```
Server Component (RSC) → Fetch data → Render
    ↓
Client Component → Interactive UI → Mutations
    ↓
React Query → Cache + Optimistic Updates → Re-fetch
    ↓
Server Component → Updated data → Re-render
```

---

## 📦 Tech Stack Summary

### Frontend
- **Framework:** Next.js 14+ (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **Components:** shadcn/ui (Radix UI primitives)
- **Animations:** Framer Motion
- **Charts:** Recharts
- **Icons:** Lucide React
- **Forms:** React Hook Form + Zod validation
- **HTTP Client:** Axios or native fetch
- **State:** React Context + TanStack Query
- **PWA:** next-pwa plugin

### Backend (Existing)
- **Framework:** FastAPI
- **Language:** Python 3.10+
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Migrations:** Alembic
- **Auth:** JWT (jose)
- **AI:** Claude API (Anthropic)
- **PDF:** PyMuPDF

---

## 🎯 Success Metrics

### Performance
- [ ] Lighthouse Score: 95+ (all categories)
- [ ] First Contentful Paint: < 1.2s
- [ ] Time to Interactive: < 2.5s
- [ ] Cumulative Layout Shift: < 0.1
- [ ] No frame drops (60fps animations)

### Design
- [ ] Consistent 8px spacing grid
- [ ] WCAG AA color contrast (4.5:1)
- [ ] No orphaned UI elements
- [ ] Proper visual hierarchy
- [ ] Smooth, delightful animations

### Code Quality
- [ ] 100% TypeScript (no `any`)
- [ ] Reusable components (DRY)
- [ ] Comprehensive error handling
- [ ] Proper loading states
- [ ] Accessibility features (ARIA labels)

---

**Last Updated:** 2025-10-24
**Version:** 1.0.0
