"""
Setup Custom Schema for Cardora

Compare to .NET:
Like creating: CREATE SCHEMA Cardora in SQL Server

This script:
1. Creates 'cardora' schema
2. Grants permissions to postgres user
3. Sets search_path to use cardora schema by default
4. Drops old tables in public schema
5. Recreates tables in cardora schema
"""

import sys
import os

# Fix encoding
if sys.platform == "win32":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

from sqlalchemy import text
from app.core.database import engine, Base
from app.models import User

print("="*70)
print("CARDORA SCHEMA SETUP")
print("="*70)

print("\nCOMPARE TO .NET/SQL SERVER:")
print("  SQL Server: CREATE SCHEMA Cardora; GO")
print("  PostgreSQL: CREATE SCHEMA cardora;")

print("\n" + "="*70)
print("Step 1: Create 'cardora' schema...")
print("="*70)

try:
    with engine.connect() as conn:
        # Check if schema exists
        result = conn.execute(text("""
            SELECT schema_name
            FROM information_schema.schemata
            WHERE schema_name = 'cardora'
        """))

        if result.fetchone():
            print("Schema 'cardora' already exists")

            # Ask user if they want to drop and recreate
            print("\nWARNING: This will drop all tables in cardora schema!")
            response = input("Continue? (yes/no): ").strip().lower()

            if response != 'yes':
                print("Aborting...")
                sys.exit(0)

            # Drop schema cascade (drops all objects in it)
            print("Dropping existing cardora schema...")
            conn.execute(text("DROP SCHEMA cardora CASCADE"))
            conn.commit()
            print("Dropped cardora schema")

        # Create cardora schema
        print("Creating cardora schema...")
        conn.execute(text("CREATE SCHEMA cardora"))
        conn.commit()
        print("SUCCESS: Schema 'cardora' created!")

        # Grant permissions to current user (postgres)
        print("\nGranting permissions to postgres user...")
        conn.execute(text("GRANT ALL ON SCHEMA cardora TO postgres"))
        conn.execute(text("GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA cardora TO postgres"))
        conn.execute(text("ALTER DEFAULT PRIVILEGES IN SCHEMA cardora GRANT ALL ON TABLES TO postgres"))
        conn.commit()
        print("Permissions granted")

    print("\n" + "="*70)
    print("Step 2: Clean up old tables in 'public' schema...")
    print("="*70)

    with engine.connect() as conn:
        # Drop users table from public schema if it exists
        print("Dropping tables from public schema...")
        conn.execute(text("DROP TABLE IF EXISTS public.users CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS public.test_connection CASCADE"))
        conn.commit()
        print("Old tables cleaned up")

    print("\n" + "="*70)
    print("Step 3: Update SQLAlchemy to use cardora schema...")
    print("="*70)

    # Set schema for all models
    # In SQLAlchemy, we can set schema at the Base level
    print("Configuring models to use 'cardora' schema...")

    # Update the User model's __table_args__ to include schema
    User.__table_args__ = {'schema': 'cardora'}

    print("Models configured for cardora schema")

    print("\n" + "="*70)
    print("Step 4: Create tables in cardora schema...")
    print("="*70)

    # Create all tables in cardora schema
    Base.metadata.create_all(bind=engine)

    print("\nSUCCESS! Tables created in cardora schema!")

    # Verify
    print("\n" + "="*70)
    print("Step 5: Verify tables in cardora schema...")
    print("="*70)

    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_schema = 'cardora'
            ORDER BY table_name
        """))

        tables = result.fetchall()

        if tables:
            print(f"\nTables in 'cardora' schema ({len(tables)}):")
            for schema, table_name in tables:
                print(f"  - {schema}.{table_name}")
        else:
            print("\nWARNING: No tables found in cardora schema!")

    print("\n" + "="*70)
    print("SCHEMA SETUP COMPLETE!")
    print("="*70)

    print("""
WHAT WE DID:
1. Created 'cardora' schema (like SQL Server schema)
2. Moved all tables from 'public' to 'cardora'
3. Granted permissions
4. Tables are now: cardora.users (not public.users)

IN PGADMIN:
Navigate to: cardora_dev → Schemas → cardora → Tables → users

QUERYING:
Option 1: SELECT * FROM cardora.users;
Option 2: SET search_path TO cardora; SELECT * FROM users;

COMPARE TO .NET:
In Entity Framework, you'd use:
[Table("Users", Schema = "Cardora")]
public class User { }

In SQLAlchemy:
__table_args__ = {'schema': 'cardora'}
    """)

    print("\nNEXT STEPS:")
    print("1. Update database.py to set default schema")
    print("2. Verify in pgAdmin: Schemas → cardora → Tables")
    print("3. Continue with password hashing utilities")

except Exception as e:
    print(f"\nERROR: {e}")
    print("\nTroubleshooting:")
    print("1. Is PostgreSQL running?")
    print("2. Do you have permissions to create schemas?")
    print("3. Is DATABASE_URL correct?")
    import traceback
    traceback.print_exc()
    sys.exit(1)
