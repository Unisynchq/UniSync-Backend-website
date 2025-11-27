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
    """
    # Build allowed origins list
    origins = [
        "http://localhost:3000",  # Development
    ]
    
    # Add frontend URL from settings if provided
    if settings.FRONTEND_URL:
        frontend_url = settings.FRONTEND_URL.strip()
        if frontend_url:
            origins.append(frontend_url)
            # Also add www variant if it's a production domain
            if frontend_url.startswith("https://") and not frontend_url.startswith("https://www."):
                origins.append(frontend_url.replace("https://", "https://www."))
            elif frontend_url.startswith("http://") and not frontend_url.startswith("http://www."):
                origins.append(frontend_url.replace("http://", "http://www."))
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"],
    )

