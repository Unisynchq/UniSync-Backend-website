"""
Email validation and sanitization utilities
"""
import re
from typing import Optional


def validate_email(email: str) -> bool:
    """
    Validate email format using lenient regex
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email is valid, False otherwise
    """
    if not email or not isinstance(email, str):
        return False
    
    # More lenient regex that allows common email formats
    # Allows: letters, numbers, dots, hyphens, underscores, plus, percent in local part
    # Allows: multiple subdomains, hyphens in domain
    # Requires: valid TLD with 2+ characters
    email_pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        return False
    
    # Additional basic checks
    if email.startswith('.') or email.startswith('@'):
        return False
    if email.count('@') != 1:
        return False
    if '..' in email:
        return False
    if email.endswith('.'):
        return False
    
    return True


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

