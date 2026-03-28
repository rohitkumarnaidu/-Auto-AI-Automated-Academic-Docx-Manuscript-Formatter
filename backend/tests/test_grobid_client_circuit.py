from __future__ import annotations

from types import SimpleNamespace

from app.pipeline.services.grobid_client import GROBIDClient


def test_grobid_client_uses_hard_timeout_from_settings(monkeypatch):
    monkeypatch.setattr("app.pipeline.services.grobid_client.settings.GROBID_TIMEOUT", 120, raising=False)
    monkeypatch.setattr("app.pipeline.services.grobid_client.settings.GROBID_MAX_RETRIES", 2, raising=False)

    client = GROBIDClient(base_url="http://grobid.local:8070")
    # Timeout is capped to avoid cascading stalls.
    assert client.timeout == 30
    assert client.max_retries == 2


def test_grobid_client_is_available_handles_request_errors(monkeypatch):
    client = GROBIDClient(base_url="http://grobid.local:8070")

    def failing_request(*args, **kwargs):
        raise RuntimeError("network down")

    monkeypatch.setattr(client, "_request", failing_request)
    assert client.is_available() is False


def test_grobid_client_request_sets_timeout_tuple(monkeypatch):
    client = GROBIDClient(base_url="http://grobid.local:8070")
    captured = {}

    def fake_request(method, url, **kwargs):
        captured["timeout"] = kwargs.get("timeout")
        return SimpleNamespace(status_code=200, text="<tei></tei>")

    monkeypatch.setattr("app.pipeline.services.grobid_client.requests.request", fake_request)
    response = client._request("GET", "http://grobid.local:8070/api/isalive")

    assert response.status_code == 200
    assert isinstance(captured["timeout"], tuple)
