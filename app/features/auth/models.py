"""
User Model for Cardora Authentication

This is like creating an Entity class in Entity Framework Core.
In .NET, you'd have a User.cs file in your Models or Entities folder.

The User model represents the 'users' table in PostgreSQL.
"""

from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class User(Base):
    """
    User Entity - Represents a Cardora user account

    public class User
    {
        [Key]
        public Guid Id { get; set; }

        [Required, EmailAddress]
        public string Email { get; set; }

        // ... more properties
    }

    Key differences:
    - SQLAlchemy: __tablename__ defines table name
    - EF Core: Table name inferred from DbSet<User> or [Table] attribute
    - SQLAlchemy: Column() explicit, EF Core: properties become columns
    - Both support constraints, defaults, and relationships
    """

    # ============================================================
    # ============================================================
    __tablename__ = "users"
    __table_args__ = {'schema': 'cardora'}

    """
    EXPLANATION: __tablename__ and __table_args__

    In .NET EF Core:
    - Table name inferred from DbSet<User> Users → "Users" table
    - Or use [Table("users", Schema = "Cardora")] attribute

    Example in C#:
    [Table("Users", Schema = "Cardora")]
    public class User { }

    In SQLAlchemy:
    - __tablename__ = "users" → table name
    - __table_args__ = {'schema': 'cardora'} → schema name
    - Full table reference: cardora.users

    Why Custom Schema?
    - Organization: Group Cardora tables together
    - Security: Separate from public schema
    - Best Practice: Don't use public schema for app tables
    - Like SQL Server: Cardora.Users vs dbo.Users
    """

    # ============================================================
    # ============================================================
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    """
    EXPLANATION: Primary Key with UUID

    In .NET EF Core:
    [Key]
    public Guid Id { get; set; }

    In SQLAlchemy:
    - Column(UUID(as_uuid=True)) → Use PostgreSQL's native UUID type
    - primary_key=True → Marks this as the primary key (like [Key])
    - default=uuid.uuid4 → Auto-generate new UUID for each record
    - as_uuid=True → Store as UUID in DB, return as Python uuid object

    Why UUID instead of Integer?
    - UUIDs are globally unique (no collisions across servers)
    - Better for distributed systems
    - Harder to guess user IDs (security)
    - Same as Guid in C#
    """

    # ============================================================
    # ============================================================
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    """
    EXPLANATION: Email field

    In .NET EF Core:
    [Required]
    [EmailAddress]
    [MaxLength(255)]
    public string Email { get; set; }

    In SQLAlchemy:
    - String(255) → VARCHAR(255) in database
    - unique=True → UNIQUE constraint (like SQL: UNIQUE)
    - nullable=False → NOT NULL (like [Required])
    - index=True → CREATE INDEX for faster email lookups

    Why index=True?
    - Users login with email → frequent WHERE email = ?
    - Index makes lookups O(log n) instead of O(n)
    - Like adding an index in SQL Server Management Studio
    """

    google_id = Column(
        String(255),
        unique=True,
        nullable=True,
        index=True,
    )

    hashed_password = Column(
        String(255),
        nullable=True
    )

    """
    EXPLANATION: Password Storage

    NEVER store plain text passwords!

    In .NET:
    public string PasswordHash { get; set; }

    We store:
    - hashed_password: bcrypt hash of the password
    - NOT the actual password!

    Example:
    Plain password: "MySecurePass123"
    Stored hash: "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/..."

    Why?
    - If database is compromised, passwords are safe
    - bcrypt is one-way (can't reverse the hash)
    - We'll create hashing utilities in Step 3
    """

    # ============================================================
    # ============================================================
    full_name = Column(
        String(255),
    )

    """
    EXPLANATION: Optional Fields

    In .NET EF Core:
    public string? FullName { get; set; }  // Nullable string

    In SQLAlchemy:
    - nullable=True → field can be NULL in database
    - nullable=False → field is required

    Default is nullable=True, but we make it explicit for clarity.
    """

    # ============================================================
    # ============================================================
    timezone = Column(
        String(50),
        nullable=False,
    )

    """
    EXPLANATION: Default Values

    In .NET EF Core:
    [DefaultValue("Asia/Singapore")]
    public string Timezone { get; set; }

    Or in constructor:
    public User()
    {
        Timezone = "Asia/Singapore";
    }

    In SQLAlchemy:
    - default="Asia/Singapore" → Set default in application code
    - server_default=text("'Asia/Singapore'") → Set default in database

    We use application default here (Python sets it).
    """

    # ============================================================
    # ============================================================
    is_active = Column(
        Boolean,
        nullable=False,
        default=True
    )

    """
    EXPLANATION: Boolean Flags

    In .NET EF Core:
    public bool IsActive { get; set; } = true;

    In SQLAlchemy:
    - Boolean → BOOLEAN type in PostgreSQL
    - default=True → New users are active by default

    Use cases:
    - is_active: Soft delete (deactivate instead of deleting)
    - Can prevent login without deleting account
    """

    is_verified = Column(
        Boolean,
        nullable=False,
        default=False
    )

    """
    EXPLANATION: Email Verification Flag

    Workflow:
    1. User registers → is_verified = False
    2. Send verification email with token
    3. User clicks link → is_verified = True
    4. Only verified users can access certain features

    In production:
    - Send verification email after registration
    - Check is_verified before sensitive operations
    """

    # ============================================================
    # ============================================================
    reset_token = Column(
        String(255),
    )

    """
    EXPLANATION: Password Reset Token

    In .NET ASP.NET Core Identity:
    public string? ResetToken { get; set; }

    Or generated via:
    var token = await _userManager.GeneratePasswordResetTokenAsync(user);

    In our implementation:
    - reset_token: Hashed version of the reset token
    - NULL when no reset is in progress
    - Set when user requests password reset
    - Cleared after successful reset or expiration

    Security:
    - We store the HASHED token (like passwords)
    - Send plain token via email
    - This way if DB is compromised, tokens are safe
    - Token is cryptographically secure (secrets.token_urlsafe)

    Workflow:
    1. User forgets password
    2. Generate token: abc123def456...
    3. Hash token and save to DB: sha256(abc123def456...)
    4. Send plain token via email
    5. User clicks link with token
    6. Hash received token and compare with DB
    7. If match and not expired → allow reset
    """

    reset_token_expires = Column(
        DateTime(timezone=True),
    )

    """
    EXPLANATION: Password Reset Token Expiration

    In .NET ASP.NET Core Identity:
    services.Configure<DataProtectionTokenProviderOptions>(options =>
    {
        options.TokenLifespan = TimeSpan.FromHours(1);
    });

    In our implementation:
    - reset_token_expires: Timestamp when token expires
    - Typically 1 hour from generation
    - Prevents old reset links from being used
    - NULL when no reset is in progress

    Security benefits:
    - Limits attack window
    - Old emails can't be used indefinitely
    - Forces users to request new link if expired

    Example:
    - Token generated at: 2024-10-22 14:00:00
    - Token expires at:   2024-10-22 15:00:00
    - If current time > expires → reject token
    """

    # ============================================================
    # ============================================================
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    """
    EXPLANATION: Created Timestamp

    In .NET EF Core:
    [DatabaseGenerated(DatabaseGeneratedOption.Identity)]
    public DateTime CreatedAt { get; set; }

    Or use interceptor:
    public override int SaveChanges()
    {
        var entries = ChangeTracker.Entries()
            .Where(e => e.State == EntityState.Added);

        foreach (var entry in entries)
        {
            ((BaseEntity)entry.Entity).CreatedAt = DateTime.UtcNow;
        }
        return base.SaveChanges();
    }

    In SQLAlchemy:
    - DateTime(timezone=True) → TIMESTAMP WITH TIME ZONE
    - server_default=func.now() → PostgreSQL sets this automatically
    - func.now() → PostgreSQL NOW() function

    Why server_default?
    - Database sets the timestamp (consistent across servers)
    - Uses database server time (not Python app server time)
    - Automatically happens on INSERT
    """

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    """
    EXPLANATION: Updated Timestamp

    In .NET EF Core:
    public override int SaveChanges()
    {
        var entries = ChangeTracker.Entries()
            .Where(e => e.State == EntityState.Modified);

        foreach (var entry in entries)
        {
            ((BaseEntity)entry.Entity).UpdatedAt = DateTime.UtcNow;
        }
        return base.SaveChanges();
    }

    In SQLAlchemy:
    - server_default=func.now() → Set initial value on INSERT
    - onupdate=func.now() → Update automatically on UPDATE

    This gives us automatic audit trail:
    - created_at: When user registered
    - updated_at: When user last updated profile
    """

    # ============================================================
    # ============================================================

    credit_cards = relationship(
        "CreditCard",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    
    transactions = relationship(
        "Transaction",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    statements = relationship(
        "Statement",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    categories = relationship(
        "Category",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    payment_alerts = relationship(
        "PaymentAlert",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    # ============================================================
    # ============================================================
    def __repr__(self):
        """
        String representation of User object

        public override string ToString()
        {
            return $"User(id={Id}, email={Email})";
        }

        Used for debugging:
        print(user)  → User(id=123, email=john@example.com)
        """
        return f"<User(id={self.id}, email={self.email})>"


# ============================================================
# ============================================================
"""
┌─────────────────────────────────────────────────────────────┐
│ SQLAlchemy vs Entity Framework Core Comparison              │
├─────────────────────────────────────────────────────────────┤
│ EF Core                    │ SQLAlchemy                     │
├────────────────────────────┼────────────────────────────────┤
│ [Key]                      │ primary_key=True               │
│ [Required]                 │ nullable=False                 │
│ [MaxLength(255)]           │ String(255)                    │
│ [EmailAddress]             │ (validation in Pydantic)       │
│ [DefaultValue(...)]        │ default=...                    │
│ Guid                       │ UUID(as_uuid=True)             │
│ DateTime                   │ DateTime(timezone=True)        │
│ bool                       │ Boolean                        │
│ public string Email        │ email = Column(String)         │
│ DbSet<User> Users          │ class User(Base)               │
│ [Table("users")]           │ __tablename__ = "users"        │
│ [Index]                    │ index=True                     │
│ Navigation properties      │ relationship()                 │
└─────────────────────────────────────────────────────────────┘

Key Takeaways:
1. SQLAlchemy is more explicit (Column() for everything)
2. EF Core infers more (properties become columns)
3. Both support the same database features
4. SQLAlchemy: Python functions (func.now())
5. EF Core: LINQ and expressions

The User model we created will generate this SQL:

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    timezone VARCHAR(50) NOT NULL DEFAULT 'Asia/Singapore',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_users_email ON users(email);
"""
