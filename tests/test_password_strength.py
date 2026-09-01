"""
Password Strength Validation Tests

Covers UserCreate.password rules:
- min 8 chars (Field constraint, min_length=8)
- at least one letter and one digit (field_validator)
- registration endpoint returns 422 for weak passwords

Run: python -m pytest tests/test_password_strength.py -v
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test-only settings so app.main can be imported without a real .env.
# setdefault keeps any real environment values intact. The endpoint test
# only exercises request validation (422), so no database is contacted.
os.environ.setdefault("DATABASE_URL", "postgresql://cardora:cardora@localhost:5433/cardora")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pytest-only")

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.features.auth.schemas import UserCreate
from app.main import app

WEAK_PASSWORD_MESSAGE = "Password must contain at least one letter and one digit"


def _registration_payload(password: str) -> dict:
    return {
        "email": "strength@example.com",
        "password": password,
        "full_name": "Password Strength Test",
        "timezone": "Asia/Singapore",
    }


def test_valid_password_passes():
    user = UserCreate(email="strength@example.com", password="Passw0rd")
    assert user.password == "Passw0rd"


def test_short_password_rejected():
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(email="strength@example.com", password="ab1")
    assert any(e["type"] == "string_too_short" for e in exc_info.value.errors())


def test_letters_only_password_rejected():
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(email="strength@example.com", password="abcdefgh")
    assert WEAK_PASSWORD_MESSAGE in str(exc_info.value)


def test_digits_only_password_rejected():
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(email="strength@example.com", password="12345678")
    assert WEAK_PASSWORD_MESSAGE in str(exc_info.value)


def test_password_without_digit_rejected():
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(email="strength@example.com", password="Abcdefgh!")
    assert WEAK_PASSWORD_MESSAGE in str(exc_info.value)


def test_password_without_letter_rejected():
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(email="strength@example.com", password="12345678!")
    assert WEAK_PASSWORD_MESSAGE in str(exc_info.value)


client = TestClient(app)


def test_registration_endpoint_returns_422_for_weak_passwords():
    weak_passwords = ["abcdefgh", "12345678", "Abcdefgh!", "12345678!"]
    for password in weak_passwords:
        response = client.post("/auth/register", json=_registration_payload(password))
        assert response.status_code == 422, f"{password!r} should be rejected with 422"
        detail = response.json()["detail"]
        assert any(
            WEAK_PASSWORD_MESSAGE in str(err) for err in detail
        ), f"422 for {password!r} should cite the password strength rule"
