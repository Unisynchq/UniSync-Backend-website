import google.generativeai as genai
import json
from typing import Dict, Any, Optional
from app.config import settings
from app.database import supabase
from app.utils.logger import logger

class AIService:
    """Service for processing form submissions using Gemini AI"""
    
    def __init__(self):
        self.api_key = settings.GOOGLE_API_KEY
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            self.model = None
            logger.warning("GOOGLE_API_KEY not set. AI features will be disabled.")

    async def analyze_submission(self, response_id: str, form_title: str, questions: list, answers: Dict[str, Any]):
        """
        Analyze a form submission in the background and store the result.
        """
        if not self.model:
            logger.error("AI Service not configured (missing API key)")
            return

        try:
            # Prepare contextual data for the prompt
            context = []
            for q in questions:
                answer = answers.get(q["id"], "No answer provided")
                context.append(f"Question: {q['text']}\nAnswer: {answer}")
            
            prompt = f"""
            Analyze the following form submission for the form titled "{form_title}".
            Provide a structured analysis in JSON format including:
            - sentiment: (positive, neutral, or negative)
            - summary: A concise summary of the responder's feedback.
            - key_insights: A list of 2-3 most important points.
            - flagged: boolean indicating if the response needs urgent admin attention.

            Submission Data:
            {chr(10).join(context)}
            
            Return ONLY the valid JSON object.
            """

            response = self.model.generate_content(prompt)
            
            # Clean up the response text if Gemini adds markdown blocks
            text = response.text.strip()
            if text.startswith("```json"):
                text = text.replace("```json", "", 1).replace("```", "", 1).strip()
            elif text.startswith("```"):
                text = text.replace("```", "", 1).replace("```", "", 1).strip()

            analysis_result = json.loads(text)
            
            # Store in database
            supabase.table("ai_analysis").insert({
                "response_id": response_id,
                "raw_analysis": analysis_result,
                "status": "completed"
            }).execute()
            
            logger.info(f"AI analysis completed for response {response_id}")

        except Exception as e:
            logger.error(f"Error in AI analysis for response {response_id}: {str(e)}")
            # Record failure
            try:
                supabase.table("ai_analysis").insert({
                    "response_id": response_id,
                    "status": "failed",
                    "error_log": str(e)
                }).execute()
            except:
                pass

ai_service = AIService()
