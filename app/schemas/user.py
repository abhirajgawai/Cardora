"""
User Pydantic Schemas (DTOs)

Compare to .NET: Like having ViewModels or DTOs
    - UserCreate → RegisterUserRequest DTO
    - UserResponse → UserDto (output)
    - UserLogin → LoginRequest DTO
    - UserUpdate → UpdateUserRequest DTO

In .NET you might have:
    public class RegisterUserRequest
    {
        [Required]
        [EmailAddress]
        public string Email { get; set; }

        [Required]
        [MinLength(8)]
        public string Password { get; set; }
    }

Pydantic provides:
    - Automatic validation (like Data Annotations)
    - Serialization/deserialization (like System.Text.Json)
    - Documentation generation (like XML comments for Swagger)
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional


# ═══════════════════════════════════════════════════════════════════
# USER CREATION (Registration)
# ═══════════════════════════════════════════════════════════════════

class UserCreate(BaseModel):
    """
    Schema for user registration (input)

    Compare to .NET:
        public class RegisterUserRequest
        {
            [Required, EmailAddress]
            public string Email { get; set; }

            [Required, MinLength(8)]
            public string Password { get; set; }

            public string FullName { get; set; }

            [Required]
            public string Timezone { get; set; }
        }
    """
    email: EmailStr = Field(
        ...,  # Required field (like [Required] in .NET)
        description="User's email address",
        examples=["john.doe@example.com"]
    )

    password: str = Field(
        ...,  # Required
        min_length=8,  # Like [MinLength(8)] in .NET
        max_length=100,
        description="User's password (min 8 characters)",
        examples=["MySecurePassword123!"]
    )

    full_name: Optional[str] = Field(
        None,  # Optional (like string? in C#)
        max_length=255,
        description="User's full name",
        examples=["John Doe"]
    )

    timezone: str = Field(
        default="Asia/Singapore",  # Default value
        max_length=50,
        description="User's timezone",
        examples=["Asia/Singapore", "America/New_York", "Europe/London"]
    )

    # Configuration
    model_config = ConfigDict(
        # Compare to .NET: Like JsonSerializerOptions
        json_schema_extra={
            "example": {
                "email": "john.doe@example.com",
                "password": "MySecurePassword123!",
                "full_name": "John Doe",
                "timezone": "Asia/Singapore"
            }
        }
    )


# ═══════════════════════════════════════════════════════════════════
# USER RESPONSE (Output)
# ═══════════════════════════════════════════════════════════════════

class UserResponse(BaseModel):
    """
    Schema for user data response (output)

    Compare to .NET:
        public class UserDto
        {
            public Guid Id { get; set; }
            public string Email { get; set; }
            public string FullName { get; set; }
            public string Timezone { get; set; }
            public bool IsActive { get; set; }
            public bool IsVerified { get; set; }
            public DateTime CreatedAt { get; set; }
            public DateTime UpdatedAt { get; set; }
        }

    IMPORTANT: Never include hashed_password in response!
    """
    id: UUID = Field(
        ...,
        description="User's unique identifier",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )

    email: EmailStr = Field(
        ...,
        description="User's email address",
        examples=["john.doe@example.com"]
    )

    full_name: Optional[str] = Field(
        None,
        description="User's full name",
        examples=["John Doe"]
    )

    timezone: str = Field(
        ...,
        description="User's timezone",
        examples=["Asia/Singapore"]
    )

    is_active: bool = Field(
        ...,
        description="Whether the user account is active",
        examples=[True]
    )

    is_verified: bool = Field(
        ...,
        description="Whether the user's email is verified",
        examples=[False]
    )

    created_at: datetime = Field(
        ...,
        description="When the user account was created",
        examples=["2024-10-22T10:30:00Z"]
    )

    updated_at: datetime = Field(
        ...,
        description="When the user account was last updated",
        examples=["2024-10-22T10:30:00Z"]
    )

    # Configuration
    model_config = ConfigDict(
        # Compare to .NET: Like setting [JsonPropertyName]
        from_attributes=True,  # Allows creation from ORM models (like AutoMapper)
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "john.doe@example.com",
                "full_name": "John Doe",
                "timezone": "Asia/Singapore",
                "is_active": True,
                "is_verified": False,
                "created_at": "2024-10-22T10:30:00Z",
                "updated_at": "2024-10-22T10:30:00Z"
            }
        }
    )


# ═══════════════════════════════════════════════════════════════════
# USER LOGIN
# ═══════════════════════════════════════════════════════════════════

class UserLogin(BaseModel):
    """
    Schema for user login (input)

    Compare to .NET:
        public class LoginRequest
        {
            [Required, EmailAddress]
            public string Email { get; set; }

            [Required]
            public string Password { get; set; }
        }
    """
    email: EmailStr = Field(
        ...,
        description="User's email address",
        examples=["john.doe@example.com"]
    )

    password: str = Field(
        ...,
        description="User's password",
        examples=["MySecurePassword123!"]
    )

    # Configuration
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "john.doe@example.com",
                "password": "MySecurePassword123!"
            }
        }
    )


# ═══════════════════════════════════════════════════════════════════
# USER UPDATE
# ═══════════════════════════════════════════════════════════════════

class UserUpdate(BaseModel):
    """
    Schema for updating user profile (input)

    Compare to .NET:
        public class UpdateUserRequest
        {
            public string? FullName { get; set; }
            public string? Timezone { get; set; }
        }

    All fields are optional (partial update)
    """
    full_name: Optional[str] = Field(
        None,
        max_length=255,
        description="User's full name",
        examples=["Jane Doe"]
    )

    timezone: Optional[str] = Field(
        None,
        max_length=50,
        description="User's timezone",
        examples=["America/New_York"]
    )

    # Configuration
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "full_name": "Jane Doe",
                "timezone": "America/New_York"
            }
        }
    )


# ═══════════════════════════════════════════════════════════════════
# USAGE EXAMPLES
# ═══════════════════════════════════════════════════════════════════
"""
# Example 1: Create user from registration data
from app.schemas import UserCreate
from app.models import User
from app.auth.password import hash_password

# Validate input (automatic with FastAPI)
user_data = UserCreate(
    email="john@example.com",
    password="MyPassword123!",
    full_name="John Doe",
    timezone="Asia/Singapore"
)

# Create database model
user = User(
    email=user_data.email,
    hashed_password=hash_password(user_data.password),  # Hash password!
    full_name=user_data.full_name,
    timezone=user_data.timezone
)
db.add(user)
db.commit()


# Example 2: Return user data (exclude password!)
from app.schemas import UserResponse

user = db.query(User).first()
# Pydantic automatically converts ORM model to response schema
response = UserResponse.from_orm(user)  # or UserResponse.model_validate(user)
# Response will NOT include hashed_password!


# Compare to .NET:
// Registration
public async Task<UserDto> RegisterUser(RegisterUserRequest request)
{
    var user = new User
    {
        Email = request.Email,
        HashedPassword = _passwordHasher.HashPassword(null, request.Password),
        FullName = request.FullName,
        Timezone = request.Timezone
    };

    _context.Users.Add(user);
    await _context.SaveChangesAsync();

    return _mapper.Map<UserDto>(user);  // AutoMapper
}

// Python equivalent:
async def register_user(user_data: UserCreate, db: Session):
    user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        timezone=user_data.timezone
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return UserResponse.model_validate(user)  # Pydantic validation
"""
