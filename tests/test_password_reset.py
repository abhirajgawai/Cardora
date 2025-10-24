"""
Test Password Reset Flow

Compare to .NET: Like integration tests for password reset in ASP.NET Core Identity
"""
import sys
import os
import requests

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://127.0.0.1:8001"


def test_password_reset_flow():
    """Test complete password reset workflow"""

    print("\n" + "="*70)
    print("TESTING PASSWORD RESET FLOW")
    print("="*70)

    # ========================================
    # SETUP: Register and login a test user
    # ========================================
    print("\n[SETUP] Creating test user...")
    test_email = "resettest@example.com"
    original_password = "OriginalPassword123!"
    new_password = "NewPassword456!"
    test_name = "Password Reset Test User"

    # Register user
    register_response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": test_email,
            "password": original_password,
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

    # Verify original password works
    print("\n[SETUP] Verifying original password works...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": test_email,
            "password": original_password
        }
    )

    if login_response.status_code == 200:
        print("  [OK] Original password works")
    else:
        print(f"  [ERROR] Original password failed: {login_response.status_code}")
        return False

    # ========================================
    # TEST 1: Request password reset
    # ========================================
    print("\n[TEST 1] Request password reset...")
    forgot_response = requests.post(
        f"{BASE_URL}/auth/forgot-password",
        json={"email": test_email}
    )

    print(f"  Status code: {forgot_response.status_code}")

    if forgot_response.status_code == 200:
        response_data = forgot_response.json()
        print(f"  Message: {response_data['message']}")
        print("  [OK] Password reset requested successfully")
    else:
        print(f"  [ERROR] Expected 200 status, got {forgot_response.status_code}")
        return False

    # ========================================
    # TEST 2: Request reset for non-existent email (should still return 200)
    # ========================================
    print("\n[TEST 2] Request reset for non-existent email...")
    forgot_response = requests.post(
        f"{BASE_URL}/auth/forgot-password",
        json={"email": "nonexistent@example.com"}
    )

    print(f"  Status code: {forgot_response.status_code}")

    if forgot_response.status_code == 200:
        print("  [OK] Returns 200 even for non-existent email (security)")
    else:
        print(f"  [ERROR] Expected 200 status, got {forgot_response.status_code}")
        return False

    # ========================================
    # TEST 3: Get reset token from database (simulating email)
    # ========================================
    print("\n[TEST 3] Retrieving reset token from database...")
    print("  [INFO] In production, user would click link in email")
    print("  [INFO] For testing, we query DB directly")

    # We need to query the database to get the reset token
    # In production, this would be sent via email
    # For testing, we'll use the database session

    # Import database utilities
    from app.core.database import SessionLocal
    from app.models.user import User
    from app.auth.password_reset import hash_reset_token

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == test_email).first()
        if user and user.reset_token:
            print(f"  [OK] Reset token found in database")
            print(f"  Token hash (first 20 chars): {user.reset_token[:20]}...")
            print(f"  Token expires at: {user.reset_token_expires}")

            # We need the PLAIN token, not the hash
            # For testing, we'll generate a new one using the password_reset utilities
            from app.auth.password_reset import create_password_reset_token
            plain_token = create_password_reset_token(db, user)
            print(f"  Generated test token (first 20 chars): {plain_token[:20]}...")
        else:
            print("  [ERROR] No reset token found in database")
            return False
    finally:
        db.close()

    # ========================================
    # TEST 4: Reset password with invalid token
    # ========================================
    print("\n[TEST 4] Try reset with invalid token...")
    reset_response = requests.post(
        f"{BASE_URL}/auth/reset-password",
        json={
            "token": "invalid_token_here",
            "new_password": new_password
        }
    )

    print(f"  Status code: {reset_response.status_code}")

    if reset_response.status_code == 400:
        error_data = reset_response.json()
        print(f"  Error: {error_data['detail']}")
        print("  [OK] Invalid token correctly rejected")
    else:
        print(f"  [ERROR] Expected 400 status, got {reset_response.status_code}")
        return False

    # ========================================
    # TEST 5: Reset password with valid token
    # ========================================
    print("\n[TEST 5] Reset password with valid token...")
    reset_response = requests.post(
        f"{BASE_URL}/auth/reset-password",
        json={
            "token": plain_token,
            "new_password": new_password
        }
    )

    print(f"  Status code: {reset_response.status_code}")

    if reset_response.status_code == 200:
        success_data = reset_response.json()
        print(f"  Message: {success_data['message']}")
        print("  [OK] Password reset successful")
    else:
        print(f"  [ERROR] Expected 200 status, got {reset_response.status_code}")
        print(f"  Response: {reset_response.json()}")
        return False

    # ========================================
    # TEST 6: Verify old password no longer works
    # ========================================
    print("\n[TEST 6] Verify old password no longer works...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": test_email,
            "password": original_password
        }
    )

    print(f"  Status code: {login_response.status_code}")

    if login_response.status_code == 401:
        print("  [OK] Old password correctly rejected")
    else:
        print(f"  [ERROR] Expected 401 status, got {login_response.status_code}")
        return False

    # ========================================
    # TEST 7: Verify new password works
    # ========================================
    print("\n[TEST 7] Verify new password works...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": test_email,
            "password": new_password
        }
    )

    print(f"  Status code: {login_response.status_code}")

    if login_response.status_code == 200:
        token_data = login_response.json()
        print(f"  JWT token received: {token_data['access_token'][:30]}...")
        print("  [OK] New password works correctly")
    else:
        print(f"  [ERROR] Expected 200 status, got {login_response.status_code}")
        return False

    # ========================================
    # TEST 8: Verify token was cleared (single-use)
    # ========================================
    print("\n[TEST 8] Verify reset token was cleared...")
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == test_email).first()
        if user.reset_token is None and user.reset_token_expires is None:
            print("  [OK] Reset token cleared from database (single-use)")
        else:
            print("  [ERROR] Reset token should be NULL after use")
            return False
    finally:
        db.close()

    # ========================================
    # TEST 9: Try to reuse the same token
    # ========================================
    print("\n[TEST 9] Try to reuse the same token (should fail)...")
    reset_response = requests.post(
        f"{BASE_URL}/auth/reset-password",
        json={
            "token": plain_token,
            "new_password": "AnotherPassword789!"
        }
    )

    print(f"  Status code: {reset_response.status_code}")

    if reset_response.status_code == 400:
        error_data = reset_response.json()
        print(f"  Error: {error_data['detail']}")
        print("  [OK] Token reuse correctly prevented")
    else:
        print(f"  [ERROR] Expected 400 status, got {reset_response.status_code}")
        return False

    # ========================================
    # FINAL SUMMARY
    # ========================================
    print("\n" + "="*70)
    print("[SUCCESS] ALL PASSWORD RESET TESTS PASSED!")
    print("="*70)
    print("\nTest Summary:")
    print("  ✓ Request password reset for existing email")
    print("  ✓ Request password reset for non-existent email (security)")
    print("  ✓ Reset token generated and stored")
    print("  ✓ Invalid token rejected")
    print("  ✓ Valid token accepted")
    print("  ✓ Old password no longer works")
    print("  ✓ New password works correctly")
    print("  ✓ Token cleared after use (single-use)")
    print("  ✓ Token reuse prevented")

    print("\nCompare to .NET:")
    print("  FastAPI password reset is like ASP.NET Core Identity:")
    print("  - UserManager.GeneratePasswordResetTokenAsync() → create_password_reset_token()")
    print("  - UserManager.ResetPasswordAsync() → verify_reset_token() + hash_password()")
    print("  - IEmailSender → SendGrid email service")
    print("  - Token expiration → DataProtectionTokenProviderOptions.TokenLifespan")
    print("  - Single-use tokens → Token cleared after successful reset")
    print("  - Security: Don't reveal if email exists (always return 200)")
    print("="*70)

    return True


if __name__ == "__main__":
    try:
        success = test_password_reset_flow()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
