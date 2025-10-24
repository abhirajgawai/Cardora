"""
Category Model

Transaction categories for organizing expenses (Groceries, Dining, Transport, etc.)

Compare to .NET:
    public class Category
    {
        public Guid Id { get; set; }
        public string Name { get; set; }
        public string Icon { get; set; }
        public string Color { get; set; }
        public Guid? UserId { get; set; }  // Nullable for system categories
        public User User { get; set; }
        public bool IsCustom { get; set; }
        public List<Transaction> Transactions { get; set; }
    }
"""

import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.core.database import Base


class Category(Base):
    """
    Transaction category for expense classification

    Two types of categories:
    1. System categories (user_id = NULL): Available to all users
       - Groceries, Dining, Transport, Shopping, etc.
       - Created during database seeding

    2. Custom categories (user_id = specific user): User-specific
       - Created by individual users for their needs
       - Private to that user only
    """

    __tablename__ = "categories"
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
    # FOREIGN KEY TO USER (Nullable for system categories)
    # ═══════════════════════════════════════════════════════════════

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("cardora.users.id"),
        nullable=True,  # NULL = system category, NOT NULL = custom user category
        index=True
    )
    # IMPORTANT: nullable=True allows system-wide categories
    # System categories: user_id = NULL (available to all)
    # Custom categories: user_id = {specific_user_id} (private)

    # Compare to .NET: [ForeignKey("User")] public Guid? UserId { get; set; }

    # ═══════════════════════════════════════════════════════════════
    # CATEGORY DATA
    # ═══════════════════════════════════════════════════════════════

    name = Column(
        String(100),
        nullable=False,
        index=True  # Index for category searches
    )
    # Example: "Groceries", "Dining", "Transport"
    # Compare to .NET: [Required] [MaxLength(100)] public string Name

    icon = Column(
        String(10),
        nullable=True  # Optional emoji icon
    )
    # Example: "🛒" (Groceries), "🍽️" (Dining), "🚗" (Transport)
    # Stores emoji character (UTF-8)
    # Compare to .NET: [MaxLength(10)] public string Icon

    color = Column(
        String(7),  # Hex color code: #RRGGBB
        nullable=True
    )
    # Example: "#4CAF50" (green for Groceries), "#FF9800" (orange for Dining)
    # Used for UI visualization (charts, cards, etc.)
    # Compare to .NET: [MaxLength(7)] public string Color

    is_custom = Column(
        Boolean,
        default=False,
        nullable=False
    )
    # True = User custom category, False = System category
    # Used to differentiate in queries
    # Compare to .NET: public bool IsCustom { get; set; } = false;

    # ═══════════════════════════════════════════════════════════════
    # TIMESTAMPS
    # ═══════════════════════════════════════════════════════════════

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # ═══════════════════════════════════════════════════════════════
    # RELATIONSHIPS
    # ═══════════════════════════════════════════════════════════════

    # Relationship to User (Many-to-One) - OPTIONAL
    # "A custom category belongs to one user (or no user for system categories)"
    user = relationship(
        "User",
        back_populates="categories"
    )
    # Compare to .NET: public User User { get; set; }

    # Relationship to Transactions (One-to-Many)
    # "A category has many transactions"
    transactions = relationship(
        "Transaction",
        back_populates="category"
    )
    # Compare to .NET: public List<Transaction> Transactions { get; set; }
    # NOTE: No cascade delete - we want to keep transactions even if category is deleted
    # Transactions will have category_id set to NULL instead

    # ═══════════════════════════════════════════════════════════════
    # STRING REPRESENTATION
    # ═══════════════════════════════════════════════════════════════

    def __repr__(self):
        category_type = "System" if not self.is_custom else "Custom"
        return f"<Category {self.name} ({category_type})>"


# ═══════════════════════════════════════════════════════════════════
# KEY CONCEPTS
# ═══════════════════════════════════════════════════════════════════

"""
┌─────────────────────────────────────────────────────────────────┐
│ CONCEPT: Nullable Foreign Keys (System vs User Categories)     │
├─────────────────────────────────────────────────────────────────┤
│ Why user_id is nullable:                                       │
│                                                                 │
│ System Categories (user_id = NULL):                            │
│ - Available to ALL users                                       │
│ - Created during initial setup                                 │
│ - Cannot be deleted by users                                   │
│ - Examples: Groceries, Dining, Transport                       │
│                                                                 │
│ Custom Categories (user_id = specific UUID):                   │
│ - Private to one user                                          │
│ - User can create, edit, delete                                │
│ - Examples: "My Pet Food", "Home Renovation"                   │
│                                                                 │
│ Query Example:                                                  │
│ # Get all categories for a user                                │
│ categories = db.query(Category).filter(                        │
│     (Category.user_id == user_id) |                             │
│     (Category.user_id == None)                                  │
│ ).all()                                                         │
│                                                                 │
│ Compare to .NET:                                                │
│   var categories = await _context.Categories                    │
│       .Where(c => c.UserId == userId || c.UserId == null)       │
│       .ToListAsync();                                           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ CONCEPT: No Cascade Delete for Categories                      │
├─────────────────────────────────────────────────────────────────┤
│ Notice: transactions relationship has NO cascade parameter     │
│                                                                 │
│ Why?                                                            │
│ - If user deletes a category, we DON'T want to delete          │
│   all transactions in that category                            │
│ - Instead, transactions.category_id → NULL                     │
│ - Preserves transaction history                                │
│ - User can later reassign transactions to different category   │
│                                                                 │
│ Compare to CreditCard:                                          │
│ - CreditCard HAS cascade delete                                │
│ - If card deleted → all transactions deleted (makes sense)     │
│                                                                 │
│ Compare to .NET EF Core:                                        │
│   modelBuilder.Entity<Transaction>()                            │
│       .HasOne(t => t.Category)                                  │
│       .WithMany(c => c.Transactions)                            │
│       .OnDelete(DeleteBehavior.SetNull);  // Set to NULL       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ DEFAULT SYSTEM CATEGORIES                                       │
├─────────────────────────────────────────────────────────────────┤
│ 1. Groceries        🛒  #4CAF50 (Green)                         │
│ 2. Dining           🍽️  #FF9800 (Orange)                        │
│ 3. Transport        🚗  #2196F3 (Blue)                          │
│ 4. Shopping         🛍️  #E91E63 (Pink)                          │
│ 5. Entertainment    🎬  #9C27B0 (Purple)                        │
│ 6. Bills & Utilities💡  #607D8B (Blue Grey)                     │
│ 7. Healthcare       🏥  #F44336 (Red)                           │
│ 8. Others           📦  #9E9E9E (Grey)                          │
│                                                                 │
│ These will be seeded during database setup.                    │
└─────────────────────────────────────────────────────────────────┘
"""
