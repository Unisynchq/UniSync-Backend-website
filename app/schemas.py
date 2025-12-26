"""
Pydantic request/response schemas
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re


class SubscribeRequest(BaseModel):
    """Request schema for subscription endpoint"""
    email: str = Field(..., description="Email address", max_length=254)  # RFC 5321 max email length
    bot_check: Optional[str] = Field(None, description="Honeypot field (should be empty)", max_length=100)
    source: Optional[str] = Field("landing_hero", description="Source of subscription", max_length=50)
    timestamp: Optional[str] = Field(None, description="Request timestamp", max_length=50)
    
    @field_validator('email', mode='before')
    @classmethod
    def trim_email(cls, v: str) -> str:
        """Trim whitespace from email before validation"""
        if isinstance(v, str):
            return v.strip()
        return v
    
    @field_validator('email')
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        """
        Validate email format with lenient rules.
        Allows common email formats while rejecting obviously invalid ones.
        """
        if not v or not isinstance(v, str):
            raise ValueError("Email is required")
        
        # Trim and lowercase
        email = v.strip().lower()
        
        # Basic length checks
        if len(email) < 3:  # Minimum: a@b.c
            raise ValueError("Email is too short")
        if len(email) > 254:  # RFC 5321 max length
            raise ValueError("Email is too long")
        
        # More lenient regex that allows:
        # - Letters, numbers, dots, hyphens, underscores, plus signs, percent signs in local part
        # - Multiple dots in domain
        # - Hyphens in domain
        # - TLD with 2+ characters
        # This is more permissive than strict RFC but catches obvious errors
        email_pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, email):
            raise ValueError("Please enter a valid email address")
        
        # Additional checks for common issues
        if email.startswith('.') or email.startswith('@'):
            raise ValueError("Please enter a valid email address")
        if email.count('@') != 1:
            raise ValueError("Please enter a valid email address")
        if '..' in email:
            raise ValueError("Please enter a valid email address")
        if email.endswith('.'):
            raise ValueError("Please enter a valid email address")
        
        return email


class SubscribeResponse(BaseModel):
    """Response schema for subscription endpoint"""
    success: bool
    message: str
    code: Optional[str] = None
    is_duplicate: Optional[bool] = False


class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str
    code: str


class HealthResponse(BaseModel):
    """Health check response schema"""
    status: str
    timestamp: str
    environment: str

