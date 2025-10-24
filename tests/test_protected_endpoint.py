"""
Test Protected Endpoint - GET /users/me

Compare to .NET: Like testing [Authorize] endpoints
"""
import sys
import os
import requests

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://127.0.0.1:8001"


def test_protected_endpoint():
    """Test protected /users/me endpoint"""

    print("\n" + "="*70)
    print("TESTING PROTECTED ENDPOINT - GET /users/me")
    print("="*70)

    # Setup: Register a test user
    print("\n[SETUP] Registering test user...")
    test_email = "protectedtest@example.com"
    test_password = "ProtectedTestPassword123!"
    test_name = "Protected Test User"

    register_response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": test_email,
            "password": test_password,
            "full_name": test_name,
            "timezone": "America/New_York"
        }
    )

    if register_response.status_code == 201:
        print(f"  [OK] Test user registered: {test_email}")
    elif register_response.status_code == 400:
        print(f"  [INFO] Test user already exists: {test_email}")
    else:
        print(f"  [ERROR] Failed to register test user: {register_response.status_code}")
        return False

    # Setup: Login to get JWT token
    print("\n[SETUP] Logging in to get JWT token...")
    try:
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": test_email,
                "password": test_password
            }
        )

        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data['access_token']
            print(f"  [OK] JWT token received: {access_token[:50]}...")
        else:
            print(f"  [ERROR] Login failed: {login_response.json()}")
            return False

    except Exception as e:
        print(f"  [ERROR] Login failed: {e}")
        return False

    # Test 1: Access protected endpoint WITH valid token
    print("\n[TEST 1] Access /users/me WITH valid JWT token...")
    try:
        response = requests.get(
            f"{BASE_URL}/users/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        print(f"  Status code: {response.status_code}")

        if response.status_code == 200:
            user_data = response.json()
            print(f"  User ID: {user_data['id']}")
            print(f"  Email: {user_data['email']}")
            print(f"  Full name: {user_data['full_name']}")
            print(f"  Timezone: {user_data['timezone']}")
            print(f"  Is active: {user_data['is_active']}")
            print(f"  Is verified: {user_data['is_verified']}")

            # Verify the data matches what we registered
            if user_data['email'] == test_email and user_data['full_name'] == test_name:
                print("  [OK] Protected endpoint returned correct user data")
            else:
                print("  [ERROR] User data mismatch!")
                return False
        else:
            print(f"  [ERROR] Expected 200 status, got {response.status_code}")
            print(f"  Response: {response.json()}")
            return False

    except Exception as e:
        print(f"  [ERROR] Test failed: {e}")
        return False

    # Test 2: Access protected endpoint WITHOUT token
    print("\n[TEST 2] Access /users/me WITHOUT token (should fail)...")
    try:
        response = requests.get(f"{BASE_URL}/users/me")

        print(f"  Status code: {response.status_code}")

        if response.status_code == 401:
            error = response.json()
            print(f"  Error: {error['detail']}")
            print("  [OK] Access denied without token")
        else:
            print(f"  [ERROR] Expected 401 status, got {response.status_code}")
            return False

    except Exception as e:
        print(f"  [ERROR] Test failed: {e}")
        return False

    # Test 3: Access protected endpoint with INVALID token
    print("\n[TEST 3] Access /users/me with INVALID token (should fail)...")
    try:
        response = requests.get(
            f"{BASE_URL}/users/me",
            headers={"Authorization": "Bearer invalid_token_here"}
        )

        print(f"  Status code: {response.status_code}")

        if response.status_code == 401:
            error = response.json()
            print(f"  Error: {error['detail']}")
            print("  [OK] Invalid token correctly rejected")
        else:
            print(f"  [ERROR] Expected 401 status, got {response.status_code}")
            return False

    except Exception as e:
        print(f"  [ERROR] Test failed: {e}")
        return False

    # Test 4: Access protected endpoint with EXPIRED token (simulated by malformed token)
    print("\n[TEST 4] Access /users/me with malformed token (should fail)...")
    try:
        response = requests.get(
            f"{BASE_URL}/users/me",
            headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature"}
        )

        print(f"  Status code: {response.status_code}")

        if response.status_code == 401:
            error = response.json()
            print(f"  Error: {error['detail']}")
            print("  [OK] Malformed token correctly rejected")
        else:
            print(f"  [ERROR] Expected 401 status, got {response.status_code}")
            return False

    except Exception as e:
        print(f"  [ERROR] Test failed: {e}")
        return False

    # Test 5: Verify password is NOT included in response
    print("\n[TEST 5] Verify password is NOT in response...")
    try:
        response = requests.get(
            f"{BASE_URL}/users/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        user_data = response.json()

        if 'hashed_password' in user_data or 'password' in user_data:
            print("  [ERROR] Password field found in response! Security issue!")
            return False
        else:
            print("  [OK] Password NOT included in response (secure)")

    except Exception as e:
        print(f"  [ERROR] Test failed: {e}")
        return False

    print("\n" + "="*70)
    print("[SUCCESS] ALL PROTECTED ENDPOINT TESTS PASSED!")
    print("="*70)
    print("\nCompare to .NET:")
    print("  FastAPI protected endpoint is like C# [Authorize] attribute:")
    print("  - JWT authentication: [OK] (like [Authorize] in ASP.NET Core)")
    print("  - Token validation: [OK] (like JwtBearerHandler)")
    print("  - User extraction: [OK] (like User.FindFirst(ClaimTypes.NameIdentifier))")
    print("  - Access denied without token: [OK] (401 Unauthorized)")
    print("  - Invalid token rejected: [OK] (401 Unauthorized)")
    print("  - Password excluded: [OK] (like [JsonIgnore] or AutoMapper)")
    print("="*70)

    return True


if __name__ == "__main__":
    try:
        success = test_protected_endpoint()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
