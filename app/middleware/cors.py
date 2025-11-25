"""
CORS middleware configuration
"""
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.config import settings


def setup_cors(app: FastAPI):
    """
    Configure CORS middleware for the FastAPI app
    
    Args:
        app: FastAPI application instance
    
    Raises:
        ValueError: If FRONTEND_URL is not configured
    """
    if not settings.FRONTEND_URL:
        raise ValueError(
            "FRONTEND_URL must be set in environment variables. "
            "CORS cannot be configured without a frontend URL."
        )
    
    # In development, allow localhost variations
    allowed_origins = [settings.FRONTEND_URL]
    if settings.ENVIRONMENT == "development":
        # Allow common localhost variations for development
        allowed_origins.extend([
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:3001",
        ])
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"],
    )

