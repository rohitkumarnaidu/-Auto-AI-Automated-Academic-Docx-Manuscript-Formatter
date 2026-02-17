"""
Metrics and Monitoring Endpoints
Provides operational visibility into database connections, rate limiting, and system health.
"""

from fastapi import APIRouter, HTTPException
from app.db.session import engine
import logging

router = APIRouter(prefix="/api/metrics", tags=["Metrics"])
logger = logging.getLogger(__name__)

@router.get("/db")
async def get_database_metrics():
    """
    Get database connection pool metrics.
    
    Returns:
        - size: Total pool size
        - checked_in: Available connections
        - checked_out: Active connections
        - overflow: Overflow connections created
        - total: Total connections (pool + overflow)
    """
    try:
        pool = engine.pool
        
        metrics = {
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "total_connections": pool.size() + pool.overflow(),
            "status": "healthy" if pool.checkedin() > 0 else "warning"
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
async def log_frontend_error(error_data: dict):
    """
    Endpoint for logging frontend errors to the backend.
    
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
async def health_check():
    """
    Comprehensive health check endpoint.
    
    Returns:
        - status: overall health status
        - database: database connection status
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
    
    # Check database connection
    try:
        pool = engine.pool
        if pool.checkedin() > 0:
            health_status["components"]["database"] = "healthy"
        else:
            health_status["components"]["database"] = "degraded"
            health_status["status"] = "degraded"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["components"]["database"] = "unhealthy"
        health_status["status"] = "degraded"
    
    return health_status
