"""
Password Reset Utilities

Compare to .NET ASP.NET Core Identity:
    var token = await _userManager.GeneratePasswordResetTokenAsync(user);
    var result = await _userManager.ResetPasswordAsync(user, token, newPassword);

This module handles password reset token generation and validation.
"""

import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.features.auth.models import User
from app.core.config import settings


def generate_reset_token() -> str:
    """
    Generate a cryptographically secure reset token

    Compare to .NET:
        var token = await _userManager.GeneratePasswordResetTokenAsync(user);

    Returns:
        str: 43-character URL-safe token

    The token is generated using Python's secrets module which is
    cryptographically strong random number generator.
    """
    # Generate 32 random bytes, encode as URL-safe base64
    # Results in ~43 characters
    return secrets.token_urlsafe(32)


def hash_reset_token(token: str) -> str:
    """
    Hash the reset token for secure storage

    Why hash tokens?
    - If database is compromised, tokens are safe
    - Similar to password hashing
    - We store hashed version, send plain version via email

    Compare to .NET:
        // ASP.NET Core Identity hashes tokens internally
        // We need to do it manually in our implementation

    Args:
        token: Plain reset token

    Returns:
        str: SHA-256 hash of the token (hex encoded)
    """
    return hashlib.sha256(token.encode()).hexdigest()


def create_password_reset_token(db: Session, user: User) -> str:
    """
    Create and store password reset token for user

    Compare to .NET:
        var token = await _userManager.GeneratePasswordResetTokenAsync(user);
        // Token is stored internally by Identity

    Args:
        db: Database session
        user: User who requested password reset

    Returns:
        str: Plain reset token (to be sent via email)

    Side effects:
        - Generates new token
        - Hashes and stores token in database
        - Sets expiration time
        - Commits to database
    """
    # Generate plain token
    plain_token = generate_reset_token()

    # Hash the token for storage
    hashed_token = hash_reset_token(plain_token)

    # Set expiration time
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES
    )

    # Update user record
    user.reset_token = hashed_token
    user.reset_token_expires = expires_at

    # Commit to database
    db.commit()
    db.refresh(user)

    # Return plain token (to be sent via email)
    return plain_token


def verify_reset_token(db: Session, token: str) -> User | None:
    """
    Verify reset token and return user if valid

    Compare to .NET:
        var result = await _userManager.VerifyUserTokenAsync(
            user,
            _userManager.Options.Tokens.PasswordResetTokenProvider,
            "ResetPassword",
            token
        );

    Args:
        db: Database session
        token: Plain reset token (from email link)

    Returns:
        User | None: User if token is valid, None if invalid/expired

    Validation checks:
        1. Hash the provided token
        2. Find user with matching hashed token
        3. Check token hasn't expired
        4. Check user account is active
    """
    # Hash the provided token
    hashed_token = hash_reset_token(token)

    # Find user with this token
    user = db.query(User).filter(
        User.reset_token == hashed_token
    ).first()

    if not user:
        return None

    # Check if token has expired
    if not user.reset_token_expires:
        return None

    now = datetime.now(timezone.utc)
    if now > user.reset_token_expires:
        # Token expired - clear it from database
        clear_reset_token(db, user)
        return None

    # Check if user account is active
    if not user.is_active:
        return None

    return user


def clear_reset_token(db: Session, user: User) -> None:
    """
    Clear password reset token from user

    Compare to .NET:
        // ASP.NET Core Identity clears token automatically after use
        // We need to do it manually

    Args:
        db: Database session
        user: User whose token should be cleared

    Side effects:
        - Sets reset_token to NULL
        - Sets reset_token_expires to NULL
        - Commits to database

    Called when:
        - Password reset is successful
        - Token has expired
        - User requests new reset token
    """
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()


def is_reset_token_expired(user: User) -> bool:
    """
    Check if user's reset token is expired

    Args:
        user: User to check

    Returns:
        bool: True if expired or no token, False if still valid
    """
    if not user.reset_token_expires:
        return True

    now = datetime.now(timezone.utc)
    return now > user.reset_token_expires


# ============================================================
# COMPARE TO .NET ASP.NET CORE IDENTITY
# ============================================================
"""
ASP.NET Core Identity handles password reset like this:

1. Generate Reset Token:
   var token = await _userManager.GeneratePasswordResetTokenAsync(user);
   // Token is generated and stored internally
   // Token is URL-encoded and time-limited

2. Send Email:
   var callbackUrl = Url.Page(
       "/Account/ResetPassword",
       pageHandler: null,
       values: new { area = "Identity", code = token },
       protocol: Request.Scheme
   );
   await _emailSender.SendEmailAsync(
       email,
       "Reset Password",
       $"Please reset your password by <a href='{callbackUrl}'>clicking here</a>."
   );

3. Verify and Reset:
   var user = await _userManager.FindByEmailAsync(email);
   var result = await _userManager.ResetPasswordAsync(user, token, newPassword);

   if (result.Succeeded)
   {
       return RedirectToPage("./ResetPasswordConfirmation");
   }

Configuration:
   services.Configure<DataProtectionTokenProviderOptions>(options =>
   {
       options.TokenLifespan = TimeSpan.FromHours(3);
   });

Key Differences:
1. ASP.NET Identity:
   - Tokens are managed internally
   - Uses data protection API
   - Tokens are more complex (include user info)
   - Automatic cleanup

2. Our Implementation:
   - We manage tokens explicitly
   - Use simple SHA-256 hashing
   - Tokens are random strings
   - Manual cleanup

Advantages of our approach:
- Simpler to understand
- Full control over token format
- No dependency on .NET's data protection
- Easy to customize expiration logic

Disadvantages:
- More code to maintain
- Need to handle edge cases manually
- No built-in security features
"""
