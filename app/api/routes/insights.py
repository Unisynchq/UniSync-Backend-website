from fastapi import APIRouter, HTTPException
from app.database import supabase
from app.schemas import CategoryInsightOut
from typing import Dict, Any

router = APIRouter(prefix="/api/insights", tags=["Insights"])

@router.get("/category/{categoryId}", response_model=CategoryInsightOut)
async def get_category_insight(categoryId: str):
    """Get AI generated insights for a specific category."""
    try:
        response = supabase.table("category_insights").select("*").eq("category_name", categoryId).execute()
        if not response.data:
            # Return empty/mock structure if not found for MVP
            return CategoryInsightOut(
                id=categoryId,
                category_name=categoryId,
                insights=[],
                themes=[],
                actionable=[],
                date_generated="2026-01-01T00:00:00Z"
            )
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/section-comparison/{categoryId}")
async def get_section_comparison(categoryId: str):
    """Get section comparison data for a category."""
    try:
        # Currently mocked as we don't have a dedicated table for this.
        # Ideally, we would aggregate feedback scores grouped by section where categories contains categoryId.
        response = supabase.table("feedback_items").select("section, score").contains("categories", [categoryId]).execute()
        
        # Aggregate scores by section
        sections: Dict[str, dict] = {}
        for item in response.data:
            sec = item.get("section", "General")
            if not sec:
                sec = "General"
            if sec not in sections:
                sections[sec] = {"total": 0, "count": 0}
            sections[sec]["total"] += item.get("score", 0)
            sections[sec]["count"] += 1
            
        result = [
            {"section": sec, "averageScore": round(data["total"] / data["count"], 1)}
            for sec, data in sections.items()
        ]
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/topic-sentiment/{categoryId}")
async def get_topic_sentiment(categoryId: str):
    """Get topic sentiment breakdown for a category."""
    try:
        # Mocked/aggregated from feedback items
        response = supabase.table("feedback_items").select("sem_type").contains("categories", [categoryId]).execute()
        
        counts = {"Positive": 0, "Neutral": 0, "Negative": 0}
        for item in response.data:
            sem_type = item.get("sem_type")
            if sem_type in counts:
                counts[sem_type] += 1
                
        return [
            {"topic": "General Sentiment", "positive": counts["Positive"], "neutral": counts["Neutral"], "negative": counts["Negative"]}
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
