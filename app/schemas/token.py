"""
JWT Token Pydantic Schemas (DTOs)

Compare to .NET: Like having LoginResponse or TokenDto
    - Token → LoginResponse (JWT token response)
    - TokenData → ClaimsPrincipal data (what's inside the token)

In .NET you might have:
    public class LoginResponse
    {
        public string AccessToken { get; set; }
        public string TokenType { get; set; } = "bearer";
    }

    public class TokenClaims
    {
        public string UserId { get; set; }
        public string Email { get; set; }
    }
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from uuid import UUID


# ═══════════════════════════════════════════════════════════════════
# TOKEN RESPONSE (Login Success)
# ═══════════════════════════════════════════════════════════════════

class Token(BaseModel):
    """
    Schema for JWT token response (output)

    Compare to .NET:
        public class LoginResponse
        {
            public string AccessToken { get; set; }
            public string TokenType { get; set; }
        }

    This is what the client receives after successful login.
    """
    access_token: str = Field(
        ...,
        description="JWT access token",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."]
    )

    token_type: str = Field(
        default="bearer",  # OAuth 2.0 standard
        description="Token type (always 'bearer' for JWT)",
        examples=["bearer"]
    )

    # Configuration
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJlbWFpbCI6ImpvaG4uZG9lQGV4YW1wbGUuY29tIiwiZXhwIjoxNjk4MzQ1NjAwfQ.xyz123",
                "token_type": "bearer"
            }
        }
    )


# ═══════════════════════════════════════════════════════════════════
# TOKEN DATA (Claims inside JWT)
# ═══════════════════════════════════════════════════════════════════

class TokenData(BaseModel):
    """
    Schema for data stored inside JWT token (claims)

    Compare to .NET:
        public class TokenClaims
        {
            public Guid UserId { get; set; }
            public string Email { get; set; }
        }

        // Or using ClaimsPrincipal:
        var claims = new[]
        {
            new Claim(ClaimTypes.NameIdentifier, userId.ToString()),
            new Claim(ClaimTypes.Email, email)
        };

    This is what we encode inside the JWT and extract when validating.
    """
    user_id: Optional[UUID] = Field(
        None,
        description="User's unique identifier",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )

    email: Optional[str] = Field(
        None,
        description="User's email address",
        examples=["john.doe@example.com"]
    )

    # Configuration
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "john.doe@example.com"
            }
        }
    )


# ═══════════════════════════════════════════════════════════════════
# USAGE EXAMPLES
# ═══════════════════════════════════════════════════════════════════
"""
# Example 1: Return JWT token after successful login
from app.schemas import Token

# After verifying credentials
token = Token(
    access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    token_type="bearer"
)
return token


# Example 2: Store user data in JWT
from app.schemas import TokenData
from jose import jwt

token_data = TokenData(
    user_id=user.id,
    email=user.email
)

# Encode to JWT
access_token = jwt.encode(
    {
        "sub": str(token_data.user_id),  # 'sub' is standard JWT claim
        "email": token_data.email,
        "exp": datetime.utcnow() + timedelta(minutes=30)
    },
    SECRET_KEY,
    algorithm="HS256"
)


# Example 3: Extract user data from JWT
from jose import jwt

payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
token_data = TokenData(
    user_id=UUID(payload.get("sub")),
    email=payload.get("email")
)


# Compare to .NET:
// Generate JWT token
var claims = new[]
{
    new Claim(ClaimTypes.NameIdentifier, user.Id.ToString()),
    new Claim(ClaimTypes.Email, user.Email)
};

var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(secretKey));
var creds = new SigningCredentials(key, SecurityAlgorithms.HmacSha256);

var token = new JwtSecurityToken(
    claims: claims,
    expires: DateTime.UtcNow.AddMinutes(30),
    signingCredentials: creds
);

var accessToken = new JwtSecurityTokenHandler().WriteToken(token);

return new LoginResponse
{
    AccessToken = accessToken,
    TokenType = "bearer"
};


// Validate JWT token
var tokenHandler = new JwtSecurityTokenHandler();
var key = Encoding.UTF8.GetBytes(secretKey);

var validationParameters = new TokenValidationParameters
{
    ValidateIssuerSigningKey = true,
    IssuerSigningKey = new SymmetricSecurityKey(key),
    ValidateIssuer = false,
    ValidateAudience = false
};

var principal = tokenHandler.ValidateToken(token, validationParameters, out var validatedToken);
var userId = principal.FindFirst(ClaimTypes.NameIdentifier)?.Value;
var email = principal.FindFirst(ClaimTypes.Email)?.Value;
"""
