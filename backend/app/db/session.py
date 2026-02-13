
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config.settings import settings
from typing import Generator

# Use Supabase PostgreSQL
SQLALCHEMY_DATABASE_URL = settings.SUPABASE_DB_URL

if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("SUPABASE_DB_URL environment variable is not set. Please configure your .env file.")

# Simple configuration - let SQLAlchemy handle defaults
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database sessions.
    Ensures sessions are always closed, even on errors.
    
    Usage:
        @router.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            # Use db here
            # Session automatically closed after request
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
