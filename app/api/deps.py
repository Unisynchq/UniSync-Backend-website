from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.auth import auth_service
from app.schemas import UserOut

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserOut:
    """
    Dependency to get the currently authenticated user.
    Verifies the JWT token against Supabase.
    """
    token = credentials.credentials
    user = auth_service.get_user(token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return UserOut(
        id=user.id,
        email=user.email,
        created_at=str(user.created_at)
    )
