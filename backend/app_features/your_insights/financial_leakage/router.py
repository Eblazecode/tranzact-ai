from fastapi import APIRouter

from .service import get_financial_leakage


router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.get("/financial-leakage")
def financial_leakage(user_name: str):
    return get_financial_leakage(user_name)
