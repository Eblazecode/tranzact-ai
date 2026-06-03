from fastapi import APIRouter

from .schemas import DetailedCategoryBreakdownResponse
from .service import get_detailed_category_breakdown


router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.get("/category-breakdown", response_model=DetailedCategoryBreakdownResponse)
def category_breakdown(user_name: str) -> DetailedCategoryBreakdownResponse:
    return get_detailed_category_breakdown(user_name)
