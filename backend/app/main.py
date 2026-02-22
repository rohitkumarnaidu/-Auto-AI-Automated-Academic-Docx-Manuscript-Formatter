
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.routers import auth, documents
from app.config.settings import settings
from app.middleware.rate_limit import RateLimitMiddleware
from contextlib import asynccontextmanager

# Initialize logging — kept commented out so terminal output remains visible during development
# from app.config.logging_config import setup_logging
# setup_logging()

# Phase 2: Silence Global AI Startup Noise
import os
import asyncio
import logging
# DISABLED: Auto-delete feature temporarily removed per user request
# from app.utils.cleanup import cleanup_old_uploads
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
from transformers import logging as transformers_logging
transformers_logging.set_verbosity_error()

# Basic logger for this module (terminal output preserved)
logger = logging.getLogger(__name__)

from app.pipeline.safety import safe_execution


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

    yield  # App is running

    # ── SHUTDOWN ──
    logger.info("ScholarForm AI shutting down...")


# ── App creation ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="ScholarForm AI Backend",
    description="Backend API for ScholarForm AI with Supabase Auth",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Configuration (from environment)
origins = settings.CORS_ORIGINS.split(",") if hasattr(settings, 'CORS_ORIGINS') and settings.CORS_ORIGINS else [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

# Include Routers
app.include_router(auth.router)
app.include_router(documents.router)

# Metrics and Monitoring
from app.routers import metrics
app.include_router(metrics.router)

# Feedback Loop (Industry Standard)
from app.routers import feedback
app.include_router(feedback.router, prefix="/api")

# Streaming Responses (Next-Gen)
from app.routers import stream
app.include_router(stream.router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global Safety Net: Catches any unhandled exception to prevent server crash.
    Returns 500 but keeps the server alive.
    """
    with safe_execution("Global Exception Handler"):
        logger.error("Unhandled exception: %s", exc, exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "An internal server error occurred."},
        )


@app.get("/ready")
async def readiness_probe():
    """
    Readiness probe for operational environments.
    Checks availability of critical dependencies.
    """
    from app.db.supabase_client import get_supabase_client
    checks = {}
    
    # Check Supabase
    try:
        sb = get_supabase_client()
        if sb:
            sb.table("documents").select("id", count="exact").limit(0).execute()
            checks["supabase"] = "healthy"
        else:
            checks["supabase"] = "unavailable"
    except Exception as e:
        checks["supabase"] = f"unhealthy: {str(e)}"

    # Check GROBID (if configured)
    from app.pipeline.services import get_grobid_client
    try:
        grobid = get_grobid_client()
        if grobid:
            # Simple ping if available or just check URL
            checks["grobid"] = "available"
        else:
            checks["grobid"] = "not_configured"
    except:
        checks["grobid"] = "unhealthy"

    # Check Ollama/Local LLM
    try:
        from app.services.llm_service import check_health as llm_check_health
        results = await llm_check_health()
        checks["llm_status"] = results
    except:
        checks["llm_status"] = "unknown"

    all_ready = all(v == "healthy" or v == "available" or isinstance(v, dict) for v in checks.values())
    
    return {
        "ready": all_ready,
        "checks": checks,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

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
            response = await client.get("http://localhost:11434/api/tags")
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

@app.get("/ready")
async def readiness_probe():
    """
    Readiness probe for deployment environments (K8s, Docker).
    Checks if critical components are ready to serve traffic.
    """
    import httpx
    from app.db.supabase_client import check_supabase_health
    from app.services.model_store import model_store
    
    checks = {}
    is_ready = True
    
    # Check Database
    try:
        sb_health = check_supabase_health()
        checks["database"] = sb_health.get("status", "unknown")
        if sb_health.get("status") != "healthy":
            is_ready = False
    except Exception as e:
        checks["database"] = f"unhealthy: {str(e)}"
        is_ready = False
        
    # Check GROBID (Optional but important)
    try:
        async with httpx.AsyncClient(timeout=2) as client:
            response = await client.get("http://localhost:8070/api/isalive")
            checks["grobid"] = "ready" if response.status_code == 200 else "unavailable"
    except (httpx.RequestError, Exception):
        checks["grobid"] = "unavailable"
        
    # Check AI Models
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
        content={"ready": is_ready, "checks": checks},
        status_code=200 if is_ready else 503
    )

