# Cardora - Credit Card Statement Analyzer

A full-stack application for analyzing credit card statements using AI, built with FastAPI and Next.js.

## ✨ Features

- 📊 **Multi-Card Analytics** - Analyze spending across multiple credit cards
- 📄 **AI-Powered PDF Processing** - Extract transactions from PDF statements using Google Gemini
- 🤖 **Smart Insights** - AI-generated spending insights and pattern detection
- 📈 **Comprehensive Analytics** - Monthly trends, category breakdowns, and comparisons
- 🎯 **Transaction Management** - Categorization, filtering, and bulk operations
- 🔐 **Secure Authentication** - JWT-based auth with password reset
- ⚡ **Payment Alerts** - Never miss a credit card payment

## 🚀 Tech Stack

### Backend
- **Framework:** Python 3.11+ with FastAPI
- **Database:** PostgreSQL with SQLAlchemy ORM
- **Migrations:** Alembic
- **AI:** Google Gemini API for PDF processing
- **Authentication:** JWT with bcrypt

### Frontend
- **Framework:** Next.js 16 with React 19
- **Language:** TypeScript
- **UI Library:** shadcn/ui with TailwindCSS
- **State Management:** React Context API
- **HTTP Client:** Axios

## 📁 Project Structure

```
Cardora/
├── app/                          # Backend (FastAPI)
│   ├── core/                     # Core infrastructure
│   │   ├── config.py             # App configuration
│   │   ├── database.py           # Database connection
│   │   ├── email_service.py      # Email functionality
│   │   ├── gemini_service.py     # AI PDF processing
│   │   └── seed_data.py          # Database seeding
│   │
│   ├── features/                 # Feature-based modules
│   │   ├── analytics/            # Spending analytics
│   │   ├── auth/                 # Authentication & users
│   │   ├── cards/                # Credit card management
│   │   ├── categories/           # Transaction categories
│   │   ├── insights/             # AI insights & alerts
│   │   ├── statements/           # PDF statement processing
│   │   └── transactions/         # Transaction CRUD
│   │
│   ├── shared/                   # Shared configurations
│   └── main.py                   # Application entry point
│
├── frontend/                     # Frontend (Next.js)
│   ├── src/
│   │   ├── app/                  # Next.js App Router pages
│   │   │   ├── analytics/        # Analytics page
│   │   │   ├── cards/            # Cards management
│   │   │   ├── dashboard/        # Dashboard
│   │   │   ├── insights/         # Insights page
│   │   │   ├── login/            # Login page
│   │   │   ├── register/         # Registration
│   │   │   ├── transactions/     # Transactions page
│   │   │   └── upload/           # Statement upload
│   │   │
│   │   ├── features/             # Feature modules (mirrors backend)
│   │   │   ├── analytics/        # Analytics types & logic
│   │   │   ├── auth/             # Auth API & models
│   │   │   ├── cards/            # Cards API & models
│   │   │   ├── insights/         # Insights components
│   │   │   ├── statements/       # Upload components
│   │   │   └── transactions/     # Transaction logic
│   │   │
│   │   └── shared/               # Shared resources
│   │       ├── components/       # Reusable components
│   │       ├── contexts/         # React contexts
│   │       ├── lib/              # Utilities & API client
│   │       └── types/            # Shared types
│   │
│   └── package.json
│
├── docs/                         # Documentation
│   ├── architecture/             # System architecture docs
│   ├── features/                 # Feature-specific guides
│   ├── guides/                   # How-to guides
│   └── planning/                 # Roadmaps & progress
│
├── alembic/                      # Database migrations
│   └── versions/                 # Migration files
│
├── tests/                        # Backend tests
├── uploads/                      # Uploaded PDFs (gitignored)
├── requirements.txt              # Python dependencies
└── .env                          # Environment variables
```

> 📖 **Detailed Architecture:** See [docs/architecture/PROJECT_STRUCTURE.md](docs/architecture/PROJECT_STRUCTURE.md) for comprehensive architecture documentation.

## 🏗️ Architecture Principles

Cardora follows a **feature-based architecture** for both backend and frontend:

### Benefits
- ✅ **Colocation** - All code for a feature lives together
- ✅ **Consistency** - Backend and frontend mirror each other
- ✅ **Discoverability** - Easy to find feature-related code
- ✅ **Scalability** - Independent feature development

### Pattern
Each feature contains:
- `models.py` - Database models (backend)
- `schemas.py` - API DTOs (backend)
- `router.py` - API endpoints (backend)
- `api/` - API client (frontend)
- `components/` - React components (frontend)
- `types/` - TypeScript types (frontend)

## 🚀 Complete Setup Guide for New Developers

### Prerequisites

Before you begin, install these tools:

1. **Python 3.11+**
   - Windows: Download from [python.org](https://www.python.org/downloads/)
   - Mac: `brew install python`
   - Linux: `sudo apt install python3`

2. **Node.js 18+**
   - Download from [nodejs.org](https://nodejs.org/)
   - Includes npm (Node Package Manager)

3. **PostgreSQL 14+**
   - Windows: Download from [postgresql.org](https://www.postgresql.org/download/)
   - Mac: `brew install postgresql`
   - Linux: `sudo apt install postgresql`

4. **Git**
   - Download from [git-scm.com](https://git-scm.com/)

### Step 1: Clone the Repository

```bash
git clone https://github.com/abhirajgawai/Cardora.git
cd Cardora
```

### Step 2: Backend Setup (Python/FastAPI)

#### 2.1 Create Python Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it:
# Windows CMD:
venv\Scripts\activate.bat

# Windows PowerShell:
venv\Scripts\Activate.ps1

# Mac/Linux:
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt when activated.

#### 2.2 Install Python Dependencies

```bash
pip install -r requirements.txt
```

#### 2.3 Configure Environment Variables

```bash
# Copy the example environment file
# Windows:
copy .env.example .env

# Mac/Linux:
cp .env.example .env
```

Edit `.env` file with your values:

```env
# Database Settings - Update with your PostgreSQL credentials
DATABASE_URL=postgresql://your_username:your_password@localhost:5432/cardora_db

# Google Gemini API - Get your key from https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your_gemini_api_key_here

# Security - Generate a secure random string
SECRET_KEY=your-secret-key-here-generate-a-strong-one
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email Settings (for password reset)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Frontend URL (for email links)
FRONTEND_URL=http://localhost:3000
```

#### 2.4 Setup PostgreSQL Database

```bash
# Connect to PostgreSQL (default user is 'postgres')
psql -U postgres

# Create the database
CREATE DATABASE cardora_db;

# Create a user (optional but recommended)
CREATE USER cardora_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE cardora_db TO cardora_user;

# Exit psql
\q
```

Update your `.env` file with the database credentials:
```env
DATABASE_URL=postgresql://cardora_user:your_secure_password@localhost:5432/cardora_db
```

#### 2.5 Run Database Migrations

```bash
# Check current migration status
alembic current

# Run all migrations to create database tables
alembic upgrade head
```

This will create all necessary tables:
- `users` - User accounts
- `credit_cards` - Credit card records
- `statements` - Uploaded statements
- `transactions` - Transaction records
- `categories` - Transaction categories (21 default + custom)
- `insights` - AI-generated insights
- `payment_alerts` - Payment due alerts

#### 2.6 Seed Default Categories (Optional)

```bash
python app/core/seed_data.py
```

This adds 21 default transaction categories to your database.

### Step 3: Frontend Setup (Next.js)

#### 3.1 Install Node Dependencies

```bash
cd frontend
npm install
```

#### 3.2 Configure Frontend Environment

Create a `.env.local` file:

```bash
# frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Step 4: Run the Application

You need to run both the backend and frontend simultaneously. Open **two terminal windows**:

#### Terminal 1: Run Backend

```bash
# Make sure you're in the Cardora root directory
# Make sure virtual environment is activated (venv)

# Run development server
python -m uvicorn app.main:app --reload --port 8000
```

Backend will be available at:
- **API:** http://localhost:8000
- **API Docs (Swagger):** http://localhost:8000/docs
- **API Docs (ReDoc):** http://localhost:8000/redoc

#### Terminal 2: Run Frontend

```bash
# Navigate to frontend directory
cd frontend

# Start Next.js development server
npm run dev
```

Frontend will be available at:
- **App:** http://localhost:3000

### Step 5: Verify Everything Works

1. Open http://localhost:3000 in your browser
2. You should see the Cardora landing page
3. Open http://localhost:8000/docs to see the API documentation
4. Try registering a new account
5. Upload a credit card statement PDF

## 📚 Documentation

Comprehensive documentation is available in the `/docs` folder:

### Architecture
- [PROJECT_STRUCTURE.md](docs/architecture/PROJECT_STRUCTURE.md) - Complete architecture guide
- [DESIGN_SYSTEM.md](docs/architecture/DESIGN_SYSTEM.md) - UI/UX design system
- [RESTRUCTURING_PLAN.md](docs/architecture/RESTRUCTURING_PLAN.md) - Migration history

### Features
- [AI_INSIGHTS_IMPLEMENTATION_PLAN.md](docs/features/AI_INSIGHTS_IMPLEMENTATION_PLAN.md) - Insights system
- [PDF_EXTRACTION_GUIDE.md](docs/features/PDF_EXTRACTION_GUIDE.md) - PDF processing guide
- [INSIGHTS_CONFIGURATION.md](docs/features/INSIGHTS_CONFIGURATION.md) - Insight configuration

### Guides
- [MIGRATIONS_GUIDE.md](docs/guides/MIGRATIONS_GUIDE.md) - Database migration guide

### Planning
- [FRONTEND_ROADMAP.md](docs/planning/FRONTEND_ROADMAP.md) - Frontend development roadmap
- [PROGRESS_TRACKER.md](docs/planning/PROGRESS_TRACKER.md) - Project progress
- [DESIGN_V2_CHANGELOG.md](docs/planning/DESIGN_V2_CHANGELOG.md) - Design updates

## 🔧 Common Commands Reference

### Backend (Python)

```bash
# Activate virtual environment (always do this first!)
# Windows CMD:
venv\Scripts\activate.bat
# Windows PowerShell:
venv\Scripts\Activate.ps1
# Mac/Linux:
source venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt

# Run backend server
python -m uvicorn app.main:app --reload --port 8000

# Database migrations
alembic current                                      # Check current migration
alembic upgrade head                                 # Apply all migrations
alembic downgrade -1                                 # Rollback last migration
alembic revision --autogenerate -m "description"     # Create new migration

# Seed default categories
python app/core/seed_data.py

# Run tests
pytest
pytest tests/test_api.py        # Run specific test
pytest --cov=app                # Run with coverage

# Code formatting
black app/
```

### Frontend (Next.js)

```bash
# Navigate to frontend
cd frontend

# Install/update dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Run production server
npm start

# Lint code
npm run lint

# Type checking
npm run type-check
```

## 🐛 Troubleshooting

### Database Connection Issues

**Problem:** `could not connect to server: Connection refused`

**Solution:**
1. Make sure PostgreSQL is running:
   ```bash
   # Windows: Check Services or run
   pg_ctl status

   # Mac:
   brew services list

   # Linux:
   sudo systemctl status postgresql
   ```
2. Verify your `DATABASE_URL` in `.env` matches your PostgreSQL credentials

### Migration Errors

**Problem:** `Target database is not up to date`

**Solution:**
```bash
# Check current migration status
alembic current

# Apply all pending migrations
alembic upgrade head
```

**Problem:** `Can't locate revision identified by 'xyz'`

**Solution:**
```bash
# Reset to a known good state
alembic downgrade base
alembic upgrade head
```

### Python Virtual Environment Issues

**Problem:** `Command not found` or `Module not found`

**Solution:**
Make sure your virtual environment is activated! You should see `(venv)` in your terminal.

### Port Already in Use

**Problem:** `Address already in use` on port 8000 or 3000

**Solution:**
```bash
# Windows - Find and kill process
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# Mac/Linux
lsof -ti:8000 | xargs kill -9
```

### Frontend Build Errors

**Problem:** TypeScript errors or module not found

**Solution:**
```bash
cd frontend
rm -rf .next node_modules
npm install
npm run dev
```

## 🏛️ Project Architecture

### Backend (FastAPI)

**Feature-Based Organization:**
- Each feature is self-contained in `app/features/`
- Features include: `auth`, `cards`, `categories`, `transactions`, `statements`, `analytics`, `insights`
- Each feature has its own `models.py`, `schemas.py`, and `router.py`
- Core infrastructure in `app/core/`
- Shared configurations in `app/shared/`

**Key Files:**
- `app/main.py` - Application entry point, CORS and middleware setup
- `app/core/database.py` - Database connection and session management
- `app/core/gemini_service.py` - AI-powered PDF processing
- `app/features/*/router.py` - API endpoints for each feature
- `alembic/versions/` - Database migration files

### Frontend (Next.js)

**Feature-Based Organization:**
- Mirrors backend structure in `src/features/`
- Each feature has its own `api/`, `components/`, `models/`, and `types/`
- Pages in `src/app/` using Next.js App Router
- Shared resources in `src/shared/`

**Key Directories:**
- `src/app/` - Next.js 14+ App Router pages
- `src/features/` - Feature-specific code (mirrors backend)
- `src/shared/components/` - Reusable React components
- `src/shared/lib/` - Utility functions and API client
- `src/shared/types/` - Shared TypeScript types

## 🌍 For Developers from Other Backgrounds

### Coming from .NET?

| .NET | Python/FastAPI | Next.js |
|------|----------------|---------|
| `dotnet run` | `uvicorn app.main:app --reload` | `npm run dev` |
| `dotnet restore` | `pip install -r requirements.txt` | `npm install` |
| `.csproj` | `requirements.txt` | `package.json` |
| `Program.cs` | `app/main.py` | `src/app/layout.tsx` |
| Controllers/ | features/*/router.py | `src/app/*/route.ts` |
| Entity Framework | SQLAlchemy + Alembic | N/A (uses backend) |
| `[HttpGet]` | `@router.get()` | `export async function GET()` |
| Clean Architecture | Feature-based modules | Feature-based modules |

### Coming from Django?

| Django | FastAPI |
|--------|---------|
| `manage.py runserver` | `uvicorn app.main:app --reload` |
| `manage.py migrate` | `alembic upgrade head` |
| `manage.py makemigrations` | `alembic revision --autogenerate` |
| `views.py` | `features/*/router.py` |
| Django ORM | SQLAlchemy |
| `settings.py` | `core/config.py` |

## 🤝 Contributing

1. Create a new branch for your feature: `git checkout -b feature/your-feature-name`
2. Make your changes following the feature-based architecture
3. Run tests and linting
4. Create a pull request with a clear description

### Code Style
- **Backend:** Follow PEP 8, use `black` for formatting
- **Frontend:** Use Prettier, follow TypeScript best practices
- **Commits:** Use conventional commits format

## 📄 License

MIT

---

**Built with ❤️ using FastAPI, Next.js, and Google Gemini AI**
