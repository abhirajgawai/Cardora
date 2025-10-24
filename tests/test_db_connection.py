"""
Database Connection Test Script

This script verifies that:
1. .env file is loaded correctly
2. Database connection works
3. Can create and query tables

Compare to .NET:
Like running: dotnet ef database update
Or testing: context.Database.CanConnect()
"""

import sys
import os

# Fix Windows console encoding issues
if sys.platform == "win32":
    os.system("chcp 65001 > nul")
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

from sqlalchemy import text, Column, Integer, String
from sqlalchemy.exc import OperationalError

# Import our database configuration
from app.core.database import engine, SessionLocal, Base
from app.core.config import settings


def test_environment_variables():
    """Test 1: Verify .env file is loaded"""
    print("\n" + "="*60)
    print("TEST 1: Environment Variables")
    print("="*60)

    print(f"✓ APP_NAME: {settings.APP_NAME}")
    print(f"✓ APP_VERSION: {settings.APP_VERSION}")
    print(f"✓ DEBUG: {settings.DEBUG}")

    # Don't print full DATABASE_URL (contains password!)
    # But verify it exists and has correct format
    if settings.DATABASE_URL.startswith("postgresql://"):
        print(f"✓ DATABASE_URL: postgresql://***:***@localhost:5432/cardora_dev")
    else:
        print(f"✗ DATABASE_URL format incorrect!")
        return False

    print("\n✓ All environment variables loaded successfully!")
    return True


def test_database_connection():
    """Test 2: Verify database connection"""
    print("\n" + "="*60)
    print("TEST 2: Database Connection")
    print("="*60)

    try:
        # Test connection using raw SQL
        # Compare to .NET: context.Database.CanConnect()
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✓ Connected to PostgreSQL!")
            print(f"✓ Version: {version[:50]}...")  # First 50 chars

            # Test current database
            result = connection.execute(text("SELECT current_database();"))
            db_name = result.fetchone()[0]
            print(f"✓ Current database: {db_name}")

            # Test current user
            result = connection.execute(text("SELECT current_user;"))
            user = result.fetchone()[0]
            print(f"✓ Connected as user: {user}")

        print("\n✓ Database connection test passed!")
        return True

    except OperationalError as e:
        print(f"\n✗ Database connection failed!")
        print(f"Error: {e}")
        print("\nTroubleshooting:")
        print("1. Is PostgreSQL running?")
        print("   - Windows: Check Services for 'postgresql-x64-16'")
        print("   - Run: Get-Service -Name postgresql*")
        print("2. Is the database created?")
        print("   - Run: psql -U postgres")
        print("   - Run: \\l  (to list databases)")
        print("3. Is the user created?")
        print("   - Run: \\du  (to list users)")
        print("4. Check .env file:")
        print("   - DATABASE_URL format correct?")
        print("   - Password matches what you set?")
        return False


def test_create_test_table():
    """Test 3: Create and query a test table"""
    print("\n" + "="*60)
    print("TEST 3: Create and Query Test Table")
    print("="*60)

    try:
        # Define a simple test table
        # Compare to .NET: defining a simple entity class
        class TestTable(Base):
            __tablename__ = "test_connection"

            id = Column(Integer, primary_key=True, index=True)
            message = Column(String, nullable=False)

        # Create the table
        # Compare to .NET: context.Database.EnsureCreated()
        Base.metadata.create_all(bind=engine)
        print("✓ Test table created: test_connection")

        # Insert test data
        # Compare to .NET: context.TestTable.Add(new TestTable { ... })
        db = SessionLocal()
        try:
            test_record = TestTable(
                id=1,
                message="Hello from Cardora! Database connection works!"
            )
            db.add(test_record)
            db.commit()
            print("✓ Test record inserted")

            # Query the data back
            # Compare to .NET: context.TestTable.FirstOrDefault()
            result = db.query(TestTable).first()
            print(f"✓ Test record retrieved: {result.message}")

            # Clean up - drop the test table
            # Compare to .NET: context.Database.ExecuteSqlRaw("DROP TABLE...")
            Base.metadata.drop_all(bind=engine)
            print("✓ Test table cleaned up")

        finally:
            db.close()

        print("\n✓ Table creation and query test passed!")
        return True

    except Exception as e:
        print(f"\n✗ Table creation test failed!")
        print(f"Error: {e}")
        return False


def test_session_dependency():
    """Test 4: Test session dependency injection pattern"""
    print("\n" + "="*60)
    print("TEST 4: Session Dependency Pattern")
    print("="*60)

    try:
        # Import and test the get_db() function
        # This is what FastAPI will use for dependency injection
        from app.core.database import get_db

        # Create a session using the dependency pattern
        # Compare to .NET: injecting DbContext in a controller
        db_generator = get_db()
        db = next(db_generator)  # Get the session from generator

        try:
            # Test a simple query
            result = db.execute(text("SELECT 1 as test"))
            value = result.fetchone()[0]
            assert value == 1
            print("✓ Session created successfully")
            print("✓ Dependency injection pattern works")
        finally:
            # Clean up (generator will handle this, but let's be explicit)
            try:
                next(db_generator)
            except StopIteration:
                pass  # Expected - generator is done

        print("\n✓ Session dependency test passed!")
        return True

    except Exception as e:
        print(f"\n✗ Session dependency test failed!")
        print(f"Error: {e}")
        return False


def main():
    """Run all database connection tests"""
    print("\n" + "="*60)
    print("CARDORA DATABASE CONNECTION TEST")
    print("="*60)
    print("\nTesting database setup for Feature 1: User Authentication")
    print("Compare to .NET: Like testing DbContext before building controllers")

    # Run all tests
    results = []
    results.append(("Environment Variables", test_environment_variables()))
    results.append(("Database Connection", test_database_connection()))
    results.append(("Table Creation", test_create_test_table()))
    results.append(("Session Dependency", test_session_dependency()))

    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")

    all_passed = all(result[1] for result in results)

    if all_passed:
        print("\n" + "="*60)
        print("🎉 ALL TESTS PASSED!")
        print("="*60)
        print("\nYour database is configured correctly!")
        print("Ready to proceed to Step 2: Create User Model")
        print("\nNext steps:")
        print("1. Confirm database is working")
        print("2. Move to Step 2: User Model creation")
        return 0
    else:
        print("\n" + "="*60)
        print("❌ SOME TESTS FAILED")
        print("="*60)
        print("\nPlease fix the issues above before proceeding.")
        print("Common issues:")
        print("- PostgreSQL service not running")
        print("- Database 'cardora_dev' not created")
        print("- User 'cardora_user' not created or wrong password")
        print("- .env file not configured correctly")
        return 1


if __name__ == "__main__":
    sys.exit(main())
