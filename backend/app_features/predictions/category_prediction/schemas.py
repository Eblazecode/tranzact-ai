from pydantic import BaseModel
from typing import Optional, List


class CategoryPredictionRequest(BaseModel):
    user_name: str
    predict_month: str = ""
    predict_month_num: int
    predict_year: int


class CatShapFactor(BaseModel):
    label: str
    value: float


class CatShapWaterfallItem(BaseModel):
    label: str
    value: float
    direction: str  # "up" or "down"


class CategoryBottomLine(BaseModel):
    driverLabel: str
    sizeWord: str
    impactAmount: float
    impactDirection: str
    pressurePct: float
    pressureLabel: str
    plainEnglishLines: List[str] = []


class CategoryPredictionItem(BaseModel):
    predictMonthLabel: str
    categoryName: str
    predictedSpend: float
    startingBaseline: float
    aiForecast: float
    actualSpend: Optional[float] = None
    forecastError: float = 0
    lastKnownMonth: str
    topUpFactors: List[CatShapFactor] = []
    topDownFactors: List[CatShapFactor] = []
    bottomLine: CategoryBottomLine
    shapWaterfall: List[CatShapWaterfallItem] = []


class CategoryPredictionResponse(BaseModel):
    categories: List[CategoryPredictionItem] = []
