"""
Payment calculations for debt payoff analysis and recommendations.

This module provides functions to calculate:
- Payoff schedules at different payment amounts
- Interest savings with increased payments
- Personalized payment recommendations
"""
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Optional
import math


class PayoffScenario:
    """
    Represents a debt payoff scenario with specific monthly payment.
    """
    def __init__(
        self,
        monthly_payment: Decimal,
        months_to_payoff: int,
        total_interest_paid: Decimal,
        total_amount_paid: Decimal
    ):
        self.monthly_payment = monthly_payment
        self.months_to_payoff = months_to_payoff
        self.total_interest_paid = total_interest_paid
        self.total_amount_paid = total_amount_paid


class PaymentRecommendation:
    """
    Personalized payment recommendation with savings calculation.
    """
    def __init__(
        self,
        recommended_payment: Decimal,
        payoff_scenario: PayoffScenario,
        interest_saved: Decimal,
        months_saved: int,
        description: str
    ):
        self.recommended_payment = recommended_payment
        self.payoff_scenario = payoff_scenario
        self.interest_saved = interest_saved
        self.months_saved = months_saved
        self.description = description


def calculate_payoff_schedule(
    balance: Decimal,
    apr: Decimal,
    monthly_payment: Decimal,
    max_months: int = 360,
) -> Optional[PayoffScenario]:
    """
    Calculate debt payoff schedule with given monthly payment.

    Uses standard amortization formula:
    - Each month, interest is calculated on remaining balance
    - Payment goes first to interest, then to principal
    - Continues until balance reaches zero

    Args:
        balance: Current debt balance
        apr: Annual Percentage Rate (e.g., 18.99 for 18.99%)
        monthly_payment: Fixed monthly payment amount
        max_months: Maximum months to calculate (prevents infinite loops)

    Returns:
        PayoffScenario or None if cannot pay off (payment too low)
    """
    if balance <= 0:
        return PayoffScenario(
            monthly_payment=Decimal("0"),
            months_to_payoff=0,
            total_interest_paid=Decimal("0"),
            total_amount_paid=Decimal("0")
        )

    if apr <= 0:
        months = int(math.ceil(balance / monthly_payment)) if monthly_payment > 0 else 0
        return PayoffScenario(
            monthly_payment=monthly_payment,
            months_to_payoff=months,
            total_interest_paid=Decimal("0"),
            total_amount_paid=balance
        )

    monthly_interest_rate = apr / Decimal("12") / Decimal("100")

    minimum_interest = balance * monthly_interest_rate

    if monthly_payment <= minimum_interest:
        return None

    remaining_balance = balance
    total_interest_paid = Decimal("0")
    months = 0

    while remaining_balance > 0 and months < max_months:
        months += 1

        interest_charge = (remaining_balance * monthly_interest_rate).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        total_interest_paid += interest_charge

        principal_payment = monthly_payment - interest_charge

        if principal_payment >= remaining_balance:
            remaining_balance = Decimal("0")
        else:
            remaining_balance -= principal_payment

    if months >= max_months:
        return None

    total_amount_paid = balance + total_interest_paid

    return PayoffScenario(
        monthly_payment=monthly_payment,
        months_to_payoff=months,
        total_interest_paid=total_interest_paid.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        total_amount_paid=total_amount_paid.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    )


def calculate_minimum_payment(
    balance: Decimal,
    apr: Decimal,
    minimum_percentage: Decimal = Decimal("2.0"),
    minimum_floor: Decimal = Decimal("25.00")
) -> Decimal:
    """
    Calculate typical credit card minimum payment.

    Most credit cards use the greater of:
    - X% of balance (typically 1-3%)
    - Or a minimum dollar amount (typically $25-$35)

    Args:
        balance: Current balance
        apr: Annual Percentage Rate
        minimum_percentage: Percentage of balance (e.g., 2.0 for 2%)
        minimum_floor: Minimum dollar amount

    Returns:
        Minimum payment amount
    """
    if balance <= 0:
        return Decimal("0")

    percentage_minimum = (balance * minimum_percentage / Decimal("100")).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    monthly_interest_rate = apr / Decimal("12") / Decimal("100")
    interest_charge = (balance * monthly_interest_rate).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    calculated_minimum = max(percentage_minimum + interest_charge, minimum_floor)

    if calculated_minimum > balance:
        return balance

    return calculated_minimum


def generate_payment_recommendations(
    balance: Decimal,
    apr: Decimal,
    minimum_payment: Decimal,
    current_payment: Decimal
) -> List[PaymentRecommendation]:
    """
    Generate personalized payment recommendations.

    Creates 3-4 scenarios:
    1. Minimum payment baseline (what happens if you keep paying minimum)
    2. Pay 2x minimum (moderate acceleration)
    3. Pay off in 12 months (aggressive)
    4. Pay off in 6 months (very aggressive, if feasible)

    Args:
        balance: Current debt balance
        apr: Annual Percentage Rate
        minimum_payment: Minimum payment required
        current_payment: What user currently pays

    Returns:
        List of payment recommendations sorted by monthly payment
    """
    recommendations: List[PaymentRecommendation] = []

    if current_payment > minimum_payment:
        baseline_payment = current_payment
        baseline_label = "Current Payment"
    else:
        baseline_payment = minimum_payment
        baseline_label = "Minimum Payment"

    baseline_scenario = calculate_payoff_schedule(balance, apr, baseline_payment)

    scenarios = []

    double_payment = baseline_payment * Decimal("2")
    double_scenario = calculate_payoff_schedule(balance, apr, double_payment)
    if double_scenario:
        scenarios.append((
            double_payment,
            double_scenario,
            f"Pay 2× {baseline_label.lower()}"
        ))

    if balance > 0 and apr >= 0:
        months = 12
        monthly_rate = apr / Decimal("12") / Decimal("100")

        if monthly_rate > 0:
            numerator = monthly_rate * balance
            denominator = Decimal("1") - (Decimal("1") + monthly_rate) ** (-months)
            payment_12_months = (numerator / denominator).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        else:
            payment_12_months = (balance / Decimal("12")).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )

        scenario_12_months = calculate_payoff_schedule(balance, apr, payment_12_months)
        if scenario_12_months and payment_12_months > baseline_payment:
            scenarios.append((
                payment_12_months,
                scenario_12_months,
                "Pay off in 1 year"
            ))

    if balance > 0 and apr >= 0:
        months = 6
        monthly_rate = apr / Decimal("12") / Decimal("100")

        if monthly_rate > 0:
            numerator = monthly_rate * balance
            denominator = Decimal("1") - (Decimal("1") + monthly_rate) ** (-months)
            payment_6_months = (numerator / denominator).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        else:
            payment_6_months = (balance / Decimal("6")).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )

        if payment_6_months <= baseline_payment * Decimal("3"):
            scenario_6_months = calculate_payoff_schedule(balance, apr, payment_6_months)
            if scenario_6_months and payment_6_months > baseline_payment:
                scenarios.append((
                    payment_6_months,
                    scenario_6_months,
                    "Pay off in 6 months"
                ))

    for payment_amount, scenario, description in scenarios:
        if baseline_scenario:
            interest_saved = baseline_scenario.total_interest_paid - scenario.total_interest_paid
            months_saved = baseline_scenario.months_to_payoff - scenario.months_to_payoff
        else:
            interest_saved = Decimal("0")
            months_saved = 0

        recommendations.append(PaymentRecommendation(
            recommended_payment=payment_amount,
            payoff_scenario=scenario,
            interest_saved=interest_saved,
            months_saved=months_saved,
            description=description
        ))

    recommendations.sort(key=lambda r: r.recommended_payment)

    return recommendations


def calculate_interest_savings(
    balance: Decimal,
    apr: Decimal,
    baseline_payment: Decimal,
    increased_payment: Decimal
) -> Dict[str, Decimal]:
    """
    Calculate interest savings from increased payment.

    Args:
        balance: Current debt balance
        apr: Annual Percentage Rate
        baseline_payment: Current/baseline monthly payment
        increased_payment: Proposed increased monthly payment

    Returns:
        Dictionary with savings metrics
    """
    baseline_scenario = calculate_payoff_schedule(balance, apr, baseline_payment)
    increased_scenario = calculate_payoff_schedule(balance, apr, increased_payment)

    if not baseline_scenario or not increased_scenario:
        return {
            "interest_saved": Decimal("0"),
            "months_saved": Decimal("0"),
            "total_saved": Decimal("0")
        }

    interest_saved = baseline_scenario.total_interest_paid - increased_scenario.total_interest_paid
    months_saved = Decimal(baseline_scenario.months_to_payoff - increased_scenario.months_to_payoff)
    total_saved = baseline_scenario.total_amount_paid - increased_scenario.total_amount_paid

    return {
        "interest_saved": interest_saved.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        "months_saved": months_saved,
        "total_saved": total_saved.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    }
