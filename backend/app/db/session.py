
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config.settings import settings

# Use Supabase PostgreSQL
SQLALCHEMY_DATABASE_URL = settings.SUPABASE_DB_URL

if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("SUPABASE_DB_URL environment variable is not set. Please configure your .env file.")

# Supabase-optimized connection pool configuration
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,  # Test connections before using them
    pool_size=5,  # Number of connections to keep in pool
    max_overflow=10,  # Additional connections when pool is full
    pool_recycle=300,  # Recycle connections after 5 minutes (Supabase timeout is 10 min)
    pool_timeout=30,  # Wait up to 30 seconds for a connection
    connect_args={
        "connect_timeout": 10,  # Connection timeout in seconds
        "options": "-c statement_timeout=300000"  # 5 minute query timeout
    },
    echo=False  # Set to True for SQL debugging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
