
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config.settings import settings

# Use Supabase PostgreSQL
SQLALCHEMY_DATABASE_URL = settings.SUPABASE_DB_URL

if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("SUPABASE_DB_URL environment variable is not set. Please configure your .env file.")

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
