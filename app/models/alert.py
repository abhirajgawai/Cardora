"""
Payment Alert Model

Alerts for upcoming credit card payments and subscription renewals.

Compare to .NET:
    [Table("payment_alerts", Schema = "cardora")]
    public class PaymentAlert
    {
        public Guid Id { get; set; }
        public Guid UserId { get; set; }
        public string AlertType { get; set; }
        public string Title { get; set; }
        public string Description { get; set; }
        public DateTime DueDate { get; set; }
        public decimal? Amount { get; set; }
        public DateTime CreatedAt { get; set; }
        public DateTime? DismissedAt { get; set; }

        public User User { get; set; }
    }
"""

import uuid
from sqlalchemy import Column, String, ForeignKey, Numeric, DateTime, Date, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.core.database import Base


class PaymentAlert(Base):
    """
    Payment reminders and alerts for users

    Alert Types:
    - payment_due: Credit card payment coming up
    - subscription_renewal: Subscription about to renew
    - unusual_charge: Detected unusual spending

    Example:
        "Chase Sapphire payment due in 3 days ($1,245.80)"
        "Netflix subscription renews tomorrow ($15.99)"
    """

    __tablename__ = "payment_alerts"
    __table_args__ = (
        # Index for fetching user alerts by due date
        Index(
            "ix_payment_alerts_user_due",
            "user_id", "due_date",
            postgresql_using="btree"
        ),

        {"schema": "cardora"}
    )

    # ═══════════════════════════════════════════════════════════════
    # PRIMARY KEY
    # ═══════════════════════════════════════════════════════════════

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )

    # ═══════════════════════════════════════════════════════════════
    # FOREIGN KEYS
    # ═══════════════════════════════════════════════════════════════

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("cardora.users.id"),
        nullable=False
    )

    # ═══════════════════════════════════════════════════════════════
    # ALERT CONTENT
    # ═══════════════════════════════════════════════════════════════

    alert_type = Column(
        String(50),
        nullable=False
    )
    # payment_due, subscription_renewal, unusual_charge

    title = Column(
        String(200),
        nullable=False
    )
    # Example: "Chase Sapphire payment due in 3 days"

    description = Column(
        Text,
        nullable=True
    )
    # Optional detailed description

    due_date = Column(
        Date,
        nullable=True
    )
    # When is this payment due (for payment_due and subscription_renewal)

    amount = Column(
        Numeric(10, 2),
        nullable=True
    )
    # Payment amount (if known)

    # ═══════════════════════════════════════════════════════════════
    # TIMESTAMPS
    # ═══════════════════════════════════════════════════════════════

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    dismissed_at = Column(
        DateTime(timezone=True),
        nullable=True
    )
    # NULL = alert still active

    # ═══════════════════════════════════════════════════════════════
    # RELATIONSHIPS
    # ═══════════════════════════════════════════════════════════════

    user = relationship(
        "User",
        back_populates="payment_alerts"
    )

    def __repr__(self):
        return f"<PaymentAlert {self.alert_type}: {self.title}>"
