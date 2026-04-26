from fastapi import APIRouter, HTTPException
from app.database import supabase
from app.schemas import DashboardStatsOut
from typing import List, Dict, Any
from collections import defaultdict
from datetime import datetime

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/stats", response_model=DashboardStatsOut)
async def get_dashboard_stats():
    """Get high-level dashboard statistics from feedback items."""
    try:
        response = supabase.table("feedback_items").select("score, sem_type").execute()
        items = response.data
        
        total_feedback = len(items)
        positive_count = sum(1 for item in items if item.get("sem_type", "").lower() == "positive")
        average_score = sum(item.get("score", 0) for item in items) / total_feedback if total_feedback > 0 else 0.0
        
        return DashboardStatsOut(
            totalFeedback=total_feedback,
            positiveCount=positive_count,
            averageScore=round(average_score, 1)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sentiment-timeline")
async def get_sentiment_timeline():
    """Get sentiment timeline aggregated by date."""
    try:
        response = supabase.table("feedback_items").select("created_at, sem_type").execute()
        items = response.data
        
        # Aggregate by date
        timeline = defaultdict(lambda: {"date": "", "positive": 0, "neutral": 0, "negative": 0})
        
        for item in items:
            if not item.get("created_at"):
                continue
                
            # Parse date and format as YYYY-MM-DD
            try:
                date_str = item["created_at"].split("T")[0]
            except Exception:
                continue
                
            timeline[date_str]["date"] = date_str
            sem_type = item.get("sem_type", "").lower()
            
            if sem_type == "positive":
                timeline[date_str]["positive"] += 1
            elif sem_type == "negative":
                timeline[date_str]["negative"] += 1
            else:
                timeline[date_str]["neutral"] += 1
                
        # Sort by date
        result = list(timeline.values())
        result.sort(key=lambda x: x["date"])
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
