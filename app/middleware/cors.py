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
    # Build allowed origins list - explicit list for production reliability
    origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "https://unisynchq.com",
        "https://www.unisynchq.com",
    ]
    
    # Add frontend URL from settings if provided
    if settings.FRONTEND_URL:
        frontend_url = settings.FRONTEND_URL.strip().rstrip('/')
        if frontend_url:
            # Add the exact URL
            if frontend_url not in origins:
                origins.append(frontend_url)
            # Also add www variant if it's a production domain
            if frontend_url.startswith("https://") and not frontend_url.startswith("https://www."):
                www_url = frontend_url.replace("https://", "https://www.")
                if www_url not in origins:
                    origins.append(www_url)
            elif frontend_url.startswith("http://") and not frontend_url.startswith("http://www."):
                www_url = frontend_url.replace("http://", "http://www.")
                if www_url not in origins:
                    origins.append(www_url)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_origins = []
    for origin in origins:
        if origin not in seen:
            seen.add(origin)
            unique_origins.append(origin)
    
    # Regex to match localhost or any subdomain of unisynchq.com
    # More permissive pattern to catch all variants
    # This regex matches:
    # - http://localhost:PORT or http://127.0.0.1:PORT (any port)
    # - https://unisynchq.com (no subdomain)
    # - https://www.unisynchq.com (www subdomain)
    # - https://any-subdomain.unisynchq.com (any subdomain)
    origin_regex = r"^(http://localhost:\d+|http://127\.0\.0\.1:\d+|https://([a-zA-Z0-9-]+\.)*unisynchq\.com)$"
    
    # Use wildcard for development, regex for production
    if settings.ENVIRONMENT == "development":
        # More permissive in development
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Allow all in development
            allow_credentials=False,  # Can't use credentials with wildcard
            allow_methods=["*"],
            allow_headers=["*"],
            expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"],
        )
    else:
        # Production: Use BOTH explicit list AND regex for maximum compatibility
        # FastAPI uses OR logic - if either matches, origin is allowed
        app.add_middleware(
            CORSMiddleware,
            allow_origins=unique_origins,  # Explicit list for known origins
            allow_origin_regex=origin_regex,  # Regex for any subdomain variants
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
            allow_headers=["*"],
            expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"],
            max_age=3600,  # Cache preflight requests for 1 hour
        )

