from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# ═══════════════════════════════════════════════════════════════════
# CARDORA CONFIGURATION
# ═══════════════════════════════════════════════════════════════════
# Import our database configuration and models
# Compare to .NET: Like referencing your DbContext and entities

from app.core.config import settings
from app.core.database import Base

# Import all models so Alembic can detect them
# Compare to .NET: EF Core scans for DbSet<T> properties
from app.features.auth.models import User
from app.features.cards.models import CreditCard
from app.features.transactions.models import Transaction
from app.features.statements.models import Statement
from app.features.categories.models import Category
from app.features.insights.models import PaymentAlert

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Set the database URL from our settings (.env file)
# Compare to .NET: Configuration.GetConnectionString("DefaultConnection")
# NOTE: We escape % by using %% for configparser compatibility
escaped_url = settings.DATABASE_URL.replace('%', '%%')
config.set_main_option("sqlalchemy.url", escaped_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata to our Base.metadata
# This tells Alembic about our database models
# Compare to .NET: DbContext.Model.GetEntityTypes()
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Use our existing engine from app.core.database
    # This ensures we use the same connection settings as the app
    # Compare to .NET: Using the same DbContext configuration
    from app.core.database import engine as connectable

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # Include schema in migration context
            # This ensures tables are created in cardora schema
            include_schemas=True
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
