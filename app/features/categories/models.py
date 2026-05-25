"""
Category Model

Transaction categories for organizing expenses (Groceries, Dining, Transport, etc.)

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
        index=True
    )

    
    # ═══════════════════════════════════════════════════════════════
    # ═══════════════════════════════════════════════════════════════

    name = Column(
        String(100),
        nullable=False,
    )
    
    icon = Column(
        String(10),
    )
    
    color = Column(
        String(10),
        nullable=True,
    )
    
    is_custom = Column(
        Boolean,
        default=False,
        nullable=False
    )
    
    # ═══════════════════════════════════════════════════════════════
    # ═══════════════════════════════════════════════════════════════

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # ═══════════════════════════════════════════════════════════════
    # ═══════════════════════════════════════════════════════════════

    user = relationship(
        "User",
        back_populates="categories"
    )
    
    transactions = relationship(
        "Transaction",
        back_populates="category"
    )

    # ═══════════════════════════════════════════════════════════════
    # ═══════════════════════════════════════════════════════════════

    def __repr__(self):
        category_type = "System" if not self.is_custom else "Custom"
        return f"<Category {self.name} ({category_type})>"


# ═══════════════════════════════════════════════════════════════════
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
│ categories = db.query(Category).filter(                        │
│     (Category.user_id == user_id) |                             │
│     (Category.user_id == None)                                  │
│ ).all()                                                         │
│                                                                 │
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
│   modelBuilder.Entity<Transaction>()                            │
│       .HasOne(t => t.Category)                                  │
│       .WithMany(c => c.Transactions)                            │
│       .OnDelete(DeleteBehavior.SetNull);  // Set to NULL       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ DEFAULT SYSTEM CATEGORIES                                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ These will be seeded during database setup.                    │
└─────────────────────────────────────────────────────────────────┘
"""
