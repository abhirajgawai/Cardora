"""
Statement Model

Represents an uploaded credit card statement PDF with metadata.

Compare to .NET:
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
        nullable=False,
        index=True  # Index for user's statements queries
    )
    # Compare to .NET: [ForeignKey("User")] public Guid UserId { get; set; }

    card_id = Column(
        UUID(as_uuid=True),
        ForeignKey("cardora.credit_cards.id"),
        nullable=False,
        index=True  # Index for card-specific queries
    )
    # Compare to .NET: [ForeignKey("CreditCard")] public Guid CardId { get; set; }

    # ═══════════════════════════════════════════════════════════════
    # FILE METADATA
    # ═══════════════════════════════════════════════════════════════

    file_name = Column(
        String(255),
        nullable=False
    )
    # Example: "DBS_Statement_Jan2025.pdf"
    # Original filename from user upload
    # Compare to .NET: [Required] [MaxLength(255)] public string FileName

    # ═══════════════════════════════════════════════════════════════
    # STATEMENT PERIOD (CRITICAL for filtering and analytics!)
    # ═══════════════════════════════════════════════════════════════

    statement_month = Column(
        Integer,  # 1-12 (January = 1, December = 12)
        nullable=False,
        index=True  # IMPORTANT: Index for monthly queries
    )
    # Example: 1 (January), 6 (June), 12 (December)
    # Extracted from statement_period.end date in Gemini response
    # Compare to .NET: [Range(1, 12)] public int StatementMonth { get; set; }

    statement_year = Column(
        Integer,  # e.g., 2025
        nullable=False,
        index=True  # IMPORTANT: Index for yearly queries
    )
    # Example: 2025, 2024
    # Extracted from statement_period.end date in Gemini response
    # Compare to .NET: public int StatementYear { get; set; }

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

    Compare to .NET LINQ:
        var janStatements = await _context.Statements
            .Where(s => s.StatementMonth == 1 && s.StatementYear == 2025)
            .ToListAsync();

    Alternative (BAD):
        - Parse statement_period string every time
        - Extract month/year from transactions table (requires JOIN)
        - Store as DateTime and use MONTH(date), YEAR(date) - slow!
    """

    # ═══════════════════════════════════════════════════════════════
    # PROCESSING RESULTS
    # ═══════════════════════════════════════════════════════════════

    total_transactions = Column(
        Integer,
        default=0,
        nullable=False
    )
    # How many transactions were extracted from the PDF
    # Updated after bulk insert of transactions
    # Example: 23 transactions found
    # Compare to .NET: public int TotalTransactions { get; set; } = 0;

    total_amount = Column(
        Numeric(10, 2),  # DECIMAL(10,2) - always use for money!
        default=0.00,
        nullable=False
    )
    # Sum of all transaction amounts
    # Example: 1245.60 SGD total spending
    # Compare to .NET: [Precision(10, 2)] public decimal TotalAmount { get; set; }

    processing_status = Column(
        String(50),
        default="processing",
        nullable=False
    )
    # Values: "processing", "completed", "failed"
    # Useful for async processing or retry logic
    # Compare to .NET: public string ProcessingStatus { get; set; } = "processing";

    ai_confidence_score = Column(
        Numeric(3, 2),  # 0.00 to 1.00 (e.g., 0.95 = 95% confidence)
        nullable=True   # NULL if not calculated
    )
    # Average confidence score from AI extraction
    # Future feature: Track AI accuracy over time
    # Example: 0.95 = 95% confidence
    # Compare to .NET: [Precision(3, 2)] public decimal? AiConfidenceScore

    processed_at = Column(
        DateTime(timezone=True),
        nullable=True  # NULL while processing, set when completed
    )
    # When the statement processing finished
    # NULL = still processing
    # Compare to .NET: public DateTime? ProcessedAt { get; set; }

    # ═══════════════════════════════════════════════════════════════
    # STATEMENT BALANCE & PAYMENT TRACKING (DEBT DETECTION!)
    # ═══════════════════════════════════════════════════════════════

    statement_date = Column(
        Date,
        nullable=True  # NULL if not extracted from PDF
    )
    # Statement closing date / billing cycle end date
    # Example: 2025-01-15 (when billing cycle closed)
    # Compare to .NET: public DateTime? StatementDate { get; set; }

    due_date = Column(
        Date,
        nullable=True
    )
    # Payment due date
    # Example: 2025-02-05 (21 days after statement date)
    # Used to calculate days_until_due
    # Compare to .NET: public DateTime? DueDate { get; set; }

    statement_balance = Column(
        Numeric(12, 2),  # Up to 9,999,999,999.99 (10 billion)
        nullable=True
    )
    # Total amount owed on this statement
    # "New Balance" or "Amount Due" on statement
    # Example: 1500.00 SGD
    # Compare to .NET: [Precision(12, 2)] public decimal? StatementBalance

    minimum_payment_due = Column(
        Numeric(10, 2),
        nullable=True
    )
    # Minimum payment required to avoid late fees
    # Usually 1-3% of statement balance or $25 minimum
    # Example: 50.00 SGD
    # Compare to .NET: [Precision(10, 2)] public decimal? MinimumPaymentDue

    previous_balance = Column(
        Numeric(12, 2),
        nullable=True
    )
    # Balance carried over from previous statement
    # CRITICAL for payment detection!
    # If previous_balance < last_statement.statement_balance, user paid something
    # Example: 1200.00 SGD (means user paid 300 from last 1500 balance)
    # Compare to .NET: [Precision(12, 2)] public decimal? PreviousBalance

    new_charges = Column(
        Numeric(12, 2),
        nullable=True
    )
    # New purchases/charges this billing cycle
    # Sum of all positive transactions
    # Example: 800.00 SGD in new spending
    # Compare to .NET: [Precision(12, 2)] public decimal? NewCharges

    payments_credits = Column(
        Numeric(12, 2),
        nullable=True
    )
    # Payments and credits received this cycle
    # Sum of all negative transactions (payments, refunds)
    # Example: -300.00 SGD (payment made)
    # Compare to .NET: [Precision(12, 2)] public decimal? PaymentsCredits

    interest_charged = Column(
        Numeric(10, 2),
        nullable=True,
        default=0.00
    )
    # Interest charged this cycle (if carrying balance)
    # ZERO if paid in full, POSITIVE if revolving balance
    # Example: 24.00 SGD (2% of unpaid balance)
    # Compare to .NET: [Precision(10, 2)] public decimal? InterestCharged

    fees_charged = Column(
        Numeric(10, 2),
        nullable=True,
        default=0.00
    )
    # Late fees, annual fees, over-limit fees, etc.
    # Example: 35.00 SGD late payment fee
    # Compare to .NET: [Precision(10, 2)] public decimal? FeesCharged

    apr = Column(
        Numeric(5, 2),
        nullable=True
    )
    # Annual Percentage Rate for purchases
    # Example: 24.99 (means 24.99% APR)
    # Used to calculate future interest costs
    # Compare to .NET: [Precision(5, 2)] public decimal? Apr

    # ═══════════════════════════════════════════════════════════════
    # PAYMENT STATUS & DETECTION
    # ═══════════════════════════════════════════════════════════════

    payment_status = Column(
        String(50),
        default="pending",
        nullable=False,
        index=True  # Index for filtering by payment status
    )
    # Values:
    # - "pending": Due date not reached yet, waiting for payment
    # - "paid_full": Paid entire statement balance (NO INTEREST!)
    # - "partial_paid": Paid more than minimum but less than full (WILL PAY INTEREST)
    # - "minimum_paid": Paid exactly minimum (WILL PAY INTEREST on rest)
    # - "late": Did not pay minimum by due date (LATE FEE + INTEREST)
    # - "unknown": Cannot determine (missing previous statement data)
    # Compare to .NET: [Required] public string PaymentStatus { get; set; } = "pending";

    amount_paid = Column(
        Numeric(12, 2),
        nullable=True,
        default=0.00
    )
    # Amount user actually paid (detected from next statement)
    # Calculated as: last_statement_balance - this_statement_previous_balance
    # Example: 300.00 SGD
    # Compare to .NET: [Precision(12, 2)] public decimal? AmountPaid

    payment_detected_at = Column(
        DateTime(timezone=True),
        nullable=True
    )
    # When we detected the payment (when next statement was uploaded)
    # NULL = not detected yet
    # Compare to .NET: public DateTime? PaymentDetectedAt { get; set; }

    revolving_balance = Column(
        Numeric(12, 2),
        nullable=True
    )
    # Unpaid balance carried to next month (subject to interest)
    # Calculated as: statement_balance - amount_paid
    # ZERO if paid in full, POSITIVE if carrying debt
    # Example: 1200.00 SGD (will accrue interest)
    # Compare to .NET: [Precision(12, 2)] public decimal? RevolvingBalance

    estimated_monthly_interest = Column(
        Numeric(10, 2),
        nullable=True
    )
    # Estimated interest user will pay next month on revolving balance
    # Calculated as: revolving_balance * (apr / 12 / 100)
    # Example: 24.00 SGD per month
    # Compare to .NET: [Precision(10, 2)] public decimal? EstimatedMonthlyInterest

    estimated_annual_cost = Column(
        Numeric(10, 2),
        nullable=True
    )
    # Estimated annual interest cost if balance unchanged
    # Calculated as: estimated_monthly_interest * 12
    # Example: 288.00 SGD per year
    # Compare to .NET: [Precision(10, 2)] public decimal? EstimatedAnnualCost

    days_until_due = Column(
        Integer,
        nullable=True
    )
    # Days remaining until payment due
    # Calculated when statement uploaded
    # Negative = overdue
    # Compare to .NET: public int? DaysUntilDue { get; set; }

    # ═══════════════════════════════════════════════════════════════
    # INSIGHTS GENERATION STATUS (NEW!)
    # ═══════════════════════════════════════════════════════════════

    insights_status = Column(
        String(50),
        default="pending",
        nullable=False
    )
    # Values: "pending", "processing", "completed", "failed"
    # Tracks background task for insights generation
    # - "pending": Not started yet
    # - "processing": Background task running
    # - "completed": Insights generated successfully
    # - "failed": Insights generation failed
    # Frontend polls this to know when to show insights

    insights_generated_at = Column(
        DateTime(timezone=True),
        nullable=True
    )
    # When insights were generated
    # NULL = not generated yet

    insights_error = Column(
        Text,
        nullable=True
    )
    # Error message if insights generation failed
    # NULL = no error or not attempted yet

    # ═══════════════════════════════════════════════════════════════
    # TIMESTAMPS
    # ═══════════════════════════════════════════════════════════════

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    # When statement was uploaded

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=True
    )
    # Last time statement metadata was updated

    # ═══════════════════════════════════════════════════════════════
    # RELATIONSHIPS
    # ═══════════════════════════════════════════════════════════════

    # Relationship to User (Many-to-One)
    # "A statement belongs to one user"
    user = relationship(
        "User",
        back_populates="statements"
    )
    # Compare to .NET: public User User { get; set; }

    # Relationship to CreditCard (Many-to-One)
    # "A statement belongs to one credit card"
    credit_card = relationship(
        "CreditCard",
        back_populates="statements"
    )
    # Compare to .NET: public CreditCard CreditCard { get; set; }

    # Relationship to Transactions (One-to-Many)
    # "A statement has many transactions"
    transactions = relationship(
        "Transaction",
        back_populates="statement",
        cascade="all, delete-orphan"  # Delete transactions when statement deleted
    )
    # Compare to .NET: public List<Transaction> Transactions { get; set; }

    # cascade="all, delete-orphan":
    # - If you delete a Statement, all its Transactions are also deleted
    # - Makes sense: transactions are extracted from this specific statement
    # - Compare to .NET: .OnDelete(DeleteBehavior.Cascade)

    # ═══════════════════════════════════════════════════════════════
    # STRING REPRESENTATION
    # ═══════════════════════════════════════════════════════════════

    def __repr__(self):
        return f"<Statement {self.file_name} ({self.statement_year}-{self.statement_month:02d})>"
    # Example: <Statement DBS_Jan2025.pdf (2025-01)>


# ═══════════════════════════════════════════════════════════════════
# KEY CONCEPTS
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
│ # Get all statements for Q1 2025                               │
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
