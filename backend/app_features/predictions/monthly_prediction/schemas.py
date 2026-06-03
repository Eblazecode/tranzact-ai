from pydantic import BaseModel
from typing import Optional, List


class MonthlyPredictionRequest(BaseModel):
    user_name: str
    predict_year: int
    predict_month_num: int


class ShapFactor(BaseModel):
    label: str
    value: float


class ShapWaterfallItem(BaseModel):
    label: str
    value: float
    direction: str  # "up" or "down"


class SpendingDnaItem(BaseModel):
    label: str
    importance: float


class BottomLine(BaseModel):
    driverLabel: str
    sizeWord: str
    impactAmount: float
    impactDirection: str
    pressurePct: float
    pressureLabel: str
    plainEnglishLines: List[str] = []


class MonthlyPredictionResponse(BaseModel):
    predictMonthLabel: str
    startingBaseline: float
    aiForecast: float
    actualSpend: Optional[float] = None
    forecastError: float = 0
    lastKnownMonth: str
    forecastAmount: float
    baselineAmount: float
    topUpFactors: List[ShapFactor] = []
    topDownFactors: List[ShapFactor] = []
    bottomLine: BottomLine
    shapWaterfall: List[ShapWaterfallItem] = []
    spendingDna: List[SpendingDnaItem] = []
