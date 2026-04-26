from fastapi import APIRouter, HTTPException, Query
from app.database import supabase
from app.schemas import FeedbackItemOut
from typing import List, Optional

router = APIRouter(prefix="/api/feedback", tags=["Feedback"])

@router.get("", response_model=List[FeedbackItemOut])
async def get_feedback_items(
    semType: Optional[str] = None,
    section: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    is_reviewed: Optional[bool] = None
):
    """Get feedback items with optional filtering."""
    try:
        query = supabase.table("feedback_items").select("*")
        
        # Apply filters if provided
        if semType:
            query = query.ilike("sem_type", f"%{semType}%")
        if section:
            query = query.ilike("section", f"%{section}%")
        if status:
            query = query.eq("status", status)
        if is_reviewed is not None:
            query = query.eq("is_reviewed", is_reviewed)
            
        # For category array, it's a bit tricky in PostgREST, we can use contains operator
        if category:
            # PostgREST array contains: cs.{"value"}
            query = query.contains("categories", [category])
            
        response = query.execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export")
async def export_feedback():
    """Export feedback data as CSV (mocked for now, returns JSON array)."""
    try:
        response = supabase.table("feedback_items").select("*").execute()
        return {"data": response.data, "message": "Export ready"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{id}", response_model=FeedbackItemOut)
async def get_feedback_item(id: str):
    """Get a specific feedback item by ID."""
    try:
        response = supabase.table("feedback_items").select("*").eq("id", id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Feedback not found")
        return response.data[0]
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reviewed")
async def mark_feedback_reviewed(item_ids: List[str]):
    """Mark multiple feedback items as reviewed."""
    try:
        # Supabase Python client doesn't support an IN update directly in a clean way,
        # so we iterate. For larger batches, an RPC is recommended.
        results = []
        for id in item_ids:
            res = supabase.table("feedback_items").update({"is_reviewed": True, "status": "reviewed"}).eq("id", id).execute()
            if res.data:
                results.append(res.data[0])
                
        return {"message": f"Successfully reviewed {len(results)} items", "updated": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
