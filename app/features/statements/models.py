"""
Statement Model

Represents an uploaded credit card statement PDF with metadata.

    public class Statement
    {
        public Guid Id { get; set; }
        public Guid UserId { get; set; }
        public Guid CardId { get; set; }

        public string FileName { get; set; }
        public int StatementMonth { get; set; }  // 1-12
        public int StatementYear { get; set; }   // e.g., 2025

        public int TotalTransactions { get; set; }
        public decimal TotalAmount { get; set; }
        public string ProcessingStatus { get; set; }
        public decimal? AiConfidenceScore { get; set; }

        public DateTime? ProcessedAt { get; set; }
        public DateTime CreatedAt { get; set; }

        public User User { get; set; }
        public CreditCard CreditCard { get; set; }
        public List<Transaction> Transactions { get; set; }
    }
"""

import uuid
from decimal import Decimal
from sqlalchemy import Column, String, Integer, ForeignKey, Numeric, DateTime, Text, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone, date

from app.core.database import Base


class Statement(Base):
    """
    Credit card statement uploaded by user

    Tracks:
    - Which PDF file was uploaded
    - Which month/year the statement covers (IMPORTANT for filtering!)
    - How many transactions were extracted
    - Processing status and AI confidence
    - Relationships to user, card, and transactions
    """

    __tablename__ = "statements"
    __table_args__ = {"schema": "cardora"}

    # ═══════════════════════════════════════════════════════════════
    # ═══════════════════════════════════════════════════════════════

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )

    # ═══════════════════════════════════════════════════════════════
    # ═══════════════════════════════════════════════════════════════

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("cardora.users.id"),
        nullable=False,
    )
    
    card_id = Column(
        UUID(as_uuid=True),
        ForeignKey("cardora.credit_cards.id"),
        nullable=False,
    )
    
    # ═══════════════════════════════════════════════════════════════
    # ═══════════════════════════════════════════════════════════════

    file_name = Column(
        String(255),
        nullable=False
    )
    
    # ═══════════════════════════════════════════════════════════════
    # ═══════════════════════════════════════════════════════════════

    statement_month = Column(
        Integer,
        nullable=False,
    )

    statement_year = Column(
        Integer,
        nullable=False,
    )
    
    """
    WHY statement_month and statement_year are CRITICAL:

    1. Fast Filtering:
       - User wants "Show me all January 2025 statements"
       - Query: WHERE statement_month = 1 AND statement_year = 2025
       - With indexes, this is INSTANT

    2. Monthly Analytics:
       - "Total spending by month"
       - "Compare Jan 2025 vs Jan 2024"
       - No need to parse dates or JOIN with transactions

    3. UI Display:
       - Group statements by month/year in dropdown
       - Show "You have 3 statements for January 2025"

        var janStatements = await _context.Statements
            .Where(s => s.StatementMonth == 1 && s.StatementYear == 2025)
            .ToListAsync();

    Alternative (BAD):
        - Parse statement_period string every time
        - Extract month/year from transactions table (requires JOIN)
        - Store as DateTime and use MONTH(date), YEAR(date) - slow!
    """

    # ═══════════════════════════════════════════════════════════════
    # ═══════════════════════════════════════════════════════════════

    total_transactions = Column(
        Integer,
        default=0,
        nullable=False
    )
    
    total_amount = Column(
        Numeric(12, 2),
        default=Decimal("0.00"),
        nullable=False,
    )
    
    processing_status = Column(
        String(50),
        default="processing",
        nullable=False
    )
    
    ai_confidence_score = Column(
        Numeric(3, 2),
        nullable=True,
    )
    
    processed_at = Column(
        DateTime(timezone=True),
    )
    
    # ═══════════════════════════════════════════════════════════════
    # ═══════════════════════════════════════════════════════════════

    statement_date = Column(
        Date,
    )
    
    due_date = Column(
        Date,
        nullable=True
    )
    
    statement_balance = Column(
        Numeric(12, 2),
        nullable=True,
    )
    
    minimum_payment_due = Column(
        Numeric(10, 2),
        nullable=True
    )
    
    previous_balance = Column(
        Numeric(12, 2),
        nullable=True
    )
    
    new_charges = Column(
        Numeric(12, 2),
        nullable=True
    )
    
    payments_credits = Column(
        Numeric(12, 2),
        nullable=True
    )
    
    interest_charged = Column(
        Numeric(10, 2),
        nullable=True,
        default=0.00
    )
    
    fees_charged = Column(
        Numeric(10, 2),
        nullable=True,
        default=0.00
    )
    
    apr = Column(
        Numeric(5, 2),
        nullable=True
    )
    
    # ═══════════════════════════════════════════════════════════════
    # ═══════════════════════════════════════════════════════════════

    payment_status = Column(
        String(50),
        default="pending",
        nullable=False,
    )
    
    amount_paid = Column(
        Numeric(12, 2),
        nullable=True,
        default=0.00
    )
    
    payment_detected_at = Column(
        DateTime(timezone=True),
        nullable=True
    )
    
    revolving_balance = Column(
        Numeric(12, 2),
        nullable=True
    )
    
    estimated_monthly_interest = Column(
        Numeric(10, 2),
        nullable=True
    )
    
    estimated_annual_cost = Column(
        Numeric(10, 2),
        nullable=True
    )
    
    days_until_due = Column(
        Integer,
        nullable=True
    )
    
    # ═══════════════════════════════════════════════════════════════
    # ═══════════════════════════════════════════════════════════════

    insights_status = Column(
        String(50),
        default="pending",
        nullable=False
    )

    insights_generated_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    insights_error = Column(
        Text,
        nullable=True
    )

    # ═══════════════════════════════════════════════════════════════
    # ═══════════════════════════════════════════════════════════════

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=True
    )

    # ═══════════════════════════════════════════════════════════════
    # ═══════════════════════════════════════════════════════════════

    user = relationship(
        "User",
        back_populates="statements"
    )
    
    credit_card = relationship(
        "CreditCard",
        back_populates="statements"
    )
    
    transactions = relationship(
        "Transaction",
        back_populates="statement",
    )
    

    # ═══════════════════════════════════════════════════════════════
    # ═══════════════════════════════════════════════════════════════

    def __repr__(self):
        return f"<Statement {self.file_name} ({self.statement_year}-{self.statement_month:02d})>"


# ═══════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════

"""
┌─────────────────────────────────────────────────────────────────┐
│ CONCEPT: Why Store Month/Year as Separate Integers?            │
├─────────────────────────────────────────────────────────────────┤
│ Option 1: statement_month + statement_year (OUR CHOICE)        │
│ ✓ Fast filtering: WHERE statement_month = 1 AND year = 2025    │
│ ✓ Easy grouping: GROUP BY statement_year, statement_month      │
│ ✓ Simple UI: Dropdown "January 2025"                           │
│ ✓ Indexed queries are INSTANT                                  │
│                                                                 │
│ Option 2: statement_date (DateTime)                            │
│ ✗ Slower: WHERE MONTH(date) = 1 AND YEAR(date) = 2025          │
│ ✗ Cannot use indexes efficiently                               │
│ ✗ More complex queries                                         │
│                                                                 │
│ Option 3: statement_period (String "2025-01-01 to 2025-01-31") │
│ ✗ Must parse string every time                                 │
│ ✗ Cannot index or sort easily                                  │
│ ✗ String manipulation = slow                                   │
│                                                                 │
│ Real-world query example:                                      │
│ statements = db.query(Statement).filter(                       │
│     Statement.statement_year == 2025,                           │
│     Statement.statement_month.in_([1, 2, 3])                    │
│ ).all()                                                         │
│                                                                 │
│ With indexes on month + year, this query is INSTANT            │
│ even with 1000+ statements in database!                        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ CONCEPT: Processing Status Flow                                │
├─────────────────────────────────────────────────────────────────┤
│ 1. User uploads PDF                                            │
│    Status: "processing"                                        │
│    ProcessedAt: NULL                                           │
│                                                                 │
│ 2. Gemini AI extracts transactions (5-15 seconds)              │
│    Status: "processing"                                        │
│    ProcessedAt: NULL                                           │
│                                                                 │
│ 3. Transactions saved to database                              │
│    Status: "completed"                                         │
│    ProcessedAt: 2025-01-15 10:30:00                            │
│    TotalTransactions: 23                                       │
│    TotalAmount: 1245.60                                        │
│                                                                 │
│ 4. If Gemini fails or invalid PDF                              │
│    Status: "failed"                                            │
│    ProcessedAt: 2025-01-15 10:30:00                            │
│    TotalTransactions: 0                                        │
│                                                                 │
│ Future Enhancement:                                             │
│ - Add "pending_review" status for low confidence scores        │
│ - Add "archived" status for old statements                     │
│ - Store error message if failed                                │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ CONCEPT: Cascade Delete Strategy                               │
├─────────────────────────────────────────────────────────────────┤
│ Statement → Transaction: CASCADE DELETE                        │
│ ✓ If statement deleted, delete all its transactions           │
│ ✓ Makes sense: transactions came from this statement          │
│ ✓ Prevents orphan transactions                                │
│                                                                 │
│ Compare to other relationships:                                │
│ Category → Transaction: SET NULL (keep transaction, lose cat)  │
│ CreditCard → Transaction: CASCADE (delete all card's txns)     │
│ User → Transaction: CASCADE (delete all user's data)           │
│                                                                 │
│ .NET EF Core equivalent:                                       │
│   modelBuilder.Entity<Transaction>()                            │
│       .HasOne(t => t.Statement)                                 │
│       .WithMany(s => s.Transactions)                            │
│       .OnDelete(DeleteBehavior.Cascade);                        │
└─────────────────────────────────────────────────────────────────┘
"""
