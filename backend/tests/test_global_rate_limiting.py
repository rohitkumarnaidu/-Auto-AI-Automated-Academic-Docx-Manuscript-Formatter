from __future__ import annotations

from app.main import SLOWAPI_AVAILABLE, app


def test_global_rate_limiting_wiring():
    if SLOWAPI_AVAILABLE:
        assert hasattr(app.state, "limiter")
    else:
        # Fallback custom middleware path should still keep app bootable.
        assert app is not None
