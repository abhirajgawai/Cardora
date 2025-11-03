"""
Statement Router - PDF Statement Upload and Management

THIS IS THE CORE FEATURE OF CARDORA!

Endpoints:
- POST /statements/upload - Upload PDF statement (AI extraction)
- GET /statements - List all statements
- GET /statements/{statement_id} - Get statement details

Compare to .NET: Like StatementsController with file upload
"""

import os
import time
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.features.auth.models import User
from app.features.cards.models import CreditCard
from app.features.categories.models import Category
from app.features.statements.models import Statement
from app.features.transactions.models import Transaction
from app.features.statements.schemas import (
    StatementResponse,
    StatementUploadResponse,
    StatementListResponse,
    StatementStatusResponse
)
from app.features.transactions.schemas import TransactionResponse
from app.features.auth.jwt import get_current_user
from app.core.gemini_service import (
    process_statement_pdf,
    match_category_by_name,
    extract_text_from_pdf,
    extract_card_metadata_from_pdf
)
# from app.services.insights_orchestrator import generate_insights_background  # Disabled for now

# ═══════════════════════════════════════════════════════════════════
# ROUTER SETUP
# ═══════════════════════════════════════════════════════════════════

router = APIRouter(
    prefix="/statements",
    tags=["Statements"]
)

# Upload directory
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ═══════════════════════════════════════════════════════════════════
# POST /statements/upload - MAIN FEATURE!
# ═══════════════════════════════════════════════════════════════════

@router.post(
    "/upload",
    response_model=StatementUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload PDF statement (AI extraction)",
    description="Upload credit card PDF statement and automatically extract transactions using AI"
)
async def upload_statement(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="PDF statement file"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload PDF statement and extract EVERYTHING automatically with AI

    THE CORE FEATURE OF CARDORA - FULLY AUTOMATIC!

    Process:
    1. Validate file (PDF only, max 10MB)
    2. Save PDF to uploads folder
    3. Extract text from PDF
    4. Use Gemini AI to extract card metadata:
       - Bank name, card type, last 4 digits
       - Statement date, due date
       - Credit limit, current balance
    5. Auto-create or find credit card
    6. Use Gemini AI to extract transactions
    7. Categorize transactions automatically
    8. Save statement and all transactions to database
    9. Return complete result with statistics

    Form Data:
    - **file**: PDF file (max 10MB) - THAT'S IT!

    Returns:
    - Card information (auto-created or matched)
    - Statement metadata
    - List of all extracted transactions
    - Processing statistics
    - Success message

    Example Usage:
    Just upload your CITI or SC Bank statement PDF,
    we handle everything automatically!
    """

    start_time = time.time()

    # ══════════════════════════════════════════════════════════════
    # STEP 1: Validate File
    # ══════════════════════════════════════════════════════════════

    # Check file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )

    # Check file size (max 10MB)
    contents = await file.read()
    file_size_mb = len(contents) / (1024 * 1024)

    if file_size_mb > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large ({file_size_mb:.2f}MB). Maximum size is 10MB"
        )

    # ══════════════════════════════════════════════════════════════
    # STEP 2: Save PDF File (Temporarily)
    # ══════════════════════════════════════════════════════════════

    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_filename = f"{current_user.id}_temp_{timestamp}_{file.filename}"
    temp_filename = temp_filename.replace(" ", "_")

    file_path = os.path.join(UPLOAD_DIR, temp_filename)

    with open(file_path, "wb") as f:
        f.write(contents)

    print(f"[INFO] PDF saved temporarily to: {file_path}")

    # ══════════════════════════════════════════════════════════════
    # STEP 3: Extract Text from PDF
    # ══════════════════════════════════════════════════════════════

    try:
        print("[INFO] Extracting text from PDF...")
        pdf_text = extract_text_from_pdf(file_path)
    except Exception as e:
        os.remove(file_path)  # Clean up
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract text from PDF: {str(e)}"
        )

    # ══════════════════════════════════════════════════════════════
    # STEP 4: Extract Card Metadata with AI
    # ══════════════════════════════════════════════════════════════

    try:
        print("[INFO] Extracting card metadata with AI...")
        card_metadata = extract_card_metadata_from_pdf(pdf_text)

        # Validate required fields
        if not card_metadata.get("bank_name") or not card_metadata.get("last_four_digits"):
            raise Exception("Could not extract bank name or card number from PDF")

        if not card_metadata.get("statement_date"):
            raise Exception("Could not extract statement date from PDF")

    except Exception as e:
        os.remove(file_path)  # Clean up
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI failed to extract card information: {str(e)}"
        )

    # ══════════════════════════════════════════════════════════════
    # STEP 5: Auto-Create or Find Credit Card
    # ══════════════════════════════════════════════════════════════

    # Try to find existing card (match by bank + last 4 digits)
    card = db.query(CreditCard).filter(
        CreditCard.user_id == current_user.id,
        CreditCard.bank_name == card_metadata["bank_name"],
        CreditCard.last_four_digits == card_metadata["last_four_digits"]
    ).first()

    if card:
        print(f"[INFO] Found existing card: {card.bank_name} ending in {card.last_four_digits}")
        card_created = False
    else:
        # Auto-create new card
        print(f"[INFO] Creating new card: {card_metadata['bank_name']} ending in {card_metadata['last_four_digits']}")

        card = CreditCard(
            user_id=current_user.id,
            bank_name=card_metadata["bank_name"],
            card_name=card_metadata.get("card_type") or card_metadata["bank_name"],
            last_four_digits=card_metadata["last_four_digits"],
            card_type=card_metadata.get("card_type"),
            credit_limit=Decimal(str(card_metadata["credit_limit"])) if card_metadata.get("credit_limit") else None,
            is_active=True
        )

        db.add(card)
        db.commit()
        db.refresh(card)

        print(f"[SUCCESS] Auto-created card: {card.id}")
        card_created = True

    # ══════════════════════════════════════════════════════════════
    # STEP 6: Extract Statement Month/Year from Date
    # ══════════════════════════════════════════════════════════════

    try:
        statement_date = datetime.strptime(card_metadata["statement_date"], "%Y-%m-%d")
        statement_month = statement_date.month
        statement_year = statement_date.year
        statement_day = statement_date.day

        print(f"[INFO] Statement period: {statement_month}/{statement_year}")
        print(f"[INFO] Statement date: Day {statement_day} of the month")

        # Update card's statement_day if not already set or if different
        # This helps users see when future statements will be generated
        if card.statement_day != str(statement_day):
            card.statement_day = str(statement_day)
            db.commit()
            db.refresh(card)
            print(f"[INFO] Updated card statement_day to: {statement_day}")

    except Exception as e:
        if card_created:
            db.delete(card)  # Rollback card creation
            db.commit()
        os.remove(file_path)  # Clean up
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Invalid statement date format: {str(e)}"
        )

    # ══════════════════════════════════════════════════════════════
    # STEP 7: Check for Duplicate Statement
    # ══════════════════════════════════════════════════════════════

    existing_statement = db.query(Statement).filter(
        Statement.card_id == card.id,
        Statement.statement_month == statement_month,
        Statement.statement_year == statement_year
    ).first()

    if existing_statement:
        if card_created:
            db.delete(card)  # Rollback card creation
            db.commit()
        os.remove(file_path)  # Clean up
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Statement for {statement_month}/{statement_year} already exists for this card"
        )

    # ══════════════════════════════════════════════════════════════
    # STEP 8: Rename PDF File (Now That We Know Card Info)
    # ══════════════════════════════════════════════════════════════

    # Rename to permanent filename with card info
    safe_filename = f"{current_user.id}_{card.bank_name}_{statement_month}_{statement_year}_{file.filename}"
    safe_filename = safe_filename.replace(" ", "_")

    new_file_path = os.path.join(UPLOAD_DIR, safe_filename)

    # Remove existing file if it exists (allow re-upload)
    if os.path.exists(new_file_path):
        os.remove(new_file_path)

    os.rename(file_path, new_file_path)
    file_path = new_file_path

    print(f"[INFO] PDF renamed to: {file_path}")

    # ══════════════════════════════════════════════════════════════
    # STEP 9: Create Statement Record (processing status)
    # ══════════════════════════════════════════════════════════════

    # Calculate days until due
    from datetime import date as date_class

    days_until_due = None
    if card_metadata.get("due_date"):
        try:
            due_date_obj = datetime.strptime(card_metadata["due_date"], "%Y-%m-%d").date()
            today = date_class.today()
            days_until_due = (due_date_obj - today).days
        except:
            pass

    statement = Statement(
        user_id=current_user.id,
        card_id=card.id,
        file_name=safe_filename,
        statement_month=statement_month,
        statement_year=statement_year,
        total_transactions=0,
        total_amount=Decimal("0.00"),
        processing_status="processing",
        ai_confidence_score=None,
        processed_at=None,
        # Balance & Payment Tracking Fields
        statement_date=datetime.strptime(card_metadata["statement_date"], "%Y-%m-%d").date() if card_metadata.get("statement_date") else None,
        due_date=datetime.strptime(card_metadata["due_date"], "%Y-%m-%d").date() if card_metadata.get("due_date") else None,
        statement_balance=Decimal(str(card_metadata["statement_balance"])) if card_metadata.get("statement_balance") else None,
        minimum_payment_due=Decimal(str(card_metadata["minimum_payment_due"])) if card_metadata.get("minimum_payment_due") else None,
        previous_balance=Decimal(str(card_metadata["previous_balance"])) if card_metadata.get("previous_balance") else None,
        new_charges=Decimal(str(card_metadata["new_charges"])) if card_metadata.get("new_charges") else None,
        payments_credits=Decimal(str(card_metadata["payments_credits"])) if card_metadata.get("payments_credits") else None,
        interest_charged=Decimal(str(card_metadata["interest_charged"])) if card_metadata.get("interest_charged") else Decimal("0.00"),
        fees_charged=Decimal(str(card_metadata["fees_charged"])) if card_metadata.get("fees_charged") else Decimal("0.00"),
        apr=Decimal(str(card_metadata["apr"])) if card_metadata.get("apr") else None,
        payment_status="pending",  # Will be updated by payment detection
        days_until_due=days_until_due
    )

    db.add(statement)
    db.commit()
    db.refresh(statement)

    print(f"[INFO] Statement record created: {statement.id}")
    print(f"[INFO] Balance data captured: Statement Balance=${statement.statement_balance}, Due=${statement.minimum_payment_due}")

    # ══════════════════════════════════════════════════════════════
    # STEP 10: Extract Transactions with Gemini AI
    # ══════════════════════════════════════════════════════════════

    try:
        # Get all available categories
        categories = db.query(Category).filter(
            (Category.user_id == None) |  # System categories
            (Category.user_id == current_user.id)  # User's custom
        ).all()

        # Process PDF with Gemini AI
        print("[INFO] Starting AI extraction...")
        transactions_data, stats = process_statement_pdf(
            pdf_path=file_path,
            categories=categories,
            statement_month=statement_month,
            statement_year=statement_year
        )

        print(f"[SUCCESS] AI extracted {len(transactions_data)} transactions")

    except Exception as e:
        # Update statement status to failed
        statement.processing_status = "failed"
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI extraction failed: {str(e)}"
        )

    # ══════════════════════════════════════════════════════════════
    # STEP 7: Save Transactions to Database
    # ══════════════════════════════════════════════════════════════

    saved_transactions = []

    for trans_data in transactions_data:
        # Match category
        category = match_category_by_name(trans_data["category_name"], categories)

        # Parse transaction date
        try:
            trans_date = datetime.strptime(trans_data["transaction_date"], "%Y-%m-%d").date()
        except:
            # Fallback: use statement month
            trans_date = datetime(statement_year, statement_month, 1).date()

        # Create transaction
        transaction = Transaction(
            user_id=current_user.id,
            card_id=card.id,
            statement_id=statement.id,
            category_id=category.id if category else None,
            merchant_name=trans_data["merchant_name"],
            amount=Decimal(str(trans_data["amount"])),
            transaction_date=trans_date,
            description=trans_data.get("description"),
            category_auto=trans_data.get("category", "unknown"),  # AI-categorized merchant type
            statement_month=statement_month,
            statement_year=statement_year,
            is_recurring=trans_data.get("is_recurring", False),
            confidence_score=Decimal(str(trans_data.get("confidence_score", 0.0)))
        )

        db.add(transaction)
        saved_transactions.append(transaction)

    db.commit()

    # Refresh transactions to get IDs and relationships
    for trans in saved_transactions:
        db.refresh(trans)

    print(f"[SUCCESS] Saved {len(saved_transactions)} transactions")

    # ══════════════════════════════════════════════════════════════
    # STEP 8: Update Statement with Final Statistics
    # ══════════════════════════════════════════════════════════════

    statement.total_transactions = len(saved_transactions)
    statement.total_amount = Decimal(str(stats["total_amount"]))
    statement.ai_confidence_score = Decimal(str(stats["avg_confidence"]))
    statement.processing_status = "completed"
    statement.processed_at = datetime.now()

    # Set insights status to processing (background task will update this)
    statement.insights_status = "processing"

    db.commit()
    db.refresh(statement)

    # ══════════════════════════════════════════════════════════════
    # STEP 8.5: Detect Payment Behavior & Generate Alerts
    # ══════════════════════════════════════════════════════════════

    # Disabled for now - payment_detection module not yet implemented
    # from app.services.payment_detection import detect_payment_behavior, get_previous_statement
    # from app.features.insights.models import PaymentAlert

    # print(f"[INFO] Detecting payment behavior...")
    # previous_stmt = get_previous_statement(db, card.id, statement_month, statement_year)

    # payment_result = detect_payment_behavior(db, statement, previous_stmt)

    # # Create alert if needed
    # if payment_result["alert_message"] and payment_result["alert_level"] != "none":
    #     print(f"[INFO] Creating payment alert: {payment_result['payment_status']}")

    #     # Determine alert type
    #     alert_type_map = {
    #         "paid_full": "payment_success",
    #         "partial_paid": "payment_warning",
    #         "below_minimum": "late_payment",
    #         "no_payment": "no_payment",
    #         "unknown": "payment_info"
    #     }

    #     alert_type = alert_type_map.get(payment_result["payment_status"], "payment_info")

    #     # Create alert title based on status
    #     title_map = {
    #         "paid_full": "✓ Paid in Full - Great Job!",
    #         "partial_paid": "⚠️ Partial Payment - Interest Will Accrue",
    #         "below_minimum": "🚨 Minimum Payment Not Met",
    #         "no_payment": "🚨 CRITICAL: No Payment Detected",
    #         "unknown": "Payment Information"
    #     }

    #     alert_title = title_map.get(payment_result["payment_status"], "Payment Alert")

    #     alert = PaymentAlert(
    #         user_id=current_user.id,
    #         statement_id=previous_stmt.id if previous_stmt else statement.id,
    #         alert_type=alert_type,
    #         alert_level=payment_result["alert_level"],
    #         title=alert_title,
    #         message=payment_result["alert_message"],
    #         recommendation=payment_result.get("recommendation"),
    #         is_read=False,
    #         is_dismissed=False
    #     )

    #     db.add(alert)
    #     db.commit()
    #     db.refresh(alert)

    #     print(f"[SUCCESS] Payment alert created: {alert.id}")

    # ══════════════════════════════════════════════════════════════
    # STEP 8.6: Schedule Background Task for Insights Generation
    # ══════════════════════════════════════════════════════════════

    # Disabled for now - using manual /insights/generate endpoint instead
    # print(f"[INFO] Scheduling background task for insights generation...")
    # background_tasks.add_task(
    #     generate_insights_background,
    #     statement_id=statement.id,
    #     user_id=current_user.id,
    #     statement_month=statement_month,
    #     statement_year=statement_year
    # )
    # print(f"[INFO] Background task scheduled successfully")

    # ══════════════════════════════════════════════════════════════
    # STEP 9: Prepare Response
    # ══════════════════════════════════════════════════════════════

    processing_time = time.time() - start_time

    # Add processing time to stats
    stats["processing_time_seconds"] = round(processing_time, 2)

    message = (
        f"Statement processed successfully! "
        f"Extracted {len(saved_transactions)} transactions in {processing_time:.2f}s."
    )

    return StatementUploadResponse(
        statement=StatementResponse.model_validate(statement),
        extracted_transactions=[
            TransactionResponse.model_validate(trans)
            for trans in saved_transactions
        ],
        message=message,
        stats=stats
    )


# ═══════════════════════════════════════════════════════════════════
# GET /statements - List All Statements
# ═══════════════════════════════════════════════════════════════════

@router.get(
    "",
    response_model=List[StatementResponse],
    status_code=status.HTTP_200_OK,
    summary="List all statements",
    description="Get all uploaded statements for current user"
)
async def list_statements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    card_id: UUID = None
):
    """
    List all user's statements

    Query Parameters:
    - **card_id**: Filter by credit card (optional)

    Returns statements ordered by newest first
    """

    query = db.query(Statement).filter(Statement.user_id == current_user.id)

    if card_id:
        query = query.filter(Statement.card_id == card_id)

    statements = query.order_by(
        Statement.statement_year.desc(),
        Statement.statement_month.desc()
    ).all()

    return [StatementResponse.model_validate(stmt) for stmt in statements]


# ═══════════════════════════════════════════════════════════════════
# GET /statements/{statement_id} - Get Statement Details
# ═══════════════════════════════════════════════════════════════════

@router.get(
    "/{statement_id}",
    response_model=StatementResponse,
    status_code=status.HTTP_200_OK,
    summary="Get statement details",
    description="Get details of a specific statement"
)
async def get_statement(
    statement_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific statement by ID"""

    statement = db.query(Statement).filter(
        Statement.id == statement_id,
        Statement.user_id == current_user.id
    ).first()

    if not statement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Statement not found"
        )

    return StatementResponse.model_validate(statement)


# ═══════════════════════════════════════════════════════════════════
# DELETE /statements/{statement_id} - Delete Statement
# ═══════════════════════════════════════════════════════════════════

@router.delete(
    "/{statement_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete statement",
    description="Delete statement and all associated transactions"
)
async def delete_statement(
    statement_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete statement

    WARNING: This will also delete all transactions from this statement
    """

    statement = db.query(Statement).filter(
        Statement.id == statement_id,
        Statement.user_id == current_user.id
    ).first()

    if not statement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Statement not found"
        )

    # Delete PDF file if it exists
    file_path = os.path.join(UPLOAD_DIR, statement.file_name)
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"[INFO] Deleted PDF file: {file_path}")

    # Delete statement (cascade will delete transactions)
    db.delete(statement)
    db.commit()

    return None


# ═══════════════════════════════════════════════════════════════════
# GET /statements/{statement_id}/status - Check Insights Status
# ═══════════════════════════════════════════════════════════════════

@router.get(
    "/{statement_id}/status",
    response_model=StatementStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Check statement processing status",
    description="Check if insights are ready for a statement (used for polling)"
)
async def get_statement_status(
    statement_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check if insights are ready for a statement

    Frontend polls this endpoint every 3-5 seconds after upload
    to know when insights are ready to display.

    Response:
    - processing_status: "processing" | "completed" | "failed"
    - insights_status: "pending" | "processing" | "completed" | "failed"
    - insights_generated_at: Timestamp when insights were generated (if completed)
    - error: Error message if failed

    When insights_status becomes "completed", frontend can:
    1. Stop polling
    2. Fetch insights from GET /insights/hero
    3. Display insights to user
    """

    statement = db.query(Statement).filter(
        Statement.id == statement_id,
        Statement.user_id == current_user.id
    ).first()

    if not statement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Statement not found"
        )

    return StatementStatusResponse(
        statement_id=statement.id,
        processing_status=statement.processing_status,
        insights_status=statement.insights_status,
        insights_generated_at=statement.insights_generated_at,
        error=statement.insights_error
    )


# ═══════════════════════════════════════════════════════════════════
# USAGE EXAMPLES
# ═══════════════════════════════════════════════════════════════════
"""
# Example 1: Upload PDF statement
POST /statements/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

Form Data:
- file: DBS_Visa_Oct2024.pdf
- card_id: 550e8400-e29b-41d4-a716-446655440000
- statement_month: 10
- statement_year: 2024

# Response 201 Created (after ~10-15 seconds):
{
    "statement": {
        "id": "880e8400-e29b-41d4-a716-446655440003",
        "file_name": "DBS_Visa_Oct2024.pdf",
        "total_transactions": 45,
        "total_amount": 1523.50,
        "processing_status": "completed",
        "ai_confidence_score": 0.92
    },
    "extracted_transactions": [...],
    "message": "Statement processed successfully! Extracted 45 transactions in 12.5s.",
    "stats": {
        "total_transactions": 45,
        "total_amount": 1523.50,
        "avg_confidence": 0.92,
        "processing_time_seconds": 12.5,
        "categories_assigned": {
            "Groceries": 12,
            "Dining": 15,
            "Transport": 8,
            "Shopping": 10
        }
    }
}

# Example 2: List all statements
GET /statements
Authorization: Bearer <token>

# Example 3: List statements for specific card
GET /statements?card_id=550e8400-e29b-41d4-a716-446655440000
Authorization: Bearer <token>
"""
