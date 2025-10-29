"""
Transaction Model

Individual credit card transactions extracted from statements or manually entered.

Compare to .NET:
    [Table("transactions", Schema = "cardora")]
    [Index(nameof(UserId), nameof(TransactionDate))]
    [Index(nameof(UserId), nameof(CategoryId))]
    [Index(nameof(CardId))]
    [Index(nameof(UserId), nameof(StatementMonth), nameof(StatementYear))]
    public class Transaction
    {
        public Guid Id { get; set; }
        public Guid UserId { get; set; }
        public Guid CardId { get; set; }
        public Guid? StatementId { get; set; }
        public Guid? CategoryId { get; set; }

        public string MerchantName { get; set; }
        public decimal Amount { get; set; }
        public DateTime TransactionDate { get; set; }
        public string Description { get; set; }

        public int StatementMonth { get; set; }
        public int StatementYear { get; set; }
        public bool IsRecurring { get; set; }
        public decimal? ConfidenceScore { get; set; }

        public User User { get; set; }
        public CreditCard CreditCard { get; set; }
        public Statement Statement { get; set; }
        public Category Category { get; set; }
    }
"""

import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, Numeric, DateTime, Date, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.core.database import Base


class Transaction(Base):
    """
    Individual credit card transaction

    Represents a single purchase/payment extracted from statement or manually entered.

    Key Features:
    - Extracted by Gemini AI from PDF statements
    - Can be manually created/edited by users
    - Categorized for expense tracking
    - Performance-optimized with multiple indexes
    """

    __tablename__ = "transactions"
    __table_args__ = (
        # ═══════════════════════════════════════════════════════════════
        # PERFORMANCE INDEXES
        # ═══════════════════════════════════════════════════════════════

        # Index 1: User + Date (for date range queries)
        # Query: "Show all transactions for user in January 2025"
        Index(
            "ix_transactions_user_date",
            "user_id", "transaction_date",
            postgresql_using="btree"
        ),
        # Compare to .NET: [Index(nameof(UserId), nameof(TransactionDate))]

        # Index 2: User + Category (for category analytics)
        # Query: "How much did user spend on Groceries?"
        Index(
            "ix_transactions_user_category",
            "user_id", "category_id",
            postgresql_using="btree"
        ),
        # Compare to .NET: [Index(nameof(UserId), nameof(CategoryId))]

        # Index 3: Card ID (for card-specific queries)
        # Query: "Show all transactions for this credit card"
        Index(
            "ix_transactions_card",
            "card_id",
            postgresql_using="btree"
        ),
        # Compare to .NET: [Index(nameof(CardId))]

        # Index 4: User + Statement Month/Year (for monthly reports)
        # Query: "Show all January 2025 transactions for user"
        # This is CRITICAL for performance in monthly views!
        Index(
            "ix_transactions_user_month_year",
            "user_id", "statement_month", "statement_year",
            postgresql_using="btree"
        ),
        # Compare to .NET: [Index(nameof(UserId), nameof(StatementMonth), nameof(StatementYear))]

        {"schema": "cardora"}
    )

    """
    EXPLANATION: Why These Indexes?

    Without indexes:
    - Query: "Show January 2025 transactions" → Scans ALL rows (SLOW!)
    - 10,000 transactions = 10,000 rows scanned
    - Takes 500ms+

    With indexes:
    - Query: "Show January 2025 transactions" → Index lookup (FAST!)
    - 10,000 transactions, 50 match → Only 50 rows examined
    - Takes 5ms

    Index Strategy:
    1. Most common queries first (user_id + transaction_date)
    2. Analytics queries (user_id + category_id)
    3. Card-specific queries (card_id)
    4. Monthly reports (user_id + month + year)

    Trade-offs:
    ✓ Queries are 100x faster
    ✗ Inserts are slightly slower (must update indexes)
    ✗ Takes more disk space

    For Cardora: WORTH IT! We read data 100x more than we write.

    Compare to .NET EF Core:
        protected override void OnModelCreating(ModelBuilder builder)
        {
            builder.Entity<Transaction>()
                .HasIndex(t => new { t.UserId, t.TransactionDate });

            builder.Entity<Transaction>()
                .HasIndex(t => new { t.UserId, t.CategoryId });
        }
    """

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
        nullable=False
    )
    # Every transaction belongs to a user
    # Note: No separate index needed (covered by composite indexes above)
    # Compare to .NET: [ForeignKey("User")] public Guid UserId { get; set; }

    card_id = Column(
        UUID(as_uuid=True),
        ForeignKey("cardora.credit_cards.id"),
        nullable=False
    )
    # Which credit card was used for this transaction
    # Note: Indexed separately (see Index 3 above)
    # Compare to .NET: [ForeignKey("CreditCard")] public Guid CardId { get; set; }

    statement_id = Column(
        UUID(as_uuid=True),
        ForeignKey("cardora.statements.id"),
        nullable=True  # NULL for manually entered transactions
    )
    # Which statement this transaction came from
    # NULL = manually entered by user (not from PDF)
    # NOT NULL = extracted from uploaded statement
    # Compare to .NET: [ForeignKey("Statement")] public Guid? StatementId

    category_id = Column(
        UUID(as_uuid=True),
        ForeignKey("cardora.categories.id"),
        nullable=True  # NULL if uncategorized
    )
    # Transaction category for expense tracking
    # NULL = uncategorized (user hasn't assigned yet)
    # Compare to .NET: [ForeignKey("Category")] public Guid? CategoryId

    # ═══════════════════════════════════════════════════════════════
    # TRANSACTION DETAILS
    # ═══════════════════════════════════════════════════════════════

    merchant_name = Column(
        String(255),
        nullable=False
    )
    # Merchant/vendor name exactly as it appears on statement
    # Example: "NTUC FAIRPRICE JURONG POINT", "GRAB", "STARBUCKS"
    # NOT cleaned - stored raw from Gemini extraction
    # Compare to .NET: [Required] [MaxLength(255)] public string MerchantName

    amount = Column(
        Numeric(10, 2),  # ALWAYS Numeric for money, NEVER Float!
        nullable=False
    )
    # Transaction amount in SGD (or user's currency)
    # Example: 45.80, 12.50, 1250.00
    # Always positive (no negative amounts)
    # Compare to .NET: [Precision(10, 2)] public decimal Amount { get; set; }

    transaction_date = Column(
        Date,  # DATE type (no time component)
        nullable=False
    )
    # Date of transaction (not datetime!)
    # Example: 2025-01-15
    # Extracted from statement or entered by user
    # Compare to .NET: [DataType(DataType.Date)] public DateTime TransactionDate

    description = Column(
        String(500),
        nullable=True  # Optional additional notes
    )
    # Optional description or notes
    # Could be user-entered or from statement
    # Example: "Monthly grocery shopping", "Taxi to airport"
    # Compare to .NET: [MaxLength(500)] public string Description

    # ═══════════════════════════════════════════════════════════════
    # DENORMALIZED FIELDS (for performance!)
    # ═══════════════════════════════════════════════════════════════

    statement_month = Column(
        Integer,  # 1-12
        nullable=False
    )
    # DENORMALIZED from statement for fast queries!
    # Stored in BOTH transactions AND statements tables
    # Why? So we can query transactions by month WITHOUT joining statements
    # Compare to .NET: [Range(1, 12)] public int StatementMonth { get; set; }

    statement_year = Column(
        Integer,
        nullable=False
    )
    # DENORMALIZED from statement for fast queries!
    # Example: 2025, 2024
    # Compare to .NET: public int StatementYear { get; set; }

    """
    WHY DENORMALIZE statement_month and statement_year?

    Normal Form (BAD for performance):
    - Transaction has statement_id
    - To get month: JOIN statements table, extract statement_month
    - Every monthly query requires JOIN
    - 10,000 transactions = 10,000 rows joined

    Denormalized (GOOD for performance):
    - Transaction has statement_month and statement_year directly
    - No JOIN needed for monthly queries
    - Query: WHERE user_id = X AND statement_month = 1 AND statement_year = 2025
    - With index, this is INSTANT!

    Trade-off:
    ✗ Data duplication (month/year stored in 2 tables)
    ✓ 10-100x faster queries
    ✓ No JOINs for common queries
    ✓ Indexed for lightning-fast filtering

    Database normalization says: "Don't duplicate data"
    Performance optimization says: "Duplicate when it matters"

    For Cardora: DENORMALIZE! Query speed > storage space

    Compare to .NET:
    // Normal approach (slow)
    var transactions = await _context.Transactions
        .Include(t => t.Statement)
        .Where(t => t.Statement.StatementMonth == 1)
        .ToListAsync();

    // Denormalized approach (fast)
    var transactions = await _context.Transactions
        .Where(t => t.StatementMonth == 1)
        .ToListAsync();
    """

    # ═══════════════════════════════════════════════════════════════
    # AI & METADATA
    # ═══════════════════════════════════════════════════════════════

    is_recurring = Column(
        Boolean,
        default=False,
        nullable=False
    )
    # Future feature: Detect recurring transactions
    # Example: Netflix subscription every month, utilities
    # For MVP: Always False
    # Compare to .NET: public bool IsRecurring { get; set; } = false;

    confidence_score = Column(
        Numeric(3, 2),  # 0.00 to 1.00
        nullable=True
    )
    # AI confidence score for this transaction extraction
    # Example: 0.95 = 95% confident about extraction accuracy
    # Future: Flag low-confidence transactions for review
    # Compare to .NET: [Precision(3, 2)] public decimal? ConfidenceScore

    # ═══════════════════════════════════════════════════════════════
    # TIMESTAMPS
    # ═══════════════════════════════════════════════════════════════

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    # When transaction was added to database (not transaction date!)

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=True
    )
    # When transaction was last modified (e.g., category changed)

    # ═══════════════════════════════════════════════════════════════
    # RELATIONSHIPS
    # ═══════════════════════════════════════════════════════════════

    # Relationship to User (Many-to-One)
    user = relationship(
        "User",
        back_populates="transactions"
    )
    # Compare to .NET: public User User { get; set; }

    # Relationship to CreditCard (Many-to-One)
    credit_card = relationship(
        "CreditCard",
        back_populates="transactions"
    )
    # Compare to .NET: public CreditCard CreditCard { get; set; }

    # Relationship to Statement (Many-to-One)
    statement = relationship(
        "Statement",
        back_populates="transactions"
    )
    # Compare to .NET: public Statement Statement { get; set; }

    # Relationship to Category (Many-to-One)
    category = relationship(
        "Category",
        back_populates="transactions"
    )
    # Compare to .NET: public Category Category { get; set; }

    # Relationship to Insights (Many-to-Many through InsightTransaction)
    # "A transaction can be referenced by multiple insights"
    insight_transactions = relationship(
        "InsightTransaction",
        back_populates="transaction"
    )
    # Compare to .NET: public List<InsightTransaction> InsightTransactions { get; set; }

    # ═══════════════════════════════════════════════════════════════
    # STRING REPRESENTATION
    # ═══════════════════════════════════════════════════════════════

    def __repr__(self):
        return f"<Transaction {self.merchant_name} ${self.amount} on {self.transaction_date}>"


# ═══════════════════════════════════════════════════════════════════
# KEY CONCEPTS
# ═══════════════════════════════════════════════════════════════════

"""
┌─────────────────────────────────────────────────────────────────┐
│ CONCEPT: Database Indexes Explained                            │
├─────────────────────────────────────────────────────────────────┤
│ What is an Index?                                              │
│ Like an index in a book - helps you find things quickly!       │
│                                                                 │
│ Without Index:                                                  │
│ "Find all transactions for user 123 in January"                │
│ → Database scans EVERY row (Full Table Scan)                   │
│ → 10,000 transactions = checks all 10,000 rows                 │
│ → Takes 500ms                                                   │
│                                                                 │
│ With Index:                                                     │
│ "Find all transactions for user 123 in January"                │
│ → Database uses index (B-tree lookup)                          │
│ → Finds 50 matching rows directly                              │
│ → Takes 5ms (100x faster!)                                     │
│                                                                 │
│ Analogy:                                                        │
│ Without index: Flip through entire phonebook page by page      │
│ With index: Jump directly to last name "S" section             │
│                                                                 │
│ PostgreSQL uses B-tree indexes by default:                     │
│ - Sorted tree structure                                        │
│ - O(log n) lookup time                                         │
│ - Perfect for equality and range queries                       │
│                                                                 │
│ Index Cost:                                                     │
│ ✓ Faster SELECT queries (100x improvement)                     │
│ ✗ Slower INSERT/UPDATE (must update index)                     │
│ ✗ Uses disk space (index data structure)                       │
│                                                                 │
│ For Cardora:                                                    │
│ - Users read transactions 1000x more than write                │
│ - Indexes are ESSENTIAL for good UX                            │
│ - Worth the trade-off!                                         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ CONCEPT: Composite Indexes                                     │
├─────────────────────────────────────────────────────────────────┤
│ Composite Index = Index on multiple columns                    │
│                                                                 │
│ Example: Index(user_id, transaction_date)                      │
│                                                                 │
│ Speeds up queries like:                                        │
│ ✓ WHERE user_id = X AND transaction_date = Y                   │
│ ✓ WHERE user_id = X AND transaction_date > Y                   │
│ ✓ WHERE user_id = X  (uses first column)                       │
│                                                                 │
│ Does NOT speed up:                                              │
│ ✗ WHERE transaction_date = Y  (doesn't use first column)       │
│                                                                 │
│ Rule: "Leftmost prefix"                                        │
│ - Index(A, B, C) works for: A, (A,B), (A,B,C)                  │
│ - Index(A, B, C) does NOT work for: B, C, (B,C)                │
│                                                                 │
│ Our indexes cover these queries:                               │
│ 1. (user_id, transaction_date) → Date range queries           │
│ 2. (user_id, category_id) → Category analytics                │
│ 3. (card_id) → Card transactions                              │
│ 4. (user_id, statement_month, statement_year) → Monthly view  │
│                                                                 │
│ These 4 indexes cover 95% of Cardora queries!                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ CONCEPT: Denormalization for Performance                       │
├─────────────────────────────────────────────────────────────────┤
│ Database Design Principle: "Normalize until it hurts,          │
│                             denormalize until it works"         │
│                                                                 │
│ Normal Form (3NF):                                              │
│ - No duplicate data                                            │
│ - Everything in its place                                      │
│ - Requires JOINs to get related data                           │
│                                                                 │
│ Denormalized:                                                   │
│ - Duplicate data strategically                                 │
│ - Fewer JOINs needed                                           │
│ - Much faster queries                                          │
│                                                                 │
│ In Cardora:                                                     │
│ statement_month and statement_year are stored in:              │
│ 1. statements table (source of truth)                          │
│ 2. transactions table (denormalized copy)                      │
│                                                                 │
│ Why?                                                            │
│ "Show January 2025 transactions" is the MOST common query      │
│ Without denormalization: JOIN statements (slow)                │
│ With denormalization: Direct WHERE clause (fast)               │
│                                                                 │
│ Trade-off:                                                      │
│ ✗ 8 bytes duplicated per transaction                           │
│ ✓ 10-100x faster queries                                       │
│ ✓ Better user experience                                       │
│                                                                 │
│ For high-traffic apps, query speed > storage space             │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ CONCEPT: Date vs DateTime for transaction_date                 │
├─────────────────────────────────────────────────────────────────┤
│ We use Date, not DateTime. Why?                                │
│                                                                 │
│ Date (our choice):                                              │
│ - Only stores: 2025-01-15                                      │
│ - No time component                                            │
│ - 4 bytes in PostgreSQL                                        │
│ - Perfect for credit card statements (no exact time)           │
│                                                                 │
│ DateTime (alternative):                                         │
│ - Stores: 2025-01-15 14:30:22                                  │
│ - Includes time                                                │
│ - 8 bytes in PostgreSQL                                        │
│ - Unnecessary for credit card transactions                     │
│                                                                 │
│ Credit card statements show:                                   │
│ "15 JAN NTUC FAIRPRICE 45.80"                                  │
│ NOT: "15 JAN 14:30:22 NTUC FAIRPRICE 45.80"                    │
│                                                                 │
│ Benefits of Date:                                               │
│ ✓ Matches statement format                                     │
│ ✓ Smaller storage (4 bytes vs 8)                               │
│ ✓ Simpler queries (no time zone issues)                        │
│ ✓ Easier date range filtering                                  │
│                                                                 │
│ Compare to .NET:                                                │
│   [DataType(DataType.Date)]                                     │
│   public DateTime TransactionDate { get; set; }                 │
└─────────────────────────────────────────────────────────────────┘
"""
