"""
Test Google Login — user resolution logic

Compare to .NET: Like unit tests for an ExternalLoginProvider handler
"""
import sys
import os
import uuid
import asyncio
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import HTTPException

from app.core.database import SessionLocal
from app.features.auth.models import User
from app.features.auth.google_auth import get_or_create_google_user
from app.features.auth import router as auth_router_module
from app.features.auth.router import google_login
from app.features.auth.schemas import GoogleLoginRequest

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


def test_password_login_rejected_for_google_only_account():
    print("\n" + "=" * 70)
    print("TEST: password login against a Google-only account returns 401, not 500")
    print("=" * 70)

    db = SessionLocal()
    try:
        email = f"google-only-{uuid.uuid4().hex[:8]}@example.com"
        sub = f"google-sub-{uuid.uuid4().hex[:8]}"

        user = get_or_create_google_user(db, _fake_claims(email, sub))
        assert user.hashed_password is None

        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": email, "password": "any-password-at-all"},
        )

        print(f"  Status code: {response.status_code}")
        db.query(User).filter(User.id == user.id).delete()
        db.commit()

        if response.status_code == 401:
            print("  [OK] Google-only account correctly rejected with 401 (not 500)")
            return True
        else:
            print(f"  [ERROR] Expected 401, got {response.status_code}: {response.text}")
            return False
    finally:
        db.close()


def test_unverified_email_claim_blocks_user_creation():
    print("\n" + "=" * 70)
    print("TEST: email_verified=False must never reach get_or_create_google_user")
    print("=" * 70)
    print("  NOTE: A real Google ID token with email_verified=False cannot be")
    print("  fabricated for a true HTTP-level integration test (tokens are")
    print("  signed by Google). Instead this test calls the real google_login()")
    print("  coroutine in-process, with verify_google_token monkeypatched to")
    print("  return a fabricated unverified claims dict — the router's own")
    print("  email_verified guard and get_or_create_google_user call run for real.")

    db = SessionLocal()
    email = f"google-unverified-{uuid.uuid4().hex[:8]}@example.com"
    sub = f"google-sub-{uuid.uuid4().hex[:8]}"
    claims = {"sub": sub, "email": email, "email_verified": False, "name": "Test User"}

    original_verify = auth_router_module.verify_google_token
    auth_router_module.verify_google_token = lambda id_token: claims

    try:
        request = GoogleLoginRequest(id_token="anything")

        raised = None
        try:
            asyncio.run(google_login(request, db))
        except HTTPException as exc:
            raised = exc

        assert raised is not None, "google_login should raise HTTPException for unverified email"
        assert raised.status_code == 401, f"expected 401, got {raised.status_code}"

        after = db.query(User).filter(
            (User.email == email) | (User.google_id == sub)
        ).first()
        assert after is None, "no user should be created for an unverified email"

        print(f"  [OK] google_login raised HTTPException 401: {raised.detail}")
        return True
    finally:
        auth_router_module.verify_google_token = original_verify
        db.query(User).filter(
            (User.email == email) | (User.google_id == sub)
        ).delete()
        db.commit()
        db.close()


def test_inactive_google_linked_user_rejected():
    print("\n" + "=" * 70)
    print("TEST: is_active=False on a Google-linked user blocks login")
    print("=" * 70)
    print("  NOTE: A full HTTP-level test of POST /auth/google for an inactive")
    print("  user would require a real Google ID token (tokens are signed by")
    print("  Google and cannot be fabricated here). Instead this test calls the")
    print("  real google_login() coroutine in-process, with verify_google_token")
    print("  monkeypatched to return claims matching a real, deactivated")
    print("  Google-linked user — the router's own is_active guard runs for real.")

    db = SessionLocal()
    email = f"google-inactive-{uuid.uuid4().hex[:8]}@example.com"
    sub = f"google-sub-{uuid.uuid4().hex[:8]}"

    user = get_or_create_google_user(db, _fake_claims(email, sub))
    user.is_active = False
    db.commit()
    db.refresh(user)

    claims = {"sub": sub, "email": email, "email_verified": True, "name": "Test User"}
    original_verify = auth_router_module.verify_google_token
    auth_router_module.verify_google_token = lambda id_token: claims

    try:
        request = GoogleLoginRequest(id_token="anything")

        raised = None
        try:
            asyncio.run(google_login(request, db))
        except HTTPException as exc:
            raised = exc

        assert raised is not None, "google_login should raise HTTPException for inactive user"
        assert raised.status_code == 403, f"expected 403, got {raised.status_code}"

        print(f"  [OK] google_login raised HTTPException 403: {raised.detail}")
        return True
    finally:
        auth_router_module.verify_google_token = original_verify
        db.query(User).filter(User.id == user.id).delete()
        db.commit()
        db.close()


if __name__ == "__main__":
    try:
        results = [
            test_creates_new_user_for_unknown_google_account(),
            test_links_google_id_to_existing_email_account(),
            test_repeat_login_returns_same_user(),
            test_invalid_token_rejected(),
            test_password_login_rejected_for_google_only_account(),
            test_unverified_email_claim_blocks_user_creation(),
            test_inactive_google_linked_user_rejected(),
        ]
        sys.exit(0 if all(results) else 1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
