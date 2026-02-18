"""
Application Settings - Secure, validated configuration loading.

All settings are loaded from environment variables with safe defaults.
Critical secrets (Supabase keys, JWT secret) are validated at startup.
The app will log a WARNING (not crash) if optional services are unconfigured.
"""

import os
import logging
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


class Settings:
    # ── Supabase Auth ──────────────────────────────────────────────────────────
    SUPABASE_URL: Optional[str] = os.getenv("SUPABASE_URL")
    SUPABASE_ANON_KEY: Optional[str] = os.getenv("SUPABASE_ANON_KEY")
    SUPABASE_JWKS_URL: Optional[str] = os.getenv("SUPABASE_JWKS_URL")
    SUPABASE_DB_URL: Optional[str] = os.getenv("SUPABASE_DB_URL")
    SUPABASE_JWT_SECRET: Optional[str] = os.getenv("SUPABASE_JWT_SECRET")

    # ── Security ───────────────────────────────────────────────────────────────
    ALGORITHM: str = "HS256"
    CORS_ORIGINS: str = os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://localhost:3000"
    )

    # ── Template Configuration ─────────────────────────────────────────────────
    DEFAULT_TEMPLATE: str = os.getenv("DEFAULT_TEMPLATE", "none")

    # ── Confidence Thresholds (tunable) ───────────────────────────────────────
    HEADING_STYLE_THRESHOLD: float = float(
        os.getenv("HEADING_STYLE_THRESHOLD", "0.4")
    )
    HEADING_FALLBACK_CONFIDENCE: float = float(
        os.getenv("HEADING_FALLBACK_CONFIDENCE", "0.45")
    )
    HEURISTIC_CONFIDENCE_HIGH: float = float(
        os.getenv("HEURISTIC_CONFIDENCE_HIGH", "0.95")
    )
    HEURISTIC_CONFIDENCE_MEDIUM: float = float(
        os.getenv("HEURISTIC_CONFIDENCE_MEDIUM", "0.9")
    )
    HEURISTIC_CONFIDENCE_LOW: float = float(
        os.getenv("HEURISTIC_CONFIDENCE_LOW", "0.5")
    )

    # ── External Tools ─────────────────────────────────────────────────────────
    LIBREOFFICE_PATH: Optional[str] = os.getenv("LIBREOFFICE_PATH", None)

    # ── GROBID Configuration ───────────────────────────────────────────────────
    GROBID_BASE_URL: str = os.getenv("GROBID_BASE_URL", "http://localhost:8070")
    GROBID_TIMEOUT: int = int(os.getenv("GROBID_TIMEOUT", "30"))
    GROBID_MAX_RETRIES: int = int(os.getenv("GROBID_MAX_RETRIES", "3"))
    GROBID_ENABLED: bool = os.getenv("GROBID_ENABLED", "true").lower() == "true"

    def validate(self) -> None:
        """
        Soft-validate critical settings at startup.
        Logs warnings for missing optional secrets instead of crashing.
        Only raises for truly unrecoverable misconfigurations.
        """
        _warn_if_missing = [
            ("SUPABASE_URL", self.SUPABASE_URL),
            ("SUPABASE_ANON_KEY", self.SUPABASE_ANON_KEY),
            ("SUPABASE_JWT_SECRET", self.SUPABASE_JWT_SECRET),
            ("SUPABASE_DB_URL", self.SUPABASE_DB_URL),
        ]
        for name, value in _warn_if_missing:
            if not value:
                logger.warning(
                    "⚠️  %s is not set. Auth/DB-dependent endpoints will fail at "
                    "request-time, but the server will still start.",
                    name,
                )

        # Validate numeric thresholds are in a sane range
        for attr in (
            "HEADING_STYLE_THRESHOLD",
            "HEADING_FALLBACK_CONFIDENCE",
            "HEURISTIC_CONFIDENCE_HIGH",
            "HEURISTIC_CONFIDENCE_MEDIUM",
            "HEURISTIC_CONFIDENCE_LOW",
        ):
            val = getattr(self, attr)
            if not (0.0 <= val <= 1.0):
                logger.warning(
                    "⚠️  %s=%s is outside [0, 1]. Clamping to valid range.", attr, val
                )
                setattr(self, attr, max(0.0, min(1.0, val)))


settings = Settings()
# Run soft validation on import — never crashes the server
try:
    settings.validate()
except Exception as exc:  # pragma: no cover
    logger.error("Settings validation error (non-fatal): %s", exc)
