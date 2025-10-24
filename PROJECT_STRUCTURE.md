# Cardora Project Structure

This document explains the organization of the Cardora codebase.

## Directory Structure

```
E:\Cardora/
│
├── app/                          # Main application code
│   ├── core/                     # Core functionality
│   │   ├── __init__.py
│   │   ├── config.py            # Configuration management (Pydantic Settings)
│   │   └── database.py          # Database connection & session management
│   │
│   ├── models/                   # Database models (ORM entities)
│   │   ├── __init__.py
│   │   └── user.py              # User model (cardora.users table)
│   │
│   ├── routers/                  # API endpoints (controllers)
│   │   └── __init__.py
│   │
│   ├── services/                 # Business logic layer
│   │   └── __init__.py
│   │
│   ├── auth/                     # Authentication utilities (future)
│   │
│   └── main.py                   # FastAPI application entry point
│
├── tests/                        # Test scripts and utilities
│   ├── __init__.py
│   ├── test_db_connection.py    # Comprehensive DB tests
│   ├── verify_users_table.py    # Table structure verification
│   ├── cleanup_test_table.py    # Cleanup utilities
│   ├── test_postgres_user.py    # User credential tests
│   ├── simple_test.py           # Simple connection tests
│   ├── verify_user.py           # User verification
│   └── README.md                # Test documentation
│
├── scripts/                      # Database setup & migration scripts
│   ├── recreate_tables.py       # ⭐ Main: Recreate all tables
│   ├── setup_schema.py          # Create cardora schema
│   ├── create_tables.py         # Quick table creation (legacy)
│   ├── fix_user.py              # Fix user credentials
│   └── README.md                # Scripts documentation
│
├── venv/                         # Python virtual environment
│
├── .env                          # Environment variables (secrets)
├── .env.example                  # Environment template
├── .gitignore                    # Git ignore rules
├── requirements.txt              # Python dependencies
├── PROJECT_STRUCTURE.md          # This file
└── README.md                     # Project README

```

## Compare to .NET Project Structure

```
.NET Solution:
Cardora/
├── Cardora.API/              → app/
│   ├── Controllers/          → app/routers/
│   ├── Models/               → app/models/
│   ├── Services/             → app/services/
│   └── Program.cs            → app/main.py
│
├── Cardora.Core/             → app/core/
│   └── Configuration/
│
├── Cardora.Tests/            → tests/
│   ├── UnitTests/
│   └── IntegrationTests/
│
└── Migrations/               → scripts/ (or use Alembic)

```

## Key Files

### Configuration
- **`.env`** - Environment variables (DATABASE_URL, SECRET_KEY, etc.)
- **`app/core/config.py`** - Settings management (like appsettings.json)
- **`app/core/database.py`** - Database setup (like DbContext)

### Models
- **`app/models/user.py`** - User entity (like User.cs in .NET)

### Main Application
- **`app/main.py`** - FastAPI app initialization (like Program.cs/Startup.cs)

### Database
- **`scripts/recreate_tables.py`** - Recreate database tables
- **Schema: `cardora`** - Custom schema for Cardora tables

## Naming Conventions

### Python vs C# Naming

| Type | Python | C# |
|------|--------|-----|
| Files | `snake_case.py` | `PascalCase.cs` |
| Classes | `PascalCase` | `PascalCase` |
| Functions | `snake_case()` | `PascalCase()` or `camelCase()` |
| Variables | `snake_case` | `camelCase` |
| Constants | `UPPER_SNAKE_CASE` | `PascalCase` or `UPPER_CASE` |

### Examples

```python
# Python
class User(Base):  # PascalCase for classes
    __tablename__ = "users"  # snake_case for table names

    def get_full_name(self):  # snake_case for methods
        return self.full_name
```

```csharp
// C#
public class User  // PascalCase for classes
{
    public string FullName { get; set; }  // PascalCase for properties

    public string GetFullName()  // PascalCase for methods
    {
        return FullName;
    }
}
```

## Database Schema

### Schema: `cardora`

All Cardora tables are in the `cardora` schema (not `public`).

**Why?**
- ✅ Organization: Group related tables
- ✅ Security: Granular permissions
- ✅ Best Practice: Don't pollute public schema

**Access:**
```sql
-- Full reference
SELECT * FROM cardora.users;

-- Or set search path
SET search_path TO cardora;
SELECT * FROM users;
```

### Compare to SQL Server:
```sql
-- SQL Server
SELECT * FROM Cardora.Users;
GO

-- PostgreSQL
SELECT * FROM cardora.users;
```

## Running the Application

### Setup
```bash
# Create virtual environment (like NuGet restore)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies (like dotnet restore)
pip install -r requirements.txt
```

### Database Setup
```bash
# Recreate all tables
python scripts/recreate_tables.py

# Verify tables
python tests/verify_users_table.py
```

### Run Application
```bash
# Run development server (like dotnet run)
uvicorn app.main:app --reload

# Access:
# - API: http://localhost:8000
# - Docs: http://localhost:8000/docs
```

## Development Workflow

1. **Create Model** → `app/models/your_model.py`
2. **Update Schema** → `python scripts/recreate_tables.py`
3. **Create Router** → `app/routers/your_router.py`
4. **Register Router** → `app/main.py`
5. **Test** → `python tests/test_your_feature.py`

Compare to .NET:
1. Create Entity → `Models/YourModel.cs`
2. Add Migration → `dotnet ef migrations add`
3. Update DB → `dotnet ef database update`
4. Create Controller → `Controllers/YourController.cs`
5. Test → Run with xUnit/NUnit

## Next Steps

- [ ] Create authentication system (JWT)
- [ ] Create user registration endpoint
- [ ] Create user login endpoint
- [ ] Create protected routes
- [ ] Add proper unit tests with pytest
- [ ] Set up Alembic for production migrations

## Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/
- **PostgreSQL Docs**: https://www.postgresql.org/docs/
