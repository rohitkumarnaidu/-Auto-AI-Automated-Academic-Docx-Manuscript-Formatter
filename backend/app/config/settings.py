"""
Application settings loaded from .env.

Policy:
- Do not hardcode runtime configuration in code.
- Read configuration from environment variables (via .env in local development).
"""

from __future__ import annotations

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

try:
    from pydantic import Field, field_validator
    from pydantic_settings import BaseSettings

    _PS = True
except Exception:
    _PS = False
    logger.warning("pydantic-settings not installed; using os.getenv fallback.")


def _parse_boolish(value, field_name: str):
    if isinstance(value, bool):
        return value
    if value is None:
        return value
    normalized = str(value).strip().lower()
    truthy = {"1", "true", "yes", "on", "debug", "development", "dev", "local"}
    falsy = {"0", "false", "no", "off", "release", "prod", "production"}
    if normalized in truthy:
        return True
    if normalized in falsy:
        return False
    logger.warning("Unexpected boolean value for %s=%r.", field_name, value)
    return value


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


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
        ALGORITHM: str
        CORS_ORIGINS: str

        # Upload Limits
        MAX_FILE_SIZE: int
        MAX_BATCH_FILES: int
        UPLOADS_PER_MINUTE: int

        # Deployment
        FORCE_HTTPS: bool = Field(
            ...,
            description="Enforce HTTPS redirect and HSTS header",
        )
        DEBUG: bool
        ENABLE_STRUCTURED_LOGGING: bool

        # Enhancement Layer
        ENHANCEMENTS_ENABLED: bool
        ENHANCEMENT_QUEUE_ENABLED: bool
        ENHANCEMENT_QUEUE_PROVIDER: str
        ENHANCEMENT_OCR_ENABLED: bool
        ENHANCEMENT_OCR_BACKENDS: str
        ENHANCEMENT_KEYWORD_ENABLED: bool
        ENHANCEMENT_KEYWORD_BACKENDS: str

        # Template
        DEFAULT_TEMPLATE: str

        # Confidence Thresholds
        HEADING_STYLE_THRESHOLD: float
        HEADING_FALLBACK_CONFIDENCE: float
        HEURISTIC_CONFIDENCE_HIGH: float
        HEURISTIC_CONFIDENCE_MEDIUM: float
        HEURISTIC_CONFIDENCE_LOW: float

        # External Tools
        LIBREOFFICE_PATH: Optional[str] = None

        # Retention / paths
        ENABLE_FILE_CLEANUP: bool
        RETENTION_DAYS: int
        GENERATED_OUTPUT_DIR: str

        # GROBID / LLM / AV
        GROBID_URL: str
        GROBID_BASE_URL: str
        GROBID_TIMEOUT: int
        GROBID_MAX_RETRIES: int
        GROBID_ENABLED: bool

        OLLAMA_URL: str
        OLLAMA_BASE_URL: str
        CLAMAV_HOST: str
        CLAMAV_PORT: int

        GROQ_API_KEY: Optional[str] = None
        GROQ_MODEL: str
        GROQ_API_BASE: str

        NVIDIA_API_KEY: Optional[str] = None
        NVIDIA_MODEL: str
        OPENAI_API_KEY: Optional[str] = None
        ANTHROPIC_API_KEY: Optional[str] = None

        # Redis / celery / integrations
        REDIS_ENABLED: bool
        REDIS_URL: str
        REDIS_HOST: str
        REDIS_PORT: int
        CELERY_BROKER_URL: str
        CELERY_RESULT_BACKEND: str
        CROSSREF_MAILTO: str
        LLM_CACHE_TTL_SECONDS: int = 3600

        # Pipeline tuning / feature toggles
        PIPELINE_GROBID_TIMEOUT_SECONDS: int
        PIPELINE_DOCLING_TIMEOUT_SECONDS: int
        PIPELINE_REASONING_TIMEOUT_SECONDS: int
        PIPELINE_SEMANTIC_TIMEOUT_SECONDS: int
        PIPELINE_ACQUIRE_TIMEOUT_SECONDS: float
        PIPELINE_DOCLING_SKIP_DIGITAL_PDF: bool
        PIPELINE_DOCLING_FORCE: bool
        ENABLE_NOUGAT_PARSER: bool
        ENABLE_NVIDIA_REASONER: bool
        USE_SCIBERT_CLASSIFICATION: bool = False

        model_config = {
            "env_file": ".env",
            "env_file_encoding": "utf-8",
            "case_sensitive": False,
            "extra": "ignore",
        }

        @field_validator(
            "DEBUG",
            "FORCE_HTTPS",
            "ENABLE_STRUCTURED_LOGGING",
            "ENHANCEMENTS_ENABLED",
            "ENHANCEMENT_QUEUE_ENABLED",
            "ENHANCEMENT_OCR_ENABLED",
            "ENHANCEMENT_KEYWORD_ENABLED",
            "ENABLE_FILE_CLEANUP",
            "GROBID_ENABLED",
            "REDIS_ENABLED",
            "PIPELINE_DOCLING_SKIP_DIGITAL_PDF",
            "PIPELINE_DOCLING_FORCE",
            "ENABLE_NOUGAT_PARSER",
            "ENABLE_NVIDIA_REASONER",
            "USE_SCIBERT_CLASSIFICATION",
            mode="before",
        )
        @classmethod
        def parse_bool_fields(cls, value, info):
            return _parse_boolish(value, info.field_name)

        @field_validator(
            "HEADING_STYLE_THRESHOLD",
            "HEADING_FALLBACK_CONFIDENCE",
            "HEURISTIC_CONFIDENCE_HIGH",
            "HEURISTIC_CONFIDENCE_MEDIUM",
            "HEURISTIC_CONFIDENCE_LOW",
            mode="before",
        )
        @classmethod
        def clamp_confidence(cls, value):
            fv = float(value)
            if not (0.0 <= fv <= 1.0):
                logger.warning("Confidence value %s outside [0,1]. Clamping.", fv)
                return max(0.0, min(1.0, fv))
            return fv

        def validate(self) -> None:
            # Keep Supabase soft warning behavior for local startup.
            for name in ("SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_JWT_SECRET", "SUPABASE_SERVICE_ROLE_KEY"):
                if not getattr(self, name):
                    logger.warning("%s is not set. DB/auth endpoints will fail at request time.", name)

            if self.RETENTION_DAYS <= 0:
                raise ValueError("RETENTION_DAYS must be > 0")


else:
    try:
        from dotenv import load_dotenv

        load_dotenv(override=True)
    except Exception:
        pass

    class Settings:  # type: ignore[no-redef]
        # Supabase Auth
        SUPABASE_URL: Optional[str] = os.getenv("SUPABASE_URL")
        SUPABASE_ANON_KEY: Optional[str] = os.getenv("SUPABASE_ANON_KEY")
        SUPABASE_JWKS_URL: Optional[str] = os.getenv("SUPABASE_JWKS_URL")
        SUPABASE_JWT_SECRET: Optional[str] = os.getenv("SUPABASE_JWT_SECRET")
        SUPABASE_SERVICE_ROLE_KEY: Optional[str] = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        SUPABASE_DB_URL: Optional[str] = os.getenv("SUPABASE_DB_URL")

        # Security
        ALGORITHM: str = _require_env("ALGORITHM")
        CORS_ORIGINS: str = _require_env("CORS_ORIGINS")

        # Upload Limits
        MAX_FILE_SIZE: int = int(_require_env("MAX_FILE_SIZE"))
        MAX_BATCH_FILES: int = int(_require_env("MAX_BATCH_FILES"))
        UPLOADS_PER_MINUTE: int = int(_require_env("UPLOADS_PER_MINUTE"))

        # Deployment
        FORCE_HTTPS: bool = bool(_parse_boolish(_require_env("FORCE_HTTPS"), "FORCE_HTTPS"))
        DEBUG: bool = bool(_parse_boolish(_require_env("DEBUG"), "DEBUG"))
        ENABLE_STRUCTURED_LOGGING: bool = bool(
            _parse_boolish(_require_env("ENABLE_STRUCTURED_LOGGING"), "ENABLE_STRUCTURED_LOGGING")
        )

        # Enhancement Layer
        ENHANCEMENTS_ENABLED: bool = bool(_parse_boolish(_require_env("ENHANCEMENTS_ENABLED"), "ENHANCEMENTS_ENABLED"))
        ENHANCEMENT_QUEUE_ENABLED: bool = bool(
            _parse_boolish(_require_env("ENHANCEMENT_QUEUE_ENABLED"), "ENHANCEMENT_QUEUE_ENABLED")
        )
        ENHANCEMENT_QUEUE_PROVIDER: str = _require_env("ENHANCEMENT_QUEUE_PROVIDER")
        ENHANCEMENT_OCR_ENABLED: bool = bool(
            _parse_boolish(_require_env("ENHANCEMENT_OCR_ENABLED"), "ENHANCEMENT_OCR_ENABLED")
        )
        ENHANCEMENT_OCR_BACKENDS: str = _require_env("ENHANCEMENT_OCR_BACKENDS")
        ENHANCEMENT_KEYWORD_ENABLED: bool = bool(
            _parse_boolish(_require_env("ENHANCEMENT_KEYWORD_ENABLED"), "ENHANCEMENT_KEYWORD_ENABLED")
        )
        ENHANCEMENT_KEYWORD_BACKENDS: str = _require_env("ENHANCEMENT_KEYWORD_BACKENDS")

        # Template / confidence
        DEFAULT_TEMPLATE: str = _require_env("DEFAULT_TEMPLATE")
        HEADING_STYLE_THRESHOLD: float = float(_require_env("HEADING_STYLE_THRESHOLD"))
        HEADING_FALLBACK_CONFIDENCE: float = float(_require_env("HEADING_FALLBACK_CONFIDENCE"))
        HEURISTIC_CONFIDENCE_HIGH: float = float(_require_env("HEURISTIC_CONFIDENCE_HIGH"))
        HEURISTIC_CONFIDENCE_MEDIUM: float = float(_require_env("HEURISTIC_CONFIDENCE_MEDIUM"))
        HEURISTIC_CONFIDENCE_LOW: float = float(_require_env("HEURISTIC_CONFIDENCE_LOW"))

        # External tools / retention / output
        LIBREOFFICE_PATH: Optional[str] = os.getenv("LIBREOFFICE_PATH")
        ENABLE_FILE_CLEANUP: bool = bool(
            _parse_boolish(_require_env("ENABLE_FILE_CLEANUP"), "ENABLE_FILE_CLEANUP")
        )
        RETENTION_DAYS: int = int(_require_env("RETENTION_DAYS"))
        GENERATED_OUTPUT_DIR: str = _require_env("GENERATED_OUTPUT_DIR")

        # GROBID / LLM / AV
        GROBID_URL: str = _require_env("GROBID_URL")
        GROBID_BASE_URL: str = _require_env("GROBID_BASE_URL")
        GROBID_TIMEOUT: int = int(_require_env("GROBID_TIMEOUT"))
        GROBID_MAX_RETRIES: int = int(_require_env("GROBID_MAX_RETRIES"))
        GROBID_ENABLED: bool = bool(_parse_boolish(_require_env("GROBID_ENABLED"), "GROBID_ENABLED"))
        OLLAMA_URL: str = _require_env("OLLAMA_URL")
        OLLAMA_BASE_URL: str = _require_env("OLLAMA_BASE_URL")
        CLAMAV_HOST: str = _require_env("CLAMAV_HOST")
        CLAMAV_PORT: int = int(_require_env("CLAMAV_PORT"))
        GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
        GROQ_MODEL: str = _require_env("GROQ_MODEL")
        GROQ_API_BASE: str = _require_env("GROQ_API_BASE")
        NVIDIA_API_KEY: Optional[str] = os.getenv("NVIDIA_API_KEY")
        NVIDIA_MODEL: str = _require_env("NVIDIA_MODEL")
        OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
        ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")

        # Redis / celery / integrations
        REDIS_ENABLED: bool = bool(_parse_boolish(_require_env("REDIS_ENABLED"), "REDIS_ENABLED"))
        REDIS_URL: str = _require_env("REDIS_URL")
        REDIS_HOST: str = _require_env("REDIS_HOST")
        REDIS_PORT: int = int(_require_env("REDIS_PORT"))
        CELERY_BROKER_URL: str = _require_env("CELERY_BROKER_URL")
        CELERY_RESULT_BACKEND: str = _require_env("CELERY_RESULT_BACKEND")
        CROSSREF_MAILTO: str = _require_env("CROSSREF_MAILTO")
        LLM_CACHE_TTL_SECONDS: int = int(os.getenv("LLM_CACHE_TTL_SECONDS", "3600"))

        # Pipeline tuning / feature toggles
        PIPELINE_GROBID_TIMEOUT_SECONDS: int = int(_require_env("PIPELINE_GROBID_TIMEOUT_SECONDS"))
        PIPELINE_DOCLING_TIMEOUT_SECONDS: int = int(_require_env("PIPELINE_DOCLING_TIMEOUT_SECONDS"))
        PIPELINE_REASONING_TIMEOUT_SECONDS: int = int(_require_env("PIPELINE_REASONING_TIMEOUT_SECONDS"))
        PIPELINE_SEMANTIC_TIMEOUT_SECONDS: int = int(_require_env("PIPELINE_SEMANTIC_TIMEOUT_SECONDS"))
        PIPELINE_ACQUIRE_TIMEOUT_SECONDS: float = float(_require_env("PIPELINE_ACQUIRE_TIMEOUT_SECONDS"))
        PIPELINE_DOCLING_SKIP_DIGITAL_PDF: bool = bool(
            _parse_boolish(_require_env("PIPELINE_DOCLING_SKIP_DIGITAL_PDF"), "PIPELINE_DOCLING_SKIP_DIGITAL_PDF")
        )
        PIPELINE_DOCLING_FORCE: bool = bool(
            _parse_boolish(_require_env("PIPELINE_DOCLING_FORCE"), "PIPELINE_DOCLING_FORCE")
        )
        ENABLE_NOUGAT_PARSER: bool = bool(
            _parse_boolish(_require_env("ENABLE_NOUGAT_PARSER"), "ENABLE_NOUGAT_PARSER")
        )
        ENABLE_NVIDIA_REASONER: bool = bool(
            _parse_boolish(_require_env("ENABLE_NVIDIA_REASONER"), "ENABLE_NVIDIA_REASONER")
        )
        USE_SCIBERT_CLASSIFICATION: bool = bool(
            _parse_boolish(os.getenv("USE_SCIBERT_CLASSIFICATION", "false"), "USE_SCIBERT_CLASSIFICATION")
        )

        def validate(self) -> None:
            if self.RETENTION_DAYS <= 0:
                raise ValueError("RETENTION_DAYS must be > 0")


settings = Settings()
settings.validate()
