"""
Authentication API routes
"""
from fastapi import APIRouter, HTTPException, Depends, Request, Response
from app.schemas import AuthRequest, AuthResponse, UserOut
from app.services.auth import auth_service
from app.services.rate_limit import rate_limit_service
from app.utils.logger import logger
from app.config import settings
from app.api.deps import get_current_user

router = APIRouter()

@router.post("/signup", response_model=AuthResponse)
def signup(request: Request, body: AuthRequest):
    """Register a new user"""
    allowed, remaining, reset_time = rate_limit_service.check_rate_limit(request)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please try again later.",
            headers={
                "X-RateLimit-Limit": str(settings.RATE_LIMIT_REQUESTS),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": reset_time.isoformat()
            }
        )

    result = auth_service.signup(body.email, body.password)
    
    if not result["success"]:
        return AuthResponse(
            success=False,
            error=result.get("error", "Signup failed")
        )
    
    user_data = result["user"]
    return AuthResponse(
        success=True,
        message=result.get("message", "Signup successful"),
        user=UserOut(
            id=user_data.id,
            email=user_data.email,
            created_at=str(user_data.created_at)
        )
    )

@router.post("/login", response_model=AuthResponse)
def login(request: Request, body: AuthRequest):
    """Authenticate user and return session"""
    allowed, remaining, reset_time = rate_limit_service.check_rate_limit(request)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Too many login attempts. Please try again later.",
            headers={
                "X-RateLimit-Limit": str(settings.RATE_LIMIT_REQUESTS),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": reset_time.isoformat()
            }
        )

    result = auth_service.login(body.email, body.password)
    
    if not result["success"]:
        return AuthResponse(
            success=False,
            error=result.get("error", "Login failed")
        )
    
    user_data = result["user"]
    session = result["session"]
    
    return AuthResponse(
        success=True,
        user=UserOut(
            id=user_data.id,
            email=user_data.email,
            created_at=str(user_data.created_at)
        ),
        access_token=session.access_token,
        refresh_token=session.refresh_token
    )

@router.get("/me", response_model=UserOut)
def get_me(current_user: UserOut = Depends(get_current_user)):
    """Get current user profile from JWT"""
    return current_user
