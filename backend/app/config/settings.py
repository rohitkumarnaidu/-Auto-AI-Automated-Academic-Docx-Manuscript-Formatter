
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
    SUPABASE_JWKS_URL = os.getenv("SUPABASE_JWKS_URL")
    SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL")
    SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000")
    ALGORITHM = "HS256"

settings = Settings()
