from fastapi import APIRouter
from fastapi import HTTPException

from .schemas import MonthlyPredictionRequest, MonthlyPredictionResponse
from .service import get_monthly_prediction


router = APIRouter(prefix="/api/predict", tags=["predictions"])


@router.post("/monthly", response_model=MonthlyPredictionResponse)
def monthly_prediction(payload: MonthlyPredictionRequest):
    try:
        return get_monthly_prediction(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
