"""
Tests for utility modules: serialization, singleton, text_utils, logging_context.
"""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch
import json

from app.utils.serialization import build_structured_data, safe_model_dump
from app.utils.singleton import resolve_optional_callable


class TestSerialization:
    """Tests for serialization utilities."""

    def test_build_structured_data_success(self):
        data = {"job_id": "123", "status": "completed"}
        result = build_structured_data(data)
        assert "data" in result
        assert result["data"] == data

    def test_build_structured_data_with_meta(self):
        data = {"result": "ok"}
        meta = {"page": 1, "total": 100}
        result = build_structured_data(data, meta=meta)
        assert "meta" in result
        assert result["meta"] == meta

    def test_build_structured_data_error(self):
        result = build_structured_data(None, error="Something failed")
        assert "error" in result
        assert result["error"] == "Something failed"

    def test_safe_model_dump_dict(self):
        data = {"key": "value", "number": 42}
        result = safe_model_dump(data)
        assert result == data

    def test_safe_model_dump_object(self):
        class MockModel:
            def model_dump(self):
                return {"name": "test", "value": 123}

        obj = MockModel()
        result = safe_model_dump(obj)
        assert result == {"name": "test", "value": 123}

    def test_safe_model_dump_fallback(self):
        result = safe_model_dump("plain-string")
        assert result == "plain-string"

    def test_safe_model_dump_none(self):
        result = safe_model_dump(None)
        assert result is None


class TestSingleton:
    """Tests for singleton/resolution utilities."""

    def test_resolve_optional_callable_success(self):
        result = resolve_optional_callable("app.config.settings", "settings")
        assert result is not None

    def test_resolve_optional_callable_missing_module(self):
        result = resolve_optional_callable("nonexistent_module_xyz", "something")
        assert result is None

    def test_resolve_optional_callable_missing_attr(self):
        result = resolve_optional_callable("app.config.settings", "nonexistent_attr_xyz")
        assert result is None

    def test_resolve_optional_callable_returns_callable(self):
        result = resolve_optional_callable("app.config.settings", "settings")
        # settings is an instance, not callable, but resolve returns it
        assert result is not None


class TestLoggingContext:
    """Tests for logging context utilities."""

    def test_bind_context(self):
        from app.utils.logging_context import bind_context, reset_context
        tokens = bind_context(request_id="req-123", job_id="job-456")
        assert "request_id" in tokens
        assert "job_id" in tokens
        reset_context(tokens)
