"""Regression tests for the startup-hardening changes introduced in commit 0eea3ab9.

The commit wrapped the bare ``_init_sentry()`` call inside
``_run_startup_step("sentry_init", _init_sentry, timeout_seconds=3.0)``
so that a slow or crashing Sentry SDK can never block application boot.

These tests verify:
  1. ``_run_startup_step`` applies a timeout and catches exceptions.
  2. ``_init_sentry`` handles missing SDK, missing DSN, and normal init.
  3. ``_sentry_before_send`` filters CancelledError / KeyboardInterrupt.
  4. The full lifespan invokes Sentry init through ``_run_startup_step``
     (not directly) and the app stays healthy even when Sentry fails.
"""

from __future__ import annotations

import asyncio
import time
from unittest.mock import MagicMock, AsyncMock, patch

import pytest

from app.main import (
    _init_sentry,
    _run_startup_step,
    _sentry_before_send,
    app,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _slow_callback():
    """Simulates a callback that blocks longer than the allowed timeout."""
    time.sleep(5)


def _crashing_callback():
    """Simulates a callback that raises an unexpected error."""
    raise RuntimeError("Sentry SDK exploded")


def _ok_callback():
    """Simulates a callback that completes successfully."""
    return "sentry-ok"


# ---------------------------------------------------------------------------
# _run_startup_step — timeout & exception resilience
# ---------------------------------------------------------------------------


class TestRunStartupStep:
    """Verify the generic startup-step wrapper introduced by the hardening commit."""

    @pytest.mark.asyncio
    async def test_returns_default_on_timeout(self):
        """A step that exceeds the timeout must NOT crash the boot sequence."""
        result = await _run_startup_step(
            "slow_step",
            _slow_callback,
            timeout_seconds=0.05,
            default_value="degraded",
        )
        assert result == "degraded"

    @pytest.mark.asyncio
    async def test_returns_default_on_exception(self):
        """A step that raises must NOT crash the boot sequence."""
        result = await _run_startup_step(
            "crashing_step",
            _crashing_callback,
            timeout_seconds=2.0,
            default_value="degraded",
        )
        assert result == "degraded"

    @pytest.mark.asyncio
    async def test_returns_callback_value_on_success(self):
        """A healthy step should propagate its return value."""
        result = await _run_startup_step(
            "ok_step",
            _ok_callback,
            timeout_seconds=2.0,
        )
        assert result == "sentry-ok"

    @pytest.mark.asyncio
    async def test_logs_warning_on_timeout(self):
        """A timed-out step must log a degraded-mode warning."""
        with patch("app.main.logger") as mock_logger:
            await _run_startup_step(
                "slow_step",
                _slow_callback,
                timeout_seconds=0.05,
            )
        mock_logger.warning.assert_called_once()
        msg = mock_logger.warning.call_args[0][0] % mock_logger.warning.call_args[0][1:]
        assert "slow_step" in msg
        assert "timed out" in msg

    @pytest.mark.asyncio
    async def test_logs_warning_on_exception(self):
        """A crashing step must log a degraded-mode warning."""
        with patch("app.main.logger") as mock_logger:
            await _run_startup_step(
                "crashing_step",
                _crashing_callback,
                timeout_seconds=2.0,
            )
        mock_logger.warning.assert_called_once()
        msg = mock_logger.warning.call_args[0][0] % mock_logger.warning.call_args[0][1:]
        assert "crashing_step" in msg
        assert "failed" in msg


# ---------------------------------------------------------------------------
# _init_sentry — SDK / DSN presence checks
# ---------------------------------------------------------------------------


class TestInitSentry:
    """Verify ``_init_sentry`` guards around SDK availability and DSN config."""

    def test_skips_when_sdk_not_available(self):
        """When the sentry_sdk package is not installed, init must be a no-op."""
        with (
            patch("app.main.SENTRY_AVAILABLE", False),
            patch("app.main.logger") as mock_logger,
        ):
            _init_sentry()
        mock_logger.info.assert_called_once()
        msg = str(mock_logger.info.call_args)
        assert "not installed" in msg.lower() or "skipping" in msg.lower()

    def test_skips_when_dsn_empty(self):
        """When SENTRY_DSN is unset, init must return without calling sentry_sdk.init."""
        with (
            patch("app.main.SENTRY_AVAILABLE", True),
            patch("app.main.settings") as mock_settings,
            patch("app.main.sentry_sdk") as mock_sdk,
        ):
            mock_settings.SENTRY_DSN = ""
            _init_sentry()
        mock_sdk.init.assert_not_called()

    def test_skips_when_dsn_none(self):
        """When SENTRY_DSN is None, init must return without calling sentry_sdk.init."""
        with (
            patch("app.main.SENTRY_AVAILABLE", True),
            patch("app.main.settings") as mock_settings,
            patch("app.main.sentry_sdk") as mock_sdk,
        ):
            mock_settings.SENTRY_DSN = None
            _init_sentry()
        mock_sdk.init.assert_not_called()

    def test_calls_sentry_init_with_correct_params(self):
        """When SDK is available and DSN is set, sentry_sdk.init must be called."""
        with (
            patch("app.main.SENTRY_AVAILABLE", True),
            patch("app.main.sentry_sdk") as mock_sdk,
            patch("app.main.settings") as mock_settings,
            patch("app.main.StarletteIntegration") as mock_starlette,
            patch("app.main.FastApiIntegration") as mock_fastapi,
            patch("app.main.LoggingIntegration") as mock_logging,
            patch.dict("os.environ", {"ENVIRONMENT": "testing", "APP_VERSION": "2.0.0"}),
        ):
            mock_settings.SENTRY_DSN = "https://key@sentry.io/123"
            _init_sentry()

        mock_sdk.init.assert_called_once()
        kwargs = mock_sdk.init.call_args
        assert kwargs.kwargs["dsn"] == "https://key@sentry.io/123"
        assert kwargs.kwargs["traces_sample_rate"] == 0.1
        assert kwargs.kwargs["send_default_pii"] is False
        assert kwargs.kwargs["environment"] == "testing"
        assert kwargs.kwargs["release"] == "2.0.0"
        assert kwargs.kwargs["before_send"] is _sentry_before_send


# ---------------------------------------------------------------------------
# _sentry_before_send — event filtering
# ---------------------------------------------------------------------------


class TestSentryBeforeSend:
    """Verify the before_send hook drops noise events and keeps real errors."""

    def test_drops_cancelled_error_via_exc_info(self):
        """CancelledError passed through hint.exc_info must be dropped."""
        event = {"exception": {"values": []}}
        hint = {"exc_info": (asyncio.CancelledError, asyncio.CancelledError(), None)}
        assert _sentry_before_send(event, hint) is None

    def test_drops_keyboard_interrupt_via_exc_info(self):
        """KeyboardInterrupt passed through hint.exc_info must be dropped."""
        event = {"exception": {"values": []}}
        hint = {"exc_info": (KeyboardInterrupt, KeyboardInterrupt(), None)}
        assert _sentry_before_send(event, hint) is None

    def test_drops_cancelled_error_via_exception_values(self):
        """CancelledError reported in event.exception.values must be dropped."""
        event = {"exception": {"values": [{"type": "CancelledError"}]}}
        assert _sentry_before_send(event, {}) is None

    def test_drops_keyboard_interrupt_via_exception_values(self):
        """KeyboardInterrupt reported in event.exception.values must be dropped."""
        event = {"exception": {"values": [{"type": "KeyboardInterrupt"}]}}
        assert _sentry_before_send(event, {}) is None

    def test_passes_real_errors_through(self):
        """A genuine ValueError event must NOT be filtered."""
        event = {"exception": {"values": [{"type": "ValueError"}]}}
        hint = {"exc_info": (ValueError, ValueError("bad input"), None)}
        result = _sentry_before_send(event, hint)
        assert result is event

    def test_passes_event_with_no_hint(self):
        """An event with no hint at all must pass through."""
        event = {"exception": {"values": [{"type": "RuntimeError"}]}}
        result = _sentry_before_send(event, None)
        assert result is event

    def test_passes_event_with_empty_exception_values(self):
        """An event with empty exception values and no hint must pass through."""
        event = {"exception": {"values": []}}
        result = _sentry_before_send(event, {})
        assert result is event


# ---------------------------------------------------------------------------
# Lifespan integration — Sentry init routed through _run_startup_step
# ---------------------------------------------------------------------------


class TestLifespanSentryIntegration:
    """Verify the lifespan uses ``_run_startup_step`` (not bare ``_init_sentry``)."""

    def test_lifespan_calls_run_startup_step_for_sentry(self):
        """The hardened lifespan must call ``_run_startup_step('sentry_init', …)``."""
        from fastapi.testclient import TestClient

        with (
            patch("app.main._run_startup_step", new_callable=AsyncMock) as mock_step,
            patch("app.main._probe_grobid_startup", new_callable=AsyncMock, return_value=False),
            patch("app.pipeline.intelligence.semantic_parser.get_semantic_parser", return_value=MagicMock()),
            patch("app.pipeline.intelligence.rag_engine.get_rag_engine", return_value=MagicMock()),
        ):
            with TestClient(app):
                pass

        # Find the sentry_init call among potentially multiple _run_startup_step calls
        sentry_calls = [c for c in mock_step.call_args_list if c.args and c.args[0] == "sentry_init"]
        assert (
            len(sentry_calls) == 1
        ), f"Expected exactly one _run_startup_step('sentry_init', ...) call, got {len(sentry_calls)}"
        _, kwargs = sentry_calls[0].args, sentry_calls[0].kwargs
        assert sentry_calls[0].args[1] is _init_sentry
        assert kwargs.get("timeout_seconds") == 3.0

    def test_app_healthy_even_when_sentry_init_times_out(self):
        """If Sentry init times out, the app must still serve /api/v1/health."""
        from fastapi.testclient import TestClient

        async def _fake_step(name, cb, *, timeout_seconds, default_value=None):
            if name == "sentry_init":
                # Simulate timeout
                return default_value
            # Run other steps normally
            return cb()

        with (
            patch("app.main._run_startup_step", side_effect=_fake_step),
            patch("app.main._probe_grobid_startup", new_callable=AsyncMock, return_value=False),
            patch("app.pipeline.intelligence.semantic_parser.get_semantic_parser", return_value=MagicMock()),
            patch("app.pipeline.intelligence.rag_engine.get_rag_engine", return_value=MagicMock()),
        ):
            with TestClient(app) as client:
                response = client.get("/api/v1/health")

        assert response.status_code == 200

    def test_app_healthy_even_when_sentry_init_raises(self):
        """If Sentry init raises, the app must still serve /api/v1/health."""
        from fastapi.testclient import TestClient

        async def _fake_step(name, cb, *, timeout_seconds, default_value=None):
            if name == "sentry_init":
                # Simulate _run_startup_step catching a real exception from cb().
                try:
                    raise RuntimeError("Sentry SDK exploded during init")
                except Exception:
                    return default_value
            return cb()

        with (
            patch("app.main._run_startup_step", side_effect=_fake_step),
            patch("app.main._probe_grobid_startup", new_callable=AsyncMock, return_value=False),
            patch("app.pipeline.intelligence.semantic_parser.get_semantic_parser", return_value=MagicMock()),
            patch("app.pipeline.intelligence.rag_engine.get_rag_engine", return_value=MagicMock()),
        ):
            with TestClient(app) as client:
                response = client.get("/api/v1/health")

        assert response.status_code == 200
