from pydantic import BaseModel


class PeakBalanceItem(BaseModel):
    amount: float
    date: str


class LowestBalanceItem(BaseModel):
    amount: float
    date: str


class DailyClosingItem(BaseModel):
    date: str
    balance: float


class Rolling30DayItem(BaseModel):
    date: str
    balance: float


class MonthlyAverageItem(BaseModel):
    month: str
    avgBalance: float


class MonthOverMonthChangeItem(BaseModel):
    month: str
    change: float


class BalanceTrajectoryResponse(BaseModel):
    startingBalance: float
    endingBalance: float
    peakBalance: PeakBalanceItem
    lowestBalance: LowestBalanceItem
    avgBalance: float
    dangerZoneDays: int
    dailyClosing: list[DailyClosingItem]
    rolling30Day: list[Rolling30DayItem]
    monthlyAverage: list[MonthlyAverageItem]
    monthOverMonthChange: list[MonthOverMonthChangeItem]
