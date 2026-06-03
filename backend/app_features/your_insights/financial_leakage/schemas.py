from pydantic import BaseModel


class LeakageBreakdownItem(BaseModel):
    category: str
    amount: float
    count: int
    avg: float


class BucketBreakdownItem(BaseModel):
    bucket: str
    amount: float


class AmountByCategoryItem(BaseModel):
    category: str
    amount: float


class FinancialLeakageResponse(BaseModel):
    totalLeakageAmount: float
    leakagePct: float
    leakageTransactionCount: int
    breakdown: list[LeakageBreakdownItem]
    bucketBreakdown: list[BucketBreakdownItem]
    amountByCategory: list[AmountByCategoryItem]
