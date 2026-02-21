"""
Application Settings - pydantic-settings backed configuration.

Replaces manual os.getenv() with pydantic-settings BaseSettings:
  - Automatic .env file loading
  - Type coercion and validation
  - field_validator for confidence thresholds

All attribute names preserved for 100% backward compatibility.
Falls back to plain os.getenv class if pydantic-settings not installed.
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)

try:
    from pydantic_settings import BaseSettings
    from pydantic import field_validator
    _PS = True
except ImportError:
    _PS = False
    logger.warning("pydantic-settings not installed - using os.getenv fallback. pip install pydantic-settings")


if _PS:
    class Settings(BaseSettings):
        """Application settings loaded from environment variables / .env file."""

        # Supabase Auth
        SUPABASE_URL: Optional[str] = None
        SUPABASE_ANON_KEY: Optional[str] = None
        SUPABASE_JWKS_URL: Optional[str] = None
        SUPABASE_JWT_SECRET: Optional[str] = None
        SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None
        SUPABASE_DB_URL: Optional[str] = None

        # Security
        ALGORITHM: str = "HS256"
        CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

        # Template
        DEFAULT_TEMPLATE: str = "none"

        # Confidence Thresholds
        HEADING_STYLE_THRESHOLD: float = 0.4
        HEADING_FALLBACK_CONFIDENCE: float = 0.45
        HEURISTIC_CONFIDENCE_HIGH: float = 0.95
        HEURISTIC_CONFIDENCE_MEDIUM: float = 0.9
        HEURISTIC_CONFIDENCE_LOW: float = 0.5

        # External Tools
        LIBREOFFICE_PATH: Optional[str] = None

        # GROBID
        GROBID_BASE_URL: str = "http://localhost:8070"
        GROBID_TIMEOUT: int = 30
        GROBID_MAX_RETRIES: int = 3
        GROBID_ENABLED: bool = True

        model_config = {
            "env_file": ".env",
            "env_file_encoding": "utf-8",
            "case_sensitive": False,
            "extra": "ignore",
        }

        @field_validator(
            "HEADING_STYLE_THRESHOLD", "HEADING_FALLBACK_CONFIDENCE",
            "HEURISTIC_CONFIDENCE_HIGH", "HEURISTIC_CONFIDENCE_MEDIUM",
            "HEURISTIC_CONFIDENCE_LOW",
            mode="before",
        )
        @classmethod
        def clamp_confidence(cls, v):
            fv = float(v)
            if not (0.0 <= fv <= 1.0):
                logger.warning("Confidence value %s outside [0,1]. Clamping.", fv)
                return max(0.0, min(1.0, fv))
            return fv

        def validate(self) -> None:
            """Soft-validate critical settings at startup. Never crashes."""
            for name in ("SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_JWT_SECRET", "SUPABASE_SERVICE_ROLE_KEY"):
                if not getattr(self, name):
                    logger.warning(
                        "⚠️  %s is not set. Auth/DB-dependent endpoints will fail "
                        "at request-time, but the server will still start.", name,
                    )
            if not self.SUPABASE_DB_URL:
                logger.info(
                    "ℹ️  SUPABASE_DB_URL not set. SQLAlchemy/Alembic migrations unavailable. "
                    "Runtime DB ops use supabase-py (SUPABASE_SERVICE_ROLE_KEY)."
                )

else:
    # Fallback: original os.getenv behaviour
    import os
    try:
        from dotenv import load_dotenv
        load_dotenv(override=True)
    except ImportError:
        pass

    class Settings:  # type: ignore[no-redef]
        SUPABASE_URL: Optional[str] = os.getenv("SUPABASE_URL")
        SUPABASE_ANON_KEY: Optional[str] = os.getenv("SUPABASE_ANON_KEY")
        SUPABASE_JWKS_URL: Optional[str] = os.getenv("SUPABASE_JWKS_URL")
        SUPABASE_JWT_SECRET: Optional[str] = os.getenv("SUPABASE_JWT_SECRET")
        SUPABASE_SERVICE_ROLE_KEY: Optional[str] = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        SUPABASE_DB_URL: Optional[str] = os.getenv("SUPABASE_DB_URL")
        ALGORITHM: str = "HS256"
        CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000")
        DEFAULT_TEMPLATE: str = os.getenv("DEFAULT_TEMPLATE", "none")
        HEADING_STYLE_THRESHOLD: float = float(os.getenv("HEADING_STYLE_THRESHOLD", "0.4"))
        HEADING_FALLBACK_CONFIDENCE: float = float(os.getenv("HEADING_FALLBACK_CONFIDENCE", "0.45"))
        HEURISTIC_CONFIDENCE_HIGH: float = float(os.getenv("HEURISTIC_CONFIDENCE_HIGH", "0.95"))
        HEURISTIC_CONFIDENCE_MEDIUM: float = float(os.getenv("HEURISTIC_CONFIDENCE_MEDIUM", "0.9"))
        HEURISTIC_CONFIDENCE_LOW: float = float(os.getenv("HEURISTIC_CONFIDENCE_LOW", "0.5"))
        LIBREOFFICE_PATH: Optional[str] = os.getenv("LIBREOFFICE_PATH")
        GROBID_BASE_URL: str = os.getenv("GROBID_BASE_URL", "http://localhost:8070")
        GROBID_TIMEOUT: int = int(os.getenv("GROBID_TIMEOUT", "30"))
        GROBID_MAX_RETRIES: int = int(os.getenv("GROBID_MAX_RETRIES", "3"))
        GROBID_ENABLED: bool = os.getenv("GROBID_ENABLED", "true").lower() == "true"

        def validate(self) -> None:
            for name in ("SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_JWT_SECRET", "SUPABASE_SERVICE_ROLE_KEY"):
                if not getattr(self, name):
                    logger.warning("⚠️  %s is not set.", name)
            if not self.SUPABASE_DB_URL:
                logger.info("ℹ️  SUPABASE_DB_URL not set.")


settings = Settings()
try:
    settings.validate()
except Exception as exc:  # pragma: no cover
    logger.error("Settings validation error (non-fatal): %s", exc)
