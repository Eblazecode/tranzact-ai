from fastapi import APIRouter, HTTPException

from .schemas import RecommendationRequest, RecommendationResponse
from .service import get_recommendations


router = APIRouter(prefix="/api", tags=["recommendations"])


@router.post("/recommend", response_model=RecommendationResponse)
def recommend(payload: RecommendationRequest):
    try:
        return get_recommendations(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
