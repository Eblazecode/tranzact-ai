from pydantic import BaseModel


class SummaryCard(BaseModel):
    label: str
    amount: float
    changePct: float


class MonthlyFlowPoint(BaseModel):
    month: str
    income: float
    expenses: float


class CategorySpendPoint(BaseModel):
    category: str
    amount: float


class TransactionHistoryItem(BaseModel):
    description: str
    category: str
    date: str
    amount: float


class SpendHighlight(BaseModel):
    amount: float
    description: str
    date: str


class SpendingHighlights(BaseModel):
    highestSingleSpend: SpendHighlight
    lowestSingleSpend: SpendHighlight


class DashboardOverviewResponse(BaseModel):
    summaryCards: list[SummaryCard]
    monthlyFinancialFlow: list[MonthlyFlowPoint]
    spendingByCategory: list[CategorySpendPoint]
    transactionHistory: list[TransactionHistoryItem]
    spendingHighlights: SpendingHighlights
