
import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()

class Settings:
    # Supabase
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
    SUPABASE_JWKS_URL = os.getenv("SUPABASE_JWKS_URL")
    SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL")
    SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000")
    ALGORITHM = "HS256"
    
    # Template Configuration (Dynamic)
    DEFAULT_TEMPLATE = os.getenv("DEFAULT_TEMPLATE", "none")  # Default to general formatting
    
    # Confidence Thresholds (Dynamic - Tunable for accuracy)
    HEADING_STYLE_THRESHOLD = float(os.getenv("HEADING_STYLE_THRESHOLD", "0.4"))
    HEADING_FALLBACK_CONFIDENCE = float(os.getenv("HEADING_FALLBACK_CONFIDENCE", "0.45"))
    HEURISTIC_CONFIDENCE_HIGH = float(os.getenv("HEURISTIC_CONFIDENCE_HIGH", "0.95"))
    HEURISTIC_CONFIDENCE_MEDIUM = float(os.getenv("HEURISTIC_CONFIDENCE_MEDIUM", "0.9"))
    HEURISTIC_CONFIDENCE_LOW = float(os.getenv("HEURISTIC_CONFIDENCE_LOW", "0.5"))
    
    # External Tools (Dynamic)
    LIBREOFFICE_PATH: Optional[str] = os.getenv("LIBREOFFICE_PATH", None)

settings = Settings()
