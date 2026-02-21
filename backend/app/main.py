
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
    with safe_execution("Application Startup"):
        # ── Supabase-py: reset interrupted jobs ───────────────────────────────
        try:
            from app.db.supabase_client import get_supabase_client
            sb = get_supabase_client()
            if sb is not None:
                result = sb.table("documents").select("id").eq("status", "RUNNING").execute()
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

# Include Routers
app.include_router(auth.router)
app.include_router(documents.router)

# Metrics and Monitoring
from app.routers import metrics
app.include_router(metrics.router)

# Feedback Loop (Industry Standard)
from app.routers import feedback
app.include_router(feedback.router)

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
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error (Safely Handled)", "error": str(exc)},
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

    return health_status