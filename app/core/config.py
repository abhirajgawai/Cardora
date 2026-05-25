"""
Configuration Management for Cardora

- This is like appsettings.json + IConfiguration interface
- Pydantic Settings automatically loads from .env file
- Type validation happens automatically
- No need for ConfigurationBuilder like in .NET
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Cardora"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # API server
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000

    # Database — required, no default (fail fast if missing)
    DATABASE_URL: str

    # JWT auth — SECRET_KEY must be set in .env
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 60

    # Frontend URL — used in password-reset emails
    FRONTEND_URL: str = "http://localhost:3000"

    # Email (SendGrid)
    SENDGRID_API_KEY: Optional[str] = None
    FROM_EMAIL: str = "noreply@cardora.com"
    FROM_NAME: str = "Cardora Support"

    # AI
    GEMINI_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True
    )

    # ============================================================
    # ============================================================

    @property
    def database_url_sync(self) -> str:
        """
        Synchronous database URL (for SQLAlchemy)

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
# ============================================================

settings = Settings()



# ============================================================
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
