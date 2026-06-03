from pydantic import BaseModel


class FinancialHealthSummaryResponse(BaseModel):
    totalIncome: float
    totalExpenses: float
    netSavings: float
    savingsRatePct: float
    healthStatus: str
    healthNarrative: str
    healthScore: int
