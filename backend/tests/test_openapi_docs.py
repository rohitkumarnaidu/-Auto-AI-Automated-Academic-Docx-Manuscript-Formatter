from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_openapi_json_is_exposed() -> None:
    with TestClient(app) as client:
        response = client.get("/openapi.json")

    assert response.status_code == 200
    assert response.headers.get("content-type", "").startswith("application/json")
    payload = response.json()
    assert payload.get("openapi")
    assert isinstance(payload.get("paths"), dict)
    assert "/api/v1/documents/upload" in payload["paths"]


def test_swagger_docs_ui_is_exposed() -> None:
    with TestClient(app) as client:
        response = client.get("/docs")

    assert response.status_code == 200
    assert "swagger-ui" in response.text.lower()


def test_redoc_ui_is_exposed() -> None:
    with TestClient(app) as client:
        response = client.get("/redoc")

    assert response.status_code == 200
    assert "redoc" in response.text.lower()
