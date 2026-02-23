"""
Pydantic request/response schemas
"""
from pydantic import BaseModel, Field, field_validator, model_validator
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
    form_id: str = Field(..., description="The unique identifier of the form")
    answers: Dict[str, Any] = Field(..., description="Key-value pairs of question_id and user answer")
    
    @field_validator('answers')
    @classmethod
    def validate_answers(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure answers dictionary is not empty and contains valid data types"""
        if not v:
            raise ValueError("Answers cannot be empty")
        for key, value in v.items():
            if not isinstance(key, str) or not key.strip():
                raise ValueError("Question IDs must be valid non-empty strings")
            if value is None:
                continue # Allow partial nulls
            if not isinstance(value, (str, int, float, list, bool)):
                raise ValueError(f"Invalid answer format for question {key}")
        return v


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


from pydantic import BaseModel, Field, field_validator, model_validator

class QuestionCreate(BaseModel):
    """Schema for adding a question to a form"""
    form_id: str
    text: str = Field(..., min_length=1)
    type: str = Field(..., pattern=r'^(text|number|select|multiselect|date)$')
    order: int = Field(..., ge=0)
    options: Optional[List[str]] = None
    
    @model_validator(mode='after')
    def validate_options(self):
        q_type = self.type
        v = self.options
        if q_type in ('select', 'multiselect'):
            if not v or len(v) < 1:
                raise ValueError(f"Options are required for question type '{q_type}'")
        else:
            if v is not None:
                raise ValueError(f"Options are not allowed for question type '{q_type}'")
        return self


class QuestionUpdate(BaseModel):
    """Schema for updating a question"""
    text: Optional[str] = Field(None, min_length=1)
    type: Optional[str] = Field(None, pattern=r'^(text|number|select|multiselect|date)$')
    order: Optional[int] = Field(None, ge=0)
    options: Optional[List[str]] = None

    @model_validator(mode='after')
    def validate_options_update(self):
        if self.type is not None:
            q_type = self.type
            v = self.options
            if q_type in ('select', 'multiselect'):
                if v is not None and len(v) < 1:
                    raise ValueError(f"Options map cannot be empty for type '{q_type}'")
            else:
                if v is not None:
                    raise ValueError(f"Options are not allowed for question type '{q_type}'")
        return self


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


# --- Phase 5: AI & Responses Schemas ---

class AIAnalysisOut(BaseModel):
    """Schema for AI analysis data"""
    id: str
    response_id: str
    raw_analysis: Optional[Dict[str, Any]] = None
    status: str
    error_log: Optional[str] = None
    created_at: str

class AIAnalysisCreate(BaseModel):
    """Schema for creating a pending AI analysis record"""
    response_id: str

class AIAnalysisUpdate(BaseModel):
    """Schema for completing an AI analysis record with the LLM output"""
    raw_analysis: Optional[Dict[str, Any]] = None
    status: str = Field(..., pattern=r"^(completed|failed)$")
    error_log: Optional[str] = None

class ResponseOut(BaseModel):
    """Schema for form response data"""
    id: str
    form_id: str
    answers: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    created_at: str
    ai_analysis: Optional[AIAnalysisOut] = None

