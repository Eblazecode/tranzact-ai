from fastapi import APIRouter, Depends, HTTPException
from .service import get_spending_analysis, get_category_spending_breakdown, get_spending_trends, get_financial_leakage_analysis
from .schemas import SpendingAnalysisResponse, CategoryBreakdownResponse, SpendingTrendsResponse, LeakageAnalysisResponse

router = APIRouter(prefix="/full-spending-analysis", tags=["full-spending-analysis"])


@router.get("/{user_name}", response_model=SpendingAnalysisResponse)
async def get_spending_analysis_endpoint(user_name: str):
    """
    Get comprehensive spending analysis for a user.
    
    Returns data for:
    - Spending by category (pie chart)
    - Top 10 largest transactions (highlights)
    - Spending behavior patterns (behavior page)
    """
    try:
        analysis = get_spending_analysis(user_name)
        return SpendingAnalysisResponse(**analysis)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{user_name}/categories", response_model=CategoryBreakdownResponse)
async def get_category_breakdown_endpoint(user_name: str):
    """
    Get detailed spending breakdown by category with statistics.
    """
    try:
        breakdown = get_category_spending_breakdown(user_name)
        return CategoryBreakdownResponse(**breakdown)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{user_name}/trends", response_model=SpendingTrendsResponse)
async def get_spending_trends_endpoint(user_name: str, period: str = "monthly"):
    """
    Get spending trends over time.
    
    Query Parameters:
    - period: 'monthly', 'weekly', or 'daily' (default: monthly)
    """
    try:
        if period not in ["monthly", "weekly", "daily"]:
            raise HTTPException(status_code=400, detail="Period must be 'monthly', 'weekly', or 'daily'")
        
        trends = get_spending_trends(user_name, period)
        return SpendingTrendsResponse(**trends)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{user_name}/leakage", response_model=LeakageAnalysisResponse)
async def get_leakage_analysis_endpoint(user_name: str):
    """
    Get financial leakage analysis (non-productive spending).
    """
    try:
        leakage = get_financial_leakage_analysis(user_name)
        return LeakageAnalysisResponse(**leakage)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
