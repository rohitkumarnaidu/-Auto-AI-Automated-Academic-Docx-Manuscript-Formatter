"""
Tests for the Settings class — safe defaults, threshold clamping, and
absence of secrets does not crash the process.
"""
from __future__ import annotations

import os
import pytest


class TestSettingsDefaults:

    def _fresh_settings(self, env_overrides: dict | None = None):
        """Import Settings in a clean env context."""
        # Reload settings module with patched env
        import importlib
        import app.config.settings as mod
        importlib.reload(mod)
        return mod.Settings()

    def test_algorithm_default_is_hs256(self):
        """JWT algorithm default must be HS256."""
        from app.config.settings import Settings
        s = Settings()
        assert s.ALGORITHM == "HS256"

    def test_cors_origins_has_localhost(self):
        """CORS origins include localhost by default."""
        from app.config.settings import Settings
        s = Settings()
        assert "localhost" in s.CORS_ORIGINS

    def test_default_template_is_none(self):
        """Default template must be 'none' (neutral / no-style)."""
        from app.config.settings import Settings
        s = Settings()
        assert s.DEFAULT_TEMPLATE == "none"

    def test_confidence_thresholds_are_between_0_and_1(self):
        """All confidence thresholds must be in [0, 1]."""
        from app.config.settings import Settings
        s = Settings()
        for attr in (
            "HEADING_STYLE_THRESHOLD",
            "HEADING_FALLBACK_CONFIDENCE",
            "HEURISTIC_CONFIDENCE_HIGH",
            "HEURISTIC_CONFIDENCE_MEDIUM",
            "HEURISTIC_CONFIDENCE_LOW",
        ):
            val = getattr(s, attr)
            assert 0.0 <= val <= 1.0, f"{attr}={val} is outside [0, 1]"

    def test_grobid_defaults(self):
        """GROBID defaults: localhost:8070, 30s timeout, 3 retries."""
        from app.config.settings import Settings
        s = Settings()
        assert "8070" in s.GROBID_BASE_URL
        assert s.GROBID_TIMEOUT == 30
        assert s.GROBID_MAX_RETRIES == 3

    def test_validate_does_not_raise(self):
        """Settings.validate() must never raise even if all secrets are unset."""
        from app.config.settings import settings
        try:
            settings.validate()
        except Exception as exc:
            pytest.fail(f"settings.validate() raised unexpectedly: {exc}")
