from fastapi import APIRouter

from .service import get_anomalies


router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.get("/anomalies")
def anomalies(user_name: str):
    return get_anomalies(user_name)
