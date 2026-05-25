"""
Payment Alert Model

Alerts for credit card payment behavior: missed payments, minimum-only payments,
partial payments, and positive reinforcement for full payment.
"""

import uuid
from sqlalchemy import Column, String, ForeignKey, Numeric, DateTime, Date, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.core.database import Base


class PaymentAlert(Base):
    """
    Payment behavior alert for a user's credit card statement.

    Alert Types:
    - payment_warning: Covers all payment behavior (full, partial, minimum, late, no payment)

    Severity (stored in description JSON under __DATA__):
    - low: Paid in full
    - medium: Partial payment
    - high: Minimum payment only
    - critical: Late or no payment detected
    """

    __tablename__ = "payment_alerts"
    __table_args__ = (
        Index(
            "ix_payment_alerts_user_due",
            "user_id", "due_date",
            postgresql_using="btree"
        ),
        {"schema": "cardora"}
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)

    user_id = Column(UUID(as_uuid=True), ForeignKey("cardora.users.id"), nullable=False)

    alert_type = Column(String(50), nullable=False)

    title = Column(String(200), nullable=False)

    description = Column(Text, nullable=True)

    due_date = Column(Date, nullable=True)

    amount = Column(Numeric(10, 2), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    dismissed_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="payment_alerts")

    def __repr__(self):
        return f"<PaymentAlert {self.alert_type}: {self.title}>"
