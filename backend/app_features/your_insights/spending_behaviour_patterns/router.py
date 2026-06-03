from fastapi import APIRouter

from .service import get_spending_behaviour_patterns


router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.get("/behaviour-patterns")
def behaviour_patterns(user_name: str):
    return get_spending_behaviour_patterns(user_name)
