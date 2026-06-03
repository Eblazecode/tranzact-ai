from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func

from core.database import Base


class UploadHistory(Base):
    __tablename__ = "upload_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    user_name = Column(String, nullable=False, index=True)
    original_filename = Column(String, nullable=False)
    processed_filename = Column(String, nullable=False)
    processed_file_path = Column(String, nullable=False)
    bank_name = Column(String, nullable=False, index=True)
    row_count = Column(Integer, nullable=False)
    date_range = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
