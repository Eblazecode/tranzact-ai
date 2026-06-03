from pydantic import BaseModel


class RecurringTransactionRow(BaseModel):
    description: str
    frequencyPct: float
    monthsRepeated: int
    totalMonths: int
    avgAmount: float


class RecurringTransactionsResponse(BaseModel):
    rows: list[RecurringTransactionRow]
    patternSummary: str
