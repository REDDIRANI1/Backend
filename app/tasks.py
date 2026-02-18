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
    logger.info(f"Task received for transaction: {transaction_id}")
    
    try:
        # Simulate external API call (long delay) 
        # We do this BEFORE opening the database connection to free up the pool
        time.sleep(25) 
        
        db = SessionLocal()
        try:
            logger.info(f"Updating status for transaction: {transaction_id}")
            transaction = db.query(Transaction).filter(
                Transaction.transaction_id == transaction_id
            ).first()
            
            if transaction:
                transaction.status = TransactionStatus.PROCESSED
                transaction.processed_at = datetime.utcnow()
                db.commit()
                logger.info(f"Successfully processed transaction: {transaction_id}")
            else:
                logger.error(f"Transaction not found in database: {transaction_id}")
        except Exception as db_err:
            db.rollback()
            raise db_err
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error processing transaction {transaction_id}: {str(e)}")
        
        # Attempt to update status to FAILED as a fallback
        fallback_db = SessionLocal()
        try:
            transaction = fallback_db.query(Transaction).filter(
                Transaction.transaction_id == transaction_id
            ).first()
            if transaction:
                transaction.status = TransactionStatus.FAILED
                transaction.processed_at = datetime.utcnow()
                fallback_db.commit()
        except Exception as update_error:
            logger.error(f"Failed to update transaction status to FAILED: {str(update_error)}")
        finally:
            fallback_db.close()
        
        # Retry the task
        raise self.retry(exc=e, countdown=60)
