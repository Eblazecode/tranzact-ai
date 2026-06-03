from pydantic import BaseModel


class SizeDistributionItem(BaseModel):
    bucket: str
    range: str
    count: int
    total: float


class CategoryConsistencyItem(BaseModel):
    category: str
    consistencyPct: float


class SpendingBehaviourPatternsResponse(BaseModel):
    weekendTotal: float
    weekdayTotal: float
    weekendAvg: float
    weekdayAvg: float
    mostExpensiveMonth: dict
    cheapestMonth: dict
    avgMonthlySpend: float
    stdDeviation: float
    sizeDistribution: list[SizeDistributionItem]
    categoryConsistency: list[CategoryConsistencyItem]
    spendingByDayOfWeek: list
