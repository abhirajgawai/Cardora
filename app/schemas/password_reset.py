"""
Password Reset Schemas (DTOs)

Compare to .NET: Like having Request/Response DTOs for password reset endpoints
"""

from pydantic import BaseModel, EmailStr, Field


class PasswordResetRequest(BaseModel):
    """
    Request schema for forgot password endpoint

    Compare to .NET:
        public class ForgotPasswordRequest
        {
            [Required]
            [EmailAddress]
            public string Email { get; set; }
        }
    """
    email: EmailStr = Field(
        ...,
        description="Email address of the user who forgot their password",
        examples=["user@example.com"]
    )


class PasswordResetConfirm(BaseModel):
    """
    Request schema for password reset confirmation

    Compare to .NET:
        public class ResetPasswordRequest
        {
            [Required]
            public string Token { get; set; }

            [Required]
            [MinLength(8)]
            public string NewPassword { get; set; }
        }
    """
    token: str = Field(
        ...,
        description="Password reset token from email",
        min_length=1,
        examples=["abc123def456ghi789..."]
    )

    new_password: str = Field(
        ...,
        description="New password (min 8 characters)",
        min_length=8,
        max_length=100,
        examples=["MyNewSecurePassword123!"]
    )


class PasswordResetResponse(BaseModel):
    """
    Response schema for password reset request

    Compare to .NET:
        public class MessageResponse
        {
            public string Message { get; set; }
        }
    """
    message: str = Field(
        ...,
        description="Success/info message",
        examples=["If your email exists, you will receive a password reset link"]
    )


class PasswordResetSuccess(BaseModel):
    """
    Response schema for successful password reset

    Compare to .NET:
        public class PasswordResetSuccessResponse
        {
            public string Message { get; set; }
        }
    """
    message: str = Field(
        ...,
        description="Success message",
        examples=["Password has been reset successfully"]
    )
