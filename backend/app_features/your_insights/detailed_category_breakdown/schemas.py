from pydantic import BaseModel


class CategoryBreakdownRow(BaseModel):
    category: str
    transactions: int
    total_spent: float
    avg_per_txn: float
    max_txn: float
    percent_of_total_spend: float


class CategorySpendBarPoint(BaseModel):
    category: str
    amount: float


class MonthlyIncomeExpensePoint(BaseModel):
    month: str
    income: float
    expense: float


class CategoryCountPiePoint(BaseModel):
    category: str
    count: int


class DailySpendingTrendPoint(BaseModel):
    date: str
    amount: float
    rolling_7_day_avg: float


class DayOfWeekPoint(BaseModel):
    day: str
    amount: float
    is_weekend: bool


class LargestTransactionPoint(BaseModel):
    date: str
    category: str
    description: str
    amount: float


class DetailedCategoryBreakdownResponse(BaseModel):
    summary: list[CategoryBreakdownRow]
    totals: dict[str, float | str]
    charts: dict[str, list[dict[str, float | int | str | bool]]]
