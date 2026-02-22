"""
llm_service.py — Unified LLM access layer powered by LiteLLM.
"""
from __future__ import annotations
import os
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# ── LiteLLM import (optional) ────────────────────────────────────────────── #
try:
    import litellm
    from litellm import completion
    litellm.drop_params = True          # Ignore unsupported params per-provider
    litellm.suppress_debug_info = True  # Quiet startup logs
    LITELLM_AVAILABLE = True
    logger.info("llm_service: LiteLLM available — unified LLM layer active.")
except ImportError:
    LITELLM_AVAILABLE = False
    logger.warning(
        "litellm not installed — llm_service will use direct provider clients. "
        "Install with: pip install litellm"
    )

# ── Model constants ──────────────────────────────────────────────────────── #
LLM_NVIDIA   = "nvidia_nim/meta/llama-3.3-70b-instruct"
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


def generate(
    messages: List[Dict[str, str]],
    model: str = LLM_NVIDIA,
    temperature: float = 0.3,
    max_tokens: int = 2048,
    timeout: int = 30,
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
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
    if not LITELLM_AVAILABLE:
        return _generate_fallback(messages, model, temperature, max_tokens, timeout, api_key, api_base)

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
        nvidia_key = os.getenv("NVIDIA_API_KEY")
        if nvidia_key:
            kwargs["api_key"] = nvidia_key
    elif model.startswith("gpt-") or model.startswith("openai/"):
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            kwargs["api_key"] = openai_key
    elif model.startswith("claude") or model.startswith("anthropic/"):
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key:
            kwargs["api_key"] = anthropic_key

    # Per-provider base URL
    if api_base:
        kwargs["api_base"] = api_base
    elif model.startswith("ollama/"):
        kwargs["api_base"] = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    response = completion(**kwargs)
    choices = response.choices
    if not choices:
        logger.warning("llm_service.generate: empty choices from %s", model)
        return ""
    return choices[0].message.content or ""


def generate_with_fallback(
    messages: List[Dict[str, str]],
    temperature: float = 0.3,
    max_tokens: int = 2048,
) -> Dict[str, Any]:
    """
    3-tier fallback: NVIDIA → DeepSeek/Ollama → raises LLMUnavailableError.

    Returns:
        {"text": str, "model": str, "tier": int}
    """
    # Tier 1: NVIDIA NIM
    nvidia_key = os.getenv("NVIDIA_API_KEY")
    if nvidia_key:
        try:
            text = generate(messages, model=LLM_NVIDIA, temperature=temperature, max_tokens=max_tokens)
            if text:
                logger.info("llm_service: Tier 1 (NVIDIA) succeeded.")
                return {"text": text, "model": LLM_NVIDIA, "tier": 1}
        except Exception as exc:
            logger.warning("llm_service: Tier 1 (NVIDIA) failed: %s — trying DeepSeek.", exc)

    # Tier 2: DeepSeek via Ollama
    try:
        text = generate(messages, model=LLM_DEEPSEEK, temperature=temperature, max_tokens=max_tokens)
        if text:
            logger.info("llm_service: Tier 2 (DeepSeek) succeeded.")
            return {"text": text, "model": LLM_DEEPSEEK, "tier": 2}
    except Exception as exc:
        logger.warning("llm_service: Tier 2 (DeepSeek) failed: %s — no LLM available.", exc)

    raise LLMUnavailableError("All LLM tiers failed. Use rule-based fallback.")


class LLMUnavailableError(Exception):
    """Raised when all LLM tiers are exhausted."""
    pass


# ── Direct-client fallback (no litellm) ─────────────────────────────────── #
def _generate_fallback(
    messages, model, temperature, max_tokens, timeout, api_key, api_base
) -> str:
    """Direct HTTP fallback used when litellm is not installed."""
    if model.startswith("nvidia_nim/") or model.startswith("openai/") or model.startswith("gpt-"):
        return _openai_compat(
            messages, model, temperature, max_tokens,
            api_key or os.getenv("NVIDIA_API_KEY") or os.getenv("OPENAI_API_KEY"),
            api_base or ("https://integrate.api.nvidia.com/v1" if model.startswith("nvidia_nim/") else None),
        )
    elif model.startswith("ollama/"):
        return _ollama_http(
            messages, model.replace("ollama/", ""), temperature, max_tokens,
            api_base or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"), timeout,
        )
    raise NotImplementedError(f"No fallback implementation for model: {model}")


def _openai_compat(messages, model, temperature, max_tokens, api_key, base_url) -> str:
    from openai import OpenAI
    # Strip provider prefix for raw OpenAI/NVIDIA
    raw_model = model.replace("nvidia_nim/", "").replace("openai/", "")
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
