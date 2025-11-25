"""
Resend email service wrapper
"""
from typing import Optional
from datetime import datetime
import asyncio
import html
import resend
from app.config import settings
from app.utils.logger import logger


class EmailService:
    """Email service using Resend"""
    
    def __init__(self):
        """Initialize Resend client"""
        resend.api_key = settings.RESEND_API_KEY
        self.emails_client = resend.Emails()
    
    async def send_welcome_email(self, email: str) -> bool:
        """
        Send welcome email to new subscriber
        
        Args:
            email: Subscriber email address
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            params = {
                "from": settings.RESEND_FROM_EMAIL,
                "to": [email],
                "subject": "Welcome to Unisync Early Access",
                "html": self._get_welcome_email_html(),
            }
            
            logger.info("Attempting to send welcome email", {
                "email": email[:5] + "***",  # Partial email for privacy
                "from": settings.RESEND_FROM_EMAIL
            })
            
            # Run blocking I/O in thread pool to avoid blocking event loop
            email_response = await asyncio.to_thread(self.emails_client.send, params)
            
            # Log the full response for debugging
            logger.info("Resend API response", {
                "email": email[:5] + "***",
                "response": str(email_response),
                "response_type": type(email_response).__name__,
                "email_id": email_response.get("id") if isinstance(email_response, dict) else None
            })
            
            if isinstance(email_response, dict) and email_response.get("id"):
                logger.info("Welcome email sent successfully", {
                    "email": email[:5] + "***",
                    "email_id": email_response.get("id")
                })
                return True
            else:
                logger.warn("Email sent but no ID returned", {
                    "email": email[:5] + "***",
                    "response": email_response
                })
                return False
            
        except Exception as e:
            logger.error("Failed to send welcome email", e, {
                "email": email[:5] + "***",
                "error_type": type(e).__name__,
                "error_message": str(e),
                "from_email": settings.RESEND_FROM_EMAIL
            })
            return False
    
    async def send_admin_notification(self, email: str, source: str = "landing_hero") -> bool:
        """
        Send notification email to admin about new subscription
        
        Args:
            email: Subscriber email address
            source: Source of subscription
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            params = {
                "from": settings.RESEND_FROM_EMAIL,
                "to": [settings.ADMIN_EMAIL],
                "subject": "New Unisync Early Access Signup",
                "html": self._get_admin_notification_html(email, source),
            }
            
            logger.info("Attempting to send admin notification", {
                "email": email[:5] + "***",
                "source": source,
                "to": settings.ADMIN_EMAIL,
                "from": settings.RESEND_FROM_EMAIL
            })
            
            # Run blocking I/O in thread pool to avoid blocking event loop
            email_response = await asyncio.to_thread(self.emails_client.send, params)
            
            logger.info("Resend API response (admin)", {
                "email": email[:5] + "***",
                "response": str(email_response),
                "response_type": type(email_response).__name__,
                "email_id": email_response.get("id") if isinstance(email_response, dict) else None
            })
            
            if isinstance(email_response, dict) and email_response.get("id"):
                logger.info("Admin notification sent successfully", {
                    "email": email[:5] + "***",
                    "source": source,
                    "email_id": email_response.get("id")
                })
                return True
            else:
                logger.warn("Admin email sent but no ID returned", {
                    "email": email[:5] + "***",
                    "response": email_response
                })
                return False
            
        except Exception as e:
            logger.error("Failed to send admin notification", e, {
                "email": email[:5] + "***",
                "source": source,
                "error_type": type(e).__name__,
                "error_message": str(e),
                "from_email": settings.RESEND_FROM_EMAIL
            })
            return False
    
    def _get_welcome_email_html(self) -> str:
        """Generate welcome email HTML"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 8px 8px 0 0;">
                <h1 style="color: white; margin: 0; font-size: 28px;">Welcome to Unisync!</h1>
            </div>
            <div style="background: #ffffff; padding: 30px; border-radius: 0 0 8px 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <p style="font-size: 16px; margin-bottom: 20px;">Thank you for joining our early access list!</p>
                <p style="font-size: 16px; margin-bottom: 20px;">We're excited to have you on board. Unisync is designed to help teams turn messy feedback into clear, actionable intelligence.</p>
                <p style="font-size: 16px; margin-bottom: 20px;">We'll be in touch within 24 hours with next steps. If you're a good fit for our 2–4 week pilot program, we'll reach out to schedule a quick call.</p>
                <div style="background: #f5f5f5; padding: 20px; border-radius: 6px; margin: 30px 0;">
                    <p style="margin: 0; font-size: 14px; color: #666;"><strong>What's next?</strong></p>
                    <ul style="margin: 10px 0 0 0; padding-left: 20px; font-size: 14px; color: #666;">
                        <li>We'll review your application</li>
                        <li>If you're a fit, we'll schedule a pilot</li>
                        <li>You'll see how Unisync works with your teams</li>
                    </ul>
                </div>
                <p style="font-size: 14px; color: #666; margin-top: 30px;">If you have any questions, feel free to reach out to us at <a href="mailto:hello@unisynchq.com" style="color: #667eea;">hello@unisynchq.com</a>.</p>
            </div>
            <div style="text-align: center; margin-top: 20px; padding-top: 20px; border-top: 1px solid #eee;">
                <p style="font-size: 12px; color: #999;">Unisync - Pre-incubated at IIM Bangalore NSRCEL</p>
            </div>
        </body>
        </html>
        """
    
    def _get_admin_notification_html(self, email: str, source: str) -> str:
        """Generate admin notification email HTML with XSS protection"""
        # Escape user input to prevent XSS attacks
        safe_email = html.escape(email)
        safe_source = html.escape(source)
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: #f5f5f5; padding: 20px; border-radius: 8px;">
                <h2 style="margin-top: 0; color: #333;">New Early Access Signup</h2>
                <p style="font-size: 16px;"><strong>Email:</strong> {safe_email}</p>
                <p style="font-size: 16px;"><strong>Source:</strong> {safe_source}</p>
                <p style="font-size: 16px;"><strong>Timestamp:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            </div>
        </body>
        </html>
        """


# Global email service instance
email_service = EmailService()

