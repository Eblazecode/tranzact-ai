from pydantic import BaseModel
from typing import List, Literal


class RecommendationRequest(BaseModel):
    user_name: str


class RecommendationCard(BaseModel):
    id: str
    number: int
    text: str


class RecommendationResponse(BaseModel):
    user: str
    healthScore: int
    healthScoreMax: int
    riskStatus: Literal["HEALTHY", "MODERATE", "AT RISK", "CRITICAL"]
    totalIncome: float
    totalSpending: float
    savingsRatePct: float
    leakageAmount: float
    leakagePct: float
    topCategoryName: str
    topCategoryAmount: float
    topCategoryPct: float
    anomalyStatus: str
    cards: List[RecommendationCard] = []
