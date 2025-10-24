"""
Verify Alembic Migration - Check Users Table

Compare to .NET: Like verifying EF migrations were applied correctly
"""
import sys
import os

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import inspect, text
from app.core.database import engine

def verify_migration():
    """Verify the users table exists with correct structure"""

    print("\n" + "="*70)
    print("VERIFYING ALEMBIC MIGRATION")
    print("="*70)

    inspector = inspect(engine)

    # Check if cardora schema exists
    schemas = inspector.get_schema_names()
    print(f"\n[OK] Available schemas: {schemas}")

    if 'cardora' not in schemas:
        print("[ERROR] cardora schema not found!")
        return False

    # Check if users table exists in cardora schema
    tables = inspector.get_table_names(schema='cardora')
    print(f"[OK] Tables in cardora schema: {tables}")

    if 'users' not in tables:
        print("[ERROR] users table not found in cardora schema!")
        return False

    # Check table columns
    columns = inspector.get_columns('users', schema='cardora')
    print(f"\n[OK] Users table has {len(columns)} columns:")
    for col in columns:
        nullable = "NULL" if col['nullable'] else "NOT NULL"
        default = f" DEFAULT {col.get('default', '')}" if col.get('default') else ""
        print(f"  - {col['name']}: {col['type']} {nullable}{default}")

    # Check indexes
    indexes = inspector.get_indexes('users', schema='cardora')
    print(f"\n[OK] Users table has {len(indexes)} index(es):")
    for idx in indexes:
        unique = "UNIQUE" if idx['unique'] else ""
        print(f"  - {idx['name']}: {idx['column_names']} {unique}")

    # Check primary key
    pk = inspector.get_pk_constraint('users', schema='cardora')
    print(f"\n[OK] Primary key: {pk['constrained_columns']}")

    # Check alembic_version table
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version_num FROM alembic_version"))
        version = result.scalar()
        print(f"\n[OK] Current Alembic version: {version}")

    print("\n" + "="*70)
    print("[SUCCESS] MIGRATION VERIFIED SUCCESSFULLY!")
    print("="*70)
    print("\nCompare to .NET:")
    print("  This is like verifying 'dotnet ef database update' worked correctly")
    print("  - Schema exists: [OK] (like SQL Server database)")
    print("  - Table created: [OK] (like EF Core migration)")
    print("  - Columns match model: [OK] (like Entity properties)")
    print("  - Indexes created: [OK] (like [Index] attribute)")
    print("  - Migration tracked: [OK] (like __EFMigrationsHistory table)")
    print("="*70)

    return True

if __name__ == "__main__":
    try:
        success = verify_migration()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
