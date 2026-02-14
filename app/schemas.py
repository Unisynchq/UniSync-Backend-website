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


class AuthRequest(BaseModel):
    """Request schema for login/signup"""
    email: str = Field(..., description="User email")
    password: str = Field(..., min_length=8, description="User password")


class UserOut(BaseModel):
    """Public user schema"""
    id: str
    email: str
    created_at: str


from typing import Optional, List, Any, Dict


class AuthResponse(BaseModel):
    """Response schema for authentication"""
    success: bool
    user: Optional[UserOut] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None


class QuestionPublicOut(BaseModel):
    """Schema for public question data"""
    id: str
    text: str
    type: str
    order: int


class FormPublicOut(BaseModel):
    """Schema for public form data"""
    id: str
    slug: str
    title: str
    description: Optional[str] = None
    questions: List[QuestionPublicOut] = []


class ResponseSubmitRequest(BaseModel):
    """Schema for submitting a form response"""
    form_id: str
    answers: Dict[str, Any] = Field(..., description="Key-value pairs of question_id and user answer")


# --- Phase 4: Core APIs Schemas ---

class FormCreate(BaseModel):
    """Schema for creating a new form"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    slug: Optional[str] = Field(None, pattern=r'^[a-z0-9-]+$')


class FormUpdate(BaseModel):
    """Schema for updating form settings"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    is_published: Optional[bool] = None


class QuestionCreate(BaseModel):
    """Schema for adding a question to a form"""
    form_id: str
    text: str = Field(..., min_length=1)
    type: str = Field(..., pattern=r'^(text|number|select|multiselect|date)$')
    order: int
    options: Optional[List[str]] = None


class QuestionUpdate(BaseModel):
    """Schema for updating a question"""
    text: Optional[str] = None
    type: Optional[str] = None
    order: Optional[int] = None
    options: Optional[List[str]] = None


class QuestionOut(BaseModel):
    """Comprehensive question schema"""
    id: str
    form_id: str
    text: str
    type: str
    order: int
    options: Optional[List[str]] = None
    created_at: str


class FormOut(BaseModel):
    """Comprehensive form schema"""
    id: str
    owner_id: str
    slug: str
    title: str
    description: Optional[str] = None
    is_published: bool
    created_at: str
    questions: List[QuestionOut] = []


class DashboardStats(BaseModel):
    """Schema for dashboard metrics"""
    total_forms: int
    total_responses: int
    published_forms_count: int
    recent_responses_count: int

