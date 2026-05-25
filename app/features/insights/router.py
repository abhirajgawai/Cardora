"""
Insights Router — Payment Alerts and Debt Payoff

Endpoints:
- GET  /insights/payment-alerts                     List user's payment alerts
- GET  /insights/payment-alerts/card/{card_id}      Alerts for a specific card
- PUT  /insights/payment-alerts/{alert_id}/dismiss  Dismiss an alert
- POST /insights/calculate-payoff                   Debt payoff calculator
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.features.auth.models import User
from app.features.insights.models import PaymentAlert
from app.features.statements.models import Statement
from app.features.cards.models import CreditCard
from app.features.auth.jwt import get_current_user
from app.features.insights.alert_service import dismiss_alert
from app.features.payments.calculations import calculate_payoff_schedule


router = APIRouter(
    prefix="/insights",
    tags=["Insights"]
)


# ═══════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════

@router.get(
    "/payment-alerts",
    status_code=status.HTTP_200_OK,
    summary="Get all payment alerts for current user"
)
async def get_payment_alerts(
    include_dismissed: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(PaymentAlert).filter(PaymentAlert.user_id == current_user.id)

    if not include_dismissed:
        query = query.filter(PaymentAlert.dismissed_at.is_(None))

    alerts = query.order_by(desc(PaymentAlert.created_at)).all()

    result = []
    for alert in alerts:
        description_text = alert.description or ""
        alert_data = None

        if "__DATA__" in description_text:
            parts = description_text.split("__DATA__")
            description_text = parts[0].strip()
            if len(parts) > 1:
                try:
                    import json
                    alert_data = json.loads(parts[1].strip())
                except Exception:
                    pass

        alert_dict = {
            "id": str(alert.id),
            "alert_type": alert.alert_type,
            "title": alert.title,
            "description": description_text,
            "due_date": alert.due_date.isoformat() if alert.due_date else None,
            "amount": float(alert.amount) if alert.amount else None,
            "created_at": alert.created_at.isoformat(),
            "dismissed_at": alert.dismissed_at.isoformat() if alert.dismissed_at else None
        }

        if alert_data:
            alert_dict["data"] = alert_data

        result.append(alert_dict)

    return {"alerts": result, "count": len(result)}


@router.get(
    "/payment-alerts/card/{card_id}",
    status_code=status.HTTP_200_OK,
    summary="Get payment alerts for a specific credit card"
)
async def get_payment_alerts_by_card(
    card_id: str,
    include_dismissed: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        card_uuid = UUID(card_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid card ID format")

    card = db.query(CreditCard).filter(
        CreditCard.id == card_uuid,
        CreditCard.user_id == current_user.id
    ).first()

    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credit card not found")

    statements = db.query(Statement).filter(Statement.card_id == card_uuid).all()
    statement_due_dates = [s.due_date for s in statements if s.due_date]

    query = db.query(PaymentAlert).filter(
        PaymentAlert.user_id == current_user.id,
        PaymentAlert.due_date.in_(statement_due_dates) if statement_due_dates else False
    )

    if not include_dismissed:
        query = query.filter(PaymentAlert.dismissed_at.is_(None))

    alerts = query.order_by(desc(PaymentAlert.created_at)).all()

    result = []
    for alert in alerts:
        description_text = alert.description or ""
        alert_data = None

        if "__DATA__" in description_text:
            parts = description_text.split("__DATA__")
            description_text = parts[0].strip()
            if len(parts) > 1:
                try:
                    import json
                    alert_data = json.loads(parts[1].strip())
                except Exception:
                    pass

        alert_dict = {
            "id": str(alert.id),
            "alert_type": alert.alert_type,
            "title": alert.title,
            "description": description_text,
            "due_date": alert.due_date.isoformat() if alert.due_date else None,
            "amount": float(alert.amount) if alert.amount else None,
            "created_at": alert.created_at.isoformat(),
            "dismissed_at": alert.dismissed_at.isoformat() if alert.dismissed_at else None
        }

        if alert_data:
            alert_dict["data"] = alert_data

        result.append(alert_dict)

    return {"card_id": str(card_uuid), "card_name": card.card_name, "alerts": result, "count": len(result)}


@router.put(
    "/payment-alerts/{alert_id}/dismiss",
    status_code=status.HTTP_200_OK,
    summary="Dismiss a payment alert"
)
async def dismiss_payment_alert(
    alert_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        alert_uuid = UUID(alert_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid alert ID format")

    dismissed = dismiss_alert(db, alert_uuid, current_user.id)

    if not dismissed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment alert not found")

    return {
        "message": "Alert dismissed successfully",
        "alert": {"id": str(dismissed.id), "dismissed_at": dismissed.dismissed_at.isoformat()}
    }


# ═══════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════

@router.post(
    "/calculate-payoff",
    status_code=status.HTTP_200_OK,
    summary="Calculate debt payoff scenarios"
)
async def calculate_debt_payoff(
    balance: float,
    apr: float,
    monthly_payment: float,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from decimal import Decimal

    if balance <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Balance must be greater than 0")
    if apr < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="APR cannot be negative")
    if monthly_payment <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Monthly payment must be greater than 0")

    scenario = calculate_payoff_schedule(
        balance=Decimal(str(balance)),
        apr=Decimal(str(apr)),
        monthly_payment=Decimal(str(monthly_payment))
    )

    if not scenario:
        return {
            "error": "Cannot calculate payoff - monthly payment is too low to cover interest",
            "minimum_payment_needed": round(balance * (apr / 12 / 100), 2)
        }

    return {
        "input": {"balance": balance, "apr": apr, "monthly_payment": monthly_payment},
        "result": {
            "months_to_payoff": scenario.months_to_payoff,
            "total_interest_paid": float(scenario.total_interest_paid),
            "total_amount_paid": float(scenario.total_amount_paid),
            "payoff_date_estimate": f"{scenario.months_to_payoff} months from now"
        }
    }
