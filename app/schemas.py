from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models import TransactionStatus


class WebhookRequest(BaseModel):
    """Schema for incoming webhook requests."""
    
    transaction_id: str = Field(..., description="Unique transaction identifier")
    source_account: str = Field(..., description="Source account identifier")
    destination_account: str = Field(..., description="Destination account identifier")
    amount: float = Field(..., gt=0, description="Transaction amount (must be positive)")
    currency: str = Field(..., min_length=3, max_length=3, description="Currency code (e.g., INR, USD)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "transaction_id": "txn_abc123def456",
                "source_account": "acc_user_789",
                "destination_account": "acc_merchant_456",
                "amount": 1500,
                "currency": "INR"
            }
        }


class WebhookResponse(BaseModel):
    """Schema for webhook acknowledgment response."""
    
    message: str = "Webhook received"
    transaction_id: str


class TransactionResponse(BaseModel):
    """Schema for transaction query response."""
    
    transaction_id: str
    source_account: str
    destination_account: str
    amount: float
    currency: str
    status: TransactionStatus
    created_at: datetime
    processed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "transaction_id": "txn_abc123def456",
                "source_account": "acc_user_789",
                "destination_account": "acc_merchant_456",
                "amount": 150.50,
                "currency": "USD",
                "status": "PROCESSED",
                "created_at": "2024-01-15T10:30:00Z",
                "processed_at": "2024-01-15T10:30:30Z"
            }
        }


class HealthResponse(BaseModel):
    """Schema for health check response."""
    
    status: str = "HEALTHY"
    current_time: datetime
