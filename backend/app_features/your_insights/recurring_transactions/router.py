from fastapi import APIRouter

from .service import get_recurring_transactions


router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.get("/recurring")
def recurring(user_name: str):
    return get_recurring_transactions(user_name)
