from sqlalchemy import Column, String, Float, DateTime, Enum as SQLEnum, Index
from sqlalchemy.sql import func
from datetime import datetime
import enum
from app.database import Base


class TransactionStatus(str, enum.Enum):
    """Transaction status enumeration."""
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"


class Transaction(Base):
    """Transaction model for storing webhook data."""
    
    __tablename__ = "transactions"
    
    transaction_id = Column(String, primary_key=True, index=True)
    source_account = Column(String, nullable=False)
    destination_account = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    status = Column(SQLEnum(TransactionStatus), default=TransactionStatus.PROCESSING, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Create index for faster queries
    __table_args__ = (
        Index('idx_transaction_status', 'status'),
        Index('idx_transaction_created_at', 'created_at'),
    )
    
    def __repr__(self):
        return f"<Transaction(transaction_id={self.transaction_id}, status={self.status})>"
