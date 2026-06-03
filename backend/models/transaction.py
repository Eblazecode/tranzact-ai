from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from core.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    upload_id = Column(Integer, ForeignKey("statement_uploads.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    user_name = Column(String, nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    category = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=False)
    debit = Column(Float, nullable=False, default=0.0)
    credit = Column(Float, nullable=False, default=0.0)
    balance = Column(Float, nullable=False, default=0.0)
    statement_user = Column(String, nullable=True)
    bank = Column(String, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    upload = relationship("StatementUpload", back_populates="transactions")
