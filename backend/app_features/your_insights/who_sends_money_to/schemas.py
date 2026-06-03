from typing import Literal

from pydantic import BaseModel


class RecipientTableItem(BaseModel):
    name: str
    frequency: int
    totalSent: float


class TransferCountByRecipientItem(BaseModel):
    name: str
    count: int


class AmountSentByRecipientItem(BaseModel):
    name: str
    amount: float


class TransfersOutResponse(BaseModel):
    availableMonths: list[str]
    availableWeeks: list[str]
    availableYears: list[str]
    table: list[RecipientTableItem]
    transferCountByRecipient: list[TransferCountByRecipientItem]
    amountSentByRecipient: list[AmountSentByRecipientItem]


class TransfersOutQuery(BaseModel):
    user_name: str
    filter: Literal["month", "week", "year"]
    period: str
    top_n: int = 10
