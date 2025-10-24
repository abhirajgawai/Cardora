# Scripts

This folder contains database setup and migration scripts for Cardora.

## Files

- **recreate_tables.py** - ⭐ **MAIN SCRIPT** - Recreate all tables in cardora schema
  - Use this to reset your database
  - Drops old tables and recreates them
  - Ensures all tables are in 'cardora' schema

- **setup_schema.py** - Create custom 'cardora' schema
  - Creates cardora schema
  - Grants permissions
  - Moves tables from public to cardora

- **create_tables.py** - Quick table creation (legacy)
  - Creates tables in default schema
  - Use recreate_tables.py instead

- **fix_user.py** - Fix user credentials (troubleshooting)
  - Reset user passwords
  - Fix permission issues

## Running Scripts

```bash
# Recreate all tables (recommended)
python scripts/recreate_tables.py

# Setup schema (if not exists)
python scripts/setup_schema.py
```

## Compare to .NET

In .NET EF Core, this would be like:
- `Migrations/` folder
- Migration files created by: `dotnet ef migrations add`
- Applied by: `dotnet ef database update`

In Python/SQLAlchemy:
- `scripts/` folder for utility scripts
- For production, use **Alembic** (like EF migrations)
- For development, use `recreate_tables.py`

## Production Note

⚠️ **For production**, use Alembic migrations instead:
```bash
# Install Alembic
pip install alembic

# Initialize Alembic
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Create users table"

# Apply migration
alembic upgrade head
```

This is similar to EF Core migrations and provides:
- Migration history
- Rollback capability
- Version control
