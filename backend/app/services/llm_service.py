"""
llm_service.py — Unified LLM access layer powered by LiteLLM.
"""
from __future__ import annotations
import sys
import logging
from typing import List, Dict, Any, Optional

from app.config.settings import settings
from app.utils.logging_context import log_extra

logger = logging.getLogger(__name__)

# ── LiteLLM import (optional) ────────────────────────────────────────────── #
try:
    # LiteLLM currently emits Python 3.14 deprecation warnings via transitive
    # dependencies. Use direct provider clients on 3.14+ until upstream catches up.
    if sys.version_info >= (3, 14):
        raise ImportError("LiteLLM disabled on Python >= 3.14.")
    import litellm
    from litellm import completion
    litellm.drop_params = True          # Ignore unsupported params per-provider
    litellm.suppress_debug_info = True  # Quiet startup logs
    LITELLM_AVAILABLE = True
    logger.info("llm_service: LiteLLM available - unified LLM layer active.", extra=log_extra())
except ImportError:
    LITELLM_AVAILABLE = False
    logger.warning(
        "LiteLLM unavailable - llm_service will use direct provider clients.",
        extra=log_extra(),
    )
LLM_NVIDIA   = settings.NVIDIA_MODEL
LLM_GROQ     = settings.GROQ_MODEL
LLM_DEEPSEEK = "ollama/deepseek-r1"
LLM_GPT4     = "gpt-4"

# ── Prompt injection guard ───────────────────────────────────────────────── #
import re

_INJECTION_PATTERNS = [
    re.compile(r'(?i)(ignore|forget|disregard)\s+(all\s+)?(previous|above|prior)\s+(instructions?|prompts?|rules?)'),
    re.compile(r'(?i)you\s+are\s+now\s+(a|an)\s+'),
    re.compile(r'(?i)system\s*:\s*'),
    re.compile(r'(?i)new\s+instructions?\s*:'),
]
MAX_LLM_INPUT_LENGTH = 8000


def sanitize_for_llm(text: str) -> str:
    """
    Sanitize user-provided text before sending to LLM.
    Strips known injection patterns and truncates to safe length.
    """
    if not text:
        return text
    for pattern in _INJECTION_PATTERNS:
        text = pattern.sub('[CONTENT_FILTERED]', text)
    if len(text) > MAX_LLM_INPUT_LENGTH:
        text = text[:MAX_LLM_INPUT_LENGTH] + "\n[... content truncated for safety ...]"
    return text


def _extract_prompts(messages: List[Dict[str, str]]) -> tuple[str, str]:
    system_parts = [m.get("content", "") for m in messages if m.get("role") == "system"]
    user_parts = [m.get("content", "") for m in messages if m.get("role") == "user"]
    return "\n".join(system_parts), "\n".join(user_parts)


def _cache_key(system_prompt: str, user_message: str, model: str, temperature: float) -> str:
    import hashlib
    key_input = f"{model}:{temperature}:{system_prompt}:{user_message}"
    return "llm_cache:" + hashlib.sha256(key_input.encode()).hexdigest()

def generate(
    messages: List[Dict[str, str]],
    model: str = LLM_NVIDIA,
    temperature: float = 0.3,
    max_tokens: int = 2048,
    timeout: int = 30,
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
    stream: bool = False,
) -> str:
    """
    Send a chat completion request via LiteLLM (or direct HTTP fallback).

    Args:
        messages:    OpenAI-format message list [{role, content}, ...]
        model:       LiteLLM model string, e.g. LLM_NVIDIA / LLM_DEEPSEEK / "gpt-4"
        temperature: Sampling temperature [0.0 – 1.0]
        max_tokens:  Maximum tokens to generate
        timeout:     Request timeout in seconds
        api_key:     Override API key (defaults to env var per provider)
        api_base:    Override API base URL

    Returns:
        Generated text string (empty string on failure)

    Raises:
        Exception: On API error — callers should catch and fall back.
    """
    system_prompt, user_message = _extract_prompts(messages)
    key = _cache_key(system_prompt, user_message, model, temperature)
    from app.cache.redis_cache import redis_cache
    
    # ── Cache Lookup ──
    cache_enabled = not stream
    if cache_enabled:
        cached = redis_cache.get_llm_result(key)
        if cached:
            logger.info("LLM cache hit", extra=log_extra())
            return cached

    if not LITELLM_AVAILABLE:
        result = _generate_fallback(messages, model, temperature, max_tokens, timeout, api_key, api_base)
        if result and cache_enabled:
            redis_cache.set_llm_result(key, result, ttl=settings.LLM_CACHE_TTL_SECONDS)
        return result

    kwargs: Dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": max(0.0, min(1.0, temperature)),
        "max_tokens": max_tokens,
        "timeout": timeout,
    }

    # Per-provider API key resolution
    if api_key:
        kwargs["api_key"] = api_key
    elif model.startswith("nvidia_nim/"):
        nvidia_key = settings.NVIDIA_API_KEY
        if nvidia_key:
            kwargs["api_key"] = nvidia_key
    elif model.startswith("gpt-") or model.startswith("openai/"):
        openai_key = settings.OPENAI_API_KEY
        if openai_key:
            kwargs["api_key"] = openai_key
    elif model.startswith("claude") or model.startswith("anthropic/"):
        anthropic_key = settings.ANTHROPIC_API_KEY
        if anthropic_key:
            kwargs["api_key"] = anthropic_key
    elif model.startswith("groq/"):
        groq_key = settings.GROQ_API_KEY
        if groq_key:
            kwargs["api_key"] = groq_key

    # Per-provider base URL
    if api_base:
        kwargs["api_base"] = api_base
    elif model.startswith("ollama/"):
        kwargs["api_base"] = settings.OLLAMA_BASE_URL
    elif model.startswith("groq/"):
        kwargs["api_base"] = settings.GROQ_API_BASE

    response = completion(**kwargs)
    choices = response.choices
    if not choices:
        logger.warning("llm_service.generate: empty choices from %s", model, extra=log_extra())
        return ""
    text = choices[0].message.content or ""
    if text and cache_enabled:
        redis_cache.set_llm_result(key, text, ttl=settings.LLM_CACHE_TTL_SECONDS)
    return text


def generate_with_fallback(
    messages: List[Dict[str, str]],
    temperature: float = 0.3,
    max_tokens: int = 2048,
) -> Dict[str, Any]:
    """
    3-tier fallback: NVIDIA -> Groq -> Ollama -> raises LLMUnavailableError.

    Returns:
        {"text": str, "model": str, "tier": int}
    """
    # Tier 1: NVIDIA NIM
    nvidia_key = settings.NVIDIA_API_KEY
    if nvidia_key:
        try:
            text = generate(messages, model=LLM_NVIDIA, temperature=temperature, max_tokens=max_tokens)
            if text:
                logger.info("llm_service: Tier 1 (NVIDIA) succeeded.", extra=log_extra())
                return {"text": text, "model": LLM_NVIDIA, "tier": 1}
        except Exception as exc:
            try:
                from app.middleware.prometheus_metrics import MetricsManager
                MetricsManager.record_llm_failure("nvidia")
            except Exception: pass
            logger.warning("llm_service: Tier 1 (NVIDIA) failed: %s - trying Groq.", exc, extra=log_extra())

    # Tier 2: Groq
    groq_model = settings.GROQ_MODEL or LLM_GROQ
    groq_key = settings.GROQ_API_KEY
    if groq_key:
        try:
            text = generate(
                messages,
                model=groq_model,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=groq_key,
            )
            if text:
                logger.info("llm_service: Tier 2 (Groq) succeeded.", extra=log_extra())
                return {"text": text, "model": groq_model, "tier": 2}
        except Exception as exc:
            try:
                from app.middleware.prometheus_metrics import MetricsManager
                MetricsManager.record_llm_failure("groq")
            except Exception:
                pass
            logger.warning("llm_service: Tier 2 (Groq) failed: %s - trying Ollama.", exc, extra=log_extra())

    # Tier 3: DeepSeek via Ollama
    try:
        text = generate(messages, model=LLM_DEEPSEEK, temperature=temperature, max_tokens=max_tokens)
        if text:
            logger.info("llm_service: Tier 3 (Ollama) succeeded.", extra=log_extra())
            return {"text": text, "model": LLM_DEEPSEEK, "tier": 3}
    except Exception as exc:
        try:
            from app.middleware.prometheus_metrics import MetricsManager
            MetricsManager.record_llm_failure("ollama")
        except Exception:
            pass
        logger.warning("llm_service: Tier 3 (Ollama) failed: %s - no LLM available.", exc, extra=log_extra())

    raise LLMUnavailableError("All LLM tiers failed. Use rule-based fallback.")


class LLMUnavailableError(Exception):
    """Raised when all LLM tiers are exhausted."""
    pass


def invalidate_llm_cache(pattern: str) -> int:
    """Invalidate cached LLM responses matching a Redis glob pattern."""
    from app.cache.redis_cache import redis_cache

    if not pattern:
        return 0
    if not redis_cache.client:
        logger.warning("LLM cache invalidation requested but Redis unavailable.", extra=log_extra())
        return 0

    removed = 0
    try:
        for key in redis_cache.client.scan_iter(match=pattern):
            removed += int(redis_cache.client.delete(key))
        logger.info(
            "LLM cache invalidated for pattern=%s (removed=%s)",
            pattern,
            removed,
            extra=log_extra(),
        )
    except Exception as exc:
        logger.error(
            "LLM cache invalidation failed for pattern=%s: %s",
            pattern,
            exc,
            extra=log_extra(),
        )
    return removed


# ── Direct-client fallback (no litellm) ─────────────────────────────────── #
def _generate_fallback(
    messages, model, temperature, max_tokens, timeout, api_key, api_base
) -> str:
    """Direct HTTP fallback used when litellm is not installed."""
    if model.startswith("nvidia_nim/") or model.startswith("openai/") or model.startswith("gpt-"):
        return _openai_compat(
            messages, model, temperature, max_tokens,
            api_key or settings.NVIDIA_API_KEY or settings.OPENAI_API_KEY,
            api_base or ("https://integrate.api.nvidia.com/v1" if model.startswith("nvidia_nim/") else None),
        )
    elif model.startswith("groq/"):
        return _openai_compat(
            messages,
            model,
            temperature,
            max_tokens,
            api_key or settings.GROQ_API_KEY,
            api_base or settings.GROQ_API_BASE,
        )
    elif model.startswith("ollama/"):
        return _ollama_http(
            messages, model.replace("ollama/", ""), temperature, max_tokens,
            api_base or settings.OLLAMA_BASE_URL, timeout,
        )
    raise NotImplementedError(f"No fallback implementation for model: {model}")


def _openai_compat(messages, model, temperature, max_tokens, api_key, base_url) -> str:
    from openai import OpenAI
    # Strip provider prefix for raw OpenAI/NVIDIA
    raw_model = model.replace("nvidia_nim/", "").replace("openai/", "").replace("groq/", "")
    client = OpenAI(api_key=api_key or "none", base_url=base_url)
    resp = client.chat.completions.create(
        model=raw_model, messages=messages,
        temperature=max(0.0, min(1.0, temperature)), max_tokens=max_tokens,
    )
    return resp.choices[0].message.content or "" if resp.choices else ""


def _ollama_http(messages, model_name, temperature, max_tokens, base_url, timeout) -> str:
    import requests, json
    # Convert messages to single prompt
    prompt = "\n".join(f"{m['role']}: {m['content']}" for m in messages)
    resp = requests.post(
        f"{base_url}/api/generate",
        json={"model": model_name, "prompt": prompt, "stream": False,
              "options": {"temperature": temperature, "num_predict": max_tokens}},
        timeout=timeout,
    )
    resp.raise_for_status()
    return resp.json().get("response", "")

async def check_health() -> Dict[str, str]:
    """Check health of underlying LLM providers."""
    results = {}
    
    # Check NVIDIA
    try:
        nvidia_key = settings.NVIDIA_API_KEY
        if nvidia_key:
            results["nvidia"] = "healthy"
        else:
            results["nvidia"] = "unconfigured"
    except Exception:
        results["nvidia"] = "unavailable"
        
    # Check Ollama/DeepSeek
    try:
        import httpx
        base_url = settings.OLLAMA_BASE_URL
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get(f"{base_url}/api/tags")
            if resp.status_code == 200:
                tags = resp.json()
                models = [m.get("name", "") for m in tags.get("models", [])]
                if any("deepseek" in m for m in models):
                    results["deepseek"] = "healthy"
                else:
                    results["deepseek"] = "model_missing"
            else:
                results["deepseek"] = "unavailable"
    except Exception:
        results["deepseek"] = "unavailable"
        
    return results

