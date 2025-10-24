"""
Authentication Router - Registration and Login Endpoints

Compare to .NET: Like having an AuthController
    [ApiController]
    [Route("api/[controller]")]
    public class AuthController : ControllerBase
    {
        [HttpPost("register")]
        public async Task<ActionResult<UserDto>> Register(RegisterRequest request)
        { ... }

        [HttpPost("login")]
        public async Task<ActionResult<LoginResponse>> Login(LoginRequest request)
        { ... }
    }
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.models.user import User
from app.schemas import (
    UserCreate, UserResponse, UserLogin, Token,
    PasswordResetRequest, PasswordResetConfirm,
    PasswordResetResponse, PasswordResetSuccess
)
from app.auth.password import hash_password, verify_password
from app.auth.jwt import create_access_token
from app.auth.password_reset import create_password_reset_token, verify_reset_token, clear_reset_token
from app.core.email_service import send_password_reset_email

# ═══════════════════════════════════════════════════════════════════
# ROUTER SETUP
# ═══════════════════════════════════════════════════════════════════
# Compare to .NET: Like [ApiController] [Route("api/auth")]

router = APIRouter(
    prefix="/auth",  # All routes will be /auth/...
    tags=["Authentication"]  # For API documentation grouping
)


# ═══════════════════════════════════════════════════════════════════
# POST /auth/register - User Registration
# ═══════════════════════════════════════════════════════════════════

@router.post(
    "/register",
    response_model=UserResponse,  # Automatic response validation
    status_code=status.HTTP_201_CREATED,  # Return 201 Created
    summary="Register new user",
    description="Create a new user account with email and password"
)
async def register(
    user_data: UserCreate,  # Automatic validation using Pydantic
    db: Session = Depends(get_db)  # Dependency injection (like DI in .NET)
):
    """
    Register a new user account.

    Compare to .NET:
        [HttpPost("register")]
        public async Task<ActionResult<UserDto>> Register(
            [FromBody] RegisterRequest request,
            [FromServices] AppDbContext db)
        {
            // Check if user exists
            if (await db.Users.AnyAsync(u => u.Email == request.Email))
                return BadRequest("Email already registered");

            // Create user
            var user = new User
            {
                Email = request.Email,
                HashedPassword = _passwordHasher.HashPassword(null, request.Password),
                FullName = request.FullName,
                Timezone = request.Timezone
            };

            db.Users.Add(user);
            await db.SaveChangesAsync();

            return CreatedAtAction(nameof(GetUser), new { id = user.Id }, _mapper.Map<UserDto>(user));
        }

    Args:
        user_data: User registration data (validated by Pydantic)
        db: Database session (injected by FastAPI)

    Returns:
        UserResponse: Created user data (without password)

    Raises:
        HTTPException 400: Email already registered
        HTTPException 500: Database error
    """

    # Check if user already exists
    # Compare to .NET: db.Users.AnyAsync(u => u.Email == request.Email)
    existing_user = db.query(User).filter(User.email == user_data.email).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    try:
        # Create new user
        # Compare to .NET: var user = new User { ... }
        new_user = User(
            email=user_data.email,
            hashed_password=hash_password(user_data.password),  # Hash password!
            full_name=user_data.full_name,
            timezone=user_data.timezone,
            is_active=True,  # Default
            is_verified=False  # Email not verified yet
        )

        # Add to database
        # Compare to .NET: db.Users.Add(user)
        db.add(new_user)

        # Commit transaction
        # Compare to .NET: await db.SaveChangesAsync()
        db.commit()

        # Refresh to get database-generated fields (id, timestamps)
        # Compare to .NET: EF Core automatically populates these
        db.refresh(new_user)

        # Return user data (Pydantic automatically excludes password)
        # Compare to .NET: return _mapper.Map<UserDto>(user)
        return UserResponse.model_validate(new_user)

    except IntegrityError as e:
        # Database constraint violation (e.g., unique email)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    except Exception as e:
        # Any other database error
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again later."
        )


# ═══════════════════════════════════════════════════════════════════
# POST /auth/login - User Login
# ═══════════════════════════════════════════════════════════════════

@router.post(
    "/login",
    response_model=Token,  # Return JWT token
    status_code=status.HTTP_200_OK,
    summary="Login user",
    description="Authenticate user and return JWT token"
)
async def login(
    credentials: UserLogin,  # Email and password
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT access token.

    Compare to .NET:
        [HttpPost("login")]
        public async Task<ActionResult<LoginResponse>> Login(
            [FromBody] LoginRequest request,
            [FromServices] AppDbContext db)
        {
            // Find user by email
            var user = await db.Users.FirstOrDefaultAsync(u => u.Email == request.Email);
            if (user == null)
                return Unauthorized("Invalid credentials");

            // Verify password
            var result = _passwordHasher.VerifyHashedPassword(user, user.HashedPassword, request.Password);
            if (result != PasswordVerificationResult.Success)
                return Unauthorized("Invalid credentials");

            // Generate JWT token
            var token = _tokenService.GenerateToken(user);

            return Ok(new LoginResponse
            {
                AccessToken = token,
                TokenType = "bearer"
            });
        }

    Args:
        credentials: User login credentials (email, password)
        db: Database session (injected by FastAPI)

    Returns:
        Token: JWT access token and token type

    Raises:
        HTTPException 401: Invalid email or password
        HTTPException 403: User account is inactive
    """

    # Find user by email
    # Compare to .NET: db.Users.FirstOrDefaultAsync(u => u.Email == request.Email)
    user = db.query(User).filter(User.email == credentials.email).first()

    # Check if user exists
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password
    # Compare to .NET: _passwordHasher.VerifyHashedPassword(user, hashedPassword, password)
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    # Generate JWT token
    # Compare to .NET: _tokenService.GenerateToken(user)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )

    # Return token
    # Compare to .NET: return new LoginResponse { AccessToken = token, TokenType = "bearer" }
    return Token(access_token=access_token, token_type="bearer")


# ═══════════════════════════════════════════════════════════════════
# POST /auth/forgot-password - Request Password Reset
# ═══════════════════════════════════════════════════════════════════

@router.post(
    "/forgot-password",
    response_model=PasswordResetResponse,
    status_code=status.HTTP_200_OK,
    summary="Request password reset",
    description="Send password reset email if account exists"
)
async def forgot_password(
    request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """
    Request password reset - sends email with reset link

    Security Note:
    - Always returns 200 OK (don't reveal if email exists)
    - Token is hashed before storing in database
    - Token expires after 1 hour
    - Email is sent via SendGrid (or logged to console in dev)
    """

    # Find user by email
    user = db.query(User).filter(User.email == request.email).first()

    if user:
        # User exists - generate token and send email
        if user.is_active:
            # Generate reset token
            reset_token = create_password_reset_token(db, user)

            # Send password reset email
            await send_password_reset_email(
                email=user.email,
                reset_token=reset_token,
                user_name=user.full_name or "User"
            )

    # ALWAYS return success message (don't reveal if email exists)
    return PasswordResetResponse(
        message="If your email exists in our system, you will receive a password reset link"
    )


# ═══════════════════════════════════════════════════════════════════
# POST /auth/reset-password - Confirm Password Reset
# ═══════════════════════════════════════════════════════════════════

@router.post(
    "/reset-password",
    response_model=PasswordResetSuccess,
    status_code=status.HTTP_200_OK,
    summary="Reset password with token",
    description="Reset user password using reset token from email"
)
async def reset_password(
    request: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """
    Reset password using token from email

    Security:
    - Token must be valid and not expired
    - Token is single-use (cleared after reset)
    - Password is hashed before storage
    - User account must be active
    """

    # Verify token and get user
    user = verify_reset_token(db, request.token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    # Hash the new password
    new_hashed_password = hash_password(request.new_password)

    # Update user password
    user.hashed_password = new_hashed_password

    # Clear reset token (single-use)
    clear_reset_token(db, user)

    # Commit changes
    db.commit()

    return PasswordResetSuccess(
        message="Password has been reset successfully. You can now login with your new password."
    )


# ═══════════════════════════════════════════════════════════════════
# USAGE EXAMPLES
# ═══════════════════════════════════════════════════════════════════
"""
# Example 1: Register a new user
POST http://localhost:8000/auth/register
Content-Type: application/json

{
    "email": "john.doe@example.com",
    "password": "MySecurePassword123!",
    "full_name": "John Doe",
    "timezone": "Asia/Singapore"
}

# Response 201 Created:
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "john.doe@example.com",
    "full_name": "John Doe",
    "timezone": "Asia/Singapore",
    "is_active": true,
    "is_verified": false,
    "created_at": "2024-10-22T10:30:00Z",
    "updated_at": "2024-10-22T10:30:00Z"
}

# Example 2: Register with duplicate email
POST http://localhost:8000/auth/register
Content-Type: application/json

{
    "email": "john.doe@example.com",  # Already exists
    "password": "AnotherPassword123!",
    "timezone": "America/New_York"
}

# Response 400 Bad Request:
{
    "detail": "Email already registered"
}


# Compare to .NET usage:
POST https://localhost:5001/api/auth/register
Content-Type: application/json

{
    "email": "john.doe@example.com",
    "password": "MySecurePassword123!",
    "fullName": "John Doe",
    "timezone": "Asia/Singapore"
}
"""
