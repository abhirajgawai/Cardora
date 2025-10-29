# Cardora - Credit Card Statement Analyzer

A full-stack application for analyzing credit card statements using AI, built with FastAPI and Next.js.

## Tech Stack

- **Backend:** Python 3.11+ with FastAPI
- **Frontend:** Next.js 16 with React 19 and TypeScript
- **Database:** PostgreSQL
- **AI:** Google Gemini API
- **Migrations:** Alembic (Python)

## Project Structure

```
Cardora/
├── app/                     # Backend (Python/FastAPI)
│   ├── main.py              # Application entry point
│   ├── routers/             # API routes
│   ├── models/              # Database models
│   └── services/            # Business logic
├── frontend/                # Frontend (Next.js)
│   ├── src/
│   │   ├── app/             # Next.js app router pages
│   │   └── components/      # React components
│   └── package.json
├── alembic/                 # Database migrations
│   └── versions/            # Migration files
├── requirements.txt         # Python dependencies
└── .env                     # Environment variables
```

## Complete Setup Guide for New Developers

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
git clone https://github.com/yourusername/Cardora.git
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

This will create all necessary tables (users, credit_cards, transactions, insights, etc.)

### Step 3: Frontend Setup (Next.js)

#### 3.1 Install Node Dependencies

```bash
cd frontend
npm install
```

#### 3.2 Configure Frontend Environment (Optional)

The frontend connects to the backend at `http://localhost:8000` by default. If you need to change this, you can create a `.env.local` file:

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

# Windows:
python -m uvicorn app.main:app --reload

# Mac/Linux:
uvicorn app.main:app --reload
```

Backend will be available at:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

#### Terminal 2: Run Frontend

```bash
# Navigate to frontend directory
cd frontend

# Start Next.js development server
npm run dev
```

Frontend will be available at:
- App: http://localhost:3000

### Step 5: Verify Everything Works

1. Open http://localhost:3000 in your browser
2. You should see the Cardora landing page
3. Open http://localhost:8000/docs to see the API documentation
4. Try the health check endpoint: http://localhost:8000/health

## Common Commands Reference

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
python -m uvicorn app.main:app --reload

# Database migrations
alembic current              # Check current migration
alembic upgrade head         # Apply all migrations
alembic downgrade -1         # Rollback last migration
alembic revision --autogenerate -m "description"  # Create new migration

# Run tests
pytest

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
```

## Troubleshooting

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

## Project Architecture

### Backend (FastAPI)
- **app/main.py** - Application entry point, CORS and middleware setup
- **app/routers/** - API endpoints organized by feature
- **app/models/** - SQLAlchemy database models and Pydantic schemas
- **app/services/** - Business logic and external integrations
- **alembic/versions/** - Database migration files

### Frontend (Next.js)
- **src/app/** - Next.js 13+ App Router pages
- **src/components/** - Reusable React components
- **src/lib/** - Utility functions and API client

## For Developers from Other Backgrounds

### Coming from .NET?

| .NET | Python/FastAPI | Next.js |
|------|----------------|---------|
| `dotnet run` | `uvicorn app.main:app --reload` | `npm run dev` |
| `dotnet restore` | `pip install -r requirements.txt` | `npm install` |
| `.csproj` | `requirements.txt` | `package.json` |
| `Program.cs` | `app/main.py` | `src/app/layout.tsx` |
| Controllers/ | routers/ | `src/app/*/route.ts` |
| Entity Framework | SQLAlchemy + Alembic | N/A (uses backend) |
| `[HttpGet]` | `@router.get()` | `export async function GET()` |

### Coming from Django?

| Django | FastAPI |
|--------|---------|
| `manage.py runserver` | `uvicorn app.main:app --reload` |
| `manage.py migrate` | `alembic upgrade head` |
| `manage.py makemigrations` | `alembic revision --autogenerate` |
| `views.py` | `routers/` |
| Django ORM | SQLAlchemy |

## Contributing

1. Create a new branch for your feature
2. Make your changes
3. Run tests and linting
4. Create a pull request

## License

MIT
