"""
Credit Card Model

Compare to .NET Entity Framework Core:
    public class CreditCard
    {
        public Guid Id { get; set; }
        public Guid UserId { get; set; }
        public User User { get; set; }  // Navigation property

        public string BankName { get; set; }
        public string CardName { get; set; }
        public string LastFourDigits { get; set; }

        public List<Transaction> Transactions { get; set; }  // Collection navigation
        public List<Statement> Statements { get; set; }
    }

SQLAlchemy uses Column() for fields and relationship() for navigations.
"""

# ═══════════════════════════════════════════════════════════════════
# IMPORTS
# ═══════════════════════════════════════════════════════════════════

import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, Numeric, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.core.database import Base

# Column: Defines a database column (like a property in .NET)
# String: VARCHAR type in PostgreSQL (like string in .NET)
# Boolean: BOOLEAN type (like bool in .NET)
# ForeignKey: Creates foreign key constraint (like [ForeignKey("UserId")] in .NET)
# UUID: PostgreSQL's native UUID type (like Guid in .NET)
# Numeric: DECIMAL type for precise money values (like decimal in .NET)
# relationship(): Creates ORM navigation property (NOT a database column!)
# Base: The declarative base all models inherit from


# ═══════════════════════════════════════════════════════════════════
# CREDIT CARD MODEL
# ═══════════════════════════════════════════════════════════════════

class CreditCard(Base):
    """
    Represents a user's credit card

    Compare to .NET:
        [Table("credit_cards", Schema = "cardora")]
        public class CreditCard
        {
            [Key]
            public Guid Id { get; set; }

            [Required]
            [ForeignKey("User")]
            public Guid UserId { get; set; }
            public User User { get; set; }

            [Required]
            [MaxLength(100)]
            public string BankName { get; set; }

            [MaxLength(4)]
            public string LastFourDigits { get; set; }

            [Precision(10, 2)]
            public decimal? CreditLimit { get; set; }

            public List<Transaction> Transactions { get; set; }
        }
    """

    # Table name in database
    __tablename__ = "credit_cards"

    # Specify schema (like [Table("credit_cards", Schema = "cardora")])
    __table_args__ = {"schema": "cardora"}

    # ═══════════════════════════════════════════════════════════════
    # PRIMARY KEY
    # ═══════════════════════════════════════════════════════════════

    id = Column(
        UUID(as_uuid=True),  # PostgreSQL UUID type
        primary_key=True,     # This is the primary key
        default=uuid.uuid4,   # Auto-generate UUID on insert
        nullable=False        # Cannot be NULL
    )
    # Compare to .NET: [Key] public Guid Id { get; set; }

    # ═══════════════════════════════════════════════════════════════
    # FOREIGN KEY TO USER
    # ═══════════════════════════════════════════════════════════════

    user_id = Column(
        UUID(as_uuid=True),                        # Type: UUID
        ForeignKey("cardora.users.id"),           # Foreign key constraint
        nullable=False,                            # Required field
        index=True                                 # Create index for faster lookups
    )
    # Compare to .NET:
    #   [ForeignKey("User")]
    #   public Guid UserId { get; set; }

    # IMPORTANT: ForeignKey() does TWO things:
    # 1. Creates a column in the database (user_id)
    # 2. Adds a foreign key CONSTRAINT (prevents orphan records)

    # ═══════════════════════════════════════════════════════════════
    # CARD DETAILS
    # ═══════════════════════════════════════════════════════════════

    bank_name = Column(
        String(100),          # VARCHAR(100)
        nullable=False,       # Required
        index=True            # Index for filtering by bank
    )
    # Example: "DBS Bank", "OCBC Bank", "UOB"
    # Compare to .NET: [Required] [MaxLength(100)] public string BankName

    card_name = Column(
        String(100),          # VARCHAR(100)
        nullable=True         # Optional field
    )
    # Example: "DBS Altitude Visa", "OCBC 365 Cashback"
    # Compare to .NET: [MaxLength(100)] public string CardName

    last_four_digits = Column(
        String(4),            # Exactly 4 characters
        nullable=False,       # Required
        index=True            # Index for card lookups
    )
    # Example: "1234", "5678"
    # Used to identify card without storing full number (PCI compliance)
    # Compare to .NET: [Required] [StringLength(4, MinimumLength=4)]

    card_type = Column(
        String(50),           # VARCHAR(50)
        nullable=True         # Optional
    )
    # Example: "Visa", "Mastercard", "American Express"
    # Compare to .NET: [MaxLength(50)] public string CardType

    credit_limit = Column(
        Numeric(10, 2),       # DECIMAL(10,2) - 10 digits total, 2 after decimal
        nullable=True         # Optional
    )
    # Example: 5000.00 means $5,000 credit limit
    # Numeric is used for money to avoid floating point errors
    # Compare to .NET: [Precision(10, 2)] public decimal? CreditLimit

    # ═══════════════════════════════════════════════════════════════
    # STATUS FLAGS
    # ═══════════════════════════════════════════════════════════════

    is_active = Column(
        Boolean,              # BOOLEAN type
        default=True,         # New cards are active by default
        nullable=False
    )
    # Used to soft-delete cards (set to False instead of DELETE)
    # Compare to .NET: public bool IsActive { get; set; } = true;

    # ═══════════════════════════════════════════════════════════════
    # TIMESTAMPS
    # ═══════════════════════════════════════════════════════════════

    created_at = Column(
        DateTime(timezone=True),                     # TIMESTAMP WITH TIME ZONE
        default=lambda: datetime.now(timezone.utc),  # Auto-set on insert
        nullable=False
    )
    # Compare to .NET: public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),  # Auto-update on modification
        nullable=True
    )
    # onupdate: Automatically updates timestamp when row is modified
    # Compare to .NET: Use EF Core interceptor or trigger

    # ═══════════════════════════════════════════════════════════════
    # RELATIONSHIPS (ORM Navigation Properties)
    # ═══════════════════════════════════════════════════════════════

    # Relationship to User (Many-to-One)
    # "A credit card belongs to one user"
    user = relationship(
        "User",                    # Target model name (as string)
        back_populates="credit_cards"  # Matching property in User model
    )
    # Compare to .NET: public User User { get; set; }

    # IMPORTANT: relationship() does NOT create a database column!
    # It's purely for ORM convenience in Python code.
    # The actual foreign key is user_id above.

    # Relationship to Transactions (One-to-Many)
    # "A credit card has many transactions"
    transactions = relationship(
        "Transaction",                # Target model
        back_populates="credit_card",  # Property in Transaction model
        cascade="all, delete-orphan"   # Delete transactions when card is deleted
    )
    # Compare to .NET: public List<Transaction> Transactions { get; set; }

    # cascade="all, delete-orphan":
    # - When you delete a CreditCard, all its Transactions are also deleted
    # - Compare to .NET: .OnDelete(DeleteBehavior.Cascade)

    # Relationship to Statements (One-to-Many)
    # "A credit card has many statements"
    statements = relationship(
        "Statement",
        back_populates="credit_card",
        cascade="all, delete-orphan"
    )
    # Compare to .NET: public List<Statement> Statements { get; set; }

    # ═══════════════════════════════════════════════════════════════
    # STRING REPRESENTATION
    # ═══════════════════════════════════════════════════════════════

    def __repr__(self):
        """String representation for debugging"""
        return f"<CreditCard {self.bank_name} *{self.last_four_digits}>"
    # Compare to .NET: public override string ToString()


# ═══════════════════════════════════════════════════════════════════
# KEY CONCEPTS EXPLAINED
# ═══════════════════════════════════════════════════════════════════

"""
┌─────────────────────────────────────────────────────────────────┐
│ CONCEPT 1: Foreign Keys in SQLAlchemy                          │
├─────────────────────────────────────────────────────────────────┤
│ .NET Way:                                                       │
│   [ForeignKey("User")]                                          │
│   public Guid UserId { get; set; }                              │
│   public User User { get; set; }  // Navigation property       │
│                                                                 │
│ SQLAlchemy Way:                                                 │
│   user_id = Column(UUID, ForeignKey("cardora.users.id"))       │
│   user = relationship("User", back_populates="credit_cards")   │
│                                                                 │
│ Key Difference:                                                 │
│ - ForeignKey() creates the COLUMN and CONSTRAINT               │
│ - relationship() creates the NAVIGATION PROPERTY (ORM only)    │
│ - They are SEPARATE in SQLAlchemy                              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ CONCEPT 2: relationship() vs back_populates                    │
├─────────────────────────────────────────────────────────────────┤
│ back_populates:                                                 │
│ - Explicitly defines BOTH sides of the relationship            │
│ - More control, clearer intent                                 │
│ - Recommended for production code                              │
│                                                                 │
│ Example:                                                        │
│ # In CreditCard model:                                          │
│ user = relationship("User", back_populates="credit_cards")     │
│                                                                 │
│ # In User model:                                                │
│ credit_cards = relationship("CreditCard", back_populates="user")│
│                                                                 │
│ backref (older style):                                          │
│ - Automatically creates the reverse relationship               │
│ - Less explicit, can be confusing                              │
│                                                                 │
│ Compare to .NET:                                                │
│ - You must define BOTH navigation properties manually          │
│ - Similar to back_populates approach                           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ CONCEPT 3: Cascade Delete                                      │
├─────────────────────────────────────────────────────────────────┤
│ cascade="all, delete-orphan":                                   │
│ - When you delete CreditCard, all Transactions are deleted     │
│ - Prevents orphan records                                      │
│                                                                 │
│ Compare to .NET EF Core:                                        │
│   modelBuilder.Entity<Transaction>()                            │
│       .HasOne(t => t.CreditCard)                                │
│       .WithMany(c => c.Transactions)                            │
│       .OnDelete(DeleteBehavior.Cascade);                        │
│                                                                 │
│ Options:                                                        │
│ - "all, delete-orphan": Full cascade delete                    │
│ - "all": Cascade updates and deletes                           │
│ - None: No cascade (default)                                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ CONCEPT 4: Numeric vs Float for Money                          │
├─────────────────────────────────────────────────────────────────┤
│ ALWAYS use Numeric (DECIMAL) for money, NEVER Float            │
│                                                                 │
│ Why?                                                            │
│ Float has rounding errors:                                      │
│   0.1 + 0.2 = 0.30000000000000004  (WRONG!)                    │
│                                                                 │
│ Numeric is exact:                                               │
│   0.1 + 0.2 = 0.30  (CORRECT!)                                 │
│                                                                 │
│ Numeric(10, 2) means:                                           │
│ - 10 digits total                                              │
│ - 2 digits after decimal                                       │
│ - Max value: 99,999,999.99                                     │
│                                                                 │
│ Compare to .NET: decimal (NOT double or float!)                │
└─────────────────────────────────────────────────────────────────┘
"""
