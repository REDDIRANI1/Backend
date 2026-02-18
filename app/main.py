from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
import logging

from app.database import get_db, engine, Base
from app.schemas import (
    WebhookRequest,
    WebhookResponse,
    TransactionResponse,
    HealthResponse
)
from app.models import Transaction, TransactionStatus
from app.tasks import process_transaction

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Transaction Webhook Service",
    description="A service that receives and processes transaction webhooks with background processing",
    version="1.0.0"
)

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables (only if they don't exist)
# This is safe to run on every startup but won't recreate existing tables
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified/created")
except Exception as db_init_error:
    logger.error(f"Database initialization error: {str(db_init_error)}")
    # Don't fail startup - tables might already exist


@app.get("/", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    
    Returns the service status and current timestamp.
    """
    return HealthResponse(
        status="HEALTHY",
        current_time=datetime.utcnow()
    )


@app.post(
    "/v1/webhooks/transactions",
    response_model=WebhookResponse,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["Webhooks"]
)
async def receive_webhook(
    webhook_data: WebhookRequest,
    db: Session = Depends(get_db)
):
    """
    Receive transaction webhook and process it in the background.
    
    This endpoint:
    - Returns 202 Accepted immediately (within 500ms)
    - Implements idempotency (duplicate transaction_id won't create duplicates)
    - Processes transactions asynchronously with a 30-second delay
    
    Args:
        webhook_data: Transaction webhook payload
        db: Database session
        
    Returns:
        Acknowledgment response with transaction_id
    """
    try:
        # Check if transaction already exists (idempotency)
        existing_transaction = db.query(Transaction).filter(
            Transaction.transaction_id == webhook_data.transaction_id
        ).first()
        
        if existing_transaction:
            logger.info(f"Duplicate webhook received for transaction: {webhook_data.transaction_id}")
            return WebhookResponse(
                message="Webhook received (duplicate)",
                transaction_id=webhook_data.transaction_id
            )
        
        # Create new transaction record
        new_transaction = Transaction(
            transaction_id=webhook_data.transaction_id,
            source_account=webhook_data.source_account,
            destination_account=webhook_data.destination_account,
            amount=webhook_data.amount,
            currency=webhook_data.currency,
            status=TransactionStatus.PROCESSING
        )
        
        db.add(new_transaction)
        db.commit()
        db.refresh(new_transaction)
        
        logger.info(f"Created transaction: {webhook_data.transaction_id}")
        
        # Trigger background processing (gracefully handle Redis/Celery unavailability)
        try:
            process_transaction.delay(webhook_data.transaction_id)
            logger.info(f"Background task queued for transaction: {webhook_data.transaction_id}")
        except Exception as celery_error:
            # If Celery/Redis is unavailable, log warning but still return success
            # The transaction is already saved, so we've fulfilled the webhook contract
            logger.warning(f"Could not queue background task (Redis/Celery may be unavailable): {str(celery_error)}")
            logger.info(f"Transaction {webhook_data.transaction_id} saved but background processing may be delayed")
        
        return WebhookResponse(
            message="Webhook received",
            transaction_id=webhook_data.transaction_id
        )
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process webhook"
        )


@app.get(
    "/v1/transactions/{transaction_id}",
    response_model=List[TransactionResponse],
    tags=["Transactions"]
)
async def get_transaction(
    transaction_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve transaction status by transaction_id.
    
    Args:
        transaction_id: Unique transaction identifier
        db: Database session
        
    Returns:
        List containing the transaction details
        
    Raises:
        404: If transaction not found
    """
    transaction = db.query(Transaction).filter(
        Transaction.transaction_id == transaction_id
    ).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction {transaction_id} not found"
        )
    
    return [transaction]


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    from app.config import get_settings
    
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=True
    )
