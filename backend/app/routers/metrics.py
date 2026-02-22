"""
Metrics and Monitoring Endpoints
Provides operational visibility into database connections, rate limiting, and system health.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from app.utils.dependencies import get_current_user

from app.services.model_metrics import get_model_metrics
from app.services.ab_testing import get_ab_testing
from app.db.supabase_client import get_supabase_client
import logging

router = APIRouter(prefix="/api/metrics", tags=["Metrics"])
logger = logging.getLogger(__name__)

@router.get("/db")
async def get_database_metrics():
    """
    Get database health metrics via Supabase client.
    
    Returns:
        - status: Connection health (healthy/unavailable)
        - backend: Database backend type
    """
    try:
        sb = get_supabase_client()
        if sb:
            # Simple health probe — fetch row count from a lightweight table
            result = sb.table("documents").select("id", count="exact").limit(0).execute()
            metrics = {
                "status": "healthy",
                "backend": "supabase",
                "document_count": result.count if hasattr(result, 'count') else 0,
            }
        else:
            metrics = {
                "status": "unavailable",
                "backend": "supabase",
                "document_count": 0,
            }
        
        logger.info(f"Database metrics: {metrics}")
        return metrics
    except Exception as e:
        logger.error(f"Failed to get database metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve database metrics: {str(e)}"
        )

@router.post("/log-error")
async def log_frontend_error(error_data: dict, current_user=Depends(get_current_user)):
    """
    Endpoint for logging frontend errors to the backend.
    Requires authentication.
    
    Payload:
        - message: Error message
        - stack: Stack trace
        - url: Page URL where error occurred
        - timestamp: Client-side timestamp
    """
    try:
        message = error_data.get("message", "Unknown frontend error")
        stack = error_data.get("stack", "No stack trace provided")
        url = error_data.get("url", "Unknown URL")
        timestamp = error_data.get("timestamp", "No timestamp provided")
        
        logger.error(
            f"Frontend Error Captured:\n"
            f"Message: {message}\n"
            f"URL: {url}\n"
            f"Timestamp: {timestamp}\n"
            f"Stack: {stack}"
        )
        
        # Increment a Prometheus counter if available
        try:
            from app.middleware.prometheus_metrics import AGENT_TOOLS_USAGE_TOTAL
            AGENT_TOOLS_USAGE_TOTAL.labels(tool_name="frontend", status="error").inc()
        except ImportError:
            pass
            
        return {"status": "logged"}
    except Exception as e:
        logger.error(f"Failed to log frontend error: {e}")
        return {"status": "error", "message": str(e)}

@router.get("/health")
async def health_check(current_user=Depends(get_current_user)):
    """
    Comprehensive health check endpoint.
    Requires authentication.
    
    Returns:
        - status: overall health status
        - components: individual component statuses
    """
    health_status = {
        "status": "healthy",
        "components": {
            "api": "healthy",
            "database": "unknown",
            "ai_models": "healthy"
        }
    }
    
    # Check LLM health
    try:
        from app.services.llm_service import check_health as llm_check_health
        llm_health = await llm_check_health()
        health_status["components"]["llm_nvidia"] = llm_health.get("nvidia", "unknown")
        health_status["components"]["llm_deepseek"] = llm_health.get("deepseek", "unknown")
        
        if llm_health.get("nvidia") != "healthy" and llm_health.get("deepseek") != "healthy":
            health_status["status"] = "degraded"
    except Exception as e:
        logger.error(f"LLM health check failed: {e}")

    # Check database connection via Supabase
    try:
        sb = get_supabase_client()
        if sb:
            sb.table("documents").select("id", count="exact").limit(0).execute()
            health_status["components"]["database"] = "healthy"
        else:
            health_status["components"]["database"] = "unavailable"
            health_status["status"] = "degraded"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["components"]["database"] = "unhealthy"
        health_status["status"] = "degraded"
    
    return health_status


@router.get("/dashboard")
async def get_metrics_dashboard() -> Dict[str, Any]:
    """Get aggregated AI metrics and A/B testing results."""
    # Local runtime metrics
    model_metrics = get_model_metrics()
    ab_testing = get_ab_testing()
    
    # Check Supabase connection
    sb = get_supabase_client()
    db_status = "connected" if sb is not None else "disconnected"
    
    db_ab_tests = 0
    db_model_metrics = 0
    
    try:
        if sb:
            # Query the exact count of persisted rows
            res_metrics = sb.table("model_metrics").select("id", count="exact").limit(1).execute()
            db_model_metrics = res_metrics.count if res_metrics else 0
            
            res_ab = sb.table("ab_test_results").select("id", count="exact").limit(1).execute()
            db_ab_tests = res_ab.count if res_ab else 0
    except Exception as exc:
        logger.warning("Failed to query metrics counts from Supabase: %s", exc)

    return {
        "status": "success",
        "persistent_db_status": db_status,
        "database_records": {
            "model_metrics_count": db_model_metrics,
            "ab_test_results_count": db_ab_tests
        },
        "live_metrics_summary": model_metrics.get_summary(),
        "live_model_comparison": model_metrics.get_model_comparison(),
        "live_ab_test_summary": ab_testing.get_test_summary()
    }

