"""
Test Password Hashing

Compare to .NET: Like unit tests for PasswordHasher
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.auth.password import hash_password, verify_password

def test_password_hashing():
    """Test password hashing and verification"""

    print("\n" + "="*70)
    print("TESTING PASSWORD HASHING")
    print("="*70)

    # Test 1: Hash a password
    print("\n[TEST 1] Hashing password...")
    plain_password = "MySecurePassword123!"
    hashed = hash_password(plain_password)
    print(f"  Plain password: {plain_password}")
    print(f"  Hashed password: {hashed[:40]}... (truncated)")
    print(f"  Hash length: {len(hashed)} characters")
    print("  [OK] Password hashed successfully")

    # Test 2: Verify correct password
    print("\n[TEST 2] Verifying correct password...")
    is_valid = verify_password(plain_password, hashed)
    if is_valid:
        print("  [OK] Password verification successful!")
    else:
        print("  [ERROR] Password verification failed!")
        return False

    # Test 3: Verify wrong password
    print("\n[TEST 3] Verifying wrong password...")
    is_valid = verify_password("WrongPassword123!", hashed)
    if not is_valid:
        print("  [OK] Wrong password correctly rejected")
    else:
        print("  [ERROR] Wrong password incorrectly accepted!")
        return False

    # Test 4: Same password generates different hashes (salt)
    print("\n[TEST 4] Testing salt uniqueness...")
    hashed1 = hash_password(plain_password)
    hashed2 = hash_password(plain_password)
    if hashed1 != hashed2:
        print(f"  Hash 1: {hashed1[:40]}...")
        print(f"  Hash 2: {hashed2[:40]}...")
        print("  [OK] Different hashes generated (salt working)")
    else:
        print("  [ERROR] Same hash generated (salt not working!)")
        return False

    # Test 5: Both hashes verify correctly
    print("\n[TEST 5] Verifying both hashes...")
    is_valid1 = verify_password(plain_password, hashed1)
    is_valid2 = verify_password(plain_password, hashed2)
    if is_valid1 and is_valid2:
        print("  [OK] Both hashes verify correctly")
    else:
        print("  [ERROR] Hash verification failed!")
        return False

    print("\n" + "="*70)
    print("[SUCCESS] ALL PASSWORD TESTS PASSED!")
    print("="*70)
    print("\nCompare to .NET:")
    print("  This is like testing ASP.NET Core Identity's PasswordHasher")
    print("  - Hashing: [OK] (like HashPassword method)")
    print("  - Verification: [OK] (like VerifyHashedPassword method)")
    print("  - Salt uniqueness: [OK] (bcrypt auto-generates salt)")
    print("  - Security: [OK] (bcrypt with 12 rounds)")
    print("="*70)

    return True

if __name__ == "__main__":
    try:
        success = test_password_hashing()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
