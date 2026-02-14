from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import get_current_user
from app.schemas import QuestionCreate, QuestionUpdate, QuestionOut, UserOut
from app.services.forms import form_service
from app.utils.logger import logger

router = APIRouter()

@router.post("/", response_model=QuestionOut, status_code=status.HTTP_201_CREATED)
async def add_question(body: QuestionCreate, current_user: UserOut = Depends(get_current_user)):
    """Add a question to a form"""
    try:
        question = form_service.add_question(current_user.id, body.model_dump())
        return question
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{question_id}", response_model=QuestionOut)
async def update_question(question_id: str, body: QuestionUpdate, current_user: UserOut = Depends(get_current_user)):
    """Update a question's content or settings"""
    try:
        question = form_service.update_question(current_user.id, question_id, body.model_dump(exclude_unset=True))
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        return question
    except Exception as e:
        if "access denied" in str(e).lower():
            raise HTTPException(status_code=403, detail="Access denied")
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(question_id: str, current_user: UserOut = Depends(get_current_user)):
    """Remove a question from its form"""
    try:
        success = form_service.delete_question(current_user.id, question_id)
        if not success:
            raise HTTPException(status_code=404, detail="Question not found")
        return None
    except Exception as e:
        if "access denied" in str(e).lower():
            raise HTTPException(status_code=403, detail="Access denied")
        raise HTTPException(status_code=400, detail=str(e))
