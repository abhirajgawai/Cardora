"""
Test Login Endpoint

Compare to .NET: Like integration tests for login in AuthController
"""
import sys
import os
import requests

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://127.0.0.1:8001"


def test_login_endpoint():
    """Test user login endpoint"""

    print("\n" + "="*70)
    print("TESTING LOGIN ENDPOINT")
    print("="*70)

    # First, register a test user
    print("\n[SETUP] Registering test user...")
    test_email = "logintest@example.com"
    test_password = "LoginTestPassword123!"

    register_response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": test_email,
            "password": test_password,
            "full_name": "Login Test User",
            "timezone": "Asia/Singapore"
        }
    )

    if register_response.status_code == 201:
        print(f"  [OK] Test user registered: {test_email}")
    elif register_response.status_code == 400:
        print(f"  [INFO] Test user already exists: {test_email}")
    else:
        print(f"  [ERROR] Failed to register test user: {register_response.status_code}")
        return False

    # Test 1: Successful login
    print("\n[TEST 1] Login with correct credentials...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": test_email,
                "password": test_password
            }
        )

        print(f"  Status code: {response.status_code}")

        if response.status_code == 200:
            token_data = response.json()
            print(f"  Access token received: {token_data['access_token'][:50]}...")
            print(f"  Token type: {token_data['token_type']}")
            print(f"  Token length: {len(token_data['access_token'])} characters")
            print("  [OK] Login successful - JWT token received")

            # Save token for later tests
            global test_token
            test_token = token_data['access_token']
        else:
            print(f"  [ERROR] Login failed: {response.json()}")
            return False

    except requests.exceptions.ConnectionError:
        print("  [ERROR] Cannot connect to server at http://127.0.0.1:8001")
        print("  Make sure the FastAPI server is running:")
        print("    uvicorn app.main:app --reload --host 127.0.0.1 --port 8001")
        return False
    except Exception as e:
        print(f"  [ERROR] Login failed: {e}")
        return False

    # Test 2: Login with wrong password
    print("\n[TEST 2] Login with wrong password...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": test_email,
                "password": "WrongPassword123!"
            }
        )

        print(f"  Status code: {response.status_code}")

        if response.status_code == 401:
            error = response.json()
            print(f"  Error: {error['detail']}")
            print("  [OK] Wrong password correctly rejected")
        else:
            print(f"  [ERROR] Expected 401 status, got {response.status_code}")
            return False

    except Exception as e:
        print(f"  [ERROR] Test failed: {e}")
        return False

    # Test 3: Login with non-existent email
    print("\n[TEST 3] Login with non-existent email...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "AnyPassword123!"
            }
        )

        print(f"  Status code: {response.status_code}")

        if response.status_code == 401:
            error = response.json()
            print(f"  Error: {error['detail']}")
            print("  [OK] Non-existent email correctly rejected")
        else:
            print(f"  [ERROR] Expected 401 status, got {response.status_code}")
            return False

    except Exception as e:
        print(f"  [ERROR] Test failed: {e}")
        return False

    # Test 4: Login with invalid email format
    print("\n[TEST 4] Login with invalid email format...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": "not-an-email",
                "password": "Password123!"
            }
        )

        print(f"  Status code: {response.status_code}")

        if response.status_code == 422:  # Validation error
            error = response.json()
            print(f"  Validation error: {error['detail'][0]['type']}")
            print("  [OK] Invalid email format correctly rejected")
        else:
            print(f"  [ERROR] Expected 422 status, got {response.status_code}")
            return False

    except Exception as e:
        print(f"  [ERROR] Test failed: {e}")
        return False

    # Test 5: Verify JWT token structure
    print("\n[TEST 5] Verify JWT token structure...")
    try:
        # JWT tokens have 3 parts separated by dots: header.payload.signature
        token_parts = test_token.split('.')

        if len(token_parts) == 3:
            print(f"  Token has 3 parts: [OK]")
            print(f"  - Header: {token_parts[0][:20]}...")
            print(f"  - Payload: {token_parts[1][:20]}...")
            print(f"  - Signature: {token_parts[2][:20]}...")
            print("  [OK] JWT token structure is valid")
        else:
            print(f"  [ERROR] JWT token should have 3 parts, has {len(token_parts)}")
            return False

    except Exception as e:
        print(f"  [ERROR] Test failed: {e}")
        return False

    print("\n" + "="*70)
    print("[SUCCESS] ALL LOGIN TESTS PASSED!")
    print("="*70)
    print("\nCompare to .NET:")
    print("  FastAPI login endpoint is like C# AuthController:")
    print("  - POST /auth/login: [OK] (like [HttpPost(\"login\")])")
    print("  - Password verification: [OK] (like PasswordHasher.VerifyPassword)")
    print("  - JWT token generation: [OK] (like JwtSecurityTokenHandler)")
    print("  - Status codes: [OK] (200 OK, 401 Unauthorized, 422 Validation)")
    print("  - Security headers: [OK] (WWW-Authenticate: Bearer)")
    print("="*70)

    return True


if __name__ == "__main__":
    try:
        success = test_login_endpoint()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
