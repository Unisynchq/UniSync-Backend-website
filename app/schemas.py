"""
Pydantic request/response schemas
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional


class SubscribeRequest(BaseModel):
    """Request schema for subscription endpoint"""
    email: EmailStr = Field(..., description="Email address", max_length=254)  # RFC 5321 max email length
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

