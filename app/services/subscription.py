"""
Subscription business logic
"""
from typing import Optional, Dict, Any
from postgrest.exceptions import APIError
from app.database import supabase
from app.utils.logger import logger


class SubscriptionService:
    """Subscription service for managing email subscriptions"""
    
    def create_subscription(
        self,
        email: str,
        source: str = "landing_hero"
    ) -> Dict[str, Any]:
        """
        Create a new subscription
        
        Uses INSERT with conflict handling to prevent race conditions.
        Attempts insert directly and handles unique constraint violations.
        
        Args:
            email: Subscriber email address
            source: Source of subscription
            
        Returns:
            Dictionary with subscription data or error information
        """
        try:
            # Create new subscription - let database handle uniqueness
            # Remove created_at/updated_at - let database defaults handle it
            subscription_data = {
                "email": email,
                "source": source,
                "status": "pending"
            }
            
            result = supabase.table("subscriptions").insert(subscription_data).execute()
            
            if result.data:
                subscription = result.data[0]
                logger.info("New subscription created", {
                    "email": email[:5] + "***",
                    "source": source,
                    "subscription_id": subscription.get("id")
                })
                
                # Note: Email sending will be handled by FastAPI BackgroundTasks
                # This keeps the subscription creation fast and non-blocking
                
                return {
                    "success": True,
                    "message": "Thank you for your interest! We'll be in touch soon.",
                    "subscription": subscription
                }
            else:
                raise Exception("Failed to create subscription in database")
                
        except APIError as e:
            # Check if error is due to unique constraint violation (duplicate email)
            error_dict = e.args[0] if e.args else {}
            error_code = error_dict.get("code", "")
            error_message = error_dict.get("message", "")
            
            # PostgreSQL unique constraint violation code: 23505
            # PostgREST may return different error formats, check for common patterns
            if "23505" in str(error_code) or "unique" in error_message.lower() or "duplicate" in error_message.lower():
                logger.info("Duplicate subscription attempt (caught by unique constraint)", {
                    "email": email[:5] + "***",
                    "source": source
                })
                return {
                    "success": True,
                    "message": "This email is already registered. We'll be in touch soon!",
                    "is_duplicate": True
                }
            
            # Re-raise if it's a different database error
            logger.error("Database error creating subscription", e, {
                "email": email[:5] + "***",
                "source": source,
                "error_code": error_code
            })
            raise
            
        except Exception as e:
            logger.error("Error creating subscription", e, {
                "email": email[:5] + "***",
                "source": source
            })
            raise
    
    def get_subscription_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get subscription by email address
        
        Args:
            email: Email address to search for
            
        Returns:
            Subscription data if found, None otherwise
        """
        try:
            result = supabase.table("subscriptions").select("*").eq("email", email).execute()
            if result.data:
                return result.data[0]
            return None
        except APIError as e:
            # Re-raise database connection errors - don't silently fail
            logger.error("Database error fetching subscription", e, {
                "email": email[:5] + "***",
                "error_code": e.args[0].get("code", "") if e.args else ""
            })
            raise
        except Exception as e:
            logger.error("Error fetching subscription", e, {
                "email": email[:5] + "***"
            })
            raise


# Global subscription service instance
subscription_service = SubscriptionService()

