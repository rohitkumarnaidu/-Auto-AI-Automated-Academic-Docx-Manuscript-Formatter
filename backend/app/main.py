
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, documents
from app.config.settings import settings
from app.middleware.rate_limit import RateLimitMiddleware

# Initialize logging FIRST (before any other imports that might log)
#from app.config.logging_config import setup_logging
# logger = setup_logging()

# Phase 2: Silence Global AI Startup Noise
import os
import asyncio
# DISABLED: Auto-delete feature temporarily removed per user request
# from app.utils.cleanup import cleanup_old_uploads
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
from transformers import logging as transformers_logging
transformers_logging.set_verbosity_error()

app = FastAPI(
    title="ScholarForm AI Backend",
    description="Backend API for ScholarForm AI with Supabase Auth",
    version="1.0.0"
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

from fastapi import Request
from fastapi.responses import JSONResponse
from app.pipeline.safety import safe_execution

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global Safety Net: Catches any unhandled exception to prevent server crash.
    Returns 500 but keeps the server alive.
    """
    with safe_execution("Global Exception Handler"):
        # We just log it here, the safe_execution will handle the traceback logging
        # But we need to return a response
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error (Safely Handled)", "error": str(exc)},
        )

@app.on_event("startup")
async def startup_event():
    """
    Perform startup tasks, including cleaning up interrupted jobs.
    Note: This project intentionally avoids automated pipeline testing at this stage.
    """
    with safe_execution("Application Startup"):
        # DISABLED: Auto-delete feature temporarily removed per user request
        # asyncio.create_task(cleanup_old_uploads())
        
        # ── Old ORM startup (kept for reference, replaced by supabase-py) ──────
        # from app.db.session import SessionLocal
        # from app.models import Document
        # from sqlalchemy.exc import OperationalError
        # db = SessionLocal()
        # interrupted_docs = db.query(Document).filter(Document.status == "RUNNING").all()
        # for doc in interrupted_docs: doc.status = "FAILED"; db.commit()

        # ── Supabase-py: reset interrupted jobs ───────────────────────────────
        try:
            from app.db.supabase_client import get_supabase_client
            sb = get_supabase_client()
            if sb is not None:
                # Find all RUNNING jobs from the previous session
                result = sb.table("documents").select("id").eq("status", "RUNNING").execute()
                interrupted = result.data or []
                if interrupted:
                    ids = [row["id"] for row in interrupted]
                    print(f"Startup: Found {len(ids)} interrupted jobs. Marking as FAILED.")
                    sb.table("documents").update({
                        "status": "FAILED",
                        "error_message": "Processing interrupted by server restart.",
                    }).in_("id", ids).execute()
            else:
                print("Startup DB Link Status: UNCONFIGURED. App starting in degraded mode.")
        except Exception as e:
            print(f"Startup DB Link Status: UNREACHABLE. Error: {e}")
            print("Note: App is starting in degraded mode. DB-dependent endpoints will fail at request-time.")
                
        # Phase 2: AI Model Pre-loading
        from app.services.model_store import model_store
        from app.pipeline.intelligence.semantic_parser import get_semantic_parser
        from app.pipeline.intelligence.rag_engine import get_rag_engine
        
        print("Startup: Pre-loading AI models into memory...")
        try:
            # Load Semantic Parser (SciBERT)
            parser = get_semantic_parser()
            parser._load_model()
            model_store.set_model("scibert_tokenizer", parser.tokenizer)
            model_store.set_model("scibert_model", parser.model)
            print("✅ SciBERT loaded.")
            
            # Load RAG Engine
            rag = get_rag_engine()
            model_store.set_model("rag_engine", rag)
            model_store.set_model("embedding_model", rag.embedding_model)
            # Trigger loading
            print(f"✅ RAG Engine initialized.")
            
            print("Startup: AI models loaded and registered successfully.")
        except Exception as e:
            print(f"⚠️ AI Model Pre-load Warning: {e}. Falling back to lazy-loading.")


@app.get("/")
async def root():
    return {"message": "ScholarForm AI Backend is running"}

@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    Returns status of Supabase DB, AI models, and Ollama server.
    """
    import requests
    from app.db.supabase_client import check_supabase_health

    # ── Old ORM health check (kept for reference, replaced by supabase-py) ─────
    # from app.db.session import SessionLocal
    # db = SessionLocal(); db.execute(text("SELECT 1")); db.close()

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

    # Check Ollama server
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            health_status["components"]["ollama"] = "healthy"
        else:
            health_status["components"]["ollama"] = "unhealthy"
            health_status["status"] = "degraded"
    except (requests.RequestException, Exception):
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