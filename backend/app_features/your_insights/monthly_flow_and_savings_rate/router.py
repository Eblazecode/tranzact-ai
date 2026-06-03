from fastapi import APIRouter

from .schemas import MonthlyFlowResponse
from .service import get_monthly_flow


router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.get("/monthly-flow", response_model=MonthlyFlowResponse)
def monthly_flow(user_name: str) -> MonthlyFlowResponse:
    return get_monthly_flow(user_name)
