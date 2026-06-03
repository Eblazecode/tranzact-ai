from fastapi import APIRouter

from .schemas import FinancialHealthSummaryResponse
from .service import get_financial_health_summary


router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.get("/health-summary", response_model=FinancialHealthSummaryResponse)
def health_summary(user_name: str) -> FinancialHealthSummaryResponse:
    return get_financial_health_summary(user_name)
