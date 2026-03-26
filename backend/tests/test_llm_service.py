from __future__ import annotations

from app.services import llm_service


def test_generate_with_fallback_uses_groq_when_nvidia_unset(monkeypatch):
    monkeypatch.setattr(llm_service.settings, "NVIDIA_API_KEY", None, raising=False)
    monkeypatch.setattr(llm_service.settings, "GROQ_API_KEY", "groq-test-key", raising=False)
    monkeypatch.setattr(llm_service, "LLM_GROQ", "groq/llama3-8b-8192")

    calls: list[tuple[str, str | None]] = []

    def fake_generate(*args, **kwargs):
        calls.append((kwargs.get("model"), kwargs.get("api_key")))
        return "groq-answer"

    monkeypatch.setattr(llm_service, "generate", fake_generate)

    result = llm_service.generate_with_fallback(
        [{"role": "user", "content": "Summarize this document"}]
    )

    assert result == {
        "text": "groq-answer",
        "model": "groq/llama3-8b-8192",
        "tier": 2,
    }
    assert calls == [("groq/llama3-8b-8192", "groq-test-key")]


def test_generate_caches_groq_responses(monkeypatch):
    from app.cache import redis_cache as redis_cache_module

    cache_store: dict[str, str] = {}
    call_count = 0

    def fake_get(cache_key: str):
        return cache_store.get(cache_key)

    def fake_set(cache_key: str, text: str, ttl: int = 3600):
        cache_store[cache_key] = text

    def fake_fallback(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        return "cached-groq-answer"

    monkeypatch.setattr(llm_service, "LITELLM_AVAILABLE", False)
    monkeypatch.setattr(llm_service.settings, "LLM_CACHE_TTL_SECONDS", 3600, raising=False)
    monkeypatch.setattr(redis_cache_module.redis_cache, "client", object(), raising=False)
    monkeypatch.setattr(redis_cache_module.redis_cache, "get_llm_result", fake_get)
    monkeypatch.setattr(redis_cache_module.redis_cache, "set_llm_result", fake_set)
    monkeypatch.setattr(llm_service, "_generate_fallback", fake_fallback)

    messages = [{"role": "user", "content": "Explain Groq caching"}]
    first = llm_service.generate(messages, model="groq/llama3-8b-8192", api_key="groq-test-key")
    second = llm_service.generate(messages, model="groq/llama3-8b-8192", api_key="groq-test-key")

    assert first == "cached-groq-answer"
    assert second == "cached-groq-answer"
    assert call_count == 1
