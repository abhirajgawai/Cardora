# Cardora Project Structure

This document explains the current organization of the Cardora codebase using **feature-based architecture**.

## Directory Structure

```
E:\Cardora/
│
├── app/                                # Backend (FastAPI + SQLAlchemy)
│   ├── core/                           # Core infrastructure
│   │   ├── config.py                   # App configuration (Pydantic Settings)
│   │   ├── database.py                 # Database connection & session
│   │   ├── email_service.py            # Email functionality
│   │   ├── gemini_service.py           # AI/PDF processing with Google Gemini
│   │   └── seed_data.py                # Database seeding
│   │
│   ├── features/                       # Feature-based modules
│   │   ├── analytics/                  # Spending analytics
│   │   │   ├── router.py               # Analytics endpoints
│   │   │   └── schemas.py              # Analytics DTOs
│   │   │
│   │   ├── auth/                       # Authentication & authorization
│   │   │   ├── auth.py                 # Auth utilities
│   │   │   ├── jwt.py                  # JWT handling
│   │   │   ├── models.py               # User model
│   │   │   ├── password.py             # Password hashing
│   │   │   ├── password_reset.py       # Password reset logic
│   │   │   ├── router.py               # Auth endpoints
│   │   │   ├── schemas.py              # Auth DTOs
│   │   │   └── users.py                # User management
│   │   │
│   │   ├── cards/                      # Credit card management
│   │   │   ├── models.py               # Card model
│   │   │   ├── router.py               # Card endpoints
│   │   │   └── schemas.py              # Card DTOs
│   │   │
│   │   ├── categories/                 # Transaction categories
│   │   │   ├── models.py               # Category model
│   │   │   ├── router.py               # Category endpoints
│   │   │   └── schemas.py              # Category DTOs
│   │   │
│   │   ├── insights/                   # AI-powered spending insights
│   │   │   ├── generators/             # Individual insight generators
│   │   │   │   ├── recurring_habit.py
│   │   │   │   ├── smart_spending_praise.py
│   │   │   │   ├── subscription_detection.py
│   │   │   │   ├── transport_savings.py
│   │   │   │   └── weekend_spending.py
│   │   │   ├── ai_insights.py          # AI insight generation
│   │   │   ├── models.py               # Insight & PaymentAlert models
│   │   │   ├── router.py               # Insight endpoints
│   │   │   └── statistics_engine.py    # Statistics computation
│   │   │
│   │   ├── statements/                 # Credit card statement upload/processing
│   │   │   ├── models.py               # Statement model
│   │   │   ├── router.py               # Statement endpoints
│   │   │   └── schemas.py              # Statement DTOs
│   │   │
│   │   └── transactions/               # Transaction management
│   │       ├── models.py               # Transaction model
│   │       ├── router.py               # Transaction endpoints
│   │       └── schemas.py              # Transaction DTOs
│   │
│   ├── shared/                         # Shared configurations
│   │   ├── insights_config.py          # Insight generation configs
│   │   └── merchant_categories.py      # Merchant categorization rules
│   │
│   └── main.py                         # FastAPI application entry point
│
├── frontend/                           # Frontend (Next.js 14+ with TypeScript)
│   ├── src/
│   │   ├── app/                        # Next.js App Router (pages)
│   │   │   ├── analytics/              # Analytics page
│   │   │   ├── cards/                  # Cards management page
│   │   │   ├── dashboard/              # Dashboard page
│   │   │   ├── insights/               # Insights page
│   │   │   ├── login/                  # Login page
│   │   │   ├── register/               # Registration page
│   │   │   ├── transactions/           # Transactions page
│   │   │   ├── upload/                 # Upload page
│   │   │   ├── layout.tsx              # Root layout
│   │   │   └── page.tsx                # Home page
│   │   │
│   │   ├── features/                   # Feature-based modules (mirrors backend)
│   │   │   ├── analytics/
│   │   │   │   └── types/              # Analytics types
│   │   │   ├── auth/
│   │   │   │   ├── api/                # Auth API client
│   │   │   │   ├── models/             # User model
│   │   │   │   └── types/              # Auth types
│   │   │   ├── cards/
│   │   │   │   ├── api/                # Cards API client
│   │   │   │   ├── models/             # Card model
│   │   │   │   └── types/              # Card types
│   │   │   ├── dashboard/
│   │   │   │   └── index.ts
│   │   │   ├── insights/
│   │   │   │   ├── api/                # Insights API client
│   │   │   │   ├── components/         # Insight components
│   │   │   │   └── types/              # Insight types
│   │   │   ├── statements/
│   │   │   │   ├── api/                # Statements API client
│   │   │   │   ├── components/         # Upload components
│   │   │   │   ├── models/             # Statement model
│   │   │   │   └── types/              # Statement types
│   │   │   └── transactions/
│   │   │       ├── api/                # Transactions API client
│   │   │       ├── models/             # Transaction & Category models
│   │   │       └── types/              # Transaction types
│   │   │
│   │   └── shared/                     # Shared resources
│   │       ├── components/
│   │       │   ├── common/             # Reusable components
│   │       │   ├── layout/             # Layout components
│   │       │   └── ui/                 # shadcn/ui components
│   │       ├── contexts/               # React contexts
│   │       ├── lib/
│   │       │   ├── api/                # Base API client
│   │       │   └── utils/              # Utility functions
│   │       └── types/                  # Shared types
│   │
│   ├── public/                         # Static assets
│   ├── .env.local                      # Frontend environment variables
│   ├── next.config.ts                  # Next.js configuration
│   ├── package.json                    # Dependencies
│   └── tsconfig.json                   # TypeScript configuration
│
├── alembic/                            # Database migrations (Alembic)
│   ├── versions/                       # Migration versions
│   └── env.py                          # Alembic configuration
│
├── tests/                              # Backend tests
│   ├── test_*.py                       # Various test files
│   └── README.md                       # Test documentation
│
├── uploads/                            # Uploaded PDF statements (gitignored)
│
├── docs/                               # Documentation
│   ├── architecture/                   # Architecture docs
│   ├── features/                       # Feature-specific docs
│   ├── guides/                         # How-to guides
│   └── planning/                       # Planning & roadmaps
│
├── venv/                               # Python virtual environment
│
├── .env                                # Backend environment variables (gitignored)
├── .env.example                        # Environment template
├── .gitignore                          # Git ignore rules
├── alembic.ini                         # Alembic configuration
├── requirements.txt                    # Python dependencies
└── README.md                           # Project README
```

## Architecture Principles

### Feature-Based Organization

Both backend and frontend follow **feature-based architecture**:

**Benefits:**
- ✅ **Colocation**: All code for a feature lives together
- ✅ **Consistency**: Backend and frontend mirror each other
- ✅ **Discoverability**: Easy to find all code related to a feature
- ✅ **Scalability**: Easy to add new features without touching existing ones
- ✅ **Team Collaboration**: Features can be developed independently

**Pattern:**
```
feature/
├── models.py        # Database models (backend only)
├── schemas.py       # Request/response DTOs (backend only)
├── router.py        # API endpoints (backend only)
├── api/             # API client (frontend only)
├── components/      # React components (frontend only)
├── types/           # TypeScript types (frontend only)
└── index.ts         # Barrel exports (frontend only)
```

## Compare to .NET Project Structure

```
.NET Clean Architecture:
Cardora/
├── Cardora.API/
│   └── Features/              → app/features/
│       ├── Auth/
│       ├── Cards/
│       └── Transactions/
│
├── Cardora.Core/              → app/core/
│   ├── Entities/              → models.py in each feature
│   └── Interfaces/
│
├── Cardora.Infrastructure/    → app/core/
│   └── Persistence/           → database.py
│
└── Cardora.Tests/             → tests/
```

## Key Technologies

### Backend
- **FastAPI** - Modern Python web framework (like ASP.NET Core)
- **SQLAlchemy** - ORM (like Entity Framework Core)
- **PostgreSQL** - Database
- **Alembic** - Database migrations (like EF Migrations)
- **Pydantic** - Data validation (like DataAnnotations)
- **Google Gemini** - AI for PDF processing

### Frontend
- **Next.js 14+** - React framework with App Router
- **TypeScript** - Type safety
- **shadcn/ui** - UI component library
- **TailwindCSS** - Utility-first CSS
- **Axios** - HTTP client

## Feature Overview

### 1. Authentication (`auth/`)
- User registration and login
- JWT token-based authentication
- Password hashing with bcrypt
- Password reset functionality
- Protected routes

### 2. Cards (`cards/`)
- Credit card management
- Card creation, editing, deletion
- Multiple cards per user
- Card metadata (bank, name, last 4 digits)

### 3. Statements (`statements/`)
- PDF statement upload
- AI-powered PDF processing (Gemini)
- Transaction extraction from PDFs
- Processing status tracking

### 4. Transactions (`transactions/`)
- Transaction CRUD operations
- Categorization
- Filtering and search
- Bulk operations
- CSV export

### 5. Categories (`categories/`)
- System categories (21 default)
- Custom user categories
- Category icons and colors
- Category-based analytics

### 6. Analytics (`analytics/`)
- Monthly spending analysis
- Month-to-month comparisons
- Multi-month trend analysis
- Annual reports
- Per-card and per-category breakdowns

### 7. Insights (`insights/`)
- AI-generated spending insights
- Pattern detection (recurring, weekend, subscriptions)
- Smart spending praise
- Transport savings detection
- Payment due alerts

## Database Schema

### Custom Schema: `cardora`

All tables are in the `cardora` schema (not `public`).

**Tables:**
- `users` - User accounts
- `credit_cards` - Credit cards
- `statements` - Uploaded statements
- `transactions` - Transaction records
- `categories` - Transaction categories
- `insights` - Generated insights
- `payment_alerts` - Payment due alerts

**Access:**
```sql
-- Full reference
SELECT * FROM cardora.users;

-- Or set search path
SET search_path TO cardora;
SELECT * FROM users;
```

## Development Workflow

### Backend Development

1. **Create Feature**:
   ```bash
   mkdir app/features/myfeature
   touch app/features/myfeature/{models.py,schemas.py,router.py}
   ```

2. **Define Model** (`models.py`):
   ```python
   from sqlalchemy import Column, String
   from app.core.database import Base

   class MyModel(Base):
       __tablename__ = "my_models"
       __table_args__ = {'schema': 'cardora'}

       id = Column(String, primary_key=True)
       name = Column(String)
   ```

3. **Create Migration**:
   ```bash
   alembic revision --autogenerate -m "Add my_models table"
   alembic upgrade head
   ```

4. **Define Schemas** (`schemas.py`):
   ```python
   from pydantic import BaseModel

   class MyModelResponse(BaseModel):
       id: str
       name: str

       class Config:
           from_attributes = True
   ```

5. **Create Router** (`router.py`):
   ```python
   from fastapi import APIRouter

   router = APIRouter(prefix="/myfeature", tags=["MyFeature"])

   @router.get("/")
   async def list_items():
       return []
   ```

6. **Register in main.py**:
   ```python
   from app.features.myfeature.router import router as myfeature_router
   app.include_router(myfeature_router)
   ```

### Frontend Development

1. **Create Feature**:
   ```bash
   mkdir -p frontend/src/features/myfeature/{api,components,types}
   ```

2. **Create API Client** (`api/myfeatureApi.ts`):
   ```typescript
   import apiClient from '@/shared/lib/api/client';

   export const getItems = async () => {
     const response = await apiClient.get('/myfeature');
     return response.data;
   };
   ```

3. **Create Types** (`types/index.ts`):
   ```typescript
   export interface MyItem {
     id: string;
     name: string;
   }
   ```

4. **Create Components** (`components/MyList.tsx`):
   ```typescript
   import { MyItem } from '../types';

   export default function MyList({ items }: { items: MyItem[] }) {
     return <div>...</div>;
   }
   ```

5. **Create Page** (`app/myfeature/page.tsx`):
   ```typescript
   import { getItems } from '@/features/myfeature';

   export default async function MyPage() {
     const items = await getItems();
     return <MyList items={items} />;
   }
   ```

## Running the Application

### Backend Setup
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Seed default categories
python app/core/seed_data.py

# Run development server
uvicorn app.main:app --reload --port 8000
```

**Access:**
- API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Frontend Setup
```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

**Access:**
- Frontend: http://localhost:3000

## Environment Variables

### Backend (`.env`)
```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/cardora
SECRET_KEY=your-secret-key
GEMINI_API_KEY=your-gemini-api-key
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email
SMTP_PASSWORD=your-app-password
FRONTEND_URL=http://localhost:3000
```

### Frontend (`.env.local`)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Testing

### Backend Tests
```bash
# Run all tests
pytest

# Run specific test
python tests/test_api.py

# Run with coverage
pytest --cov=app
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Deployment Checklist

- [ ] Update environment variables for production
- [ ] Run all database migrations
- [ ] Build frontend for production (`npm run build`)
- [ ] Set up HTTPS/SSL
- [ ] Configure CORS properly
- [ ] Set up monitoring and logging
- [ ] Back up database regularly
- [ ] Secure uploads directory
- [ ] Review security settings

## Resources

### Backend
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

### Frontend
- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [shadcn/ui Components](https://ui.shadcn.com/)

### Database
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## Migration from Old Structure

The project was recently migrated from a flat layer-based structure to feature-based architecture:

**Before:**
```
app/
├── models/user.py
├── models/card.py
├── routers/auth.py
├── routers/cards.py
└── services/auth_service.py
```

**After:**
```
app/features/
├── auth/
│   ├── models.py
│   ├── schemas.py
│   └── router.py
└── cards/
    ├── models.py
    ├── schemas.py
    └── router.py
```

This new structure provides better organization, scalability, and developer experience.
