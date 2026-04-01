"""
Application settings loaded from .env.

Policy:
- Do not hardcode runtime configuration in code.
- Read configuration from environment variables (via .env in local development).
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Iterable, Optional

logger = logging.getLogger(__name__)
BACKEND_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = BACKEND_ROOT / ".env"
DEFAULT_LOCAL_CORS_ORIGINS = ",".join(
    (
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    )
)

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


def _normalize_cors_origins(value) -> str:
    if value is None:
        return DEFAULT_LOCAL_CORS_ORIGINS

    origins = [origin.strip() for origin in str(value).split(",") if origin.strip()]
    filtered = [origin for origin in origins if "<your-frontend-domain>" not in origin]
    if filtered:
        return ",".join(filtered)
    return DEFAULT_LOCAL_CORS_ORIGINS


DEFAULT_GROBID_URL = "http://localhost:8070"
DEFAULT_GROBID_HEALTH_PATH = "/api/isalive"
DEFAULT_GENERIC_HEALTH_PATH = "/"


def _normalize_base_url(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip()
    if not normalized:
        return None
    return normalized.rstrip("/")


def _split_urls(raw_value: str | None) -> list[str]:
    if raw_value is None:
        return []
    values = []
    for part in str(raw_value).split(","):
        normalized = _normalize_base_url(part)
        if normalized:
            values.append(normalized)
    return values


def _dedupe(values: Iterable[str]) -> list[str]:
    deduped: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value in seen:
            continue
        deduped.append(value)
        seen.add(value)
    return deduped


def _resolve_service_urls(
    raw_urls_value: str | None,
    single_url_values: Iterable[str | None],
    *,
    default_urls: Iterable[str] = (),
) -> list[str]:
    urls = _split_urls(raw_urls_value)
    if urls:
        return _dedupe(urls)

    fallback_urls = [_normalize_base_url(value) for value in single_url_values]
    filtered_fallback_urls = [value for value in fallback_urls if value]
    if filtered_fallback_urls:
        return _dedupe(filtered_fallback_urls)

    return _dedupe([value for value in default_urls if value])


def _normalize_health_path(value: str | None, *, default_path: str) -> str:
    normalized = str(value or default_path).strip()
    if not normalized:
        normalized = default_path
    if not normalized.startswith("/"):
        normalized = f"/{normalized}"
    if len(normalized) > 1:
        normalized = normalized.rstrip("/")
    return normalized or default_path


class _ServiceUrlMixin:
    def get_grobid_urls(self) -> list[str]:
        return _resolve_service_urls(
            getattr(self, "GROBID_URLS", None),
            (
                getattr(self, "GROBID_URL", None),
                getattr(self, "GROBID_BASE_URL", None),
            ),
            default_urls=(DEFAULT_GROBID_URL,),
        )

    def get_docling_urls(self) -> list[str]:
        return _resolve_service_urls(
            getattr(self, "DOCLING_URLS", None),
            (getattr(self, "DOCLING_URL", None),),
        )

    def get_ocr_urls(self) -> list[str]:
        return _resolve_service_urls(
            getattr(self, "OCR_URLS", None),
            (getattr(self, "OCR_URL", None),),
        )

    def get_docx_converter_urls(self) -> list[str]:
        return _resolve_service_urls(
            getattr(self, "DOCX_CONVERTER_URLS", None),
            (getattr(self, "DOCX_CONVERTER_URL", None),),
        )

    def get_nougat_urls(self) -> list[str]:
        return _resolve_service_urls(
            getattr(self, "NOUGAT_URLS", None),
            (getattr(self, "NOUGAT_URL", None),),
        )

    def get_scibert_urls(self) -> list[str]:
        return _resolve_service_urls(
            getattr(self, "SCIBERT_URLS", None),
            (getattr(self, "SCIBERT_URL", None),),
        )

    def get_service_health_path(self, service_name: str) -> str:
        normalized_name = service_name.strip().lower()
        if normalized_name == "grobid":
            return _normalize_health_path(
                getattr(self, "GROBID_HEALTH_PATH", DEFAULT_GROBID_HEALTH_PATH),
                default_path=DEFAULT_GROBID_HEALTH_PATH,
            )
        if normalized_name == "docling":
            return _normalize_health_path(
                getattr(self, "DOCLING_HEALTH_PATH", DEFAULT_GENERIC_HEALTH_PATH),
                default_path=DEFAULT_GENERIC_HEALTH_PATH,
            )
        if normalized_name == "ocr":
            return _normalize_health_path(
                getattr(self, "OCR_HEALTH_PATH", DEFAULT_GENERIC_HEALTH_PATH),
                default_path=DEFAULT_GENERIC_HEALTH_PATH,
            )
        if normalized_name == "docx_converter":
            return _normalize_health_path(
                getattr(self, "DOCX_CONVERTER_HEALTH_PATH", DEFAULT_GENERIC_HEALTH_PATH),
                default_path=DEFAULT_GENERIC_HEALTH_PATH,
            )
        if normalized_name == "nougat":
            return _normalize_health_path(
                getattr(self, "NOUGAT_HEALTH_PATH", DEFAULT_GENERIC_HEALTH_PATH),
                default_path=DEFAULT_GENERIC_HEALTH_PATH,
            )
        if normalized_name == "scibert":
            return _normalize_health_path(
                getattr(self, "SCIBERT_HEALTH_PATH", DEFAULT_GENERIC_HEALTH_PATH),
                default_path=DEFAULT_GENERIC_HEALTH_PATH,
            )
        raise ValueError(f"Unknown service_name: {service_name!r}")


if _PS:
    class Settings(_ServiceUrlMixin, BaseSettings):
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
        SIGNED_URL_SECRET: Optional[str] = None

        # Billing
        STRIPE_API_KEY: Optional[str] = None
        STRIPE_WEBHOOK_SECRET: Optional[str] = None

        # Upload Limits
        MAX_FILE_SIZE: int
        MAX_BATCH_FILES: int
        UPLOADS_PER_MINUTE: int

        # Deployment
        FORCE_HTTPS: bool = Field(
            ...,
            description="Enforce HTTPS redirect and HSTS header",
        )
        GLOBAL_RATE_LIMIT_PER_MINUTE: int = 120
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
        GROBID_URL: str = DEFAULT_GROBID_URL
        GROBID_BASE_URL: str = DEFAULT_GROBID_URL
        GROBID_URLS: str = ""
        GROBID_HEALTH_PATH: str = DEFAULT_GROBID_HEALTH_PATH
        GROBID_TIMEOUT: int
        GROBID_MAX_RETRIES: int
        GROBID_ENABLED: bool
        USE_DOCLING_FALLBACK: bool = True
        PYMUPDF_FALLBACK: bool = True

        DOCLING_URL: Optional[str] = None
        DOCLING_URLS: str = ""
        DOCLING_HEALTH_PATH: str = DEFAULT_GENERIC_HEALTH_PATH
        OCR_URL: Optional[str] = None
        OCR_URLS: str = ""
        OCR_HEALTH_PATH: str = DEFAULT_GENERIC_HEALTH_PATH
        DOCX_CONVERTER_URL: Optional[str] = None
        DOCX_CONVERTER_URLS: str = ""
        DOCX_CONVERTER_HEALTH_PATH: str = DEFAULT_GENERIC_HEALTH_PATH
        NOUGAT_URL: Optional[str] = None
        NOUGAT_URLS: str = ""
        NOUGAT_HEALTH_PATH: str = DEFAULT_GENERIC_HEALTH_PATH
        SCIBERT_URL: Optional[str] = None
        SCIBERT_URLS: str = ""
        SCIBERT_HEALTH_PATH: str = DEFAULT_GENERIC_HEALTH_PATH

        OLLAMA_URL: str
        OLLAMA_BASE_URL: str
        CLAMAV_HOST: str
        CLAMAV_PORT: int

        GROQ_API_KEY: Optional[str] = None
        GROQ_MODEL: str
        GROQ_API_BASE: str
        SENTRY_DSN: Optional[str] = None
        LLM_PROVIDER_TIMEOUT_SECONDS: int = 15
        EXTERNAL_CIRCUIT_BREAKER_ENABLED: bool = True
        EXTERNAL_CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = 3
        EXTERNAL_CIRCUIT_BREAKER_RESET_SECONDS: int = 60

        NVIDIA_API_KEY: Optional[str] = None
        NVIDIA_MODEL: str
        OPENAI_API_KEY: Optional[str] = None
        ANTHROPIC_API_KEY: Optional[str] = None
        OPENROUTER_API_KEY: Optional[str] = None
        OPENROUTER_MODEL: str = "openai/gpt-4o-mini"
        OPENROUTER_API_BASE: str = "https://openrouter.ai/api/v1"

        # Redis / celery / integrations
        REDIS_ENABLED: bool
        REDIS_URL: str
        REDIS_HOST: str
        REDIS_PORT: int
        CELERY_BROKER_URL: str
        CELERY_RESULT_BACKEND: str
        CROSSREF_MAILTO: str
        LLM_CACHE_TTL_SECONDS: int = 3600
        READINESS_CACHE_TTL_SECONDS: int = 15
        HEALTH_CACHE_TTL_SECONDS: int = 15
        CSL_SEARCH_CACHE_TTL_SECONDS: int = 300
        CSL_FETCH_CACHE_TTL_SECONDS: int = 1800
        GENERATOR_SESSION_CACHE_TTL_SECONDS: float = 2.0
        GENERATOR_MESSAGES_CACHE_TTL_SECONDS: float = 1.0
        GENERATOR_SESSION_LIST_CACHE_TTL_SECONDS: float = 3.0
        GENERATOR_DOCUMENT_CACHE_TTL_SECONDS: float = 2.0
        DOCUMENT_STATUS_CACHE_TTL_SECONDS: float = 1.0

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
        SCIBERT_AUTO_ENABLE_FROM_BENCHMARK: bool = True
        SCIBERT_MIN_BENCHMARK_F1: float = 0.85
        SCIBERT_BENCHMARK_STATE_PATH: str = ".metrics/scibert_benchmark_state.json"
        LOW_MEMORY_MODE: bool = False
        PRELOAD_AI_MODELS: bool = True
        RAG_USE_TRANSFORMERS: bool = True
        DEFAULT_FAST_MODE: bool = False
        CROSSREF_MAX_WORKERS: int = 4
        ENHANCEMENT_QUEUE_MIN_SECONDS: float = 5.0
        VLLM_ADOPTION_ENABLED: bool = True
        VLLM_TARGET_MODEL: str = "meta-llama/Meta-Llama-3.1-8B-Instruct"
        VLLM_TARGET_GPU: str = "L4 24GB"
        VLLM_REQUESTS_PER_HOUR_THRESHOLD: int = 2000
        VLLM_DAILY_TOKENS_THRESHOLD: int = 5000000

        model_config = {
            "env_file": ENV_FILE,
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
            "USE_DOCLING_FALLBACK",
            "PYMUPDF_FALLBACK",
            "REDIS_ENABLED",
            "PIPELINE_DOCLING_SKIP_DIGITAL_PDF",
            "PIPELINE_DOCLING_FORCE",
            "ENABLE_NOUGAT_PARSER",
            "ENABLE_NVIDIA_REASONER",
            "USE_SCIBERT_CLASSIFICATION",
            "SCIBERT_AUTO_ENABLE_FROM_BENCHMARK",
            "LOW_MEMORY_MODE",
            "PRELOAD_AI_MODELS",
            "RAG_USE_TRANSFORMERS",
            "DEFAULT_FAST_MODE",
            "VLLM_ADOPTION_ENABLED",
            "EXTERNAL_CIRCUIT_BREAKER_ENABLED",
            mode="before",
        )
        @classmethod
        def parse_bool_fields(cls, value, info):
            return _parse_boolish(value, info.field_name)

        @field_validator("CORS_ORIGINS", mode="before")
        @classmethod
        def normalize_cors_origins(cls, value):
            return _normalize_cors_origins(value)

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

            # URL list precedence: *_URLS > single *_URL.
            grobid_urls = self.get_grobid_urls()
            if grobid_urls:
                self.GROBID_URL = grobid_urls[0]
                self.GROBID_BASE_URL = grobid_urls[0]
            else:
                self.GROBID_URL = DEFAULT_GROBID_URL
                self.GROBID_BASE_URL = DEFAULT_GROBID_URL

            self.GROBID_HEALTH_PATH = self.get_service_health_path("grobid")
            self.DOCLING_HEALTH_PATH = self.get_service_health_path("docling")
            self.OCR_HEALTH_PATH = self.get_service_health_path("ocr")
            self.DOCX_CONVERTER_HEALTH_PATH = self.get_service_health_path("docx_converter")

            if self.RETENTION_DAYS <= 0:
                raise ValueError("RETENTION_DAYS must be > 0")


else:
    try:
        from dotenv import load_dotenv

        load_dotenv(ENV_FILE, override=True)
    except Exception:
        pass

    class Settings(_ServiceUrlMixin):  # type: ignore[no-redef]
        # Supabase Auth
        SUPABASE_URL: Optional[str] = os.getenv("SUPABASE_URL")
        SUPABASE_ANON_KEY: Optional[str] = os.getenv("SUPABASE_ANON_KEY")
        SUPABASE_JWKS_URL: Optional[str] = os.getenv("SUPABASE_JWKS_URL")
        SUPABASE_JWT_SECRET: Optional[str] = os.getenv("SUPABASE_JWT_SECRET")
        SUPABASE_SERVICE_ROLE_KEY: Optional[str] = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        SUPABASE_DB_URL: Optional[str] = os.getenv("SUPABASE_DB_URL")

        # Security
        ALGORITHM: str = _require_env("ALGORITHM")
        CORS_ORIGINS: str = _normalize_cors_origins(os.getenv("CORS_ORIGINS"))
        SIGNED_URL_SECRET: Optional[str] = os.getenv("SIGNED_URL_SECRET")

        # Billing
        STRIPE_API_KEY: Optional[str] = os.getenv("STRIPE_API_KEY")
        STRIPE_WEBHOOK_SECRET: Optional[str] = os.getenv("STRIPE_WEBHOOK_SECRET")

        # Upload Limits
        MAX_FILE_SIZE: int = int(_require_env("MAX_FILE_SIZE"))
        MAX_BATCH_FILES: int = int(_require_env("MAX_BATCH_FILES"))
        UPLOADS_PER_MINUTE: int = int(_require_env("UPLOADS_PER_MINUTE"))

        # Deployment
        FORCE_HTTPS: bool = bool(_parse_boolish(_require_env("FORCE_HTTPS"), "FORCE_HTTPS"))
        GLOBAL_RATE_LIMIT_PER_MINUTE: int = int(os.getenv("GLOBAL_RATE_LIMIT_PER_MINUTE", "120"))
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
        GROBID_URL: str = os.getenv("GROBID_URL", DEFAULT_GROBID_URL)
        GROBID_BASE_URL: str = os.getenv("GROBID_BASE_URL", GROBID_URL)
        GROBID_URLS: str = os.getenv("GROBID_URLS", "")
        GROBID_HEALTH_PATH: str = os.getenv("GROBID_HEALTH_PATH", DEFAULT_GROBID_HEALTH_PATH)
        GROBID_TIMEOUT: int = int(_require_env("GROBID_TIMEOUT"))
        GROBID_MAX_RETRIES: int = int(_require_env("GROBID_MAX_RETRIES"))
        GROBID_ENABLED: bool = bool(_parse_boolish(_require_env("GROBID_ENABLED"), "GROBID_ENABLED"))
        USE_DOCLING_FALLBACK: bool = bool(
            _parse_boolish(os.getenv("USE_DOCLING_FALLBACK", "true"), "USE_DOCLING_FALLBACK")
        )
        PYMUPDF_FALLBACK: bool = bool(
            _parse_boolish(os.getenv("PYMUPDF_FALLBACK", "true"), "PYMUPDF_FALLBACK")
        )
        DOCLING_URL: Optional[str] = os.getenv("DOCLING_URL")
        DOCLING_URLS: str = os.getenv("DOCLING_URLS", "")
        DOCLING_HEALTH_PATH: str = os.getenv("DOCLING_HEALTH_PATH", DEFAULT_GENERIC_HEALTH_PATH)
        OCR_URL: Optional[str] = os.getenv("OCR_URL")
        OCR_URLS: str = os.getenv("OCR_URLS", "")
        OCR_HEALTH_PATH: str = os.getenv("OCR_HEALTH_PATH", DEFAULT_GENERIC_HEALTH_PATH)
        DOCX_CONVERTER_URL: Optional[str] = os.getenv("DOCX_CONVERTER_URL")
        DOCX_CONVERTER_URLS: str = os.getenv("DOCX_CONVERTER_URLS", "")
        DOCX_CONVERTER_HEALTH_PATH: str = os.getenv(
            "DOCX_CONVERTER_HEALTH_PATH",
            DEFAULT_GENERIC_HEALTH_PATH,
        )
        NOUGAT_URL: Optional[str] = os.getenv("NOUGAT_URL")
        NOUGAT_URLS: str = os.getenv("NOUGAT_URLS", "")
        NOUGAT_HEALTH_PATH: str = os.getenv("NOUGAT_HEALTH_PATH", DEFAULT_GENERIC_HEALTH_PATH)
        SCIBERT_URL: Optional[str] = os.getenv("SCIBERT_URL")
        SCIBERT_URLS: str = os.getenv("SCIBERT_URLS", "")
        SCIBERT_HEALTH_PATH: str = os.getenv("SCIBERT_HEALTH_PATH", DEFAULT_GENERIC_HEALTH_PATH)
        OLLAMA_URL: str = _require_env("OLLAMA_URL")
        OLLAMA_BASE_URL: str = _require_env("OLLAMA_BASE_URL")
        CLAMAV_HOST: str = _require_env("CLAMAV_HOST")
        CLAMAV_PORT: int = int(_require_env("CLAMAV_PORT"))
        GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
        GROQ_MODEL: str = _require_env("GROQ_MODEL")
        GROQ_API_BASE: str = _require_env("GROQ_API_BASE")
        SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")
        LLM_PROVIDER_TIMEOUT_SECONDS: int = int(os.getenv("LLM_PROVIDER_TIMEOUT_SECONDS", "15"))
        EXTERNAL_CIRCUIT_BREAKER_ENABLED: bool = bool(
            _parse_boolish(
                os.getenv("EXTERNAL_CIRCUIT_BREAKER_ENABLED", "true"),
                "EXTERNAL_CIRCUIT_BREAKER_ENABLED",
            )
        )
        EXTERNAL_CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = int(
            os.getenv("EXTERNAL_CIRCUIT_BREAKER_FAILURE_THRESHOLD", "3")
        )
        EXTERNAL_CIRCUIT_BREAKER_RESET_SECONDS: int = int(
            os.getenv("EXTERNAL_CIRCUIT_BREAKER_RESET_SECONDS", "60")
        )
        NVIDIA_API_KEY: Optional[str] = os.getenv("NVIDIA_API_KEY")
        NVIDIA_MODEL: str = _require_env("NVIDIA_MODEL")
        OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
        ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
        OPENROUTER_API_KEY: Optional[str] = os.getenv("OPENROUTER_API_KEY")
        OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
        OPENROUTER_API_BASE: str = os.getenv("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1")

        # Redis / celery / integrations
        REDIS_ENABLED: bool = bool(_parse_boolish(_require_env("REDIS_ENABLED"), "REDIS_ENABLED"))
        REDIS_URL: str = _require_env("REDIS_URL")
        REDIS_HOST: str = _require_env("REDIS_HOST")
        REDIS_PORT: int = int(_require_env("REDIS_PORT"))
        CELERY_BROKER_URL: str = _require_env("CELERY_BROKER_URL")
        CELERY_RESULT_BACKEND: str = _require_env("CELERY_RESULT_BACKEND")
        CROSSREF_MAILTO: str = _require_env("CROSSREF_MAILTO")
        LLM_CACHE_TTL_SECONDS: int = int(os.getenv("LLM_CACHE_TTL_SECONDS", "3600"))
        READINESS_CACHE_TTL_SECONDS: int = int(os.getenv("READINESS_CACHE_TTL_SECONDS", "15"))
        HEALTH_CACHE_TTL_SECONDS: int = int(os.getenv("HEALTH_CACHE_TTL_SECONDS", "15"))
        CSL_SEARCH_CACHE_TTL_SECONDS: int = int(os.getenv("CSL_SEARCH_CACHE_TTL_SECONDS", "300"))
        CSL_FETCH_CACHE_TTL_SECONDS: int = int(os.getenv("CSL_FETCH_CACHE_TTL_SECONDS", "1800"))
        GENERATOR_SESSION_CACHE_TTL_SECONDS: float = float(
            os.getenv("GENERATOR_SESSION_CACHE_TTL_SECONDS", "2")
        )
        GENERATOR_MESSAGES_CACHE_TTL_SECONDS: float = float(
            os.getenv("GENERATOR_MESSAGES_CACHE_TTL_SECONDS", "1")
        )
        GENERATOR_SESSION_LIST_CACHE_TTL_SECONDS: float = float(
            os.getenv("GENERATOR_SESSION_LIST_CACHE_TTL_SECONDS", "3")
        )
        GENERATOR_DOCUMENT_CACHE_TTL_SECONDS: float = float(
            os.getenv("GENERATOR_DOCUMENT_CACHE_TTL_SECONDS", "2")
        )
        DOCUMENT_STATUS_CACHE_TTL_SECONDS: float = float(
            os.getenv("DOCUMENT_STATUS_CACHE_TTL_SECONDS", "1")
        )

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
        SCIBERT_AUTO_ENABLE_FROM_BENCHMARK: bool = bool(
            _parse_boolish(
                os.getenv("SCIBERT_AUTO_ENABLE_FROM_BENCHMARK", "true"),
                "SCIBERT_AUTO_ENABLE_FROM_BENCHMARK",
            )
        )
        SCIBERT_MIN_BENCHMARK_F1: float = float(os.getenv("SCIBERT_MIN_BENCHMARK_F1", "0.85"))
        SCIBERT_BENCHMARK_STATE_PATH: str = os.getenv(
            "SCIBERT_BENCHMARK_STATE_PATH",
            ".metrics/scibert_benchmark_state.json",
        )
        LOW_MEMORY_MODE: bool = bool(
            _parse_boolish(os.getenv("LOW_MEMORY_MODE", "false"), "LOW_MEMORY_MODE")
        )
        PRELOAD_AI_MODELS: bool = bool(
            _parse_boolish(os.getenv("PRELOAD_AI_MODELS", "true"), "PRELOAD_AI_MODELS")
        )
        RAG_USE_TRANSFORMERS: bool = bool(
            _parse_boolish(os.getenv("RAG_USE_TRANSFORMERS", "true"), "RAG_USE_TRANSFORMERS")
        )
        DEFAULT_FAST_MODE: bool = bool(
            _parse_boolish(os.getenv("DEFAULT_FAST_MODE", "false"), "DEFAULT_FAST_MODE")
        )
        CROSSREF_MAX_WORKERS: int = int(os.getenv("CROSSREF_MAX_WORKERS", "4"))
        ENHANCEMENT_QUEUE_MIN_SECONDS: float = float(os.getenv("ENHANCEMENT_QUEUE_MIN_SECONDS", "5"))
        VLLM_ADOPTION_ENABLED: bool = bool(
            _parse_boolish(os.getenv("VLLM_ADOPTION_ENABLED", "true"), "VLLM_ADOPTION_ENABLED")
        )
        VLLM_TARGET_MODEL: str = os.getenv(
            "VLLM_TARGET_MODEL",
            "meta-llama/Meta-Llama-3.1-8B-Instruct",
        )
        VLLM_TARGET_GPU: str = os.getenv("VLLM_TARGET_GPU", "L4 24GB")
        VLLM_REQUESTS_PER_HOUR_THRESHOLD: int = int(
            os.getenv("VLLM_REQUESTS_PER_HOUR_THRESHOLD", "2000")
        )
        VLLM_DAILY_TOKENS_THRESHOLD: int = int(
            os.getenv("VLLM_DAILY_TOKENS_THRESHOLD", "5000000")
        )

        def validate(self) -> None:
            grobid_urls = self.get_grobid_urls()
            if grobid_urls:
                self.GROBID_URL = grobid_urls[0]
                self.GROBID_BASE_URL = grobid_urls[0]
            else:
                self.GROBID_URL = DEFAULT_GROBID_URL
                self.GROBID_BASE_URL = DEFAULT_GROBID_URL

            self.GROBID_HEALTH_PATH = self.get_service_health_path("grobid")
            self.DOCLING_HEALTH_PATH = self.get_service_health_path("docling")
            self.OCR_HEALTH_PATH = self.get_service_health_path("ocr")
            self.DOCX_CONVERTER_HEALTH_PATH = self.get_service_health_path("docx_converter")
            self.NOUGAT_HEALTH_PATH = self.get_service_health_path("nougat")
            self.SCIBERT_HEALTH_PATH = self.get_service_health_path("scibert")

            if self.RETENTION_DAYS <= 0:
                raise ValueError("RETENTION_DAYS must be > 0")


settings = Settings()
settings.validate()
