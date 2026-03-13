
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.routers import auth, documents
from app.config.settings import settings
from app.middleware.request_id import RequestIdMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.routers.v1 import v1_router
from app.services.health_checks import get_readiness_payload
from contextlib import asynccontextmanager

# Initialize logging — kept commented out so terminal output remains visible during development
# from app.config.logging_config import setup_logging
# setup_logging()

# Phase 2: Silence Global AI Startup Noise
import os
import asyncio
import logging
# Optional structured logging for production environments.
if settings.ENABLE_STRUCTURED_LOGGING:
    from app.config.logging_config import setup_logging
    setup_logging()

# DISABLED: Auto-delete feature temporarily removed per user request
# from app.utils.cleanup import cleanup_old_uploads
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
from transformers import logging as transformers_logging
transformers_logging.set_verbosity_error()

# Basic logger for this module (terminal output preserved)
logger = logging.getLogger(__name__)

from app.pipeline.safety import safe_execution
from app.services.enhancement_manager import enhancement_manager


def _build_cors_origins(raw_origins: str) -> list[str]:
    origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

    # In local development, Next/Vite frequently shift to the next available port
    # (3001, 3002, etc.). Keep loopback origins open on common dev ports so the
    # browser does not fail CORS preflight with a generic "Failed to fetch".
    if settings.DEBUG:
        loopback_hosts = ("localhost", "127.0.0.1")
        dev_ports = tuple(range(3000, 3011)) + (4173, 5173)
        for host in loopback_hosts:
            for port in dev_ports:
                candidate = f"http://{host}:{port}"
                if candidate not in origins:
                    origins.append(candidate)

    return origins


def _cleanup_expired_uploads(*, upload_dir: str = "uploads", retention_days: int) -> int:
    if not os.path.isdir(upload_dir):
        return 0

    cutoff_epoch = datetime.now(timezone.utc).timestamp() - (retention_days * 86400)
    deleted = 0
    for entry in os.scandir(upload_dir):
        if not entry.is_file():
            continue
        try:
            if entry.stat().st_mtime < cutoff_epoch:
                os.remove(entry.path)
                deleted += 1
        except OSError as exc:
            logger.warning("Cleanup failed for %s: %s", entry.path, exc)
    return deleted


async def _periodic_file_cleanup(retention_days: int) -> None:
    while True:
        cleaned = _cleanup_expired_uploads(retention_days=retention_days)
        logger.info(
            "Scheduled file cleanup complete. Removed %d files older than %d days.",
            cleaned,
            retention_days,
        )
        await asyncio.sleep(24 * 60 * 60)


# ── Lifespan (replaces deprecated @app.on_event) ─────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan: startup and shutdown logic.
    Note: This project intentionally avoids automated pipeline testing at this stage.
    """
    # ── STARTUP ──
    # DISABLED: Auto-delete feature temporarily removed per user request
    # cleanup_task = asyncio.create_task(cleanup_old_uploads())
    cleanup_task = None
    enable_cleanup = settings.ENABLE_FILE_CLEANUP
    retention_days = int(settings.RETENTION_DAYS)
    if enable_cleanup:
        cleaned = _cleanup_expired_uploads(retention_days=retention_days)
        logger.info(
            "Startup file cleanup complete. Removed %d files older than %d days.",
            cleaned,
            retention_days,
        )
        cleanup_task = asyncio.create_task(_periodic_file_cleanup(retention_days))
    else:
        logger.info("File cleanup disabled (ENABLE_FILE_CLEANUP=false in .env).")

    with safe_execution("Application Startup"):
        # ── Supabase-py: reset interrupted jobs ───────────────────────────────
        try:
            from app.db.supabase_client import get_supabase_client
            sb = get_supabase_client()
            if sb is not None:
                result = sb.table("documents").select("id").eq("status", "PROCESSING").execute()
                interrupted = result.data or []
                if interrupted:
                    ids = [row["id"] for row in interrupted]
                    logger.info("Startup: Found %d interrupted jobs. Marking as FAILED.", len(ids))
                    sb.table("documents").update({
                        "status": "FAILED",
                        "error_message": "Processing interrupted by server restart.",
                    }).in_("id", ids).execute()
            else:
                logger.warning("Startup DB Link Status: UNCONFIGURED. App starting in degraded mode.")
        except Exception as e:
            logger.warning("Startup DB Link Status: UNREACHABLE. Error: %s", e)
            logger.info("Note: App is starting in degraded mode. DB-dependent endpoints will fail at request-time.")
                
        # Phase 2: AI Model Pre-loading
        from app.services.model_store import model_store
        from app.pipeline.intelligence.semantic_parser import get_semantic_parser
        from app.pipeline.intelligence.rag_engine import get_rag_engine
        
        logger.info("Startup: Pre-loading AI models into memory...")
        try:
            parser = get_semantic_parser()
            parser._load_model()
            model_store.set_model("scibert_tokenizer", parser.tokenizer)
            model_store.set_model("scibert_model", parser.model)
            logger.info("SciBERT loaded.")
            
            rag = get_rag_engine()
            model_store.set_model("rag_engine", rag)
            model_store.set_model("embedding_model", rag.embedding_model)
            logger.info("RAG Engine initialized.")
            
            logger.info("Startup: AI models loaded and registered successfully.")
        except Exception as e:
            logger.warning("AI Model Pre-load Warning: %s. Falling back to lazy-loading.", e)

        try:
            profile = enhancement_manager.refresh()
            logger.info("Enhancement capabilities loaded: %s", profile.to_dict())
        except Exception as e:
            logger.warning("Enhancement capability bootstrap failed: %s", e)

        try:
            from app.services.preview_renderer import preload_template_css
            preload_template_css()
            logger.info("Preview template CSS preloaded.")
        except Exception as e:
            logger.warning("Preview CSS preload failed: %s", e)

    yield  # App is running

    # ── SHUTDOWN ──
    if cleanup_task is not None:
        cleanup_task.cancel()
        try:
            await cleanup_task
        except asyncio.CancelledError:
            pass
    logger.info("ScholarForm AI shutting down...")


# ── App creation ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="ScholarForm AI Backend",
    description="Backend API for ScholarForm AI with Supabase Auth",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Configuration (from environment + local dev fallbacks)
origins = _build_cors_origins(settings.CORS_ORIGINS)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "X-Requested-With",
        "Accept",
        "X-Request-Id",
        "Idempotency-Key",
    ],
)

# Rate Limiting Middleware (DoS Protection)
app.add_middleware(RateLimitMiddleware, requests_per_minute=60)

# Security Headers Middleware (CSP, X-Frame-Options, etc.)
from app.middleware.security_headers import SecurityHeadersMiddleware, MaxBodySizeMiddleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(MaxBodySizeMiddleware, max_size=60 * 1024 * 1024)  # 60MB global limit

# HTTPS Redirect (production only)
if settings.FORCE_HTTPS:
    from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

    app.add_middleware(HTTPSRedirectMiddleware)

    @app.middleware("http")
    async def add_hsts_header(request: Request, call_next):
        response = await call_next(request)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        return response

app.add_middleware(RequestIdMiddleware)

# Include Routers
app.include_router(v1_router)
app.include_router(auth.router)
app.include_router(documents.router)

from app.routers import templates
app.include_router(templates.templates_router, prefix="/api/templates", tags=["Templates"])

# Metrics and Monitoring
from app.routers import metrics
app.include_router(metrics.router)

# Feedback Loop (Industry Standard)
from app.routers import feedback
app.include_router(feedback.router, prefix="/api")

# Streaming Responses (Next-Gen)
from app.routers import stream
app.include_router(stream.router)

# Live Preview (Formatter Mode B)
from app.routers import preview
app.include_router(preview.router)

# Document Generator (generate from scratch — no upload needed)
from app.routers import generator
app.include_router(generator.router, prefix="/api")


@app.get("/ready")
async def readiness_probe():
    """
    Readiness probe for operational environments (K8s, Docker).
    Checks availability of critical dependencies and AI models.
    """
    payload, status_code = await get_readiness_payload()
    return JSONResponse(content=payload, status_code=status_code)

    import httpx
    from app.db.supabase_client import get_supabase_client, check_supabase_health
    from app.services.model_store import model_store
    
    checks = {}
    is_ready = True
    
    # ── Check Supabase ──
    try:
        sb_health = check_supabase_health()
        checks["database"] = sb_health.get("status", "unknown")
        if sb_health.get("status") != "healthy":
            is_ready = False
    except Exception as e:
        checks["database"] = f"unhealthy: {str(e)}"
        is_ready = False

    # ── Check GROBID ──
    try:
        async with httpx.AsyncClient(timeout=2) as client:
            response = await client.get(f"{settings.GROBID_URL}/api/isalive")
            checks["grobid"] = "ready" if response.status_code == 200 else "unavailable"
    except (httpx.RequestError, Exception):
        checks["grobid"] = "unavailable"

    # ── Check Ollama/Local LLM ──
    try:
        from app.services.llm_service import check_health as llm_check_health
        results = await llm_check_health()
        checks["llm_status"] = results
    except Exception:
        checks["llm_status"] = "unknown"

    # ── Check AI Models ──
    try:
        if model_store.get_model("scibert_model") is not None:
            checks["ai_models"] = "loaded"
        else:
            checks["ai_models"] = "not_loaded"
            is_ready = False
    except Exception:
        checks["ai_models"] = "error"
        is_ready = False

    return JSONResponse(
        content={
            "ready": is_ready, 
            "checks": checks,
            "timestamp": datetime.now(timezone.utc).isoformat()
        },
        status_code=200 if is_ready else 503
    )

@app.get("/")
async def root():
    return {"message": "ScholarForm AI Backend is running"}

@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    Returns status of Supabase DB, AI models, and Ollama server.
    """
    import httpx
    from app.db.supabase_client import check_supabase_health

    health_status = {
        "status": "healthy",
        "version": "1.0.0",
        "components": {},
    }

    # Check Supabase DB
    try:
        sb_health = check_supabase_health()
        health_status["components"]["supabase_db"] = sb_health.get("status", "unknown")
        if sb_health.get("status") != "healthy":
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["components"]["supabase_db"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"

    # Check Ollama server (non-blocking)
    try:
        async with httpx.AsyncClient(timeout=2) as client:
            response = await client.get(f"{settings.OLLAMA_URL}/api/tags")
            if response.status_code == 200:
                health_status["components"]["ollama"] = "healthy"
            else:
                health_status["components"]["ollama"] = "unhealthy"
                health_status["status"] = "degraded"
    except (httpx.RequestError, Exception):
        health_status["components"]["ollama"] = "unavailable (fallback active)"
        health_status["status"] = "degraded"

    # Check AI models
    try:
        from app.services.model_store import model_store
        if model_store.get_model("scibert_model") is not None:
            health_status["components"]["ai_models"] = "loaded"
        else:
            health_status["components"]["ai_models"] = "not_loaded"
    except Exception:
        health_status["components"]["ai_models"] = "error"

    # Return 503 if any component is degraded
    status_code = 200 if health_status["status"] == "healthy" else 503
    return JSONResponse(content=health_status, status_code=status_code)


