"""
Recreate Tables in Cardora Schema

This script ensures all tables are in the 'cardora' schema
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
print("RECREATE TABLES IN CARDORA SCHEMA")
print("="*70)

try:
    with engine.connect() as conn:
        # Drop all old tables
        print("\nStep 1: Cleaning up old tables...")
        conn.execute(text("DROP TABLE IF EXISTS public.users CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS cardora.users CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS public.test_connection CASCADE"))
        conn.commit()
        print("Old tables dropped")

        # Ensure cardora schema exists
        print("\nStep 2: Ensuring cardora schema exists...")
        result = conn.execute(text("""
            SELECT schema_name
            FROM information_schema.schemata
            WHERE schema_name = 'cardora'
        """))

        if not result.fetchone():
            conn.execute(text("CREATE SCHEMA cardora"))
            conn.execute(text("GRANT ALL ON SCHEMA cardora TO postgres"))
            conn.commit()
            print("Created cardora schema")
        else:
            print("Cardora schema already exists")

    # Create tables
    print("\nStep 3: Creating tables in cardora schema...")
    Base.metadata.create_all(bind=engine)
    print("Tables created!")

    # Verify
    print("\nStep 4: Verifying tables...")
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_schema IN ('cardora', 'public')
            AND table_type = 'BASE TABLE'
            ORDER BY table_schema, table_name
        """))

        tables = result.fetchall()

        print(f"\nAll application tables:")
        for schema, table_name in tables:
            print(f"  {schema}.{table_name}")

        # Check specifically for cardora.users
        result = conn.execute(text("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = 'cardora'
            AND table_name = 'users'
        """))

        count = result.scalar()

        if count > 0:
            print("\n" + "="*70)
            print("SUCCESS! Table created in cardora schema")
            print("="*70)
            print("\nTable: cardora.users")
            print("You can query it with: SELECT * FROM cardora.users;")
        else:
            print("\nERROR: Table not found in cardora schema!")
            sys.exit(1)

except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
