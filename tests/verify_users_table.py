"""
Verify Users Table Structure

Compare to .NET:
Like viewing table schema in SQL Server Management Studio (SSMS)
Or running: SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Users'
"""

import sys
import os

# Fix encoding
if sys.platform == "win32":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

from sqlalchemy import inspect, text
from app.core.database import engine

print("="*70)
print("VERIFY USERS TABLE IN POSTGRESQL")
print("="*70)

try:
    # Create inspector (like SSMS Object Explorer)
    inspector = inspect(engine)

    # Check if users table exists
    print("\nStep 1: Check if 'users' table exists...")
    tables = inspector.get_table_names()
    print(f"Tables in database: {tables}")

    if 'users' not in tables:
        print("\nERROR: 'users' table not found!")
        print("Run: python create_tables.py")
        sys.exit(1)

    print("SUCCESS: 'users' table exists!")

    # Get column information
    print("\n" + "="*70)
    print("Step 2: Inspect 'users' table structure...")
    print("="*70)

    columns = inspector.get_columns('users')

    print(f"\nTable: users")
    print(f"Total columns: {len(columns)}")
    print("\n" + "-"*70)
    print(f"{'Column':<20} {'Type':<25} {'Nullable':<10} {'Default'}")
    print("-"*70)

    for column in columns:
        col_name = column['name']
        col_type = str(column['type'])
        nullable = "Yes" if column['nullable'] else "No"
        default = column.get('default', 'None')
        print(f"{col_name:<20} {col_type:<25} {nullable:<10} {default}")

    # Get indexes
    print("\n" + "="*70)
    print("Step 3: Check indexes...")
    print("="*70)

    indexes = inspector.get_indexes('users')
    print(f"\nTotal indexes: {len(indexes)}")

    for index in indexes:
        print(f"\nIndex: {index['name']}")
        print(f"  Columns: {index['column_names']}")
        print(f"  Unique: {index['unique']}")

    # Get primary key
    print("\n" + "="*70)
    print("Step 4: Check primary key...")
    print("="*70)

    pk = inspector.get_pk_constraint('users')
    print(f"\nPrimary Key: {pk['name'] or 'users_pkey'}")
    print(f"Columns: {pk['constrained_columns']}")

    # Test insert and query
    print("\n" + "="*70)
    print("Step 5: Test INSERT and SELECT...")
    print("="*70)

    with engine.connect() as conn:
        # Check row count
        result = conn.execute(text("SELECT COUNT(*) FROM users"))
        count = result.scalar()
        print(f"\nCurrent rows in users table: {count}")

        if count == 0:
            print("\nTable is empty (no users registered yet)")
            print("This is expected - users will be added via registration endpoint")

    print("\n" + "="*70)
    print("VERIFICATION COMPLETE!")
    print("="*70)

    print("\nCOMPARISON TO .NET EF CORE:")
    print("""
    In .NET, you would verify by:
    1. View in SQL Server Object Explorer
    2. Check migrations history: __EFMigrationsHistory table
    3. Run query: SELECT * FROM Users

    In Python/SQLAlchemy:
    1. Use Inspector to get table metadata
    2. Query information_schema (PostgreSQL system tables)
    3. Run queries via engine.connect()
    """)

    print("\nNEXT STEPS:")
    print("1. Open pgAdmin to view table visually")
    print("2. Create password hashing utilities")
    print("3. Create Pydantic schemas (DTOs)")
    print("4. Create registration endpoint to add users")

except Exception as e:
    print(f"\nERROR: {e}")
    print("\nTroubleshooting:")
    print("1. Did you run create_tables.py?")
    print("2. Is PostgreSQL running?")
    print("3. Is DATABASE_URL correct?")
    sys.exit(1)
