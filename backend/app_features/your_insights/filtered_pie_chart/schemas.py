from typing import Literal

from pydantic import BaseModel


class CategoryBreakdownItem(BaseModel):
    category: str
    amount: float


class ComparisonBreakdownItem(BaseModel):
    category: str
    current: float
    previous: float


class MonthlyPieGridItem(BaseModel):
    month: str
    slices: list[CategoryBreakdownItem]


class FilteredPieChartQuery(BaseModel):
    user_name: str
    filter: Literal["month", "week"]
    period: str


class FilteredPieChartResponse(BaseModel):
    availableMonths: list[str]
    availableWeeks: list[str]
    categoryBreakdown: list[CategoryBreakdownItem]
    comparisonBreakdown: list[ComparisonBreakdownItem]
    monthlyPieGrid: list[MonthlyPieGridItem]
