from fastapi import APIRouter, HTTPException
from app.database import supabase
from app.schemas import TrendDataPointOut
from typing import List

router = APIRouter(prefix="/api/trends", tags=["Trends"])

@router.get("/historical", response_model=List[TrendDataPointOut])
async def get_historical_trends():
    """Get all historical trend data points."""
    try:
        response = supabase.table("trend_data_points").select("*").eq("period_type", "daily").order("date").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/weekly", response_model=List[TrendDataPointOut])
async def get_weekly_trends():
    """Get weekly aggregated trend data points."""
    try:
        response = supabase.table("trend_data_points").select("*").eq("period_type", "weekly").order("date").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monthly", response_model=List[TrendDataPointOut])
async def get_monthly_trends():
    """Get monthly aggregated trend data points."""
    try:
        response = supabase.table("trend_data_points").select("*").eq("period_type", "monthly").order("date").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
