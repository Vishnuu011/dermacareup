import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from src.config.config import settings
from src.logger.custom_logger import logger



def send_password_reset_email(user_email: str, reset_token: str):
    """
    Send password reset email to user
    """
    try:
        if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD or not settings.SMTP_FROM_EMAIL:
            logger.warning("SMTP credentials not configured. Email will not be sent.")
            logger.info(f"Password reset token for {user_email}: {reset_token}")
            return
        
        reset_url = f"http://127.0.0.1:8000/api/v1/auth/password-reset?token={reset_token}"
        subject = "Password Reset Request"
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h2 style="color: #333; margin-top: 0;">Password Reset Request</h2>
                    <p style="color: #666; line-height: 1.6;">
                        We received a request to reset your password. Click the button below to create a new password.
                    </p>
                    <div style="margin: 30px 0; text-align: center;">
                        <a href="{reset_url}" style="display: inline-block; background-color: #007bff; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                            Reset Password
                        </a>
                    </div>
                    <p style="color: #999; font-size: 14px;">
                        This link will expire in 30 minutes.
                    </p>
                    <p style="color: #999; font-size: 12px;">
                        If you didn't request this, please ignore this email.
                    </p>
                </div>
            </body>
        </html>
        """
        
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = settings.SMTP_FROM_EMAIL
        message["To"] = user_email
        
        message.attach(MIMEText(html_body, "html"))
        
        with smtplib.SMTP_SSL(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM_EMAIL, user_email, message.as_string())
        
        logger.info(f"Password reset email sent to {user_email}")
    except Exception as e:
        logger.error(f"Failed to send password reset email: {str(e)}")
        raise Exception(f"Failed to send email: {str(e)}")
