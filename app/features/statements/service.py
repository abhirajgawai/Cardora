"""
Statement processing business logic.

All heavy lifting for PDF upload lives here so the router stays thin.
"""

import logging
import os
from datetime import date, datetime
from decimal import Decimal
from typing import List, Tuple
from uuid import UUID

from sqlalchemy.orm import Session

from app.features.cards.models import CreditCard
from app.features.categories.models import Category
from app.features.statements.models import Statement
from app.features.transactions.models import Transaction
from app.core.gemini_service import (
    extract_card_metadata_from_pdf,
    extract_text_from_pdf,
    match_category_by_name,
    process_statement_pdf,
)
from app.features.insights.alert_service import create_payment_alert
from app.features.payments.services import (
    detect_payment_behavior,
    retroactively_detect_payments,
    update_statement_payment_status,
)

logger = logging.getLogger(__name__)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
MAX_FILE_MB = 10


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_pdf(filename: str, contents: bytes) -> None:
    """Raise ValueError if the file is not a valid PDF within size limits."""
    if not filename.lower().endswith(".pdf"):
        raise ValueError("Only PDF files are allowed")

    file_size_mb = len(contents) / (1024 * 1024)
    if file_size_mb > MAX_FILE_MB:
        raise ValueError(f"File too large ({file_size_mb:.2f} MB). Maximum is {MAX_FILE_MB} MB")

    if not contents.startswith(b"%PDF"):
        raise ValueError("Invalid PDF file — magic bytes not found")


# ---------------------------------------------------------------------------
# File storage
# ---------------------------------------------------------------------------

def save_temp_file(user_id: UUID, filename: str, contents: bytes) -> str:
    """Write raw bytes to a temporary upload path, return the path."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = f"{user_id}_temp_{timestamp}_{filename}".replace(" ", "_")
    path = os.path.join(UPLOAD_DIR, safe)
    with open(path, "wb") as fh:
        fh.write(contents)
    logger.info("PDF saved temporarily to %s", path)
    return path


def rename_to_permanent(
    temp_path: str, user_id: UUID, bank_name: str,
    statement_month: int, statement_year: int, original_filename: str
) -> str:
    """Move temp file to its permanent name, return the new path."""
    safe_filename = (
        f"{user_id}_{bank_name}_{statement_month}_{statement_year}_{original_filename}"
        .replace(" ", "_")
    )
    new_path = os.path.join(UPLOAD_DIR, safe_filename)
    if os.path.exists(new_path):
        os.remove(new_path)
    os.rename(temp_path, new_path)
    logger.info("PDF renamed to %s", new_path)
    return safe_filename, new_path


# ---------------------------------------------------------------------------
# Card management
# ---------------------------------------------------------------------------

def get_or_create_card(db: Session, user_id: UUID, metadata: dict) -> Tuple[CreditCard, bool]:
    """Return (card, created). Creates the card if it does not exist."""
    card = db.query(CreditCard).filter(
        CreditCard.user_id == user_id,
        CreditCard.bank_name == metadata["bank_name"],
        CreditCard.last_four_digits == metadata["last_four_digits"],
    ).first()

    if card:
        logger.info("Found existing card: %s *%s", card.bank_name, card.last_four_digits)
        return card, False

    card = CreditCard(
        user_id=user_id,
        bank_name=metadata["bank_name"],
        card_name=metadata.get("card_type") or metadata["bank_name"],
        last_four_digits=metadata["last_four_digits"],
        card_type=metadata.get("card_type"),
        credit_limit=Decimal(str(metadata["credit_limit"])) if metadata.get("credit_limit") else None,
        is_active=True,
    )
    db.add(card)
    db.commit()
    db.refresh(card)
    logger.info("Auto-created card %s", card.id)
    return card, True


# ---------------------------------------------------------------------------
# Statement management
# ---------------------------------------------------------------------------

def check_duplicate_statement(
    db: Session, card_id: UUID, statement_month: int, statement_year: int
) -> bool:
    return db.query(Statement).filter(
        Statement.card_id == card_id,
        Statement.statement_month == statement_month,
        Statement.statement_year == statement_year,
    ).first() is not None


def _parse_decimal(value) -> Decimal | None:
    try:
        return Decimal(str(value)) if value is not None else None
    except Exception:
        return None


def create_statement_record(
    db: Session, user_id: UUID, card_id: UUID,
    safe_filename: str, statement_month: int, statement_year: int,
    metadata: dict,
) -> Statement:
    due_date = None
    days_until_due = None
    if metadata.get("due_date"):
        try:
            due_date = datetime.strptime(metadata["due_date"], "%Y-%m-%d").date()
            days_until_due = (due_date - date.today()).days
        except ValueError:
            pass

    statement = Statement(
        user_id=user_id,
        card_id=card_id,
        file_name=safe_filename,
        statement_month=statement_month,
        statement_year=statement_year,
        total_transactions=0,
        total_amount=Decimal("0.00"),
        processing_status="processing",
        statement_date=(
            datetime.strptime(metadata["statement_date"], "%Y-%m-%d").date()
            if metadata.get("statement_date") else None
        ),
        due_date=due_date,
        statement_balance=_parse_decimal(metadata.get("statement_balance")),
        minimum_payment_due=_parse_decimal(metadata.get("minimum_payment_due")),
        previous_balance=_parse_decimal(metadata.get("previous_balance")),
        new_charges=_parse_decimal(metadata.get("new_charges")),
        payments_credits=_parse_decimal(metadata.get("payments_credits")),
        interest_charged=_parse_decimal(metadata.get("interest_charged")) or Decimal("0.00"),
        fees_charged=_parse_decimal(metadata.get("fees_charged")) or Decimal("0.00"),
        apr=_parse_decimal(metadata.get("apr")),
        days_until_due=days_until_due,
    )
    db.add(statement)
    db.commit()
    db.refresh(statement)
    return statement


# ---------------------------------------------------------------------------
# Transaction management
# ---------------------------------------------------------------------------

def save_transactions(
    db: Session,
    user_id: UUID,
    card_id: UUID,
    statement: Statement,
    transactions_data: list,
    categories: List[Category],
    statement_month: int,
    statement_year: int,
) -> List[Transaction]:
    saved = []
    for td in transactions_data:
        category = match_category_by_name(td["category_name"], categories)
        try:
            trans_date = datetime.strptime(td["transaction_date"], "%Y-%m-%d").date()
        except (ValueError, KeyError):
            trans_date = date(statement_year, statement_month, 1)

        txn = Transaction(
            user_id=user_id,
            card_id=card_id,
            statement_id=statement.id,
            category_id=category.id if category else None,
            merchant_name=td["merchant_name"],
            amount=Decimal(str(td["amount"])),
            transaction_date=trans_date,
            description=td.get("description"),
            statement_month=statement_month,
            statement_year=statement_year,
            is_recurring=td.get("is_recurring", False),
            confidence_score=Decimal(str(td.get("confidence_score", 0.0))),
        )
        db.add(txn)
        saved.append(txn)

    db.commit()
    for txn in saved:
        db.refresh(txn)
    return saved


# ---------------------------------------------------------------------------
# Post-processing
# ---------------------------------------------------------------------------

def run_payment_detection(
    db: Session, statement: Statement, card: CreditCard
) -> None:
    """Detect payment behaviour and create an alert. Errors are logged, not raised."""
    try:
        behavior = detect_payment_behavior(db, statement)
        if not behavior:
            logger.info("No previous statement — skipping payment detection")
            return

        update_statement_payment_status(db, statement, behavior)
        card_label = f"{card.bank_name} {card.card_name or ''} (...{card.last_four_digits})"
        alert = create_payment_alert(db, statement, behavior, card_label)
        if alert:
            logger.info("Payment alert created: %s", alert.id)
    except Exception:
        logger.exception("Payment detection failed")


def run_retroactive_detection(db: Session, card_id: UUID, user_id: UUID) -> None:
    """Retroactively detect payments for older statements. Errors are logged, not raised."""
    try:
        from app.features.payments.services import retroactively_detect_payments
        count = retroactively_detect_payments(db=db, card_id=card_id, user_id=user_id)
        if count:
            logger.info("Retroactively processed %d statement(s)", count)
    except Exception:
        logger.exception("Retroactive payment detection failed")


# ---------------------------------------------------------------------------
# Top-level orchestrator (called by the router)
# ---------------------------------------------------------------------------

def process_upload(
    db: Session,
    user_id: UUID,
    original_filename: str,
    contents: bytes,
) -> Tuple[Statement, List[Transaction], dict]:
    """
    Full upload pipeline. Returns (statement, transactions, stats).
    Raises ValueError for user-facing errors, Exception for unexpected ones.
    """
    # 1 — validate
    validate_pdf(original_filename, contents)

    # 2 — save temp file
    temp_path = save_temp_file(user_id, original_filename, contents)

    try:
        # 3 — extract text
        pdf_text = extract_text_from_pdf(temp_path)

        # 4 — AI card metadata
        metadata = extract_card_metadata_from_pdf(pdf_text)
        if not metadata.get("bank_name") or not metadata.get("last_four_digits"):
            raise ValueError("Could not extract bank name or card number from PDF")
        if not metadata.get("statement_date"):
            raise ValueError("Could not extract statement date from PDF")

        statement_date = datetime.strptime(metadata["statement_date"], "%Y-%m-%d")
        statement_month = statement_date.month
        statement_year = statement_date.year
        statement_day = statement_date.day

        # 5 — card create/match
        card, _ = get_or_create_card(db, user_id, metadata)

        # sync statement_day on card
        if card.statement_day != str(statement_day):
            card.statement_day = str(statement_day)
            db.commit()

        # 6 — duplicate check
        if check_duplicate_statement(db, card.id, statement_month, statement_year):
            raise ValueError(
                f"Statement for {statement_month}/{statement_year} already exists for this card"
            )

        # 7 — rename file
        safe_filename, file_path = rename_to_permanent(
            temp_path, user_id, card.bank_name,
            statement_month, statement_year, original_filename,
        )
        temp_path = None  # ownership transferred

        # 8 — create statement record
        statement = create_statement_record(
            db, user_id, card.id, safe_filename,
            statement_month, statement_year, metadata,
        )

        # 9 — AI transaction extraction (user-scoped categories)
        categories = db.query(Category).filter(
            (Category.user_id == user_id) | (Category.user_id.is_(None))
        ).all()

        transactions_data, stats = process_statement_pdf(
            pdf_path=file_path,
            categories=categories,
            statement_month=statement_month,
            statement_year=statement_year,
        )

        # 10 — save transactions
        saved = save_transactions(
            db, user_id, card.id, statement,
            transactions_data, categories,
            statement_month, statement_year,
        )

        # 11 — finalise statement
        statement.total_transactions = len(saved)
        statement.total_amount = Decimal(str(stats["total_amount"]))
        statement.ai_confidence_score = Decimal(str(stats["avg_confidence"]))
        statement.processing_status = "completed"
        statement.processed_at = datetime.now()
        statement.insights_status = "processing"
        db.commit()
        db.refresh(statement)

        # 12 — payment detection (non-fatal)
        run_payment_detection(db, statement, card)
        run_retroactive_detection(db, card.id, user_id)

        return statement, saved, stats

    except Exception:
        # clean up temp file if still present
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
        raise
