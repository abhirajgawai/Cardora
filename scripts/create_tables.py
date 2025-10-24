"""
Database Table Creation Script for Cardora

Compare to .NET:
This is like running: dotnet ef database update

In .NET EF Core, migrations track database schema changes.
In SQLAlchemy (quick way), we just create all tables from models.

Usage:
    python create_tables.py
"""

import sys
import os

# Fix encoding for Windows
if sys.platform == "win32":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

from app.core.database import engine, Base
from app.models import User  # Import User to register it with Base

print("="*60)
print("CARDORA DATABASE TABLE CREATION")
print("="*60)

print("\nCompare to .NET:")
print("  .NET: dotnet ef database update")
print("  Python: Base.metadata.create_all(engine)")

print("\n" + "="*60)
print("Step 1: Import all models...")
print("="*60)
print(f"Imported models: {Base.metadata.tables.keys()}")
print(f"Models registered with Base: {len(Base.metadata.tables)}")

print("\n" + "="*60)
print("Step 2: Create tables in PostgreSQL...")
print("="*60)

try:
    # Create all tables
    # Compare to .NET: context.Database.EnsureCreated()
    Base.metadata.create_all(bind=engine)

    print("\nSUCCESS! Tables created successfully!")
    print("\nTables created:")
    for table_name in Base.metadata.tables.keys():
        print(f"  - {table_name}")

    print("\n" + "="*60)
    print("WHAT JUST HAPPENED?")
    print("="*60)
    print("""
SQLAlchemy executed SQL similar to:

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    timezone VARCHAR(50) NOT NULL DEFAULT 'Asia/Singapore',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_users_email ON users(email);

Compare to .NET EF Core:
- EF Core generates similar SQL from your model
- EF Core tracks migrations (can rollback)
- SQLAlchemy create_all() doesn't track migrations
- For production, use Alembic (like EF migrations)
    """)

    print("="*60)
    print("NEXT STEPS:")
    print("="*60)
    print("1. Verify table in pgAdmin")
    print("2. Create password hashing utilities")
    print("3. Create Pydantic schemas (DTOs)")
    print("4. Create registration endpoint")

except Exception as e:
    print(f"\nERROR creating tables: {e}")
    print("\nTroubleshooting:")
    print("1. Is PostgreSQL running?")
    print("2. Is DATABASE_URL correct in .env?")
    print("3. Does the database exist?")
    sys.exit(1)
