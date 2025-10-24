"""
Users Router - Protected User Endpoints

Compare to .NET: Like having a UsersController with [Authorize] attribute
    [ApiController]
    [Route("api/[controller]")]
    [Authorize]  // All endpoints require authentication
    public class UsersController : ControllerBase
    {
        [HttpGet("me")]
        public async Task<ActionResult<UserDto>> GetCurrentUser()
        {
            var userId = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
            var user = await _context.Users.FindAsync(Guid.Parse(userId));
            return Ok(_mapper.Map<UserDto>(user));
        }
    }
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.schemas import UserResponse
from app.auth.jwt import get_current_user


# ═══════════════════════════════════════════════════════════════════
# ROUTER SETUP
# ═══════════════════════════════════════════════════════════════════
# Compare to .NET: Like [ApiController] [Route("api/users")]

router = APIRouter(
    prefix="/users",  # All routes will be /users/...
    tags=["Users"]  # For API documentation grouping
)


# ═══════════════════════════════════════════════════════════════════
# GET /users/me - Get Current User Profile (PROTECTED)
# ═══════════════════════════════════════════════════════════════════

@router.get(
    "/me",
    response_model=UserResponse,  # Automatic response validation
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
    description="Get the profile of the currently authenticated user. Requires valid JWT token."
)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)  # JWT authentication required!
):
    """
    Get current authenticated user's profile.

    Compare to .NET:
        [HttpGet("me")]
        [Authorize]  // Requires authentication
        public async Task<ActionResult<UserDto>> GetCurrentUser()
        {
            // User is automatically populated by [Authorize] attribute
            var userId = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
            var user = await _context.Users.FindAsync(Guid.Parse(userId));

            if (user == null)
                return NotFound();

            return Ok(_mapper.Map<UserDto>(user));
        }

    **How JWT authentication works here:**

    1. Client sends request with header:
       Authorization: Bearer <jwt_token>

    2. FastAPI extracts token from header (oauth2_scheme)

    3. get_current_user dependency:
       - Validates the JWT token
       - Extracts user_id from token
       - Queries database for user
       - Returns User object

    4. If token is invalid/expired/missing → 401 Unauthorized

    5. If token is valid → endpoint receives authenticated user

    Args:
        current_user: Authenticated user (injected by FastAPI dependency)

    Returns:
        UserResponse: Current user's profile data (without password)

    Raises:
        HTTPException 401: If JWT token is invalid, expired, or missing
        HTTPException 403: If user account is inactive

    Example:
        # Request with valid JWT token:
        GET /users/me
        Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

        # Response 200 OK:
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

        # Request without token or invalid token:
        GET /users/me

        # Response 401 Unauthorized:
        {
            "detail": "Not authenticated"
        }
    """

    # The user is already authenticated and fetched from database
    # by the get_current_user dependency!
    # Compare to .NET: User is already available from [Authorize] attribute

    # Simply return the user data (Pydantic automatically excludes password)
    # Compare to .NET: return _mapper.Map<UserDto>(user)
    return UserResponse.model_validate(current_user)


# ═══════════════════════════════════════════════════════════════════
# USAGE EXAMPLES
# ═══════════════════════════════════════════════════════════════════
"""
# Example 1: Get current user with valid token
# First, login to get a token:
POST http://localhost:8001/auth/login
Content-Type: application/json

{
    "email": "john.doe@example.com",
    "password": "MySecurePassword123!"
}

# Response: {"access_token": "eyJhbGci...", "token_type": "bearer"}

# Then, use the token to get current user:
GET http://localhost:8001/users/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Response 200 OK:
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


# Example 2: Get current user without token
GET http://localhost:8001/users/me

# Response 401 Unauthorized:
{
    "detail": "Not authenticated"
}


# Example 3: Get current user with invalid token
GET http://localhost:8001/users/me
Authorization: Bearer invalid_token_here

# Response 401 Unauthorized:
{
    "detail": "Could not validate credentials"
}


# Compare to .NET usage:
// 1. Login and get token
POST https://localhost:5001/api/auth/login
Content-Type: application/json

{
    "email": "john.doe@example.com",
    "password": "MySecurePassword123!"
}

// 2. Get current user with token
GET https://localhost:5001/api/users/me
Authorization: Bearer eyJhbGci...

// C# Controller code:
[ApiController]
[Route("api/[controller]")]
public class UsersController : ControllerBase
{
    private readonly AppDbContext _context;

    [HttpGet("me")]
    [Authorize]  // Requires authentication
    public async Task<ActionResult<UserDto>> GetMe()
    {
        // Get user ID from JWT token
        var userId = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;

        // Fetch user from database
        var user = await _context.Users.FindAsync(Guid.Parse(userId));

        if (user == null)
            return NotFound();

        return Ok(_mapper.Map<UserDto>(user));
    }
}
"""
