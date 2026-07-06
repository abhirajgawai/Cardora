"""
Google Sign-In — ID token verification and user resolution.

Google Identity Services hands the frontend a signed ID token (a JWT).
verify_google_token() checks that signature against Google's public keys
and confirms the token was issued for our app (the `aud` claim).
get_or_create_google_user() then maps the verified claims onto a User row.
"""

from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.features.auth.models import User


def verify_google_token(token: str) -> dict:
    """Verify a Google ID token and return its claims. Raises ValueError if invalid."""
    return google_id_token.verify_oauth2_token(
        token,
        google_requests.Request(),
        settings.GOOGLE_CLIENT_ID,
    )


def get_or_create_google_user(db: Session, claims: dict) -> User:
    """
    Resolve a verified Google claims dict to a User row.

    - Existing google_id -> return that user (repeat Google login)
    - No google_id match but matching email -> link google_id onto that account
    - No match at all -> create a new Google-only user (no password)

    IMPORTANT: Callers MUST verify `claims["email_verified"]` is True before
    calling this function. This function does not check that claim itself and
    will happily auto-link (or create a user for) an unverified email if that
    precondition is skipped by the caller.
    """
    google_id = claims["sub"]

    user = db.query(User).filter(User.google_id == google_id).first()
    if user:
        return user

    email = claims["email"]
    user = db.query(User).filter(User.email == email).first()
    if user:
        user.google_id = google_id
        db.commit()
        db.refresh(user)
        return user

    new_user = User(
        email=email,
        google_id=google_id,
        full_name=claims.get("name"),
        hashed_password=None,
        timezone="Asia/Singapore",
        is_active=True,
        is_verified=True,
    )
    db.add(new_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # Concurrent first-time Google login for the same account raced us —
        # the other request already created the user, so resolve to it.
        existing = db.query(User).filter(
            (User.google_id == google_id) | (User.email == email)
        ).first()
        if existing:
            return existing
        raise
    db.refresh(new_user)
    return new_user
