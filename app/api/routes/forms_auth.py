from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.api.deps import get_current_user
from app.schemas import FormCreate, FormUpdate, FormOut, DashboardStats, UserOut
from app.services.forms import form_service
from app.utils.logger import logger

router = APIRouter()

@router.get("/", response_model=List[FormOut])
def list_forms(current_user: UserOut = Depends(get_current_user)):
    """List all forms owned by the current user"""
    forms = form_service.list_user_forms(current_user.id)
    return forms

@router.post("/", response_model=FormOut, status_code=status.HTTP_201_CREATED)
def create_form(body: FormCreate, current_user: UserOut = Depends(get_current_user)):
    """Create a new form"""
    form = form_service.create_form(current_user.id, body.model_dump())
    return form

@router.get("/stats", response_model=DashboardStats)
def get_stats(current_user: UserOut = Depends(get_current_user)):
    """Get dashboard statistics for the current user"""
    stats = form_service.get_dashboard_stats(current_user.id)
    return stats

@router.get("/{form_id}", response_model=FormOut)
def get_form(form_id: str, current_user: UserOut = Depends(get_current_user)):
    """Get details of a specific form"""
    form = form_service.get_user_form(current_user.id, form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found or access denied")
    return form

@router.patch("/{form_id}", response_model=FormOut)
def update_form(form_id: str, body: FormUpdate, current_user: UserOut = Depends(get_current_user)):
    """Update form settings"""
    form = form_service.update_form(current_user.id, form_id, body.model_dump(exclude_unset=True))
    if not form:
        raise HTTPException(status_code=404, detail="Form not found or access denied")
    return form

@router.delete("/{form_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_form(form_id: str, current_user: UserOut = Depends(get_current_user)):
    """Delete a form"""
    success = form_service.delete_form(current_user.id, form_id)
    if not success:
        raise HTTPException(status_code=404, detail="Form not found or access denied")
    return None
