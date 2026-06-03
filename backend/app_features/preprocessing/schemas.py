from pydantic import BaseModel, Field
from typing import Literal


class PreprocessingRequest(BaseModel):
    user_name: str = Field(..., min_length=2, max_length=100)
    bank_name: Literal["OPay", "GTBank", "Moniepoint", "Ecobank", "Zenith Bank"]


class PreprocessingResponse(BaseModel):
    message: str
    user_name: str
    statement_user_name: str | None = None
    bank_name: str
    file_path: str
    row_count: int
    date_range: str
    categories: list[str]


class UploadHistoryItem(BaseModel):
    filename: str
    display_name: str
    bank_name: str
    uploaded_at: str
    uploaded_date: str
    uploaded_time: str
    is_current: bool = False


class UploadHistoryResponse(BaseModel):
    uploads: list[UploadHistoryItem]


class SelectUploadRequest(BaseModel):
    user_name: str = Field(..., min_length=2, max_length=100)
    filename: str = Field(..., min_length=1, max_length=255)
