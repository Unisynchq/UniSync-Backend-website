"""
Environment configuration and validation
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Supabase
    SUPABASE_URL: str = Field(..., description="Supabase project URL")
    SUPABASE_KEY: str = Field(..., description="Supabase anon/service key")
    
    # Resend
    RESEND_API_KEY: str = Field(..., description="Resend API key for email sending")
    RESEND_FROM_EMAIL: str = Field(default="noreply@unisync.app", description="Email address to send from")
    ADMIN_EMAIL: str = Field(default="hello@unisynchq.com", description="Admin email for notifications")
    
    # Application
    ENVIRONMENT: str = Field(default="development", description="Application environment")
    FRONTEND_URL: str = Field(..., description="Frontend URL for CORS configuration")
    API_PREFIX: str = Field(default="/api", description="API route prefix")
    
    # Optional
    REDIS_URL: Optional[str] = Field(default=None, description="Redis URL for distributed rate limiting")
    SENTRY_DSN: Optional[str] = Field(default=None, description="Sentry DSN for error tracking")
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = Field(default=10, description="Maximum requests per window")
    RATE_LIMIT_WINDOW_MINUTES: int = Field(default=15, description="Rate limit window in minutes")
    
    @field_validator('ENVIRONMENT')
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment value"""
        allowed = ['development', 'staging', 'production']
        if v not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of {allowed}")
        return v
    
    @field_validator('FRONTEND_URL')
    @classmethod
    def validate_frontend_url(cls, v: str, info) -> str:
        """Validate frontend URL format"""
        if not v:
            raise ValueError("FRONTEND_URL is required and cannot be empty")
        if not v.startswith(('http://', 'https://')):
            raise ValueError("FRONTEND_URL must start with http:// or https://")
        return v
    
    @field_validator('SUPABASE_URL')
    @classmethod
    def validate_supabase_url(cls, v: str) -> str:
        """Validate Supabase URL format"""
        if not v:
            raise ValueError("SUPABASE_URL is required and cannot be empty")
        if not v.startswith('https://'):
            raise ValueError("SUPABASE_URL must start with https://")
        return v
    
    @field_validator('RESEND_API_KEY')
    @classmethod
    def validate_resend_key(cls, v: str) -> str:
        """Validate Resend API key format"""
        if not v:
            raise ValueError("RESEND_API_KEY is required and cannot be empty")
        if not v.startswith('re_'):
            raise ValueError("RESEND_API_KEY should start with 're_'")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance with validation
    
    Raises:
        ValueError: If required environment variables are missing or invalid
    """
    try:
        return Settings()
    except Exception as e:
        error_msg = (
            f"Failed to load application settings: {str(e)}\n"
            "Please check your .env file and ensure all required variables are set.\n"
            "Required variables: SUPABASE_URL, SUPABASE_KEY, RESEND_API_KEY, FRONTEND_URL"
        )
        raise ValueError(error_msg) from e


# Global settings instance
# This will raise an error at import time if configuration is invalid
settings = get_settings()

