from fastapi import APIRouter

from .service import get_dashboard_payload


router = APIRouter(prefix="/api", tags=["dashboard"])


@router.get("/dashboard")
def dashboard(user_name: str):
    return get_dashboard_payload(user_name)
