from fastapi import APIRouter, HTTPException

from .schemas import CategoryPredictionRequest, CategoryPredictionResponse
from .service import get_category_prediction


router = APIRouter(prefix="/api/predict", tags=["predictions"])


@router.post("/category", response_model=CategoryPredictionResponse)
def category_prediction(payload: CategoryPredictionRequest):
    try:
        return CategoryPredictionResponse(categories=get_category_prediction(payload))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
