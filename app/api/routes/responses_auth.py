from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.api.deps import get_current_user
from app.schemas import ResponseOut, AIAnalysisOut, UserOut
from app.services.responses import response_service
from app.utils.logger import logger

router = APIRouter()

@router.get("/form/{form_id}", response_model=List[ResponseOut])
async def list_form_responses(form_id: str, current_user: UserOut = Depends(get_current_user)):
    """List all responses for a specific form"""
    # Note: RLS handles ownership, so if user doesn't own form, they get empty list.
    responses = response_service.get_form_responses(current_user.id, form_id)
    return responses

@router.get("/detail/{response_id}", response_model=ResponseOut)
async def get_response_detail(response_id: str, current_user: UserOut = Depends(get_current_user)):
    """Get full detail of a specific response including AI analysis"""
    response = response_service.get_response_detail(current_user.id, response_id)
    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Response not found or access denied"
        )
    return response

@router.get("/analysis/{response_id}", response_model=AIAnalysisOut)
async def get_response_analysis(response_id: str, current_user: UserOut = Depends(get_current_user)):
    """Get only the AI analysis for a response"""
    analysis = response_service.get_response_analysis(current_user.id, response_id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Analysis not found or still processing"
        )
    return analysis
