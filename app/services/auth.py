"""
Auth service to handle Supabase authentication
"""
from typing import Dict, Any, Optional
from app.database import supabase
from app.utils.logger import logger

class AuthService:
    """Service for managing user authentication via Supabase"""

    def signup(self, email: str, password: str) -> Dict[str, Any]:
        """
        Create a new user in Supabase
        """
        try:
            response = supabase.auth.sign_up({
                "email": email,
                "password": password,
            })
            
            if response.user:
                logger.info("User signed up successfully", {"email": email})
                return {
                    "success": True,
                    "user": response.user,
                    "message": "Signup successful. Please check your email for verification."
                }
            else:
                return {
                    "success": False,
                    "error": "Signup failed. No user returned."
                }
        except Exception as e:
            logger.error("Signup error", e, {"email": email})
            return {
                "success": False,
                "error": str(e)
            }

    def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate a user and return session tokens
        """
        try:
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password,
            })
            
            if response.user and response.session:
                logger.info("User logged in successfully", {"email": email})
                return {
                    "success": True,
                    "user": response.user,
                    "session": response.session
                }
            else:
                return {
                    "success": False,
                    "error": "Login failed. Invalid credentials."
                }
        except Exception as e:
            logger.error("Login error", e, {"email": email})
            return {
                "success": False,
                "error": "Invalid email or password"
            }

    def get_user(self, jwt: str):
        """
        Verify JWT and get user profile
        """
        try:
            response = supabase.auth.get_user(jwt)
            return response.user
        except Exception as e:
            logger.error("Token verification error", e)
            return None

# Global instance
auth_service = AuthService()
