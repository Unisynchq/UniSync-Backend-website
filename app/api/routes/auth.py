"""
Authentication API routes
"""
from fastapi import APIRouter, HTTPException, Depends
from app.schemas import AuthRequest, AuthResponse, UserOut
from app.services.auth import auth_service
from app.utils.logger import logger

router = APIRouter()

@router.post("/signup", response_model=AuthResponse)
async def signup(body: AuthRequest):
    """Register a new user"""
    result = auth_service.signup(body.email, body.password)
    
    if not result["success"]:
        return AuthResponse(
            success=False,
            error=result["error"]
        )
    
    user_data = result["user"]
    return AuthResponse(
        success=True,
        message=result["message"],
        user=UserOut(
            id=user_data.id,
            email=user_data.email,
            created_at=str(user_data.created_at)
        )
    )

from app.api.deps import get_current_user

@router.post("/login", response_model=AuthResponse)
async def login(body: AuthRequest):
    """Authenticate user and return session"""
    result = auth_service.login(body.email, body.password)
    
    if not result["success"]:
        return AuthResponse(
            success=False,
            error=result["error"]
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
async def get_me(current_user: UserOut = Depends(get_current_user)):
    """Get current user profile from JWT"""
    return current_user
