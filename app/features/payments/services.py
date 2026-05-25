"""
Payment detection and analysis service.

This module detects payment behavior by comparing consecutive statements
and determines if users paid in full, partial, minimum, or nothing.
"""
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, desc
from sqlalchemy.orm import Session

from app.features.statements.models import Statement


class PaymentBehavior:
    """
    Payment behavior detection result.
    """
    def __init__(
        self,
        payment_status: str,
        amount_paid: Decimal,
        revolving_balance: Decimal,
        estimated_monthly_interest: Decimal,
        estimated_annual_cost: Decimal,
        previous_statement_balance: Decimal,
        paid_percentage: Decimal
    ):
        self.payment_status = payment_status
        self.amount_paid = amount_paid
        self.revolving_balance = revolving_balance
        self.estimated_monthly_interest = estimated_monthly_interest
        self.estimated_annual_cost = estimated_annual_cost
        self.previous_statement_balance = previous_statement_balance
        self.paid_percentage = paid_percentage


def get_previous_statement(
    db: Session,
    credit_card_id: UUID,
    current_statement_date: datetime
) -> Optional[Statement]:
    """
    Get the previous statement for a credit card.

    Args:
        db: Database session
        credit_card_id: Credit card ID
        current_statement_date: Current statement date

    Returns:
        Previous statement or None if not found
    """
    return (
        db.query(Statement)
        .filter(
            and_(
                Statement.card_id == credit_card_id,
                Statement.statement_date < current_statement_date,
                Statement.statement_date.isnot(None)
            )
        )
        .order_by(desc(Statement.statement_date))
        .first()
    )


def detect_payment_behavior(
    db: Session,
    statement: Statement
) -> Optional[PaymentBehavior]:
    """
    Detect payment behavior by comparing with previous statement.

    Logic:
    1. Find previous statement for same card
    2. Calculate amount paid: previous_balance difference
    3. Determine payment status (paid_full, partial_paid, minimum_paid, late, no_payment)
    4. Calculate revolving balance and interest projections

    Args:
        db: Database session
        statement: Current statement to analyze

    Returns:
        PaymentBehavior object or None if cannot detect
    """
    if not statement.statement_date:
        return None

    previous_statement = get_previous_statement(
        db,
        statement.card_id,
        statement.statement_date
    )

    if not previous_statement:
        return None

    if not previous_statement.statement_balance:
        return None

    # ════════════════════════════════════════════════════════════════
    # ════════════════════════════════════════════════════════════════
    #
    #

    previous_statement_balance = previous_statement.statement_balance
    current_previous_balance = statement.previous_balance or Decimal("0")
    payments_this_cycle = statement.payments_credits or Decimal("0")

    print(f"[PAYMENT DETECTION] Comparing statements:")
    print(f"  Previous: {previous_statement.statement_month}/{previous_statement.statement_year}")
    print(f"  Current:  {statement.statement_month}/{statement.statement_year}")
    print(f"[PAYMENT DETECTION] Data from current statement:")
    print(f"  Previous statement_balance: ${previous_statement_balance:,.2f}")
    print(f"  Current previous_balance:   ${current_previous_balance:,.2f}")
    print(f"  Payments & Credits (this cycle): ${payments_this_cycle:,.2f}")

    if payments_this_cycle > 0:
        amount_paid = payments_this_cycle
        print(f"[PAYMENT DETECTION] Using METHOD A (payments during cycle)")
        print(f"  Amount paid = ${amount_paid:,.2f}")
    else:
        amount_paid = previous_statement_balance - current_previous_balance
        print(f"[PAYMENT DETECTION] Using METHOD B (previous balance reduction)")
        print(f"  Amount paid = ${previous_statement_balance:,.2f} - ${current_previous_balance:,.2f}")
        print(f"  = ${amount_paid:,.2f}")

        if amount_paid < 0:
            amount_paid = Decimal("0")
            print(f"  Adjusted to $0.00 (negative payment not valid)")

    # ════════════════════════════════════════════════════════════════
    # ════════════════════════════════════════════════════════════════

    previous_minimum_payment = previous_statement.minimum_payment_due or Decimal("0")
    paid_percentage = (amount_paid / previous_statement_balance * 100) if previous_statement_balance > 0 else Decimal("0")

    tolerance = Decimal("1.00")

    if amount_paid >= (previous_statement_balance - tolerance):
        payment_status = "paid_full"
        revolving_balance = Decimal("0")

    elif amount_paid >= previous_minimum_payment and previous_minimum_payment > 0:
        if abs(amount_paid - previous_minimum_payment) < tolerance:
            payment_status = "minimum_paid"
        else:
            payment_status = "partial_paid"

        revolving_balance = previous_statement_balance - amount_paid

    elif amount_paid > 0:
        payment_status = "late"
        revolving_balance = previous_statement_balance - amount_paid

    else:
        payment_status = "no_payment"
        revolving_balance = previous_statement_balance

    # ════════════════════════════════════════════════════════════════
    # ════════════════════════════════════════════════════════════════

    apr = statement.apr or Decimal("0")

    if revolving_balance > 0 and apr > 0:
        estimated_monthly_interest = revolving_balance * (apr / Decimal("12") / Decimal("100"))

        estimated_annual_cost = estimated_monthly_interest * Decimal("12")
    else:
        estimated_monthly_interest = Decimal("0")
        estimated_annual_cost = Decimal("0")

    # ════════════════════════════════════════════════════════════════
    # ════════════════════════════════════════════════════════════════

    return PaymentBehavior(
        payment_status=payment_status,
        amount_paid=amount_paid,
        revolving_balance=revolving_balance,
        estimated_monthly_interest=estimated_monthly_interest,
        estimated_annual_cost=estimated_annual_cost,
        previous_statement_balance=previous_statement_balance,
        paid_percentage=paid_percentage
    )


def update_statement_payment_status(
    db: Session,
    statement: Statement,
    payment_behavior: PaymentBehavior
) -> Statement:
    """
    Update statement with payment detection results.

    Args:
        db: Database session
        statement: Statement to update
        payment_behavior: Payment behavior analysis

    Returns:
        Updated statement
    """
    statement.payment_status = payment_behavior.payment_status
    statement.amount_paid = payment_behavior.amount_paid
    statement.revolving_balance = payment_behavior.revolving_balance
    statement.estimated_monthly_interest = payment_behavior.estimated_monthly_interest
    statement.estimated_annual_cost = payment_behavior.estimated_annual_cost
    statement.payment_detected_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(statement)

    return statement


def retroactively_detect_payments(
    db: Session,
    card_id: UUID,
    user_id: UUID
) -> int:
    """
    Retroactively detect payment behavior for all statements on a card.

    This is called after uploading a new statement to fill in any gaps
    caused by out-of-order uploads.

    Example scenario:
    - User uploads Sept statement first → No alert (no previous statement)
    - User uploads July statement → Alert created for July vs nothing
    - User uploads Aug statement → Alert created for Aug vs July
    - This function runs → Alert created for Sept vs Aug (retroactively!)

    Args:
        db: Database session
        card_id: Credit card ID to process
        user_id: User ID (for creating alerts)

    Returns:
        Number of statements that were retroactively processed
    """
    from app.features.insights.alert_service import create_payment_alert
    from app.features.cards.models import CreditCard

    print(f"[RETROACTIVE] Starting retroactive payment detection for card {card_id}")

    statements = (
        db.query(Statement)
        .filter(
            Statement.card_id == card_id,
            Statement.user_id == user_id,
            Statement.statement_date.isnot(None)
        )
        .order_by(Statement.statement_date.asc())
        .all()
    )

    if len(statements) < 2:
        print(f"[RETROACTIVE] Only {len(statements)} statement(s) found - need at least 2 for comparison")
        return 0

    print(f"[RETROACTIVE] Found {len(statements)} statements to check")

    card = db.query(CreditCard).filter(CreditCard.id == card_id).first()
    card_name = f"{card.bank_name} {card.card_name or ''} (...{card.last_four_digits})" if card else "Credit Card"

    processed_count = 0

    for i in range(1, len(statements)):
        current_statement = statements[i]

        if current_statement.payment_detected_at is not None:
            print(f"[RETROACTIVE] Skipping statement {i+1}/{len(statements)} - already processed")
            continue

        print(f"[RETROACTIVE] Processing statement {i+1}/{len(statements)}: {current_statement.statement_month}/{current_statement.statement_year}")

        payment_behavior = detect_payment_behavior(db, current_statement)

        if payment_behavior:
            update_statement_payment_status(db, current_statement, payment_behavior)

            try:
                alert = create_payment_alert(db, current_statement, payment_behavior, card_name)
                if alert:
                    print(f"[RETROACTIVE] ✓ Created alert: {alert.title}")
                    processed_count += 1
                else:
                    print(f"[RETROACTIVE] No alert created (status: {payment_behavior.payment_status})")
            except Exception as e:
                print(f"[RETROACTIVE] Warning: Failed to create alert: {str(e)}")
        else:
            print(f"[RETROACTIVE] No payment behavior detected (no previous statement)")

    print(f"[RETROACTIVE] Completed: {processed_count} statement(s) retroactively processed")
    return processed_count
