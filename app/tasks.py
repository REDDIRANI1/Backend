import time
from datetime import datetime
from sqlalchemy.orm import Session
from app.celery_app import celery_app
from app.database import SessionLocal
from app.models import Transaction, TransactionStatus
import logging

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def process_transaction(self, transaction_id: str):
    """
    Background task to process a transaction.
    
    This task simulates external API calls with a 30-second delay,
    then updates the transaction status to PROCESSED.
    
    Args:
        transaction_id: The unique transaction identifier
    """
    db: Session = SessionLocal()
    
    try:
        logger.info(f"Starting processing for transaction: {transaction_id}")
        
        # Simulate external API call with 30-second delay
        time.sleep(30)
        
        # Update transaction status
        transaction = db.query(Transaction).filter(
            Transaction.transaction_id == transaction_id
        ).first()
        
        if transaction:
            transaction.status = TransactionStatus.PROCESSED
            transaction.processed_at = datetime.utcnow()
            db.commit()
            logger.info(f"Successfully processed transaction: {transaction_id}")
        else:
            logger.error(f"Transaction not found: {transaction_id}")
            
    except Exception as e:
        logger.error(f"Error processing transaction {transaction_id}: {str(e)}")
        db.rollback()
        
        # Update status to FAILED
        try:
            transaction = db.query(Transaction).filter(
                Transaction.transaction_id == transaction_id
            ).first()
            if transaction:
                transaction.status = TransactionStatus.FAILED
                transaction.processed_at = datetime.utcnow()
                db.commit()
        except Exception as update_error:
            logger.error(f"Failed to update transaction status: {str(update_error)}")
        
        # Retry the task
        raise self.retry(exc=e, countdown=60)
        
    finally:
        db.close()
