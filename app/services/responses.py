from typing import Optional, Dict, Any, List
from app.database import supabase
from app.utils.logger import logger

class ResponseService:
    """Service for retrieving responses and AI analysis"""

    def get_form_responses(self, user_id: str, form_id: str) -> List[Dict[str, Any]]:
        """
        List all responses for a specific form owned by the user.
        Relies on RLS policies to ensure user can only see their own form's responses.
        """
        try:
            # Multi-line chaining in Python requires backslashes or parentheses
            result = supabase.table("responses") \
                .select("id, created_at, answers, metadata") \
                .eq("form_id", form_id) \
                .order("created_at", descending=True) \
                .execute()
            
            # Note: Embedding ai_analysis status requires it to be a single object or related.
            # Postgrest allows embedding: .select("*, ai_analysis(*)")
            # Let's keep it simple first and fetch basic response info.
            return result.data
        except Exception as e:
            logger.error(f"Error listing responses for form {form_id}: {str(e)}")
            raise

    def get_response_detail(self, user_id: str, response_id: str) -> Optional[Dict[str, Any]]:
        """
        Get full details of a single response.
        """
        try:
            result = supabase.table("responses") \
                .select("*") \
                .eq("id", response_id) \
                .execute()
            
            if not result.data:
                return None
            
            response = result.data[0]
            
            # Separately fetch analysis to keep code clean
            analysis = self.get_response_analysis(user_id, response_id)
            response["ai_analysis"] = analysis
            
            return response
        except Exception as e:
            logger.error(f"Error getting response {response_id}: {str(e)}")
            raise

    def get_response_analysis(self, user_id: str, response_id: str) -> Optional[Dict[str, Any]]:
        """
        Get just the AI analysis for a response.
        """
        try:
            result = supabase.table("ai_analysis") \
                .select("*") \
                .eq("response_id", response_id) \
                .execute()
            
            if not result.data:
                return None
            
            return result.data[0]
        except Exception as e:
            logger.error(f"Error getting analysis for response {response_id}: {str(e)}")
            raise

response_service = ResponseService()
