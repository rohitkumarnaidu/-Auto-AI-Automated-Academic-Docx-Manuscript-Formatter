
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, documents
from app.config.settings import settings
from app.middleware.rate_limit import RateLimitMiddleware

# Initialize logging FIRST (before any other imports that might log)
from app.config.logging_config import setup_logging
logger = setup_logging()

# Phase 2: Silence Global AI Startup Noise
import os
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

@app.on_event("startup")
async def startup_event():
    """
    Perform startup tasks, including cleaning up interrupted jobs.
    Note: This project intentionally avoids automated pipeline testing at this stage.
    """
    from app.db.session import SessionLocal
    from app.models import Document
    from sqlalchemy.exc import OperationalError
    
    db = None
    try:
        # Lazy instantiation inside try block
        db = SessionLocal()
        # Find jobs stuck in RUNNING state from previous session
        # This will trigger the connection attempt
        interrupted_docs = db.query(Document).filter(Document.status == "RUNNING").all()
        if interrupted_docs:
            print(f"Startup: Found {len(interrupted_docs)} interrupted jobs. Marking as FAILED.")
            for doc in interrupted_docs:
                doc.status = "FAILED"
                doc.error_message = "Processing interrupted by server restart."
            db.commit()
    except (OperationalError, Exception) as e:
        # Log a clear warning instead of crashing the process
        # This ensures the app starts even if DNS or DB is down
        print(f"Startup DB Link Status: UNREACHABLE. Error: {e}")
        print("Note: App is starting in degraded mode. DB-dependent endpoints will fail at request-time.")
    finally:
        if db:
            db.close()
            
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
        
        # Load RagEngine (SentenceTransformer + Vector Store)
        rag = get_rag_engine()
        model_store.set_model("rag_engine", rag)
        model_store.set_model("embedding_model", rag.embedding_model)
        
        print("Startup: AI models loaded and registered successfully.")
    except Exception as e:
        print(f"Startup AI Error: Failed to pre-load models ({e}). Falling back to lazy-loading.")

@app.get("/")
async def root():
    return {"message": "ScholarForm AI Backend is running"}

@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    Returns status of database, AI models, and Ollama server.
    """
    from app.db.session import SessionLocal
    from app.pipeline.intelligence.reasoning_engine import get_reasoning_engine
    import requests
    
    health_status = {
        "status": "healthy",
        "version": "1.0.0",
        "components": {}
    }
    
    # Check database
    try:
        db = SessionLocal()
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        db.close()
        health_status["components"]["database"] = "healthy"
    except Exception as e:
        health_status["components"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check Ollama server
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            health_status["components"]["ollama"] = "healthy"
        else:
            health_status["components"]["ollama"] = "unhealthy"
            health_status["status"] = "degraded"
    except (requests.RequestException, Exception) as e:
        health_status["components"]["ollama"] = "unavailable (fallback active)"
        health_status["status"] = "degraded"
    
    # Check AI models
    try:
        from app.services.model_store import model_store
        if model_store.get_model("scibert_model") is not None:
            health_status["components"]["ai_models"] = "loaded"
        else:
            health_status["components"]["ai_models"] = "not_loaded"
    except Exception as e:
        health_status["components"]["ai_models"] = "error"
    
    return health_status