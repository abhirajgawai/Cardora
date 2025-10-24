"""
Configuration Management for Cardora

Compare to .NET:
- This is like appsettings.json + IConfiguration interface
- Pydantic Settings automatically loads from .env file
- Type validation happens automatically
- No need for ConfigurationBuilder like in .NET
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """
    Application Settings

    Compare to .NET:
    This is like having a strongly-typed configuration class that
    automatically binds to IConfiguration in ASP.NET Core.

    The difference: Instead of injecting IConfiguration and using
    Configuration.GetSection(), Pydantic automatically reads from
    environment variables or .env file.
    """

    # ============================================================
    # Application Settings
    # ============================================================
    APP_NAME: str = "Cardora"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # ============================================================
    # API Settings
    # ============================================================
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000

    # ============================================================
    # Database Settings
    # ============================================================
    DATABASE_URL: str
    # ^ This is REQUIRED (no default value)
    # If not found in .env, application will fail to start
    # This prevents running without a database connection

    # ============================================================
    # Security Settings (for JWT authentication)
    # ============================================================
    SECRET_KEY: str  # Required - used to sign JWT tokens
    ALGORITHM: str = "HS256"  # JWT signing algorithm
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # Token lifetime

    # ============================================================
    # Password Reset Settings
    # ============================================================
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 60  # 1 hour
    FRONTEND_URL: str = "http://localhost:3000"  # Frontend app URL for reset links

    # ============================================================
    # SendGrid Email Settings (for password reset emails)
    # ============================================================
    SENDGRID_API_KEY: Optional[str] = None
    # ^ Get your free API key from https://sendgrid.com/
    # Free tier: 100 emails/day

    FROM_EMAIL: str = "noreply@cardora.com"
    # ^ Must be verified in SendGrid (or use Single Sender Verification)

    FROM_NAME: str = "Cardora Support"
    # ^ Display name shown in email "From" field

    # ============================================================
    # Google Gemini API (for PDF extraction - Feature 3)
    # ============================================================
    GEMINI_API_KEY: Optional[str] = None
    # ^ Optional for now - we'll need this in Feature 3

    # ============================================================
    # Pydantic Configuration
    # ============================================================
    model_config = SettingsConfigDict(
        # Tell Pydantic to read from .env file
        env_file=".env",
        env_file_encoding="utf-8",
        # Allow extra fields in .env that we don't define here
        extra="ignore",
        # Make field names case-sensitive
        case_sensitive=True
    )

    # ============================================================
    # Helper Properties (computed values)
    # ============================================================

    @property
    def database_url_sync(self) -> str:
        """
        Synchronous database URL (for SQLAlchemy)

        Compare to .NET:
        This is like having a computed property that transforms
        the connection string for different use cases.

        PostgreSQL drivers:
        - psycopg2: Synchronous (blocking) driver
        - asyncpg: Asynchronous (non-blocking) driver

        For FastAPI, we typically use async, but for migrations
        and simple scripts, sync is easier.
        """
        return self.DATABASE_URL

    @property
    def database_url_async(self) -> str:
        """
        Asynchronous database URL (for async SQLAlchemy)

        Replaces 'postgresql://' with 'postgresql+asyncpg://'
        to use the async driver.
        """
        return self.DATABASE_URL.replace(
            "postgresql://",
            "postgresql+asyncpg://"
        )


# ============================================================
# Create a global settings instance
# ============================================================
# Compare to .NET:
# In .NET, you'd inject IConfiguration or IOptions<Settings>
# In FastAPI, we create a singleton instance here and import it

settings = Settings()

# Usage in other files:
# from app.core.config import settings
# print(settings.DATABASE_URL)


# ============================================================
# EXPLANATION OF KEY CONCEPTS
# ============================================================
"""
1. BaseSettings (Pydantic)
   - Automatically reads from environment variables
   - Validates types (str, int, bool)
   - Fails fast if required fields are missing
   - Like IConfiguration + DataAnnotations validation combined

2. model_config = SettingsConfigDict(...)
   - This is Pydantic v2 syntax (newer)
   - Old way was: class Config: env_file = ".env"
   - Tells Pydantic WHERE to read configuration

3. Type Hints (str, int, bool, Optional[str])
   - Python's way of declaring types
   - Optional[str] = can be None (like string? in C#)
   - Required if no default value provided

4. @property decorator
   - Creates computed properties (like C# properties with get)
   - No stored value, computed on access
   - Useful for transforming configuration values

5. Why DATABASE_URL has no default:
   - Forces you to set it in .env
   - Application fails immediately if forgotten
   - Better than runtime errors later

6. Why settings is lowercase:
   - Python convention: constants are UPPERCASE
   - But instances are lowercase
   - settings is an instance of Settings class
"""
