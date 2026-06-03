from pydantic import BaseModel


class MonthlyFlowPoint(BaseModel):
    month: str
    income: float
    expenses: float
    savings: float
    savingsRate: float
    savingsDirection: str


class MonthlyFlowResponse(BaseModel):
    monthly: list[MonthlyFlowPoint]
    thresholdExplanation: str
    healthyThresholdNote: str
