from pydantic import BaseModel


class FlaggedMonthItem(BaseModel):
    month: str
    zScore: float
    amount: float


class FlaggedWeekItem(BaseModel):
    week: str
    zScore: float
    amount: float


class MonthlySeriesItem(BaseModel):
    month: str
    amount: float
    isAnomaly: bool


class WeeklySeriesItem(BaseModel):
    week: str
    amount: float
    isAnomaly: bool


class AnomalyDetectionResponse(BaseModel):
    flaggedMonths: list[FlaggedMonthItem]
    flaggedWeeks: list[FlaggedWeekItem]
    monthlySeries: list[MonthlySeriesItem]
    weeklySeries: list[WeeklySeriesItem]
