from typing import Literal

from fastapi import APIRouter

from .service import get_transfers_out


router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.get("/transfers-out")
def transfers_out(
    user_name: str,
    filter_by: Literal["month", "week", "year"] = "month",
    period_value: str = "all",
    top_n: int = 10,
):
    return get_transfers_out(user_name, filter_by, period_value, top_n)
