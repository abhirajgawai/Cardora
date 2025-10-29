"""
Models package for Cardora

This file makes the models easily importable.

Compare to .NET:
In .NET, you'd have all your entity classes in a Models folder,
and EF Core would automatically discover them through DbSet<T> properties.

In SQLAlchemy, we import all models here so they're registered with Base.
This is important for migrations and table creation.

Usage:
    from app.models import User
    # or
    from app.models.user import User
"""

from app.models.user import User
from app.models.credit_card import CreditCard
from app.models.category import Category
from app.models.statement import Statement
from app.models.transaction import Transaction
from app.models.insight import Insight, InsightTransaction
from app.models.alert import PaymentAlert

# Export all models
# IMPORTANT: All models MUST be imported here so SQLAlchemy Base can find them!
# This is required for:
# 1. Table creation (Base.metadata.create_all)
# 2. Alembic migrations (autogenerate)
# 3. Relationship resolution
__all__ = ["User", "CreditCard", "Category", "Statement", "Transaction", "Insight", "InsightTransaction", "PaymentAlert"]
