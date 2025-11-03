"""
Auth Feature Module

Exports:
- auth_router: Authentication endpoints (/auth/*)
- users_router: User profile endpoints (/users/*)
- User: User model
"""

from app.features.auth.router import auth_router, users_router
from app.features.auth.models import User

__all__ = ["auth_router", "users_router", "User"]
