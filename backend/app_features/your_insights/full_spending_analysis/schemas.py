from pydantic import BaseModel
from typing import List, Dict, Optional


class CategoryAmount(BaseModel):
    category: str
    amount: float


class Transaction(BaseModel):
    amount: float
    desc: str
    date: str


class MonthAmount(BaseModel):
    month: str
    amount: float


class SizeDistribution(BaseModel):
    bucket: str
    range: str
    count: int
    total: float


class CategoryConsistency(BaseModel):
    category: str
    consistency_pct: float


class BehaviourData(BaseModel):
    weekendTotal: float
    weekdayTotal: float
    weekendAvg: float
    weekdayAvg: float
    mostExpensiveMonth: MonthAmount
    cheapestMonth: MonthAmount
    avgMonthlySpend: float
    stdDeviation: float
    sizeDistribution: List[SizeDistribution]
    categoryConsistency: List[CategoryConsistency]


class SpendingAnalysisResponse(BaseModel):
    spendByCategory: List[CategoryAmount]
    top10LargestTransactions: List[Transaction]
    behaviour: BehaviourData


class CategoryStats(BaseModel):
    category: str
    transactions: int
    totalSpent: float
    avgPerTxn: float
    maxTxn: float
    minTxn: float
    percentOfTotal: float


class CategorySummary(BaseModel):
    totalSpent: float
    totalTransactions: int
    avgSpendPerTxn: float
    mostActiveCategory: Optional[str]
    uniqueCategories: int


class CategoryBreakdownResponse(BaseModel):
    categories: List[CategoryStats]
    summary: CategorySummary


class TrendData(BaseModel):
    period: str
    totalSpent: float
    transactionCount: int
    avgSpend: float
    rollingAvg: float


class TrendSummary(BaseModel):
    period: str
    avgSpend: float
    maxSpend: float
    minSpend: float
    totalPeriods: int
    trendDirection: str


class SpendingTrendsResponse(BaseModel):
    trends: List[TrendData]
    summary: TrendSummary


class LeakageCategory(BaseModel):
    category: str
    amount: float
    percentage: float
    transactionCount: int


class LeakageData(BaseModel):
    totalAmount: float
    percentage: float
    transactionCount: int
    breakdown: List[LeakageCategory]


class SpendingBreakdown(BaseModel):
    type: str
    amount: float


class LeakageAnalysisResponse(BaseModel):
    leakage: LeakageData
    breakdown: List[SpendingBreakdown]
