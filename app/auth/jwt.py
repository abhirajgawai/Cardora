"""
JWT Token Utilities - Token Generation and Validation

Compare to .NET: Like using JwtSecurityTokenHandler in ASP.NET Core
    var tokenHandler = new JwtSecurityTokenHandler();
    var token = tokenHandler.CreateToken(tokenDescriptor);
    var principal = tokenHandler.ValidateToken(token, validationParameters, out var validatedToken);

In Python with python-jose:
    token = create_access_token(data)
    payload = verify_token(token)
    user = get_current_user(token, db)
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.schemas.token import TokenData


# ═══════════════════════════════════════════════════════════════════
# OAUTH2 SCHEME SETUP
# ═══════════════════════════════════════════════════════════════════
# Compare to .NET: Like configuring JWT Bearer authentication
# services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
#     .AddJwtBearer(options => { ... });

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
# This tells FastAPI where to get the token from
# Client will send: Authorization: Bearer <token>

# HTTPBearer scheme for Swagger UI - allows directly pasting JWT tokens
http_bearer = HTTPBearer()


# ═══════════════════════════════════════════════════════════════════
# CREATE ACCESS TOKEN (Generate JWT)
# ═══════════════════════════════════════════════════════════════════

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Compare to .NET:
        var tokenHandler = new JwtSecurityTokenHandler();
        var key = Encoding.UTF8.GetBytes(_configuration["Jwt:Key"]);

        var tokenDescriptor = new SecurityTokenDescriptor
        {
            Subject = new ClaimsIdentity(new[]
            {
                new Claim(ClaimTypes.NameIdentifier, userId.ToString()),
                new Claim(ClaimTypes.Email, email)
            }),
            Expires = DateTime.UtcNow.AddMinutes(30),
            SigningCredentials = new SigningCredentials(
                new SymmetricSecurityKey(key),
                SecurityAlgorithms.HmacSha256Signature
            )
        };

        var token = tokenHandler.CreateToken(tokenDescriptor);
        return tokenHandler.WriteToken(token);

    Args:
        data: Dictionary containing claims to encode in token
              Usually: {"sub": user_id, "email": email}
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string

    Example:
        >>> token = create_access_token(
        ...     data={"sub": str(user.id), "email": user.email}
        ... )
        >>> print(token)
        eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    """
    # Create a copy of the data to avoid modifying the original
    to_encode = data.copy()

    # Set expiration time
    # Compare to .NET: Expires = DateTime.UtcNow.AddMinutes(30)
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    # Add expiration claim to token
    # Compare to .NET: Adding Expires to SecurityTokenDescriptor
    to_encode.update({"exp": expire})

    # Encode the JWT token
    # Compare to .NET: tokenHandler.WriteToken(token)
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,  # Signing key
        algorithm=settings.ALGORITHM  # HMAC-SHA256
    )

    return encoded_jwt


# ═══════════════════════════════════════════════════════════════════
# VERIFY TOKEN (Validate and Decode JWT)
# ═══════════════════════════════════════════════════════════════════

def verify_token(token: str, credentials_exception: HTTPException) -> TokenData:
    """
    Verify and decode a JWT token.

    Compare to .NET:
        var tokenHandler = new JwtSecurityTokenHandler();
        var validationParameters = new TokenValidationParameters
        {
            ValidateIssuerSigningKey = true,
            IssuerSigningKey = new SymmetricSecurityKey(key),
            ValidateIssuer = false,
            ValidateAudience = false
        };

        try
        {
            var principal = tokenHandler.ValidateToken(
                token,
                validationParameters,
                out var validatedToken
            );

            var userId = principal.FindFirst(ClaimTypes.NameIdentifier)?.Value;
            var email = principal.FindFirst(ClaimTypes.Email)?.Value;
        }
        catch (Exception)
        {
            throw new UnauthorizedException();
        }

    Args:
        token: JWT token string
        credentials_exception: Exception to raise if validation fails

    Returns:
        TokenData containing user_id and email

    Raises:
        HTTPException: If token is invalid, expired, or missing claims
    """
    try:
        # Decode and validate the JWT token
        # Compare to .NET: tokenHandler.ValidateToken()
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        # Extract claims from token
        # Compare to .NET: principal.FindFirst(ClaimTypes.NameIdentifier)
        user_id_str: str = payload.get("sub")  # "sub" is standard JWT claim for subject
        email: str = payload.get("email")

        # Validate that required claims exist
        if user_id_str is None or email is None:
            raise credentials_exception

        # Convert user_id string to UUID
        user_id = UUID(user_id_str)

        # Return token data
        token_data = TokenData(user_id=user_id, email=email)
        return token_data

    except JWTError:
        # Token is invalid, expired, or malformed
        raise credentials_exception


# ═══════════════════════════════════════════════════════════════════
# GET CURRENT USER (Extract user from token and fetch from DB)
# ═══════════════════════════════════════════════════════════════════

async def get_current_user_from_bearer(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current user from HTTPBearer token (for Swagger UI).
    This allows users to directly paste JWT tokens in Swagger.
    """
    token = credentials.credentials

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = verify_token(token, credentials_exception)
    user = db.query(User).filter(User.id == token_data.user_id).first()

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    return user


async def get_current_user(
    token: str = Depends(oauth2_scheme),  # Extract token from Authorization header
    db: Session = Depends(get_db)  # Database session
) -> User:
    """
    Get the current authenticated user from JWT token.

    Compare to .NET: Like getting User from HttpContext
        [Authorize]
        public async Task<IActionResult> GetProfile()
        {
            var userId = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
            var user = await _context.Users.FindAsync(Guid.Parse(userId));
            return Ok(user);
        }

    This is a FastAPI dependency that:
    1. Extracts the JWT token from Authorization header
    2. Validates the token
    3. Extracts user_id from token
    4. Fetches the user from database
    5. Returns the User object

    Usage in endpoints:
        @router.get("/users/me")
        async def get_me(current_user: User = Depends(get_current_user)):
            return current_user

    Args:
        token: JWT token from Authorization header (injected by oauth2_scheme)
        db: Database session (injected by FastAPI)

    Returns:
        User object of the authenticated user

    Raises:
        HTTPException 401: If token is invalid or user not found
    """
    # Define the exception to raise for invalid credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},  # OAuth2 standard header
    )

    # Verify and decode the token
    token_data = verify_token(token, credentials_exception)

    # Fetch user from database
    # Compare to .NET: _context.Users.FindAsync(userId)
    user = db.query(User).filter(User.id == token_data.user_id).first()

    # Check if user exists
    if user is None:
        raise credentials_exception

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    return user


# ═══════════════════════════════════════════════════════════════════
# USAGE EXAMPLES
# ═══════════════════════════════════════════════════════════════════
"""
# Example 1: Generate token after login
from app.auth.jwt import create_access_token

user = db.query(User).filter(User.email == "john@example.com").first()
if user and verify_password(password, user.hashed_password):
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )
    return {"access_token": access_token, "token_type": "bearer"}


# Example 2: Protect an endpoint with authentication
from app.auth.jwt import get_current_user

@router.get("/users/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    '''Get current user profile - requires authentication'''
    return current_user


# Example 3: Custom token expiration
from datetime import timedelta

token = create_access_token(
    data={"sub": str(user.id), "email": user.email},
    expires_delta=timedelta(hours=24)  # Custom 24-hour expiration
)


# Compare to .NET full flow:

// 1. Generate token (Login)
[HttpPost("login")]
public async Task<IActionResult> Login(LoginRequest request)
{
    var user = await _context.Users.FirstOrDefaultAsync(u => u.Email == request.Email);
    if (user == null || !_passwordHasher.VerifyPassword(user, request.Password))
        return Unauthorized();

    var tokenHandler = new JwtSecurityTokenHandler();
    var key = Encoding.UTF8.GetBytes(_configuration["Jwt:Key"]);

    var tokenDescriptor = new SecurityTokenDescriptor
    {
        Subject = new ClaimsIdentity(new[]
        {
            new Claim(ClaimTypes.NameIdentifier, user.Id.ToString()),
            new Claim(ClaimTypes.Email, user.Email)
        }),
        Expires = DateTime.UtcNow.AddMinutes(30),
        SigningCredentials = new SigningCredentials(
            new SymmetricSecurityKey(key),
            SecurityAlgorithms.HmacSha256Signature
        )
    };

    var token = tokenHandler.CreateToken(tokenDescriptor);
    return Ok(new { AccessToken = tokenHandler.WriteToken(token) });
}


// 2. Protect endpoint (Get current user)
[HttpGet("me")]
[Authorize]  // This validates the JWT token automatically
public async Task<IActionResult> GetMe()
{
    var userId = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
    var user = await _context.Users.FindAsync(Guid.Parse(userId));
    return Ok(user);
}
"""
