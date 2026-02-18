from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import get_settings

settings = get_settings()

# Create database engine with optimized settings for production
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=10,  # Increased for concurrent tasks
    max_overflow=20,
    pool_recycle=3600,  # Recycle connections after 1 hour
    echo=False,  # Disable SQL logging for performance
    connect_args={
        "connect_timeout": 5,  # 5 second connection timeout (faster failure)
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
        # Note: statement_timeout should be set via SQL, not connection args
    }
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
