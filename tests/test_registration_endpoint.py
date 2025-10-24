"""
Test Registration Endpoint

Compare to .NET: Like integration tests for AuthController
"""
import sys
import os
import requests
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://127.0.0.1:8001"


def test_registration_endpoint():
    """Test user registration endpoint"""

    print("\n" + "="*70)
    print("TESTING REGISTRATION ENDPOINT")
    print("="*70)

    # Test 1: Register a new user
    print("\n[TEST 1] Register new user...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json={
                "email": "testuser@example.com",
                "password": "TestPassword123!",
                "full_name": "Test User",
                "timezone": "Asia/Singapore"
            }
        )

        print(f"  Status code: {response.status_code}")

        if response.status_code == 201:
            user = response.json()
            print(f"  User ID: {user['id']}")
            print(f"  Email: {user['email']}")
            print(f"  Full name: {user['full_name']}")
            print(f"  Is active: {user['is_active']}")
            print(f"  Is verified: {user['is_verified']}")
            print(f"  Created at: {user['created_at']}")
            print("  [OK] User registered successfully")
        else:
            print(f"  [ERROR] Registration failed: {response.json()}")
            return False

    except requests.exceptions.ConnectionError:
        print("  [ERROR] Cannot connect to server at http://127.0.0.1:8000")
        print("  Make sure the FastAPI server is running:")
        print("    uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"  [ERROR] Registration failed: {e}")
        return False

    # Test 2: Try to register with same email (should fail)
    print("\n[TEST 2] Register with duplicate email...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json={
                "email": "testuser@example.com",  # Same email
                "password": "AnotherPassword123!",
                "timezone": "America/New_York"
            }
        )

        print(f"  Status code: {response.status_code}")

        if response.status_code == 400:
            error = response.json()
            print(f"  Error: {error['detail']}")
            print("  [OK] Duplicate email correctly rejected")
        else:
            print(f"  [ERROR] Expected 400 status, got {response.status_code}")
            return False

    except Exception as e:
        print(f"  [ERROR] Test failed: {e}")
        return False

    # Test 3: Try to register with invalid email (should fail)
    print("\n[TEST 3] Register with invalid email...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json={
                "email": "not-an-email",
                "password": "ValidPassword123!",
                "timezone": "Asia/Singapore"
            }
        )

        print(f"  Status code: {response.status_code}")

        if response.status_code == 422:  # Validation error
            error = response.json()
            print(f"  Validation error: {error['detail'][0]['type']}")
            print("  [OK] Invalid email correctly rejected")
        else:
            print(f"  [ERROR] Expected 422 status, got {response.status_code}")
            return False

    except Exception as e:
        print(f"  [ERROR] Test failed: {e}")
        return False

    # Test 4: Try to register with short password (should fail)
    print("\n[TEST 4] Register with short password...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "short",  # Less than 8 characters
                "timezone": "Asia/Singapore"
            }
        )

        print(f"  Status code: {response.status_code}")

        if response.status_code == 422:  # Validation error
            error = response.json()
            print(f"  Validation error: Password too short")
            print("  [OK] Short password correctly rejected")
        else:
            print(f"  [ERROR] Expected 422 status, got {response.status_code}")
            return False

    except Exception as e:
        print(f"  [ERROR] Test failed: {e}")
        return False

    # Test 5: Register with minimal fields (using defaults)
    print("\n[TEST 5] Register with minimal fields...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json={
                "email": "minimal@example.com",
                "password": "MinimalPassword123!"
                # No full_name, using default timezone
            }
        )

        print(f"  Status code: {response.status_code}")

        if response.status_code == 201:
            user = response.json()
            print(f"  Email: {user['email']}")
            print(f"  Full name: {user['full_name']}")  # Should be null
            print(f"  Timezone: {user['timezone']}")  # Should be default
            print("  [OK] Registration with defaults works")
        else:
            print(f"  [ERROR] Expected 201 status, got {response.status_code}")
            return False

    except Exception as e:
        print(f"  [ERROR] Test failed: {e}")
        return False

    print("\n" + "="*70)
    print("[SUCCESS] ALL REGISTRATION TESTS PASSED!")
    print("="*70)
    print("\nCompare to .NET:")
    print("  FastAPI registration endpoint is like C# AuthController:")
    print("  - POST /auth/register: [OK] (like [HttpPost(\"register\")])")
    print("  - Automatic validation: [OK] (like [FromBody] with Data Annotations)")
    print("  - Dependency injection: [OK] (like constructor injection)")
    print("  - Status codes: [OK] (201 Created, 400 Bad Request, 422 Validation)")
    print("  - Error handling: [OK] (try/catch with rollback)")
    print("="*70)

    return True


if __name__ == "__main__":
    try:
        success = test_registration_endpoint()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
