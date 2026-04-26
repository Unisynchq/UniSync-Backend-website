from fastapi import APIRouter, HTTPException
from app.database import supabase
from app.schemas import ActionTaskOut, ActionTaskCreate, ActionTaskUpdate
from typing import List

router = APIRouter(prefix="/api/actions", tags=["Actions"])

@router.get("/board")
async def get_action_board():
    """Get all tasks grouped by status for the board."""
    try:
        response = supabase.table("action_tasks").select("*").execute()
        
        # Group by status
        board = {
            "todo": [],
            "inProgress": [],
            "completed": []
        }
        
        for task in response.data:
            status = task.get("status", "todo")
            if status in board:
                board[status].append(task)
            else:
                board["todo"].append(task)
                
        return board
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tasks", response_model=List[ActionTaskOut])
async def get_all_tasks():
    """Get all action tasks."""
    try:
        response = supabase.table("action_tasks").select("*").order("created_at", desc=True).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tasks", response_model=ActionTaskOut)
async def create_task(task: ActionTaskCreate):
    """Create a new action task."""
    try:
        response = supabase.table("action_tasks").insert(task.model_dump()).execute()
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create task")
        return response.data[0]
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/tasks/{taskId}/move", response_model=ActionTaskOut)
async def move_task(taskId: str, update: ActionTaskUpdate):
    """Move a task to a different status."""
    try:
        response = supabase.table("action_tasks").update({"status": update.status}).eq("id", taskId).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Task not found")
        return response.data[0]
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/tasks/{taskId}")
async def delete_task(taskId: str):
    """Delete an action task."""
    try:
        response = supabase.table("action_tasks").delete().eq("id", taskId).execute()
        return {"message": "Task deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
