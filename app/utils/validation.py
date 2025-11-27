"""
Email validation and sanitization utilities
"""
import re
from typing import Optional


def validate_email(email: str) -> bool:
    """
    Validate email format using regex
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email is valid, False otherwise
    """
    if not email or not isinstance(email, str):
        return False
    
    # RFC 5322 compliant regex (simplified)
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_regex, email))


def sanitize_email(email: str) -> Optional[str]:
    """
    Sanitize email address by trimming and lowercasing.
    Note: Email format is already validated by Pydantic's EmailStr before this function is called.
    
    Args:
        email: Email address to sanitize (already validated by Pydantic)
        
    Returns:
        Sanitized email (trimmed and lowercased) or None if input is invalid
    """
    if not email or not isinstance(email, str):
        return None
    
    # Just sanitize (trim and lowercase) - validation already done by Pydantic
    sanitized = email.strip().lower()
    
    # Basic check to ensure we have something after sanitization
    if not sanitized:
        return None
    
    return sanitized


def is_honeypot_filled(bot_check: Optional[str]) -> bool:
    """
    Check if honeypot field is filled (indicates bot)
    
    Args:
        bot_check: Value from honeypot field
        
    Returns:
        True if honeypot is filled (bot detected), False otherwise
    """
    return bool(bot_check and bot_check.strip())

