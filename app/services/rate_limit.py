"""
Rate limiting service using slowapi
"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from datetime import datetime, timedelta
from typing import Dict, Tuple
from app.config import settings


# In-memory rate limit store (for development)
# In production, use Redis with slowapi's Redis backend
_rate_limit_store: Dict[str, Dict] = {}


class RateLimitService:
    """Rate limiting service"""
    
    def __init__(self):
        self.max_requests = settings.RATE_LIMIT_REQUESTS
        self.window_minutes = settings.RATE_LIMIT_WINDOW_MINUTES
        self.window_ms = self.window_minutes * 60 * 1000
    
    def get_client_ip(self, request: Request) -> str:
        """
        Extract client IP from request
        
        Args:
            request: FastAPI request object
            
        Returns:
            Client IP address
        """
        # Check various headers for IP (for proxies/load balancers)
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        cf_connecting_ip = request.headers.get("cf-connecting-ip")
        if cf_connecting_ip:
            return cf_connecting_ip
        
        # Fallback to direct client IP
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def check_rate_limit(self, request: Request) -> Tuple[bool, int, datetime]:
        """
        Check if request is within rate limit
        
        Args:
            request: FastAPI request object
            
        Returns:
            Tuple of (allowed, remaining, reset_time)
        """
        ip = self.get_client_ip(request)
        key = f"rate_limit:{ip}"
        now = datetime.utcnow()
        
        # Get or create rate limit record
        record = _rate_limit_store.get(key)
        
        if not record or now > record["reset_time"]:
            # New window - reset counter
            reset_time = now + timedelta(minutes=self.window_minutes)
            _rate_limit_store[key] = {
                "count": 1,
                "reset_time": reset_time
            }
            
            # Cleanup old entries periodically
            self._cleanup_old_entries()
            
            return True, self.max_requests - 1, reset_time
        
        if record["count"] >= self.max_requests:
            # Rate limit exceeded
            return False, 0, record["reset_time"]
        
        # Increment counter
        record["count"] += 1
        return True, self.max_requests - record["count"], record["reset_time"]
    
    def _cleanup_old_entries(self):
        """Remove expired rate limit entries"""
        if len(_rate_limit_store) > 1000:
            now = datetime.utcnow()
            expired_keys = [
                key for key, value in _rate_limit_store.items()
                if now > value["reset_time"]
            ]
            for key in expired_keys:
                _rate_limit_store.pop(key, None)


# Global rate limit service instance
rate_limit_service = RateLimitService()

