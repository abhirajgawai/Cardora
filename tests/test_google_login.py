"""
Test Google Login — user resolution logic

Compare to .NET: Like unit tests for an ExternalLoginProvider handler
"""
import sys
import os
import uuid
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.features.auth.models import User
from app.features.auth.google_auth import get_or_create_google_user

BASE_URL = "http://127.0.0.1:8000"


def _fake_claims(email: str, sub: str, name: str = "Test User") -> dict:
    return {"sub": sub, "email": email, "email_verified": True, "name": name}


def test_creates_new_user_for_unknown_google_account():
    print("\n" + "=" * 70)
    print("TEST: new Google account creates a new user")
    print("=" * 70)

    db = SessionLocal()
    try:
        email = f"google-new-{uuid.uuid4().hex[:8]}@example.com"
        sub = f"google-sub-{uuid.uuid4().hex[:8]}"

        user = get_or_create_google_user(db, _fake_claims(email, sub))

        assert user.email == email
        assert user.google_id == sub
        assert user.hashed_password is None
        assert user.is_verified is True
        print("  [OK] New Google-only user created correctly")

        db.query(User).filter(User.id == user.id).delete()
        db.commit()
        return True
    finally:
        db.close()


def test_links_google_id_to_existing_email_account():
    print("\n" + "=" * 70)
    print("TEST: existing email/password account gets auto-linked")
    print("=" * 70)

    db = SessionLocal()
    try:
        email = f"google-link-{uuid.uuid4().hex[:8]}@example.com"
        sub = f"google-sub-{uuid.uuid4().hex[:8]}"

        existing = User(
            email=email,
            hashed_password="not-a-real-hash",
            timezone="Asia/Singapore",
            is_active=True,
            is_verified=False,
        )
        db.add(existing)
        db.commit()
        db.refresh(existing)

        linked = get_or_create_google_user(db, _fake_claims(email, sub))

        assert linked.id == existing.id
        assert linked.google_id == sub
        assert linked.hashed_password == "not-a-real-hash"
        print("  [OK] Existing account auto-linked, password untouched")

        db.query(User).filter(User.id == existing.id).delete()
        db.commit()
        return True
    finally:
        db.close()


def test_repeat_login_returns_same_user():
    print("\n" + "=" * 70)
    print("TEST: repeat Google login resolves to the same user")
    print("=" * 70)

    db = SessionLocal()
    try:
        email = f"google-repeat-{uuid.uuid4().hex[:8]}@example.com"
        sub = f"google-sub-{uuid.uuid4().hex[:8]}"
        claims = _fake_claims(email, sub)

        first = get_or_create_google_user(db, claims)
        second = get_or_create_google_user(db, claims)

        assert first.id == second.id
        print("  [OK] Second login found the same user, no duplicate created")

        db.query(User).filter(User.id == first.id).delete()
        db.commit()
        return True
    finally:
        db.close()


def test_invalid_token_rejected():
    print("\n" + "=" * 70)
    print("TEST: garbage id_token is rejected with 401")
    print("=" * 70)

    response = requests.post(
        f"{BASE_URL}/auth/google",
        json={"id_token": "not-a-real-google-token"},
    )

    print(f"  Status code: {response.status_code}")
    if response.status_code == 401:
        print("  [OK] Invalid token correctly rejected")
        return True
    else:
        print(f"  [ERROR] Expected 401, got {response.status_code}: {response.text}")
        return False


if __name__ == "__main__":
    try:
        results = [
            test_creates_new_user_for_unknown_google_account(),
            test_links_google_id_to_existing_email_account(),
            test_repeat_login_returns_same_user(),
            test_invalid_token_rejected(),
        ]
        sys.exit(0 if all(results) else 1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
