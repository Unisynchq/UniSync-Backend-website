from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks
from app.schemas import FormPublicOut, ResponseSubmitRequest
from app.services.forms import form_service
from app.services.rate_limit import rate_limit_service
from app.utils.logger import logger

router = APIRouter()

@router.get("/{slug}", response_model=FormPublicOut)
def get_public_form(slug: str):
    """
    Get a public form and its questions by slug.
    """
    form = form_service.get_public_form_by_slug(slug)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found or not published")
    return form

@router.post("/{slug}/submit")
def submit_form_response(request: Request, slug: str, body: ResponseSubmitRequest, background_tasks: BackgroundTasks):
    """
    Submit a form response anonymously.
    Rate limited according to global settings.
    """
    allowed, remaining, reset_time = rate_limit_service.check_rate_limit(request)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please try again later.",
            headers={"X-RateLimit-Reset": reset_time.isoformat()}
        )
    
    # First verify form exists and is published
    form = form_service.get_public_form_by_slug(slug)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found or not published")
    
    # Ensure form_id in body matches the form found by slug
    if body.form_id != form["id"]:
        raise HTTPException(status_code=400, detail="Invalid form ID for this slug")
    
    result = form_service.submit_response(form["id"], body.answers, background_tasks)
    return result
