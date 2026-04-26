from fastapi import APIRouter, HTTPException
from app.schemas import AILiveAnalyzeRequest, AILiveAnalyzeResponse, ErrorResponse
from app.services.ai import ai_service
from app.utils.logger import logger

router = APIRouter()

@router.post("/live", response_model=AILiveAnalyzeResponse, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def analyze_live_input(request: AILiveAnalyzeRequest):
    """
    Analyzes live form input for quality and AI-generation indicators.
    This endpoint is intended to be called with debounced input from the frontend.
    """
    try:
        logger.info(f"Live analysis requested for form {request.form_id}, question {request.question_id}")
        
        # We don't perform authentication here because this is a public-facing form feature
        # (similar to how anyone can view a form without logging in)
        
        result = await ai_service.analyze_live_input(request)
        return result
        
    except ValueError as e:
        logger.error(f"Live analysis value error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Live analysis unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal AI service error")
