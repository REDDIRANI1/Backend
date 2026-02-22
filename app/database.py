from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import get_settings

settings = get_settings()

# Create database engine - pool sized for concurrent (e.g. 3+ simultaneous POSTs + GETs)
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=15,
    max_overflow=25,
    pool_recycle=3600,
    echo=False,
    connect_args={
        "connect_timeout": 2,
        "options": "-c statement_timeout=5000"
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
