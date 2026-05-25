"""Payment alert generation service."""

import json
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, Dict, Any, List
from uuid import UUID

from sqlalchemy.orm import Session

from app.features.insights.models import PaymentAlert
from app.features.statements.models import Statement
from app.features.payments.services import PaymentBehavior
from app.features.payments.calculations import generate_payment_recommendations


class AlertSeverity:
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


def get_alert_severity(payment_status: str) -> str:
    severity_map = {
        "paid_full": AlertSeverity.LOW,
        "partial_paid": AlertSeverity.MEDIUM,
        "minimum_paid": AlertSeverity.HIGH,
        "late": AlertSeverity.CRITICAL,
        "no_payment": AlertSeverity.CRITICAL,
    }
    return severity_map.get(payment_status, AlertSeverity.MEDIUM)


def generate_alert_title(
    payment_status: str,
    card_name: str,
    amount_paid: Decimal,
    statement_balance: Decimal,
) -> str:
    titles = {
        "paid_full": f"✓ {card_name} - Paid in Full!",
        "partial_paid": f"⚠️ {card_name} - Partial Payment Made",
        "minimum_paid": f"⚠️ {card_name} - Minimum Payment Only",
        "late": f"🚨 {card_name} - Payment Below Minimum",
        "no_payment": f"🚨 CRITICAL: {card_name} - No Payment Detected",
    }
    return titles.get(payment_status, f"ℹ️ {card_name} - Payment Status Update")


def generate_educational_content(
    payment_status: str,
    revolving_balance: Decimal,
    estimated_monthly_interest: Decimal,
    estimated_annual_cost: Decimal,
) -> Dict[str, Any]:
    if payment_status == "paid_full":
        return {
            "message": "Excellent! Paying your balance in full means you pay zero interest.",
            "tips": [
                "Keep up this habit to maximize your credit score",
                "You're using credit cards as a tool, not a trap",
                "Consider using rewards to offset future purchases",
            ],
        }

    if payment_status == "partial_paid":
        return {
            "debt_warning": "When you don't pay the full balance, you're charged interest on the remaining amount.",
            "interest_explanation": (
                f"Your revolving balance of ${revolving_balance:,.2f} will cost you "
                f"${estimated_monthly_interest:,.2f} in interest next month."
            ),
            "annual_impact": (
                f"If this continues, you'll pay ${estimated_annual_cost:,.2f} in interest over the next year."
            ),
            "action_steps": [
                "Try to pay more than the minimum each month",
                "Even an extra $50-100 can save significant interest",
                "Create a budget to identify extra payment capacity",
            ],
        }

    if payment_status == "minimum_paid":
        return {
            "debt_warning": "⚠️ MINIMUM PAYMENT TRAP: Paying only the minimum keeps you in debt for years.",
            "minimum_trap_explanation": (
                "Credit card companies design minimum payments to maximise their profit. "
                "Most of your payment goes to interest, barely touching the principal."
            ),
            "real_cost": (
                f"At minimum payments, your ${revolving_balance:,.2f} balance could take "
                f"7-10 years to pay off and cost ${estimated_annual_cost * Decimal('5'):,.2f}+ in interest."
            ),
            "urgent_actions": [
                "PRIORITY: Pay more than the minimum — even $25 extra helps",
                "Stop using this card for new purchases",
                "Consider a balance transfer to a 0% APR card",
                "Create a debt payoff plan immediately",
            ],
        }

    if payment_status in ("late", "no_payment"):
        return {
            "critical_warning": "🚨 URGENT: Missing payments has serious consequences!",
            "immediate_consequences": [
                "Late fee: Typically $25–$39 (charged next cycle)",
                "Credit score damage: Payment history is 35% of your score",
                "Penalty APR: Your rate could increase to 29.99%",
            ],
            "take_action_now": [
                "1. Make at least the minimum payment TODAY",
                "2. Set up autopay to prevent future missed payments",
                "3. Contact your card issuer if you're having financial difficulties",
            ],
        }

    return {"message": "Monitor your payment behaviour to avoid interest charges."}


def generate_payment_recommendations_text(
    statement: Statement,
    payment_behavior: PaymentBehavior,
) -> List[str]:
    if payment_behavior.payment_status == "paid_full":
        return ["Keep paying in full to avoid interest charges!"]

    balance = payment_behavior.revolving_balance
    apr = statement.apr or Decimal("0")
    minimum_payment = statement.minimum_payment_due or Decimal("25")
    current_payment = payment_behavior.amount_paid

    payment_recs = generate_payment_recommendations(
        balance=balance,
        apr=apr,
        minimum_payment=minimum_payment,
        current_payment=current_payment,
    )

    recommendations = []
    for rec in payment_recs:
        scenario = rec.payoff_scenario
        savings_text = (
            f"(save ${rec.interest_saved:,.2f} in interest)" if rec.interest_saved > 0 else ""
        )
        recommendations.append(
            f"Pay ${rec.recommended_payment:,.2f}/month → "
            f"Pay off in {scenario.months_to_payoff} months {savings_text}"
        )

    if apr > Decimal("15") and balance > Decimal("1000") and statement.estimated_annual_cost:
        recommendations.append(
            f"Consider balance transfer to 0% APR card to eliminate "
            f"${statement.estimated_annual_cost:,.2f}/year in interest"
        )

    return recommendations


def create_payment_alert(
    db: Session,
    statement: Statement,
    payment_behavior: PaymentBehavior,
    card_name: str,
) -> Optional[PaymentAlert]:
    """Create a payment alert from detected payment behaviour. Returns None if status is pending."""
    if payment_behavior.payment_status == "pending":
        return None

    severity = get_alert_severity(payment_behavior.payment_status)
    title = generate_alert_title(
        payment_status=payment_behavior.payment_status,
        card_name=card_name,
        amount_paid=payment_behavior.amount_paid,
        statement_balance=payment_behavior.previous_statement_balance,
    )
    educational_content = generate_educational_content(
        payment_status=payment_behavior.payment_status,
        revolving_balance=payment_behavior.revolving_balance,
        estimated_monthly_interest=payment_behavior.estimated_monthly_interest,
        estimated_annual_cost=payment_behavior.estimated_annual_cost,
    )
    recommendations = generate_payment_recommendations_text(statement, payment_behavior)

    description_data = {
        "payment_status": payment_behavior.payment_status,
        "severity": severity,
        "financial_summary": {
            "amount_paid": float(payment_behavior.amount_paid),
            "previous_balance": float(payment_behavior.previous_statement_balance),
            "revolving_balance": float(payment_behavior.revolving_balance),
            "paid_percentage": float(payment_behavior.paid_percentage),
            "minimum_payment": float(statement.minimum_payment_due or Decimal("0")),
        },
        "interest_breakdown": {
            "monthly_interest": float(payment_behavior.estimated_monthly_interest),
            "annual_cost": float(payment_behavior.estimated_annual_cost),
            "apr": float(statement.apr or Decimal("0")),
        },
        "recommendations": recommendations,
        "educational_content": educational_content,
    }

    status = payment_behavior.payment_status
    if status == "paid_full":
        description_text = (
            f"Great job! You paid ${payment_behavior.amount_paid:,.2f} "
            f"(the full balance). No interest charged. Keep it up!"
        )
    elif status == "partial_paid":
        description_text = (
            f"You paid ${payment_behavior.amount_paid:,.2f} "
            f"({payment_behavior.paid_percentage:.1f}% of balance). "
            f"Remaining balance: ${payment_behavior.revolving_balance:,.2f}. "
            f"Interest this month: ${payment_behavior.estimated_monthly_interest:,.2f}."
        )
    elif status == "minimum_paid":
        description_text = (
            f"You paid ${payment_behavior.amount_paid:,.2f} (minimum only). "
            f"Remaining balance: ${payment_behavior.revolving_balance:,.2f}. "
            f"At this rate, you'll pay ${payment_behavior.estimated_annual_cost:,.2f} "
            f"in interest per year. Consider paying more to save on interest."
        )
    else:
        description_text = (
            f"⚠️ Payment issue detected. "
            f"Previous balance: ${payment_behavior.previous_statement_balance:,.2f}. "
            f"Amount paid: ${payment_behavior.amount_paid:,.2f}. "
            f"Please make a payment immediately to avoid late fees and credit score damage."
        )

    full_description = f"{description_text}\n\n__DATA__\n{json.dumps(description_data, indent=2)}"

    alert = PaymentAlert(
        user_id=statement.user_id,
        title=title,
        description=full_description,
        due_date=statement.due_date,
        amount=payment_behavior.revolving_balance,
        dismissed_at=None,
    )

    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def check_existing_alert(db: Session, user_id: UUID, statement_id: UUID) -> bool:
    """Return True if an alert already exists for this statement."""
    from app.features.insights.models import PaymentAlert  # avoid circular at module level

    statement = (
        db.query(Statement)
        .filter(Statement.id == statement_id, Statement.user_id == user_id)
        .first()
    )
    if not statement:
        return False

    existing = (
        db.query(PaymentAlert)
        .filter(
            PaymentAlert.user_id == user_id,
            PaymentAlert.due_date == statement.due_date,
        )
        .first()
    )
    return existing is not None


def dismiss_alert(
    db: Session,
    alert_id: UUID,
    user_id: UUID,
) -> Optional[PaymentAlert]:
    """Mark an alert as dismissed. Returns None if not found or not owned by user."""
    alert = (
        db.query(PaymentAlert)
        .filter(PaymentAlert.id == alert_id, PaymentAlert.user_id == user_id)
        .first()
    )
    if not alert:
        return None

    alert.dismissed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(alert)
    return alert
