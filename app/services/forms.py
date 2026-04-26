from typing import Optional, Dict, Any, List
from app.database import supabase
from app.utils.logger import logger
from postgrest.exceptions import APIError

class FormService:
    """Service for managing forms and submissions"""

    def get_public_form_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a public form and its questions by slug.
        Only returns if the form is published.
        """
        try:
            # Fetch form
            form_result = supabase.table("forms") \
                .select("id, slug, title, description, is_published, is_ai_enabled") \
                .eq("slug", slug) \
                .eq("is_published", True) \
                .execute()
            
            if not form_result.data:
                return None
            
            form = form_result.data[0]
            
            # Fetch questions for this form
            questions_result = supabase.table("questions") \
                .select("id, text, type, order") \
                .eq("form_id", form["id"]) \
                .order("order") \
                .execute()
            
            form["questions"] = questions_result.data if questions_result.data else []
            return form
            
        except APIError as e:
            logger.error(f"Database error fetching form by slug {slug}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching form by slug {slug}", e)
            raise

    def list_user_forms(self, user_id: str) -> List[Dict[str, Any]]:
        """List all forms owned by a user"""
        try:
            result = supabase.table("forms") \
                .select("id, slug, title, description, is_published, is_ai_enabled, created_at") \
                .eq("owner_id", user_id) \
                .order("created_at", descending=True) \
                .execute()
            return result.data
        except Exception as e:
            logger.error(f"Error listing forms for user {user_id}", e)
            raise

    def get_user_form(self, user_id: str, form_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific form owned by the user, including its questions"""
        try:
            # Fetch form
            form_result = supabase.table("forms") \
                .select("*") \
                .eq("id", form_id) \
                .eq("owner_id", user_id) \
                .execute()
            
            if not form_result.data:
                return None
            
            form = form_result.data[0]
            
            # Fetch questions
            questions_result = supabase.table("questions") \
                .select("*") \
                .eq("form_id", form_id) \
                .order("order") \
                .execute()
            
            form["questions"] = questions_result.data
            return form
        except Exception as e:
            logger.error(f"Error getting form {form_id} for user {user_id}", e)
            raise

    def create_form(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new form for a user"""
        try:
            # Generate slug if not provided
            if not data.get("slug"):
                import uuid
                data["slug"] = f"form-{uuid.uuid4().hex[:8]}"
            
            form_data = {
                "owner_id": user_id,
                "title": data["title"],
                "description": data.get("description"),
                "slug": data["slug"],
                "is_published": False,
                "is_ai_enabled": data.get("is_ai_enabled", True)
            }
            
            result = supabase.table("forms").insert(form_data).execute()
            return result.data[0]
        except Exception as e:
            logger.error(f"Error creating form for user {user_id}", e)
            raise

    def update_form(self, user_id: str, form_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a form owned by the user"""
        try:
            # Only update allowed fields
            update_data = {}
            for field in ["title", "description", "is_published", "is_ai_enabled"]:
                if field in data and data[field] is not None:
                    update_data[field] = data[field]
            
            if not update_data:
                return self.get_user_form(user_id, form_id)

            result = supabase.table("forms") \
                .update(update_data) \
                .eq("id", form_id) \
                .eq("owner_id", user_id) \
                .execute()
            
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error updating form {form_id} for user {user_id}", e)
            raise

    def delete_form(self, user_id: str, form_id: str) -> bool:
        """Delete a form owned by the user"""
        try:
            result = supabase.table("forms") \
                .delete() \
                .eq("id", form_id) \
                .eq("owner_id", user_id) \
                .execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error deleting form {form_id} for user {user_id}", e)
            raise

    def get_dashboard_stats(self, user_id: str) -> Dict[str, Any]:
        """Get dashboard statistics for a user"""
        try:
            # Get forms count
            forms_result = supabase.table("forms").select("id, is_published").eq("owner_id", user_id).execute()
            total_forms = len(forms_result.data)
            published_forms = len([f for f in forms_result.data if f.get("is_published")])
            
            # Get total responses across all user's forms
            # We first get the list of form IDs
            form_ids = [f["id"] for f in forms_result.data]
            
            total_responses = 0
            recent_responses = 0
            
            if form_ids:
                responses_result = supabase.table("responses") \
                    .select("id, created_at") \
                    .in_("form_id", form_ids) \
                    .execute()
                
                total_responses = len(responses_result.data)
                
                # Simple recent count (last 24h)
                from datetime import datetime, timedelta
                day_ago = datetime.utcnow() - timedelta(days=1)
                recent_responses = len([
                    r for r in responses_result.data 
                    if datetime.fromisoformat(r["created_at"].replace("Z", "+00:00")) > day_ago.replace(tzinfo=None)
                ])

            return {
                "total_forms": total_forms,
                "total_responses": total_responses,
                "published_forms_count": published_forms,
                "recent_responses_count": recent_responses
            }
        except Exception as e:
            logger.error(f"Error getting dashboard stats for user {user_id}", e)
            raise
    def submit_response(self, form_id: str, answers: Dict[str, Any], background_tasks: Optional[Any] = None) -> Dict[str, Any]:
        """Submit a response to a form anonymously"""
        try:
            response_data = {
                "form_id": form_id,
                "answers": answers
            }
            
            result = supabase.table("responses").insert(response_data).execute()
            
            if result.data:
                response_id = result.data[0].get("id")
                logger.info(f"New response submitted for form {form_id}")
                
                # Trigger AI Analysis in the background if possible
                if background_tasks:
                    try:
                        from app.services.ai import ai_service
                        # Fetch form title and questions for AI context
                        form = self.get_public_form_by_slug_by_id(form_id)
                        if form:
                            # 1. Establish pending state safely to DB before async dispatch
                            ai_service.create_pending_analysis(response_id)
                            
                            # 2. Dispatch LLM logic sequentially to the thread pool
                            background_tasks.add_task(
                                ai_service.analyze_submission,
                                response_id,
                                form["title"],
                                form["questions"],
                                answers
                            )
                    except Exception as e:
                        logger.error(f"Failed to enqueue AI analysis: {str(e)}")

                return {
                    "success": True,
                    "message": "Response submitted successfully",
                    "response_id": response_id
                }
            else:
                raise Exception("Failed to save response in database")
                
        except APIError as e:
            logger.error(f"Database error submitting response for form {form_id}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error submitting response for form {form_id}", e)
            raise

    def get_public_form_by_slug_by_id(self, form_id: str) -> Optional[Dict[str, Any]]:
        """Helper to get form and questions for AI context"""
        try:
            form_result = supabase.table("forms").select("id, title").eq("id", form_id).execute()
            if not form_result.data: return None
            form = form_result.data[0]
            questions_result = supabase.table("questions").select("id, text").eq("form_id", form_id).execute()
            form["questions"] = questions_result.data
            return form
        except:
            return None

    # --- Questions CRUD ---

    def add_question(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a question to a form owned by the user"""
        try:
            # Verify form ownership
            form = self.get_user_form(user_id, data["form_id"])
            if not form:
                raise Exception("Form not found or access denied")

            question_data = {
                "form_id": data["form_id"],
                "text": data["text"],
                "type": data["type"],
                "order": data["order"],
                "options": data.get("options")
            }
            
            result = supabase.table("questions").insert(question_data).execute()
            return result.data[0]
        except Exception as e:
            logger.error(f"Error adding question to form {data.get('form_id')}", e)
            raise

    def update_question(self, user_id: str, question_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a question in a form owned by the user"""
        try:
            # We need to verify ownership via form_id
            # First get the question to find its form_id
            q_result = supabase.table("questions").select("form_id").eq("id", question_id).execute()
            if not q_result.data:
                return None
            
            form_id = q_result.data[0]["form_id"]
            form = self.get_user_form(user_id, form_id)
            if not form:
                raise Exception("Access denied to question's form")

            update_data = {}
            for field in ["text", "type", "order", "options"]:
                if field in data and data[field] is not None:
                    update_data[field] = data[field]
            
            if not update_data:
                return supabase.table("questions").select("*").eq("id", question_id).execute().data[0]

            result = supabase.table("questions").update(update_data).eq("id", question_id).execute()
            return result.data[0]
        except Exception as e:
            logger.error(f"Error updating question {question_id}", e)
            raise

    def delete_question(self, user_id: str, question_id: str) -> bool:
        """Delete a question from a form owned by the user and clean up orphaned responses"""
        try:
            q_result = supabase.table("questions").select("form_id").eq("id", question_id).execute()
            if not q_result.data:
                return False
            
            form_id = q_result.data[0]["form_id"]
            form = self.get_user_form(user_id, form_id)
            if not form:
                raise Exception("Access denied to question's form")

            # First, clean up orphaned answers in the responses table
            # Supabase Python SDK doesn't natively support deep JSONB mutation yet
            # So we fetch all responses for this form_id, strip the question_id key, and update
            responses_result = supabase.table("responses").select("id, answers").eq("form_id", form_id).execute()
            
            if responses_result.data:
                for resp in responses_result.data:
                    answers = resp.get("answers", {})
                    if question_id in answers:
                        del answers[question_id]
                        supabase.table("responses").update({"answers": answers}).eq("id", resp["id"]).execute()

            # Now safely delete the question
            result = supabase.table("questions").delete().eq("id", question_id).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error deleting question {question_id}", e)
            raise

# Global instance
form_service = FormService()
