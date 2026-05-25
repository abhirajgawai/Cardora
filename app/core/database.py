"""
Database Configuration and Session Management for Cardora

- This file sets up SQLAlchemy (Python's Entity Framework Core)
- Engine = database connection pool
- SessionLocal = factory for database sessions
- Base = base class for all models (like DbContext inheritance)
- get_db() = dependency injection for database sessions
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.core.config import settings


# ============================================================
# ============================================================
"""
In EF Core: services.AddDbContext<ApplicationDbContext>(options =>
    options.UseNpgsql(connectionString));

In SQLAlchemy: create_engine() creates a connection pool
"""

database_url = settings.DATABASE_URL
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)

engine = create_engine(
    database_url,
)

"""
EXPLANATION:

1. create_engine(settings.DATABASE_URL)
   - Creates a database connection pool
   - Does NOT connect yet (lazy connection)
   - Like DbContextOptionsBuilder.UseNpgsql() in .NET

2. pool_pre_ping=True
   - Tests connection before using it
   - Prevents "server has gone away" errors
   - Automatically reconnects if connection dropped
   - Like connection resilience in EF Core

3. pool_size=10
   - Maintains 10 persistent connections
   - Reuses connections (more efficient)
   - Like EF Core's connection pooling

4. max_overflow=20
   - Can create up to 20 additional temporary connections
   - Total max = pool_size + max_overflow = 30
   - Handles traffic spikes gracefully

5. echo=settings.DEBUG
   - When DEBUG=True, logs all SQL queries to console
   - Useful for development
   - Like EnableSensitiveDataLogging() in EF Core
"""


# ============================================================
# ============================================================
"""
In EF Core, DbContext IS the session.
In SQLAlchemy, Session is separate from the engine.

Think of it this way:
- Engine = Connection Pool (infrastructure)
- Session = Unit of Work (per-request transaction)
"""

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)

"""
EXPLANATION:

1. SessionLocal
   - This is a CLASS (factory), not an instance
   - Call SessionLocal() to create a session instance
   - Like calling new ApplicationDbContext() in .NET

2. autocommit=False
   - We control when to commit transactions
   - db.commit() explicitly saves changes
   - Like DbContext.SaveChanges() in .NET
   - Prevents accidental commits

3. autoflush=False
   - We control when to flush (send SQL to DB)
   - db.flush() sends SQL but doesn't commit
   - More control over transaction boundaries

4. bind=engine
   - Ties sessions to our connection pool
   - Sessions will use the engine's connections
"""


# ============================================================
# ============================================================
"""
In EF Core: public class User { ... } (no base class needed)
            DbContext has DbSet<User> property

In SQLAlchemy: class User(Base) inherits from declarative_base()
               Base tracks all models automatically
"""

Base = declarative_base()

"""
EXPLANATION:

1. declarative_base()
   - Creates a base class for all models
   - All models inherit from this: class User(Base)
   - Automatically tracks model classes
   - Provides common functionality (like __tablename__)

2. Why we need this:
   - SQLAlchemy uses metaclasses to track models
   - Base keeps a registry of all model classes
   - Used later for: Base.metadata.create_all(engine)
   - Like DbContext.Model.FindEntityTypes() in EF Core

3. Usage in models:
   class User(Base):
       __tablename__ = "users"
       ...
"""


# ============================================================
# ============================================================
"""
In .NET controllers:
    public MyController(ApplicationDbContext context) { }

In FastAPI:
    def my_endpoint(db: Session = Depends(get_db)):
        ...
"""

def get_db() -> Generator[Session, None, None]:
    """Yield a database session for the duration of a request, then close it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

"""
EXPLANATION:

1. Generator[Session, None, None]
   - Type hint for generator function
   - Generates Session objects
   - Like IEnumerable<Session> in C#

2. yield db
   - Pauses function and returns db to caller
   - Function resumes after endpoint finishes
   - Like returning IDisposable in C#

3. try/finally pattern
   - Ensures db.close() always runs
   - Even if endpoint throws exception

4. Why not just return db?
   - FastAPI's Depends() needs a generator
   - Allows cleanup code in finally block
   - Proper resource management

5. Session lifecycle:
   Request comes in → get_db() creates session → endpoint uses session
   → endpoint finishes → finally block closes session → response sent
"""


# ============================================================
# ============================================================

def init_db() -> None:
    """
    Create all database tables

    This is like: context.Database.EnsureCreated()
    Or running: dotnet ef database update

    Usage:
    - Call once at application startup
    - Creates all tables defined in models
    - Only for development! Use Alembic migrations for production

    NOTE: We'll use this in testing. For production, we'll use
    Alembic migrations (like EF Core migrations).
    """

    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully!")


# ============================================================
# ============================================================
"""
┌─────────────────────────────────────────────────────────────┐
│ SQLAlchemy vs Entity Framework Core                         │
├─────────────────────────────────────────────────────────────┤
│ EF Core Concept          │ SQLAlchemy Equivalent            │
├──────────────────────────┼──────────────────────────────────┤
│ DbContext                │ Session                          │
│ DbContextOptions         │ Engine                           │
│ DbSet<T>                 │ db.query(Model)                  │
│ context.SaveChanges()    │ db.commit()                      │
│ context.Add(entity)      │ db.add(entity)                   │
│ using (var db = ...)     │ try/finally + db.close()         │
│ Database.EnsureCreated() │ Base.metadata.create_all()       │
│ Migration                │ Alembic migration                │
│ [Key] attribute          │ Column(primary_key=True)         │
│ [Required] attribute     │ Column(nullable=False)           │
│ navigation properties    │ relationship() with backref      │
└─────────────────────────────────────────────────────────────┘

Key Differences:
1. SQLAlchemy separates Engine (connection) from Session (UoW)
2. No DbContext inheritance - just use Session directly
3. Must explicitly bind Session to Engine
4. Must call db.commit() to save (no automatic SaveChanges)
5. Use dependency injection with Depends(get_db)

Why this design:
- More explicit control over transactions
- Better for microservices (separate concerns)
- Easier to test (mock sessions)
- More flexible (use different engines per session)
"""
