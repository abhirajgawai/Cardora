"""
Test Pydantic Schemas (DTOs)

Compare to .NET: Like unit tests for ViewModels/DTOs
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from uuid import uuid4
from datetime import datetime
from app.schemas import UserCreate, UserResponse, UserLogin, Token, TokenData


def test_schemas():
    """Test Pydantic schemas validation"""

    print("\n" + "="*70)
    print("TESTING PYDANTIC SCHEMAS (DTOs)")
    print("="*70)

    # Test 1: UserCreate schema (registration)
    print("\n[TEST 1] UserCreate schema validation...")
    try:
        user_create = UserCreate(
            email="john.doe@example.com",
            password="MySecurePassword123!",
            full_name="John Doe",
            timezone="Asia/Singapore"
        )
        print(f"  Email: {user_create.email}")
        print(f"  Password length: {len(user_create.password)} chars")
        print(f"  Full name: {user_create.full_name}")
        print(f"  Timezone: {user_create.timezone}")
        print("  [OK] UserCreate schema valid")
    except Exception as e:
        print(f"  [ERROR] UserCreate validation failed: {e}")
        return False

    # Test 2: UserCreate with invalid email
    print("\n[TEST 2] UserCreate with invalid email...")
    try:
        invalid_user = UserCreate(
            email="not-an-email",
            password="Password123!",
            timezone="Asia/Singapore"
        )
        print("  [ERROR] Invalid email was accepted!")
        return False
    except Exception as e:
        print(f"  [OK] Invalid email rejected: {type(e).__name__}")

    # Test 3: UserCreate with short password
    print("\n[TEST 3] UserCreate with short password...")
    try:
        invalid_user = UserCreate(
            email="john@example.com",
            password="short",
            timezone="Asia/Singapore"
        )
        print("  [ERROR] Short password was accepted!")
        return False
    except Exception as e:
        print(f"  [OK] Short password rejected: {type(e).__name__}")

    # Test 4: UserCreate with default timezone
    print("\n[TEST 4] UserCreate with default timezone...")
    try:
        user_with_default = UserCreate(
            email="jane@example.com",
            password="Password123!"
        )
        print(f"  Email: {user_with_default.email}")
        print(f"  Timezone (default): {user_with_default.timezone}")
        print("  [OK] Default timezone applied")
    except Exception as e:
        print(f"  [ERROR] UserCreate with defaults failed: {e}")
        return False

    # Test 5: UserResponse schema (output)
    print("\n[TEST 5] UserResponse schema...")
    try:
        user_response = UserResponse(
            id=uuid4(),
            email="john.doe@example.com",
            full_name="John Doe",
            timezone="Asia/Singapore",
            is_active=True,
            is_verified=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        print(f"  ID: {user_response.id}")
        print(f"  Email: {user_response.email}")
        print(f"  Is active: {user_response.is_active}")
        print(f"  Is verified: {user_response.is_verified}")
        print("  [OK] UserResponse schema valid")
    except Exception as e:
        print(f"  [ERROR] UserResponse validation failed: {e}")
        return False

    # Test 6: UserLogin schema
    print("\n[TEST 6] UserLogin schema...")
    try:
        user_login = UserLogin(
            email="john@example.com",
            password="Password123!"
        )
        print(f"  Email: {user_login.email}")
        print(f"  Password present: {bool(user_login.password)}")
        print("  [OK] UserLogin schema valid")
    except Exception as e:
        print(f"  [ERROR] UserLogin validation failed: {e}")
        return False

    # Test 7: Token schema
    print("\n[TEST 7] Token schema...")
    try:
        token = Token(
            access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xyz",
            token_type="bearer"
        )
        print(f"  Access token: {token.access_token[:30]}...")
        print(f"  Token type: {token.token_type}")
        print("  [OK] Token schema valid")
    except Exception as e:
        print(f"  [ERROR] Token validation failed: {e}")
        return False

    # Test 8: TokenData schema
    print("\n[TEST 8] TokenData schema...")
    try:
        token_data = TokenData(
            user_id=uuid4(),
            email="john@example.com"
        )
        print(f"  User ID: {token_data.user_id}")
        print(f"  Email: {token_data.email}")
        print("  [OK] TokenData schema valid")
    except Exception as e:
        print(f"  [ERROR] TokenData validation failed: {e}")
        return False

    # Test 9: JSON serialization
    print("\n[TEST 9] JSON serialization...")
    try:
        user_create = UserCreate(
            email="test@example.com",
            password="Password123!",
            full_name="Test User"
        )
        json_data = user_create.model_dump_json()
        print(f"  JSON output: {json_data[:80]}...")
        print("  [OK] JSON serialization works")
    except Exception as e:
        print(f"  [ERROR] JSON serialization failed: {e}")
        return False

    # Test 10: Optional fields
    print("\n[TEST 10] Optional fields...")
    try:
        user_minimal = UserCreate(
            email="minimal@example.com",
            password="Password123!"
            # No full_name (optional)
        )
        print(f"  Email: {user_minimal.email}")
        print(f"  Full name: {user_minimal.full_name}")  # Should be None
        print("  [OK] Optional fields work correctly")
    except Exception as e:
        print(f"  [ERROR] Optional fields test failed: {e}")
        return False

    print("\n" + "="*70)
    print("[SUCCESS] ALL SCHEMA TESTS PASSED!")
    print("="*70)
    print("\nCompare to .NET:")
    print("  Pydantic schemas are like C# ViewModels/DTOs with:")
    print("  - Automatic validation: [OK] (like Data Annotations)")
    print("  - JSON serialization: [OK] (like System.Text.Json)")
    print("  - Type safety: [OK] (like C# properties)")
    print("  - Documentation: [OK] (like XML comments)")
    print("  - Default values: [OK] (like property initializers)")
    print("="*70)

    return True


if __name__ == "__main__":
    try:
        success = test_schemas()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
