from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from core.database import Base


class StatementUpload(Base):
    __tablename__ = "statement_uploads"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    user_name = Column(String, nullable=False, index=True)
    bank_name = Column(String, nullable=False, index=True)
    original_filename = Column(String, nullable=False)
    statement_user_name = Column(String, nullable=True)
    row_count = Column(Integer, nullable=False, default=0)
    is_current = Column(Boolean, nullable=False, default=True, index=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    transactions = relationship(
        "Transaction",
        back_populates="upload",
        cascade="all, delete-orphan",
    )
