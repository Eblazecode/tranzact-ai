from fastapi import APIRouter

from .service import get_balance_trajectory


router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.get("/balance-trajectory")
def balance_trajectory(user_name: str):
    return get_balance_trajectory(user_name)
