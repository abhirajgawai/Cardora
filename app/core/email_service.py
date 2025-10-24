"""
Email Service - SendGrid Integration

Compare to .NET:
- Like using IEmailSender interface in ASP.NET Core Identity
- Or using MailKit / SendGrid.NET library in .NET

This module handles all email sending functionality using SendGrid.
"""

import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from app.core.config import settings

# Setup logging
logger = logging.getLogger(__name__)


async def send_password_reset_email(email: str, reset_token: str, user_name: str) -> bool:
    """
    Send password reset email via SendGrid

    Compare to .NET:
        await _emailSender.SendEmailAsync(
            user.Email,
            "Reset Password",
            $"Click here to reset: {resetLink}"
        );

    Args:
        email: Recipient email address
        reset_token: Password reset token (plain, not hashed)
        user_name: User's full name for personalization

    Returns:
        bool: True if email sent successfully, False otherwise

    Raises:
        No exceptions - errors are logged and False is returned
    """

    # Build reset link
    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"

    # HTML email body
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Password Reset - Cardora</title>
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background-color: #f8f9fa; border-radius: 10px; padding: 30px; margin-bottom: 20px;">
            <h1 style="color: #007bff; margin-top: 0;">Cardora - Password Reset Request</h1>

            <p>Hello <strong>{user_name}</strong>,</p>

            <p>We received a request to reset your password for your Cardora account.</p>

            <p>Click the button below to reset your password:</p>

            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_link}"
                   style="background-color: #007bff; color: white; padding: 12px 30px;
                          text-decoration: none; border-radius: 5px; display: inline-block;
                          font-weight: bold;">
                    Reset Password
                </a>
            </div>

            <p>Or copy and paste this link into your browser:</p>
            <p style="background-color: #e9ecef; padding: 10px; border-radius: 5px; word-break: break-all;">
                {reset_link}
            </p>

            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6;">
                <p style="color: #6c757d; font-size: 14px; margin-bottom: 10px;">
                    <strong>Important Security Information:</strong>
                </p>
                <ul style="color: #6c757d; font-size: 14px;">
                    <li>This link will expire in <strong>1 hour</strong></li>
                    <li>If you didn't request this reset, please ignore this email</li>
                    <li>Your password will not change until you create a new one</li>
                    <li>Never share this link with anyone</li>
                </ul>
            </div>
        </div>

        <div style="text-align: center; color: #6c757d; font-size: 12px;">
            <p>This email was sent by Cardora - Credit Card Statement Analyzer</p>
            <p>If you have any questions, please contact support.</p>
        </div>
    </body>
    </html>
    """

    # Plain text fallback
    text_content = f"""
    Password Reset Request - Cardora

    Hello {user_name},

    We received a request to reset your password for your Cardora account.

    Click the link below to reset your password:
    {reset_link}

    IMPORTANT SECURITY INFORMATION:
    - This link will expire in 1 hour
    - If you didn't request this reset, please ignore this email
    - Your password will not change until you create a new one
    - Never share this link with anyone

    This email was sent by Cardora - Credit Card Statement Analyzer
    """

    try:
        # Check if SendGrid API key is configured
        if not settings.SENDGRID_API_KEY or settings.SENDGRID_API_KEY == "your_sendgrid_api_key_here":
            logger.warning("SendGrid API key not configured. Email not sent.")
            logger.info(f"\n{'='*70}")
            logger.info("PASSWORD RESET EMAIL (SendGrid not configured)")
            logger.info(f"{'='*70}")
            logger.info(f"To: {email}")
            logger.info(f"Subject: Reset Your Cardora Password")
            logger.info(f"Reset Link: {reset_link}")
            logger.info(f"{'='*70}\n")
            # Return True for development - email is "sent" to console
            return True

        # Create SendGrid message
        message = Mail(
            from_email=Email(settings.FROM_EMAIL, settings.FROM_NAME),
            to_emails=To(email),
            subject="Reset Your Cardora Password",
            html_content=Content("text/html", html_content),
            plain_text_content=Content("text/plain", text_content)
        )

        # Send email via SendGrid
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)

        # Check response status
        if response.status_code in [200, 201, 202]:
            logger.info(f"Password reset email sent successfully to {email}")
            return True
        else:
            logger.error(f"SendGrid returned status {response.status_code}")
            return False

    except Exception as e:
        logger.error(f"Failed to send password reset email: {str(e)}")
        return False


async def send_welcome_email(email: str, user_name: str) -> bool:
    """
    Send welcome email to new users

    Compare to .NET:
        await _emailSender.SendEmailAsync(
            user.Email,
            "Welcome to Cardora!",
            welcomeEmailBody
        );

    Args:
        email: Recipient email address
        user_name: User's full name

    Returns:
        bool: True if sent successfully, False otherwise
    """

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Welcome to Cardora!</title>
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background-color: #f8f9fa; border-radius: 10px; padding: 30px;">
            <h1 style="color: #007bff;">Welcome to Cardora!</h1>

            <p>Hello <strong>{user_name}</strong>,</p>

            <p>Thank you for signing up for Cardora - your intelligent credit card statement analyzer!</p>

            <p>With Cardora, you can:</p>
            <ul>
                <li>Upload and analyze credit card statements</li>
                <li>Track spending by category</li>
                <li>Get insights into your spending habits</li>
                <li>Generate detailed reports</li>
            </ul>

            <p>Get started by logging in and uploading your first statement!</p>

            <div style="text-align: center; margin: 30px 0;">
                <a href="{settings.FRONTEND_URL}/login"
                   style="background-color: #28a745; color: white; padding: 12px 30px;
                          text-decoration: none; border-radius: 5px; display: inline-block;
                          font-weight: bold;">
                    Get Started
                </a>
            </div>
        </div>

        <div style="text-align: center; color: #6c757d; font-size: 12px; margin-top: 20px;">
            <p>Welcome aboard!</p>
            <p>The Cardora Team</p>
        </div>
    </body>
    </html>
    """

    try:
        if not settings.SENDGRID_API_KEY or settings.SENDGRID_API_KEY == "your_sendgrid_api_key_here":
            logger.info(f"Welcome email would be sent to: {email}")
            return True

        message = Mail(
            from_email=Email(settings.FROM_EMAIL, settings.FROM_NAME),
            to_emails=To(email),
            subject="Welcome to Cardora!",
            html_content=Content("text/html", html_content)
        )

        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)

        if response.status_code in [200, 201, 202]:
            logger.info(f"Welcome email sent to {email}")
            return True
        else:
            logger.error(f"SendGrid returned status {response.status_code}")
            return False

    except Exception as e:
        logger.error(f"Failed to send welcome email: {str(e)}")
        return False


# ============================================================
# COMPARE TO .NET
# ============================================================
"""
In ASP.NET Core, you'd typically use:

1. Built-in IEmailSender (simple):
   public interface IEmailSender
   {
       Task SendEmailAsync(string email, string subject, string htmlMessage);
   }

2. SendGrid.NET library:
   var client = new SendGridClient(apiKey);
   var msg = new SendGridMessage()
   {
       From = new EmailAddress("no-reply@cardora.com", "Cardora"),
       Subject = "Reset Password",
       HtmlContent = htmlContent
   };
   msg.AddTo(new EmailAddress(email));
   await client.SendEmailAsync(msg);

3. MailKit (more complex, but more control):
   var message = new MimeMessage();
   message.From.Add(new MailboxAddress("Cardora", "noreply@cardora.com"));
   message.To.Add(new MailboxAddress(userName, email));
   message.Subject = "Reset Password";
   message.Body = new TextPart("html") { Text = htmlContent };

   using var client = new SmtpClient();
   await client.ConnectAsync("smtp.sendgrid.net", 587);
   await client.AuthenticateAsync(apiKey, apiKey);
   await client.SendAsync(message);
   await client.DisconnectAsync(true);

Our Python implementation is most similar to Option 2 (SendGrid.NET library).
"""
