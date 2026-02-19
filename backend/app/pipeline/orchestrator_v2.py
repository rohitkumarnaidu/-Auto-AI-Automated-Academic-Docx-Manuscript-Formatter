"""
Orchestrator V2 — Agent-based orchestration with fallback, metrics, caching,
streaming, batch processing, health checks, and async support.

This is the next-generation orchestrator that wraps the legacy PipelineOrchestrator
with a full agent layer, circuit breaker, retry logic, and observability.

Architecture:
    ┌─────────────────────────────────────────────────────┐
    │                  AgentOrchestrator (V2)              │
    │                                                     │
    │  ┌──────────────┐    ┌──────────────────────────┐  │
    │  │ DocumentAgent │    │  LegacyOrchestrator (V1)  │  │
    │  │  (LangChain)  │───▶│  (Fallback / Hybrid)     │  │
    │  └──────────────┘    └──────────────────────────┘  │
    │         │                                           │
    │  ┌──────▼──────────────────────────────────────┐   │
    │  │  Safety Layer: CircuitBreaker + RetryGuard   │   │
    │  └─────────────────────────────────────────────┘   │
    │         │                                           │
    │  ┌──────▼──────────────────────────────────────┐   │
    │  │  Observability: PerformanceTracker + Metrics  │   │
    │  └─────────────────────────────────────────────┘   │
    │         │                                           │
    │  ┌──────▼──────────────────────────────────────┐   │
    │  │  Cache Layer: RedisCache (GROBID + Results)   │   │
    │  └─────────────────────────────────────────────┘   │
    └─────────────────────────────────────────────────────┘
"""

import asyncio
import logging
import os
import time
import traceback
from datetime import datetime, timezone
from typing import Any, AsyncIterator, Dict, List, Optional

from app.cache.redis_cache import redis_cache
from app.db.supabase_client import get_supabase_client
from app.models import (
    Block,
    BlockType,
    PipelineDocument,
    TemplateInfo,
)
from app.pipeline.agents.document_agent import DocumentAgent
from app.pipeline.agents.metrics import PerformanceTracker
from app.pipeline.orchestrator import PipelineOrchestrator as LegacyOrchestrator
from app.pipeline.safety import safe_execution

logger = logging.getLogger(__name__)

# ── Constants ─────────────────────────────────────────────────────────────────

_SUPPORTED_PROVIDERS = {"openai", "anthropic", "ollama", "nvidia", "deepseek"}
_DEFAULT_CIRCUIT_THRESHOLD = 3   # failures before circuit opens
_DEFAULT_CIRCUIT_RESET_SEC = 60  # seconds before circuit half-opens
_DEFAULT_MAX_RETRIES = 2
_DEFAULT_RETRY_DELAY = 1.5       # seconds (exponential base)


# ── Internal Circuit Breaker ──────────────────────────────────────────────────

class _CircuitBreaker:
    """
    Lightweight in-process circuit breaker for the agent layer.

    States: CLOSED (normal) → OPEN (failing) → HALF_OPEN (testing recovery).
    """

    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

    def __init__(self, failure_threshold: int = _DEFAULT_CIRCUIT_THRESHOLD,
                 reset_timeout: float = _DEFAULT_CIRCUIT_RESET_SEC):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self._failures = 0
        self._state = self.CLOSED
        self._opened_at: Optional[float] = None

    @property
    def state(self) -> str:
        if self._state == self.OPEN:
            if time.monotonic() - self._opened_at >= self.reset_timeout:
                self._state = self.HALF_OPEN
                logger.info("CircuitBreaker: OPEN → HALF_OPEN (testing recovery)")
        return self._state

    def is_open(self) -> bool:
        return self.state == self.OPEN

    def record_success(self) -> None:
        self._failures = 0
        if self._state != self.CLOSED:
            logger.info("CircuitBreaker: %s → CLOSED (recovered)", self._state)
        self._state = self.CLOSED
        self._opened_at = None

    def record_failure(self) -> None:
        self._failures += 1
        if self._failures >= self.failure_threshold:
            if self._state != self.OPEN:
                logger.warning(
                    "CircuitBreaker: OPEN after %d failures. Will reset in %ds.",
                    self._failures, self.reset_timeout
                )
            self._state = self.OPEN
            self._opened_at = time.monotonic()

    def reset(self) -> None:
        self._failures = 0
        self._state = self.CLOSED
        self._opened_at = None


# ── Health Status ─────────────────────────────────────────────────────────────

class OrchestratorHealth:
    """Snapshot of the orchestrator's health at a point in time."""

    def __init__(self, agent_available: bool, circuit_state: str,
                 cache_available: bool, legacy_available: bool,
                 provider: str, model: str):
        self.agent_available = agent_available
        self.circuit_state = circuit_state
        self.cache_available = cache_available
        self.legacy_available = legacy_available
        self.provider = provider
        self.model = model
        self.checked_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_available": self.agent_available,
            "circuit_state": self.circuit_state,
            "cache_available": self.cache_available,
            "legacy_available": self.legacy_available,
            "provider": self.provider,
            "model": self.model,
            "checked_at": self.checked_at,
        }


# ── Main Orchestrator ─────────────────────────────────────────────────────────

class AgentOrchestrator:
    """
    Agent-based orchestrator with fallback to legacy implementation.

    Enhanced with:
    - Performance metrics tracking (PerformanceTracker)
    - Streaming support (async generator)
    - Custom LLM providers (openai, anthropic, ollama, nvidia, deepseek)
    - Agent memory (multi-turn reasoning)
    - Redis result caching
    - In-process circuit breaker (prevents cascade failures)
    - Exponential-backoff retry logic
    - Async run_pipeline_async() for non-blocking execution
    - Batch processing (process_batch / process_batch_async)
    - Health check (health_check())
    - Edit flow (run_edit_flow) — mirrors legacy orchestrator
    """

    def __init__(
        self,
        use_agent: bool = True,
        llm_provider: str = "openai",
        llm_model: str = "gpt-4",
        grobid_url: str = "http://localhost:8070",
        enable_metrics: bool = True,
        enable_streaming: bool = False,
        enable_memory: bool = True,
        enable_cache: bool = True,
        circuit_failure_threshold: int = _DEFAULT_CIRCUIT_THRESHOLD,
        circuit_reset_timeout: float = _DEFAULT_CIRCUIT_RESET_SEC,
        max_retries: int = _DEFAULT_MAX_RETRIES,
        templates_dir: str = "app/templates",
        temp_dir: Optional[str] = None,
    ):
        """
        Initialise the agent orchestrator.

        Args:
            use_agent: Use agent-based orchestration (falls back to legacy if unavailable).
            llm_provider: LLM provider — one of "openai", "anthropic", "ollama", "nvidia", "deepseek".
            llm_model: LLM model name (e.g. "gpt-4", "llama3", "deepseek-r1").
            grobid_url: GROBID service URL for metadata extraction.
            enable_metrics: Enable PerformanceTracker.
            enable_streaming: Enable streaming token output.
            enable_memory: Enable agent conversation memory.
            enable_cache: Enable Redis result caching.
            circuit_failure_threshold: Failures before circuit opens.
            circuit_reset_timeout: Seconds before circuit half-opens.
            max_retries: Maximum agent retry attempts before fallback.
            templates_dir: Path to journal templates directory.
            temp_dir: Temporary file directory.
        """
        self._provider = llm_provider
        self._model = llm_model
        self._enable_streaming = enable_streaming
        self._enable_cache = enable_cache
        self._max_retries = max_retries
        self._templates_dir = templates_dir
        self._temp_dir = temp_dir or "temp"

        # Circuit breaker guards the agent layer
        self._circuit = _CircuitBreaker(
            failure_threshold=circuit_failure_threshold,
            reset_timeout=circuit_reset_timeout,
        )

        # Performance tracker
        self.tracker = PerformanceTracker() if enable_metrics else None

        # Determine if agent is usable
        self.use_agent = use_agent and self._check_llm_available(llm_provider)

        # Initialise agent (with safe fallback)
        self.agent: Optional[DocumentAgent] = None
        if self.use_agent:
            try:
                self.agent = DocumentAgent(
                    llm_provider=llm_provider,
                    llm_model=llm_model,
                    grobid_url=grobid_url,
                    enable_memory=enable_memory,
                    enable_streaming=enable_streaming,
                )
                logger.info(
                    "AgentOrchestrator V2: agent initialised with %s/%s",
                    llm_provider, llm_model
                )
            except Exception as exc:
                logger.warning(
                    "AgentOrchestrator V2: agent init failed (%s). Falling back to legacy.", exc
                )
                self.use_agent = False

        # Legacy orchestrator — always available as fallback
        self.legacy_orchestrator = LegacyOrchestrator(
            templates_dir=templates_dir,
            temp_dir=self._temp_dir,
        )
        logger.info("AgentOrchestrator V2: legacy orchestrator ready as fallback.")

    # ── LLM Availability ──────────────────────────────────────────────────────

    def _check_llm_available(self, provider: str) -> bool:
        """Return True if the given LLM provider has credentials / is reachable."""
        provider = provider.lower()
        if provider not in _SUPPORTED_PROVIDERS:
            logger.warning("Unknown LLM provider '%s'. Disabling agent.", provider)
            return False
        if provider == "openai":
            return bool(os.getenv("OPENAI_API_KEY"))
        if provider == "anthropic":
            return bool(os.getenv("ANTHROPIC_API_KEY"))
        if provider == "nvidia":
            return bool(os.getenv("NVIDIA_API_KEY"))
        if provider == "deepseek":
            return bool(os.getenv("DEEPSEEK_API_KEY"))
        if provider == "ollama":
            # Ollama runs locally — assume available; will fail gracefully at runtime
            return True
        return False

    # ── Status Helpers ────────────────────────────────────────────────────────

    def _update_status(
        self, document_id: str, phase: str, status: str,
        message: Optional[str] = None, progress: Optional[int] = None
    ) -> None:
        """Persist a phase status update to Supabase DB."""
        document_id = str(document_id)
        sb = get_supabase_client()
        if not sb:
            logger.warning("Supabase client unavailable for status update: %s -> %s", phase, status)
            return

        try:
            # 1. Update/Upsert ProcessingStatus
            data = {
                "document_id": document_id,
                "phase": phase,
                "status": status,
                "message": message,
                "progress_percentage": progress,
                "updated_at": "now()"
            }
            
            existing = sb.table("processing_status").select("id").match({"document_id": document_id, "phase": phase}).execute()
            
            if existing.data:
                sb.table("processing_status").update(data).match({"document_id": document_id, "phase": phase}).execute()
            else:
                sb.table("processing_status").insert(data).execute()

            # 2. Update Parent Document
            doc_data = {
                "current_stage": phase,
                "updated_at": "now()"
            }
            
            if status == "COMPLETED":
                if phase == "PERSISTENCE":
                    doc_data["status"] = "COMPLETED"
                else:
                    doc_data["status"] = "RUNNING"
            elif status == "FAILED":
                doc_data["status"] = "FAILED"
                doc_data["error_message"] = message
            else:
                doc_data["status"] = status

            if progress is not None:
                doc_data["progress"] = progress
            
            sb.table("documents").update(doc_data).eq("id", document_id).execute()
        except Exception as exc:
            logger.error("_update_status failed for job %s: %s", document_id, exc)

    # ── Cache Helpers ─────────────────────────────────────────────────────────

    def _cache_get(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve a cached pipeline result (no-op if cache disabled or unavailable)."""
        if not self._enable_cache:
            return None
        try:
            return redis_cache.get_grobid_result(key)
        except Exception as exc:
            logger.debug("Cache get failed (non-blocking): %s", exc)
            return None

    def _cache_set(self, key: str, value: Dict[str, Any], ttl: int = 3600) -> None:
        """Store a pipeline result in cache (no-op if cache disabled or unavailable)."""
        if not self._enable_cache:
            return
        try:
            redis_cache.set_grobid_result(key, value, ttl=ttl)
        except Exception as exc:
            logger.debug("Cache set failed (non-blocking): %s", exc)

    # ── Core Processing ───────────────────────────────────────────────────────

    def process(self, document: PipelineDocument) -> PipelineDocument:
        """
        Process a PipelineDocument using agent or legacy orchestrator.

        The agent layer is protected by a circuit breaker and retry logic.
        Falls back to the legacy orchestrator on any failure.

        Args:
            document: PipelineDocument to process.

        Returns:
            Processed PipelineDocument.
        """
        orchestrator_type = "agent" if (self.use_agent and not self._circuit.is_open()) else "legacy"

        if self.tracker:
            self.tracker.start_tracking(document.document_id, orchestrator_type)

        try:
            if self.use_agent and not self._circuit.is_open():
                return self._process_with_agent(document)
            else:
                if self._circuit.is_open():
                    logger.warning(
                        "CircuitBreaker OPEN for job %s — routing directly to legacy.",
                        document.document_id
                    )
                return self._process_with_legacy(document)

        except Exception as exc:
            logger.error("process() failed for job %s: %s", document.document_id, exc)
            if self.tracker:
                self.tracker.end_tracking(success=False, error_message=str(exc))
            raise

    def _process_with_agent(self, document: PipelineDocument) -> PipelineDocument:
        """
        Attempt agent-based processing with retry + circuit breaker.
        Falls back to legacy on persistent failure.
        """
        last_exc: Optional[Exception] = None

        for attempt in range(1, self._max_retries + 2):  # +1 for initial attempt
            try:
                logger.info(
                    "Agent processing: job=%s attempt=%d/%d",
                    document.document_id, attempt, self._max_retries + 1
                )

                agent_result = self.agent.process_document(
                    file_path=document.source_path,
                    document=document,
                )

                # Record tool usage in tracker
                if self.tracker:
                    for step in agent_result.get("intermediate_steps", []):
                        if step:
                            tool_name = getattr(step[0], "tool", "unknown")
                            self.tracker.record_tool_use(tool_name)

                if agent_result.get("success") and not agent_result.get("should_fallback"):
                    logger.info(
                        "Agent succeeded for job %s. Analysis: %s",
                        document.document_id,
                        str(agent_result.get("analysis", ""))[:200],
                    )
                    # Hybrid: agent analysis → legacy pipeline for formatting
                    result = self.legacy_orchestrator.process(document)
                    self._circuit.record_success()

                    if self.tracker:
                        self.tracker.end_tracking(
                            success=True, document=result, fallback_triggered=False
                        )
                    return result

                else:
                    logger.warning(
                        "Agent recommended fallback for job %s (attempt %d).",
                        document.document_id, attempt
                    )
                    # Treat as a soft failure — break immediately to legacy
                    break

            except Exception as exc:
                last_exc = exc
                self._circuit.record_failure()
                logger.error(
                    "Agent attempt %d failed for job %s: %s",
                    attempt, document.document_id, exc
                )

                if self.tracker:
                    self.tracker.record_retry()

                if attempt <= self._max_retries and not self._circuit.is_open():
                    delay = _DEFAULT_RETRY_DELAY * (2 ** (attempt - 1))
                    logger.info("Retrying in %.1fs...", delay)
                    time.sleep(delay)
                else:
                    break

        # All attempts exhausted — fall back to legacy
        logger.warning(
            "Agent exhausted retries for job %s. Falling back to legacy. Last error: %s",
            document.document_id, last_exc
        )
        return self._fallback_to_legacy(document, fallback_triggered=True)

    def _process_with_legacy(self, document: PipelineDocument) -> PipelineDocument:
        """Process using the legacy orchestrator directly."""
        logger.info("Legacy processing: job=%s", document.document_id)
        result = self.legacy_orchestrator.process(document)

        if self.tracker:
            self.tracker.end_tracking(
                success=True, document=result, fallback_triggered=False
            )
        return result

    def _fallback_to_legacy(
        self, document: PipelineDocument, fallback_triggered: bool = True
    ) -> PipelineDocument:
        """
        Fallback to the legacy orchestrator.

        Args:
            document: PipelineDocument to process.
            fallback_triggered: Whether this is a fallback from agent failure.

        Returns:
            Processed PipelineDocument.
        """
        logger.info(
            "Fallback to legacy: job=%s fallback_triggered=%s",
            document.document_id, fallback_triggered
        )
        result = self.legacy_orchestrator.process(document)

        if self.tracker:
            self.tracker.end_tracking(
                success=True, document=result, fallback_triggered=fallback_triggered
            )
        return result

    # ── Full Pipeline (mirrors legacy run_pipeline) ───────────────────────────

    def run_pipeline(
        self,
        input_path: str,
        job_id: str,
        template_name: Optional[str] = "IEEE",
        formatting_options: Optional[Dict[str, Any]] = None,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """
        Execute the full document processing pipeline.

        This is the V2 equivalent of LegacyOrchestrator.run_pipeline().
        It adds:
        - Result caching (skip re-processing identical files)
        - Agent pre-analysis before the legacy pipeline
        - Circuit breaker protection on the agent layer
        - Structured response with agent metadata

        Args:
            input_path: Absolute path to the uploaded file.
            job_id: UUID of the processing job.
            template_name: Journal template to apply (e.g. "IEEE").
            formatting_options: Dict of formatting preferences.
            use_cache: Check Redis cache before processing (default True).

        Returns:
            Dict with keys: status, job_id, message, agent_used, fallback_triggered.
        """
        logger.info(
            "AgentOrchestrator V2: run_pipeline started — job=%s template=%s",
            job_id, template_name
        )

        if formatting_options is None:
            formatting_options = {}

        response: Dict[str, Any] = {
            "status": "processing",
            "job_id": job_id,
            "message": "",
            "agent_used": False,
            "fallback_triggered": False,
            "orchestrator_version": "v2",
        }

        # ── Cache check ───────────────────────────────────────────────────────
        if use_cache and self._enable_cache:
            cache_key = f"pipeline:{job_id}:{template_name}"
            cached = self._cache_get(cache_key)
            if cached:
                logger.info("Cache HIT for job %s — skipping re-processing.", job_id)
                response.update(cached)
                response["from_cache"] = True
                return response

        # ── Agent pre-analysis (non-blocking) ─────────────────────────────────
        agent_metadata: Dict[str, Any] = {}
        agent_used = False
        fallback_triggered = False

        if self.use_agent and not self._circuit.is_open():
            with safe_execution(f"Agent Pre-Analysis (job={job_id})"):
                try:
                    logger.info("Running agent pre-analysis for job %s", job_id)
                    agent_result = self.agent.process_document(
                        file_path=input_path,
                        document=None,  # Pre-analysis before parsing
                    )
                    if agent_result.get("success"):
                        agent_metadata = {
                            "analysis": agent_result.get("analysis", ""),
                            "recommendations": agent_result.get("recommendations", []),
                            "confidence": agent_result.get("confidence", 0.0),
                        }
                        agent_used = True
                        self._circuit.record_success()
                        logger.info(
                            "Agent pre-analysis complete for job %s (confidence=%.2f)",
                            job_id, agent_metadata.get("confidence", 0.0)
                        )
                    else:
                        logger.warning(
                            "Agent pre-analysis returned no success for job %s.", job_id
                        )
                        fallback_triggered = True
                except Exception as exc:
                    self._circuit.record_failure()
                    logger.error(
                        "Agent pre-analysis failed for job %s: %s. Continuing with legacy.",
                        job_id, exc
                    )
                    fallback_triggered = True
        else:
            if self._circuit.is_open():
                logger.warning(
                    "CircuitBreaker OPEN — skipping agent pre-analysis for job %s.", job_id
                )
                fallback_triggered = True

        # ── Delegate to legacy pipeline ───────────────────────────────────────
        legacy_response = self.legacy_orchestrator.run_pipeline(
            input_path=input_path,
            job_id=job_id,
            template_name=template_name,
            formatting_options=formatting_options,
        )

        # ── Merge responses ───────────────────────────────────────────────────
        response.update(legacy_response)
        response["agent_used"] = agent_used
        response["fallback_triggered"] = fallback_triggered
        response["agent_metadata"] = agent_metadata
        response["orchestrator_version"] = "v2"

        # ── Cache successful results ──────────────────────────────────────────
        if use_cache and self._enable_cache and legacy_response.get("status") == "success":
            cache_key = f"pipeline:{job_id}:{template_name}"
            self._cache_set(cache_key, response, ttl=7200)

        # ── Metrics ───────────────────────────────────────────────────────────
        if self.tracker:
            self.tracker.end_tracking(
                success=(legacy_response.get("status") == "success"),
                fallback_triggered=fallback_triggered,
            )

        return response

    # ── Async Pipeline ────────────────────────────────────────────────────────

    async def run_pipeline_async(
        self,
        input_path: str,
        job_id: str,
        template_name: Optional[str] = "IEEE",
        formatting_options: Optional[Dict[str, Any]] = None,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """
        Async wrapper around run_pipeline().

        Runs the synchronous pipeline in a thread pool executor so it does not
        block the FastAPI event loop.

        Args:
            input_path: Absolute path to the uploaded file.
            job_id: UUID of the processing job.
            template_name: Journal template to apply.
            formatting_options: Dict of formatting preferences.
            use_cache: Check Redis cache before processing.

        Returns:
            Same dict as run_pipeline().
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.run_pipeline(
                input_path=input_path,
                job_id=job_id,
                template_name=template_name,
                formatting_options=formatting_options or {},
                use_cache=use_cache,
            ),
        )

    # ── Streaming ─────────────────────────────────────────────────────────────

    async def stream_pipeline(
        self,
        input_path: str,
        job_id: str,
        template_name: Optional[str] = "IEEE",
        formatting_options: Optional[Dict[str, Any]] = None,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Stream pipeline progress events as an async generator.

        Yields dicts with keys: event, phase, progress, message, data.
        Suitable for Server-Sent Events (SSE) via the /api/stream endpoint.

        Args:
            input_path: Absolute path to the uploaded file.
            job_id: UUID of the processing job.
            template_name: Journal template to apply.
            formatting_options: Dict of formatting preferences.

        Yields:
            Progress event dicts.
        """
        yield {"event": "start", "phase": "INIT", "progress": 0,
               "message": f"V2 pipeline started for job {job_id}",
               "orchestrator_version": "v2"}

        # Agent pre-analysis event
        if self.use_agent and not self._circuit.is_open():
            yield {"event": "progress", "phase": "AGENT_ANALYSIS", "progress": 5,
                   "message": "Running agent pre-analysis..."}
            await asyncio.sleep(0)  # yield control

        # Run the pipeline in a thread pool
        try:
            result = await self.run_pipeline_async(
                input_path=input_path,
                job_id=job_id,
                template_name=template_name,
                formatting_options=formatting_options or {},
            )

            final_event = "complete" if result.get("status") == "success" else "error"
            yield {
                "event": final_event,
                "phase": "PERSISTENCE",
                "progress": 100,
                "message": result.get("message", ""),
                "data": {
                    "agent_used": result.get("agent_used", False),
                    "fallback_triggered": result.get("fallback_triggered", False),
                    "orchestrator_version": "v2",
                },
            }

        except Exception as exc:
            logger.error("stream_pipeline error for job %s: %s", job_id, exc)
            yield {
                "event": "error",
                "phase": "UNKNOWN",
                "progress": 0,
                "message": f"Pipeline error: {exc}",
            }

    # ── Edit Flow (mirrors legacy run_edit_flow) ──────────────────────────────

    def run_edit_flow(
        self,
        job_id: str,
        edited_structured_data: Dict[str, Any],
        template_name: str = "IEEE",
    ) -> Dict[str, Any]:
        """
        Re-run validation and formatting on user-edited structured data.

        Mirrors LegacyOrchestrator.run_edit_flow() but adds:
        - Agent re-validation advice (non-blocking)
        - Cache invalidation for the edited job

        Args:
            job_id: UUID of the original processing job.
            edited_structured_data: Modified structured document data.
            template_name: Journal template to apply.

        Returns:
            Dict with keys: status, output_path, agent_advice (optional).
        """
        logger.info("AgentOrchestrator V2: run_edit_flow — job=%s", job_id)

        # Invalidate cache for this job (data has changed)
        if self._enable_cache:
            cache_key = f"pipeline:{job_id}:{template_name}"
            try:
                redis_cache.set_grobid_result(cache_key, {}, ttl=1)  # expire immediately
            except Exception:
                pass

        # Optional: agent advice on the edit (non-blocking)
        agent_advice: Dict[str, Any] = {}
        if self.use_agent and not self._circuit.is_open():
            with safe_execution(f"Agent Edit Advice (job={job_id})"):
                try:
                    # Build a minimal context for the agent
                    sections_summary = {
                        k: len(v) for k, v in edited_structured_data.get("sections", {}).items()
                    }
                    agent_result = self.agent.process_document(
                        file_path=None,
                        document=None,
                        context={"edited_sections": sections_summary, "template": template_name},
                    )
                    if agent_result.get("success"):
                        agent_advice = {
                            "recommendations": agent_result.get("recommendations", []),
                            "confidence": agent_result.get("confidence", 0.0),
                        }
                        self._circuit.record_success()
                except Exception as exc:
                    self._circuit.record_failure()
                    logger.warning("Agent edit advice failed (non-blocking): %s", exc)

        # Delegate to legacy edit flow
        legacy_response = self.legacy_orchestrator.run_edit_flow(
            job_id=job_id,
            edited_structured_data=edited_structured_data,
            template_name=template_name,
        )

        legacy_response["agent_advice"] = agent_advice
        legacy_response["orchestrator_version"] = "v2"
        return legacy_response

    async def run_edit_flow_async(
        self,
        job_id: str,
        edited_structured_data: Dict[str, Any],
        template_name: str = "IEEE",
    ) -> Dict[str, Any]:
        """
        Async wrapper around run_edit_flow().

        Runs in a thread pool executor to avoid blocking the event loop.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.run_edit_flow(
                job_id=job_id,
                edited_structured_data=edited_structured_data,
                template_name=template_name,
            ),
        )

    # ── Batch Processing ──────────────────────────────────────────────────────

    def process_batch(
        self,
        jobs: List[Dict[str, Any]],
        max_concurrent: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Process a batch of documents sequentially (synchronous).

        Each job dict must have keys: input_path, job_id.
        Optional keys: template_name, formatting_options.

        Args:
            jobs: List of job dicts.
            max_concurrent: Ignored in sync mode (kept for API parity with async version).

        Returns:
            List of result dicts, one per job (in the same order).
        """
        results = []
        for i, job in enumerate(jobs):
            logger.info(
                "Batch processing job %d/%d: %s", i + 1, len(jobs), job.get("job_id")
            )
            try:
                result = self.run_pipeline(
                    input_path=job["input_path"],
                    job_id=job["job_id"],
                    template_name=job.get("template_name", "IEEE"),
                    formatting_options=job.get("formatting_options", {}),
                )
                results.append(result)
            except Exception as exc:
                logger.error("Batch job %s failed: %s", job.get("job_id"), exc)
                results.append({
                    "status": "error",
                    "job_id": job.get("job_id"),
                    "message": str(exc),
                    "orchestrator_version": "v2",
                })
        return results

    async def process_batch_async(
        self,
        jobs: List[Dict[str, Any]],
        max_concurrent: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Process a batch of documents concurrently (async).

        Each job dict must have keys: input_path, job_id.
        Optional keys: template_name, formatting_options.

        Args:
            jobs: List of job dicts.
            max_concurrent: Maximum concurrent jobs (semaphore-controlled).

        Returns:
            List of result dicts, one per job (in the same order as input).
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def _run_one(job: Dict[str, Any]) -> Dict[str, Any]:
            async with semaphore:
                try:
                    return await self.run_pipeline_async(
                        input_path=job["input_path"],
                        job_id=job["job_id"],
                        template_name=job.get("template_name", "IEEE"),
                        formatting_options=job.get("formatting_options", {}),
                    )
                except Exception as exc:
                    logger.error("Async batch job %s failed: %s", job.get("job_id"), exc)
                    return {
                        "status": "error",
                        "job_id": job.get("job_id"),
                        "message": str(exc),
                        "orchestrator_version": "v2",
                    }

        return list(await asyncio.gather(*[_run_one(j) for j in jobs]))

    # ── Health Check ──────────────────────────────────────────────────────────

    def health_check(self) -> OrchestratorHealth:
        """
        Return a health snapshot of the orchestrator.

        Checks: agent availability, circuit breaker state, cache connectivity,
        legacy orchestrator availability.

        Returns:
            OrchestratorHealth instance (call .to_dict() for JSON serialisation).
        """
        # Check cache
        cache_available = False
        if self._enable_cache:
            try:
                cache_available = redis_cache.client is not None
            except Exception:
                cache_available = False

        # Check legacy orchestrator
        legacy_available = self.legacy_orchestrator is not None

        return OrchestratorHealth(
            agent_available=self.use_agent and self.agent is not None,
            circuit_state=self._circuit.state,
            cache_available=cache_available,
            legacy_available=legacy_available,
            provider=self._provider,
            model=self._model,
        )

    # ── Metrics & Observability ───────────────────────────────────────────────

    def get_performance_summary(self) -> Optional[Dict[str, Any]]:
        """Return aggregated performance metrics from the PerformanceTracker."""
        if self.tracker:
            return self.tracker.get_summary()
        return None

    def get_comparison(self) -> Optional[Dict[str, Any]]:
        """Return agent vs legacy performance comparison from the PerformanceTracker."""
        if self.tracker:
            return self.tracker.get_comparison()
        return None

    def reset_circuit(self) -> None:
        """Manually reset the circuit breaker (e.g. after a deployment fix)."""
        self._circuit.reset()
        logger.info("CircuitBreaker manually reset.")

    def get_circuit_state(self) -> str:
        """Return the current circuit breaker state string."""
        return self._circuit.state


# ── Convenience Factory ───────────────────────────────────────────────────────

def create_orchestrator(
    use_agent: bool = True,
    llm_provider: str = "openai",
    llm_model: str = "gpt-4",
    enable_metrics: bool = True,
    enable_cache: bool = True,
    enable_streaming: bool = False,
    templates_dir: str = "app/templates",
    temp_dir: Optional[str] = None,
) -> AgentOrchestrator:
    """
    Create an AgentOrchestrator instance with sensible defaults.

    This is the primary entry point for creating a V2 orchestrator.
    Automatically falls back to legacy if the LLM provider is unavailable.

    Args:
        use_agent: Use agent-based orchestration.
        llm_provider: LLM provider ("openai", "anthropic", "ollama", "nvidia", "deepseek").
        llm_model: LLM model name.
        enable_metrics: Enable PerformanceTracker.
        enable_cache: Enable Redis result caching.
        enable_streaming: Enable streaming token output.
        templates_dir: Path to journal templates directory.
        temp_dir: Temporary file directory.

    Returns:
        Configured AgentOrchestrator instance.
    """
    return AgentOrchestrator(
        use_agent=use_agent,
        llm_provider=llm_provider,
        llm_model=llm_model,
        enable_metrics=enable_metrics,
        enable_cache=enable_cache,
        enable_streaming=enable_streaming,
        templates_dir=templates_dir,
        temp_dir=temp_dir,
    )


# ── Auto-select Best Available Provider ──────────────────────────────────────

def create_best_orchestrator(
    enable_metrics: bool = True,
    enable_cache: bool = True,
    templates_dir: str = "app/templates",
) -> AgentOrchestrator:
    """
    Create an orchestrator using the best available LLM provider.

    Priority order: nvidia → openai → anthropic → deepseek → ollama → legacy-only.

    Args:
        enable_metrics: Enable PerformanceTracker.
        enable_cache: Enable Redis result caching.
        templates_dir: Path to journal templates directory.

    Returns:
        Configured AgentOrchestrator instance.
    """
    priority = [
        ("nvidia", "meta/llama-3.1-70b-instruct"),
        ("openai", "gpt-4"),
        ("anthropic", "claude-3-5-sonnet-20241022"),
        ("deepseek", "deepseek-chat"),
        ("ollama", "deepseek-r1:7b"),
    ]

    for provider, model in priority:
        key_map = {
            "nvidia": "NVIDIA_API_KEY",
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "deepseek": "DEEPSEEK_API_KEY",
        }
        env_key = key_map.get(provider)
        if env_key and not os.getenv(env_key):
            continue  # Skip — no credentials
        if provider == "ollama":
            pass  # Always try Ollama last

        logger.info(
            "create_best_orchestrator: selected provider=%s model=%s", provider, model
        )
        return create_orchestrator(
            use_agent=True,
            llm_provider=provider,
            llm_model=model,
            enable_metrics=enable_metrics,
            enable_cache=enable_cache,
            templates_dir=templates_dir,
        )

    # No provider available — legacy only
    logger.warning(
        "create_best_orchestrator: no LLM provider available. Using legacy-only mode."
    )
    return create_orchestrator(
        use_agent=False,
        llm_provider="openai",
        enable_metrics=enable_metrics,
        enable_cache=enable_cache,
        templates_dir=templates_dir,
    )
