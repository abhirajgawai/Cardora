# Database Migrations Guide - Alembic vs .NET EF Core

This guide explains how database migrations work in Python/Alembic compared to .NET/Entity Framework Core.

## Quick Reference

| Task | .NET (EF Core) | Python (Alembic) |
|------|---------------|-----------------|
| **Create migration** | `dotnet ef migrations add InitialCreate` | `alembic revision --autogenerate -m "Initial create"` |
| **Apply migrations** | `dotnet ef database update` | `alembic upgrade head` |
| **Rollback one migration** | `dotnet ef database update PreviousMigration` | `alembic downgrade -1` |
| **Show migration history** | `dotnet ef migrations list` | `alembic history` |
| **Show current version** | (check __EFMigrationsHistory) | `alembic current` |
| **Rollback all** | `dotnet ef database update 0` | `alembic downgrade base` |

---

## Setup (One-Time)

### .NET Approach

```bash
# Install EF Core tools
dotnet tool install --global dotnet-ef

# Add EF Core packages
dotnet add package Microsoft.EntityFrameworkCore.Design
dotnet add package Npgsql.EntityFrameworkCore.PostgreSQL
```

### Python/Alembic Approach

```bash
# Install Alembic
pip install alembic==1.13.1

# Initialize Alembic in your project
alembic init alembic

# Configure alembic/env.py to import your models
```

**We've already done this in Cardora!**

Configuration is in:
- `alembic.ini` - Main configuration
- `alembic/env.py` - Environment setup (imports our models)

---

## Development Workflow

### Scenario 1: Create Your First Migration

#### .NET Way

```csharp
// 1. Define your model in Models/User.cs
public class User
{
    public Guid Id { get; set; }
    public string Email { get; set; }
    public string HashedPassword { get; set; }
}

// 2. Add to DbContext
public class AppDbContext : DbContext
{
    public DbSet<User> Users { get; set; }
}
```

```bash
# 3. Create migration
dotnet ef migrations add InitialCreate

# 4. Apply to database
dotnet ef database update
```

#### Python/Alembic Way

```python
# 1. Define your model in app/models/user.py
class User(Base):
    __tablename__ = "users"
    __table_args__ = {'schema': 'cardora'}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
```

```bash
# 2. Generate migration (auto-detects changes!)
alembic revision --autogenerate -m "Initial create"

# 3. Apply to database
alembic upgrade head
```

**Result**: Migration file created in `alembic/versions/` with upgrade and downgrade functions.

---

### Scenario 2: Adding a New Column

#### .NET Way

```csharp
// 1. Modify your model
public class User
{
    public Guid Id { get; set; }
    public string Email { get; set; }
    public string HashedPassword { get; set; }
    public string FullName { get; set; }  // NEW
}

// 2. Create migration
dotnet ef migrations add AddFullNameToUser

// 3. Apply migration
dotnet ef database update
```

#### Python/Alembic Way

```python
# 1. Modify your model
class User(Base):
    __tablename__ = "users"
    __table_args__ = {'schema': 'cardora'}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)  # NEW
```

```bash
# 2. Generate migration (auto-detects the new column!)
alembic revision --autogenerate -m "Add full name to user"

# 3. Apply migration
alembic upgrade head
```

---

### Scenario 3: Team Collaboration (Clone Repo)

#### .NET Way

```bash
# 1. Clone repository
git clone https://github.com/your-team/project.git

# 2. Restore packages
dotnet restore

# 3. Apply all pending migrations
dotnet ef database update

# Done! Database is up to date
```

#### Python/Alembic Way

```bash
# 1. Clone repository
git clone https://github.com/your-team/cardora.git

# 2. Create virtual environment and install dependencies
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# 3. Apply all pending migrations
alembic upgrade head

# Done! Database is up to date
```

---

## Migration Files

### .NET Migration File Structure

```csharp
// 20241022_InitialCreate.cs
public partial class InitialCreate : Migration
{
    protected override void Up(MigrationBuilder migrationBuilder)
    {
        migrationBuilder.CreateTable(
            name: "Users",
            columns: table => new
            {
                Id = table.Column<Guid>(nullable: false),
                Email = table.Column<string>(nullable: false)
            });
    }

    protected override void Down(MigrationBuilder migrationBuilder)
    {
        migrationBuilder.DropTable(name: "Users");
    }
}
```

### Alembic Migration File Structure

```python
# alembic/versions/29a6658e640d_initial_create.py
def upgrade() -> None:
    op.create_table('users',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        schema='cardora'
    )
    op.create_index('ix_cardora_users_email', 'users', ['email'],
                    unique=True, schema='cardora')

def downgrade() -> None:
    op.drop_index('ix_cardora_users_email', table_name='users',
                  schema='cardora')
    op.drop_table('users', schema='cardora')
```

**Similarity**: Both have `upgrade()` (Up) and `downgrade()` (Down) methods!

---

## How Migrations are Tracked

### .NET: __EFMigrationsHistory Table

```sql
-- EF Core creates this table automatically
CREATE TABLE __EFMigrationsHistory (
    MigrationId VARCHAR(150) PRIMARY KEY,
    ProductVersion VARCHAR(32)
);

-- Example data:
-- MigrationId                            | ProductVersion
-- 20241022123456_InitialCreate           | 8.0.0
-- 20241022134567_AddFullNameToUser       | 8.0.0
```

### Python: alembic_version Table

```sql
-- Alembic creates this table automatically
CREATE TABLE alembic_version (
    version_num VARCHAR(32) PRIMARY KEY
);

-- Example data:
-- version_num
-- 29a6658e640d   (stores CURRENT version only)
```

**Key Difference**:
- EF Core stores **all applied migrations**
- Alembic stores **only the current version** (migration files track history)

---

## Common Operations

### View Migration History

```bash
# .NET
dotnet ef migrations list

# Python
alembic history
```

### Rollback Last Migration

```bash
# .NET
# Get previous migration name first
dotnet ef migrations list
# Then rollback to it
dotnet ef database update PreviousMigrationName

# Python (simpler!)
alembic downgrade -1
```

### Rollback to Specific Version

```bash
# .NET
dotnet ef database update SpecificMigrationName

# Python
alembic downgrade <revision>
# Example: alembic downgrade 29a6658e640d
```

### Rollback Everything

```bash
# .NET
dotnet ef database update 0

# Python
alembic downgrade base
```

### Check Current Version

```bash
# .NET (query database)
SELECT * FROM __EFMigrationsHistory ORDER BY MigrationId DESC;

# Python
alembic current
```

---

## Pro Tips

### Alembic Advantages

1. **Auto-detection**: Like EF Core, Alembic can auto-detect model changes
2. **Lightweight**: No heavy framework, just migration files
3. **Flexible**: Can write custom SQL migrations easily
4. **Version Control**: Migration files are just Python scripts

### Best Practices

1. **Always review auto-generated migrations** before applying
   ```bash
   # Generate migration
   alembic revision --autogenerate -m "Add feature"

   # Review the generated file in alembic/versions/
   # Edit if needed, then apply
   alembic upgrade head
   ```

2. **Test migrations with rollback**
   ```bash
   alembic upgrade head      # Apply
   alembic downgrade -1      # Test rollback
   alembic upgrade head      # Re-apply
   ```

3. **Never edit applied migrations** - Create new ones instead

4. **Use descriptive messages**
   ```bash
   # Good
   alembic revision --autogenerate -m "Add user profile fields"

   # Bad
   alembic revision --autogenerate -m "update"
   ```

---

## Troubleshooting

### Migration Not Auto-Detecting Changes?

```python
# Make sure your model is imported in alembic/env.py
from app.models import User  # Import ALL models here

# Set target_metadata
target_metadata = Base.metadata
```

### Database Out of Sync?

```bash
# Check current version
alembic current

# Check what Alembic thinks should be applied
alembic history

# Force stamp to a specific version (CAREFUL!)
alembic stamp head
```

### Migration Failed Halfway?

```bash
# Alembic uses transactions, so it should rollback automatically
# If database is in bad state, you can:

# 1. Check current version
alembic current

# 2. Manually rollback
alembic downgrade -1

# 3. Fix the migration file
# Edit alembic/versions/<revision>_xxx.py

# 4. Re-apply
alembic upgrade head
```

---

## Summary

| Feature | .NET EF Core | Python Alembic |
|---------|-------------|----------------|
| **Auto-detection** | ✅ Yes | ✅ Yes |
| **Up/Down methods** | ✅ Yes | ✅ Yes |
| **Version tracking** | __EFMigrationsHistory | alembic_version |
| **Transaction safety** | ✅ Yes | ✅ Yes |
| **Team workflow** | `dotnet ef database update` | `alembic upgrade head` |
| **Rollback** | Update to previous | `alembic downgrade -1` |

**Both systems work similarly and achieve the same goal: version-controlled, reversible database changes!**

---

## Our Cardora Setup

We've configured Alembic to:
- ✅ Auto-load settings from `.env` file
- ✅ Import all models automatically
- ✅ Support custom `cardora` schema
- ✅ Use our existing database engine
- ✅ Handle password special characters correctly

### Cardora Migration Commands

```bash
# Create new migration after modifying models
alembic revision --autogenerate -m "Description of changes"

# Apply all pending migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# Check current version
alembic current

# View history
alembic history

# Verify migration succeeded
python tests/verify_migration.py
```

---

## Next Steps

1. ✅ Alembic is configured and tested
2. ✅ Initial migration created and applied
3. ⏭️ Continue building authentication system
4. ⏭️ Add more models? Just create migration and upgrade!

For more information:
- Alembic docs: https://alembic.sqlalchemy.org/
- SQLAlchemy docs: https://docs.sqlalchemy.org/
