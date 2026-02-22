"""
Prometheus metrics definition and middleware for the application.
"""
import time
import logging
from typing import Callable
from fastapi import Request, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

logger = logging.getLogger(__name__)

# --- Metrics Definitions ---

# Pipeline Metrics
PIPELINE_REQUESTS_TOTAL = Counter(
    "pipeline_requests_total",
    "Total number of pipeline requests",
    ["status"]  # active, completed, failed
)

PIPELINE_DURATION_SECONDS = Histogram(
    "pipeline_duration_seconds",
    "Time spent processing a pipeline request",
    ["status"],  # success, error
    buckets=(1, 5, 10, 30, 60, 120, 300, 600, 1800)
)

PIPELINE_STEPS_DURATION_SECONDS = Histogram(
    "pipeline_step_duration_seconds",
    "Time spent in specific pipeline steps",
    ["step"],
    buckets=(0.1, 0.5, 1, 2, 5, 10, 30, 60)
)

# Agent Metrics
AGENT_TOOLS_USAGE_TOTAL = Counter(
    "agent_tools_usage_total",
    "Total usage of agent tools",
    ["tool_name", "status"]  # success, error
)

AGENT_LLM_TOKENS_TOTAL = Counter(
    "agent_llm_tokens_total",
    "Total LLM tokens consumed",
    ["provider", "model", "type"]  # input, output
)

AGENT_RETRIES_TOTAL = Counter(
    "agent_retries_total",
    "Total number of agent retries triggered"
)

# System Metrics
ACTIVE_PROCESSING_JOBS = Gauge(
    "active_processing_jobs",
    "Number of currently active processing jobs"
)

LLM_FAILURES_TOTAL = Counter(
    "llm_failures_total",
    "Total number of LLM API failures",
    ["provider"]
)

# --- Middleware ---

async def prometheus_metrics_middleware(request: Request, call_next: Callable) -> Response:
    """
    Middleware to handle /metrics endpoint and track basic request metrics.
    """
    if request.url.path == "/metrics":
        return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
    
    return await call_next(request)

class MetricsManager:
    """Helper class to record metrics from anywhere in the app."""
    
    @staticmethod
    def record_pipeline_start():
        PIPELINE_REQUESTS_TOTAL.labels(status="active").inc()
        ACTIVE_PROCESSING_JOBS.inc()

    @staticmethod
    def record_pipeline_completion(duration: float, success: bool):
        status = "success" if success else "error"
        PIPELINE_REQUESTS_TOTAL.labels(status="completed" if success else "failed").inc()
        PIPELINE_DURATION_SECONDS.labels(status=status).observe(duration)
        ACTIVE_PROCESSING_JOBS.dec()

    @staticmethod
    def record_step_duration(step_name: str, duration: float):
        PIPELINE_STEPS_DURATION_SECONDS.labels(step=step_name).observe(duration)

    @staticmethod
    def record_tool_usage(tool_name: str, success: bool):
        status = "success" if success else "error"
        AGENT_TOOLS_USAGE_TOTAL.labels(tool_name=tool_name, status=status).inc()

    @staticmethod
    def record_llm_usage(provider: str, model: str, input_tokens: int, output_tokens: int):
        AGENT_LLM_TOKENS_TOTAL.labels(provider=provider, model=model, type="input").inc(input_tokens)
        AGENT_LLM_TOKENS_TOTAL.labels(provider=provider, model=model, type="output").inc(output_tokens)
    
    @staticmethod
    def record_llm_failure(provider: str):
        LLM_FAILURES_TOTAL.labels(provider=provider).inc()
    
    @staticmethod
    def record_retry():
        AGENT_RETRIES_TOTAL.inc()
