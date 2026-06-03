from typing import Literal

from fastapi import APIRouter

from .service import get_filtered_pie_chart


router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.get("/pie-chart")
def pie_chart(user_name: str, filter_by: Literal["month", "week"] = "month", period_value: str = "all"):
    return get_filtered_pie_chart(user_name, filter_by, period_value)
