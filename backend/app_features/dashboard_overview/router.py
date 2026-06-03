from fastapi import APIRouter

from .schemas import DashboardOverviewResponse
from .service import get_dashboard_overview


router = APIRouter(prefix="/api", tags=["dashboard-overview"])


@router.get("/dashboard-overview", response_model=DashboardOverviewResponse)
def dashboard_overview(user_name: str) -> DashboardOverviewResponse:
    return DashboardOverviewResponse(**get_dashboard_overview(user_name))
