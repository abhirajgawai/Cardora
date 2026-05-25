"""Statement endpoints — upload, list, get, delete, status poll."""

import logging
import os
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.features.auth.jwt import get_current_user
from app.features.auth.models import User
from app.features.statements.models import Statement
from app.features.statements.schemas import (
    StatementListResponse,
    StatementResponse,
    StatementStatusResponse,
    StatementUploadResponse,
)
from app.features.statements.service import process_upload
from app.features.transactions.schemas import TransactionResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/statements", tags=["Statements"])

UPLOAD_DIR = "uploads"


@router.post(
    "/upload",
    response_model=StatementUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload PDF statement (AI extraction)",
)
async def upload_statement(
    file: UploadFile = File(..., description="PDF statement file"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload a credit card PDF statement and automatically extract transactions via Gemini AI."""
    import time
    start = time.time()

    contents = await file.read()

    try:
        statement, transactions, stats = process_upload(
            db=db,
            user_id=current_user.id,
            original_filename=file.filename,
            contents=contents,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        logger.exception("Statement processing failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Statement processing failed. Please try again.",
        )

    processing_time = round(time.time() - start, 2)
    stats["processing_time_seconds"] = processing_time

    return StatementUploadResponse(
        statement=StatementResponse.model_validate(statement),
        extracted_transactions=[TransactionResponse.model_validate(t) for t in transactions],
        message=(
            f"Statement processed successfully! "
            f"Extracted {len(transactions)} transactions in {processing_time}s."
        ),
        stats=stats,
    )


@router.get(
    "",
    response_model=List[StatementResponse],
    status_code=status.HTTP_200_OK,
    summary="List statements",
)
async def list_statements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    card_id: Optional[UUID] = None,
):
    query = db.query(Statement).filter(Statement.user_id == current_user.id)
    if card_id:
        query = query.filter(Statement.card_id == card_id)
    statements = query.order_by(
        Statement.statement_year.desc(), Statement.statement_month.desc()
    ).all()
    return [StatementResponse.model_validate(s) for s in statements]


@router.get(
    "/{statement_id}",
    response_model=StatementResponse,
    status_code=status.HTTP_200_OK,
    summary="Get statement",
)
async def get_statement(
    statement_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    statement = db.query(Statement).filter(
        Statement.id == statement_id, Statement.user_id == current_user.id
    ).first()
    if not statement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Statement not found")
    return StatementResponse.model_validate(statement)


@router.delete(
    "/{statement_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete statement",
)
async def delete_statement(
    statement_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    statement = db.query(Statement).filter(
        Statement.id == statement_id, Statement.user_id == current_user.id
    ).first()
    if not statement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Statement not found")

    file_path = os.path.join(UPLOAD_DIR, statement.file_name)
    if os.path.exists(file_path):
        os.remove(file_path)

    db.delete(statement)
    db.commit()


@router.get(
    "/{statement_id}/status",
    response_model=StatementStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Poll statement processing status",
)
async def get_statement_status(
    statement_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    statement = db.query(Statement).filter(
        Statement.id == statement_id, Statement.user_id == current_user.id
    ).first()
    if not statement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Statement not found")

    return StatementStatusResponse(
        statement_id=statement.id,
        processing_status=statement.processing_status,
        insights_status=statement.insights_status,
        insights_generated_at=statement.insights_generated_at,
        error=statement.insights_error,
    )
