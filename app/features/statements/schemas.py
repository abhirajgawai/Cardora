"""
Statement Pydantic Schemas (DTOs)

Compare to .NET: Like having DTOs for Statements
    - StatementResponse → StatementDto (output)
    - StatementUploadResponse → UploadResultDto (output)

Statements in Cardora:
- Represents uploaded credit card PDF statements
- Contains metadata about the statement
- Links to extracted transactions
- Tracks AI processing status and confidence
"""

from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from decimal import Decimal

# Import TransactionResponse for nested response
from app.features.transactions.schemas import TransactionResponse


# ═══════════════════════════════════════════════════════════════════
# STATEMENT RESPONSE (Output)
# ═══════════════════════════════════════════════════════════════════

class StatementResponse(BaseModel):
    """
    Schema for statement data response (output)

    Compare to .NET:
        public class StatementDto
        {
            public Guid Id { get; set; }
            public Guid UserId { get; set; }
            public Guid CardId { get; set; }
            public string FileName { get; set; }
            public int StatementMonth { get; set; }
            public int StatementYear { get; set; }
            public int TotalTransactions { get; set; }
            public decimal TotalAmount { get; set; }
            public string ProcessingStatus { get; set; }
            public decimal? AiConfidenceScore { get; set; }
            public DateTime? ProcessedAt { get; set; }
            public DateTime CreatedAt { get; set; }
            public DateTime UpdatedAt { get; set; }
        }

    Used for:
    - Listing statements
    - Displaying statement details
    - Statement history
    """
    id: UUID = Field(
        ...,
        description="Statement's unique identifier",
        examples=["880e8400-e29b-41d4-a716-446655440003"]
    )

    user_id: UUID = Field(
        ...,
        description="Owner's user ID",
        examples=["660e8400-e29b-41d4-a716-446655440001"]
    )

    card_id: UUID = Field(
        ...,
        description="Credit card ID",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )

    file_name: str = Field(
        ...,
        description="Original PDF file name",
        examples=["DBS_Visa_Oct2024.pdf", "statement_october.pdf"]
    )

    statement_month: int = Field(
        ...,
        ge=1,
        le=12,
        description="Statement month (1-12)",
        examples=[10]
    )

    statement_year: int = Field(
        ...,
        ge=2020,
        le=2100,
        description="Statement year",
        examples=[2024]
    )

    total_transactions: int = Field(
        ...,
        ge=0,
        description="Number of transactions extracted",
        examples=[45, 78]
    )

    total_amount: Decimal = Field(
        ...,
        description="Total amount of all transactions",
        examples=[1523.50, 2845.00]
    )

    processing_status: str = Field(
        ...,
        description="Processing status: 'processing', 'completed', 'failed'",
        examples=["completed", "processing", "failed"]
    )

    ai_confidence_score: Optional[Decimal] = Field(
        None,
        ge=0,
        le=1,
        description="Average AI confidence score (0.00-1.00)",
        examples=[0.92, 0.88]
    )

    processed_at: Optional[datetime] = Field(
        None,
        description="When processing completed",
        examples=["2024-10-22T10:35:00Z"]
    )

    created_at: datetime = Field(
        ...,
        description="When the statement was uploaded",
        examples=["2024-10-22T10:30:00Z"]
    )

    updated_at: datetime = Field(
        ...,
        description="When the statement was last updated",
        examples=["2024-10-22T10:35:00Z"]
    )

    # Configuration
    model_config = ConfigDict(
        from_attributes=True,  # Allows creation from ORM models
        json_schema_extra={
            "example": {
                "id": "880e8400-e29b-41d4-a716-446655440003",
                "user_id": "660e8400-e29b-41d4-a716-446655440001",
                "card_id": "550e8400-e29b-41d4-a716-446655440000",
                "file_name": "DBS_Visa_Oct2024.pdf",
                "statement_month": 10,
                "statement_year": 2024,
                "total_transactions": 45,
                "total_amount": 1523.50,
                "processing_status": "completed",
                "ai_confidence_score": 0.92,
                "processed_at": "2024-10-22T10:35:00Z",
                "created_at": "2024-10-22T10:30:00Z",
                "updated_at": "2024-10-22T10:35:00Z"
            }
        }
    )


# ═══════════════════════════════════════════════════════════════════
# STATEMENT UPLOAD RESPONSE (Output - after PDF upload)
# ═══════════════════════════════════════════════════════════════════

class StatementUploadResponse(BaseModel):
    """
    Schema for statement upload result (output)

    Compare to .NET:
        public class UploadResultDto
        {
            public StatementDto Statement { get; set; }
            public List<TransactionDto> ExtractedTransactions { get; set; }
            public string Message { get; set; }
            public ProcessingStats Stats { get; set; }
        }

    Used for:
    - POST /statements/upload response
    - Shows complete upload result with extracted transactions
    """
    statement: StatementResponse = Field(
        ...,
        description="Statement metadata"
    )

    extracted_transactions: List[TransactionResponse] = Field(
        ...,
        description="List of extracted transactions from PDF"
    )

    message: str = Field(
        ...,
        description="Success/status message",
        examples=[
            "Statement processed successfully! Extracted 45 transactions.",
            "Processing completed with high confidence (92%)"
        ]
    )

    stats: dict = Field(
        ...,
        description="Processing statistics",
        examples=[{
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
        }]
    )

    # Configuration
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "statement": {
                    "id": "880e8400-e29b-41d4-a716-446655440003",
                    "file_name": "DBS_Visa_Oct2024.pdf",
                    "statement_month": 10,
                    "statement_year": 2024,
                    "total_transactions": 45,
                    "total_amount": 1523.50,
                    "processing_status": "completed",
                    "ai_confidence_score": 0.92
                },
                "extracted_transactions": [
                    {
                        "merchant_name": "Starbucks",
                        "amount": 6.50,
                        "transaction_date": "2024-10-15",
                        "category": {
                            "name": "Dining",
                            "icon": "🍽️",
                            "color": "#FF9800"
                        }
                    }
                ],
                "message": "Statement processed successfully! Extracted 45 transactions.",
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
        }
    )


# ═══════════════════════════════════════════════════════════════════
# STATEMENT LIST RESPONSE (for pagination)
# ═══════════════════════════════════════════════════════════════════

class StatementListResponse(BaseModel):
    """
    Schema for paginated statement list

    Used for:
    - GET /statements?page=1&limit=10
    - Listing all user's statements
    """
    statements: List[StatementResponse] = Field(
        ...,
        description="List of statements"
    )

    total: int = Field(
        ...,
        description="Total number of statements",
        examples=[12]
    )

    page: int = Field(
        ...,
        description="Current page number",
        examples=[1]
    )

    page_size: int = Field(
        ...,
        description="Number of items per page",
        examples=[10]
    )

    # Configuration
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "statements": [
                    {
                        "id": "880e8400-e29b-41d4-a716-446655440003",
                        "file_name": "DBS_Visa_Oct2024.pdf",
                        "statement_month": 10,
                        "statement_year": 2024,
                        "total_transactions": 45,
                        "total_amount": 1523.50,
                        "processing_status": "completed"
                    }
                ],
                "total": 12,
                "page": 1,
                "page_size": 10
            }
        }
    )


# ═══════════════════════════════════════════════════════════════════
# STATEMENT STATUS RESPONSE (for polling insights generation)
# ═══════════════════════════════════════════════════════════════════

class StatementStatusResponse(BaseModel):
    """
    Schema for statement processing status (used for polling)

    Used for:
    - GET /statements/{statement_id}/status
    - Frontend polls this to check if insights are ready
    """
    statement_id: UUID = Field(
        ...,
        description="Statement ID",
        examples=["880e8400-e29b-41d4-a716-446655440003"]
    )

    processing_status: str = Field(
        ...,
        description="Processing status: 'processing', 'completed', 'failed'",
        examples=["completed", "processing", "failed"]
    )

    insights_status: Optional[str] = Field(
        None,
        description="Insights generation status: 'pending', 'processing', 'completed', 'failed'",
        examples=["completed", "processing", "pending"]
    )

    insights_generated_at: Optional[datetime] = Field(
        None,
        description="When insights were generated",
        examples=["2024-10-22T10:36:00Z"]
    )

    error: Optional[str] = Field(
        None,
        description="Error message if processing failed",
        examples=["Failed to generate insights: insufficient data"]
    )

    # Configuration
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "statement_id": "880e8400-e29b-41d4-a716-446655440003",
                "processing_status": "completed",
                "insights_status": "completed",
                "insights_generated_at": "2024-10-22T10:36:00Z",
                "error": None
            }
        }
    )


# ═══════════════════════════════════════════════════════════════════
# USAGE EXAMPLES
# ═══════════════════════════════════════════════════════════════════
"""
# Example 1: Upload PDF statement (THE MAIN FEATURE!)
POST /statements/upload
Content-Type: multipart/form-data
Authorization: Bearer <token>

Form Data:
- file: DBS_Visa_Oct2024.pdf (PDF file)
- card_id: 550e8400-e29b-41d4-a716-446655440000
- statement_month: 10
- statement_year: 2024

# Response 201 Created (after ~10-15 seconds of AI processing):
{
    "statement": {
        "id": "880e8400-e29b-41d4-a716-446655440003",
        "user_id": "660e8400-e29b-41d4-a716-446655440001",
        "card_id": "550e8400-e29b-41d4-a716-446655440000",
        "file_name": "DBS_Visa_Oct2024.pdf",
        "statement_month": 10,
        "statement_year": 2024,
        "total_transactions": 45,
        "total_amount": 1523.50,
        "processing_status": "completed",
        "ai_confidence_score": 0.92,
        "processed_at": "2024-10-22T10:35:00Z",
        "created_at": "2024-10-22T10:30:00Z",
        "updated_at": "2024-10-22T10:35:00Z"
    },
    "extracted_transactions": [
        {
            "id": "770e8400-e29b-41d4-a716-446655440002",
            "merchant_name": "Starbucks",
            "amount": 6.50,
            "transaction_date": "2024-10-15",
            "statement_month": 10,
            "statement_year": 2024,
            "confidence_score": 0.95,
            "category": {
                "id": "990e8400-e29b-41d4-a716-446655440004",
                "name": "Dining",
                "icon": "🍽️",
                "color": "#FF9800",
                "is_custom": false
            }
        },
        {
            "id": "110e8400-e29b-41d4-a716-446655440005",
            "merchant_name": "NTUC FairPrice",
            "amount": 125.00,
            "transaction_date": "2024-10-16",
            "statement_month": 10,
            "statement_year": 2024,
            "confidence_score": 0.98,
            "category": {
                "id": "220e8400-e29b-41d4-a716-446655440006",
                "name": "Groceries",
                "icon": "🛒",
                "color": "#4CAF50",
                "is_custom": false
            }
        }
        // ... 43 more transactions
    ],
    "message": "Statement processed successfully! Extracted 45 transactions.",
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
GET /statements?page=1&limit=10
Authorization: Bearer <token>

# Response 200 OK:
{
    "statements": [
        {
            "id": "880e8400-e29b-41d4-a716-446655440003",
            "card_id": "550e8400-e29b-41d4-a716-446655440000",
            "file_name": "DBS_Visa_Oct2024.pdf",
            "statement_month": 10,
            "statement_year": 2024,
            "total_transactions": 45,
            "total_amount": 1523.50,
            "processing_status": "completed",
            "ai_confidence_score": 0.92,
            "created_at": "2024-10-22T10:30:00Z"
        },
        {
            "id": "330e8400-e29b-41d4-a716-446655440007",
            "card_id": "550e8400-e29b-41d4-a716-446655440000",
            "file_name": "DBS_Visa_Sep2024.pdf",
            "statement_month": 9,
            "statement_year": 2024,
            "total_transactions": 52,
            "total_amount": 1845.00,
            "processing_status": "completed",
            "ai_confidence_score": 0.89,
            "created_at": "2024-09-22T14:00:00Z"
        }
    ],
    "total": 12,
    "page": 1,
    "page_size": 10
}


# Example 3: Get specific statement with transactions
GET /statements/880e8400-e29b-41d4-a716-446655440003
Authorization: Bearer <token>

# Response 200 OK:
{
    "statement": {
        "id": "880e8400-e29b-41d4-a716-446655440003",
        "file_name": "DBS_Visa_Oct2024.pdf",
        "statement_month": 10,
        "statement_year": 2024,
        "total_transactions": 45,
        "total_amount": 1523.50,
        "processing_status": "completed"
    },
    "transactions": [
        // ... all 45 transactions
    ]
}
"""
