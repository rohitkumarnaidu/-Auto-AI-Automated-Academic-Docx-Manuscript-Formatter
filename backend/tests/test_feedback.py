from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.user import User
from app.utils.dependencies import get_current_user


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def authenticated_user():
    user = User(id="user-123", email="user@example.com", role="authenticated")
    app.dependency_overrides[get_current_user] = lambda: user
    yield user
    app.dependency_overrides.pop(get_current_user, None)


def test_feedback_submission(client, authenticated_user):
    payload = {
        "document_id": "doc-1",
        "field": "title",
        "original_value": "Old Title",
        "corrected_value": "New Title",
        "comments": "Fix typo",
    }

    table = MagicMock()
    table.insert.return_value = table
    table.execute.return_value = SimpleNamespace(data=[{"id": "fb-1"}])
    sb = MagicMock()
    sb.table.return_value = table

    memory = MagicMock()
    with patch("app.routers.feedback.memory", memory), patch(
        "app.routers.feedback.get_supabase_client", return_value=sb
    ):
        response = client.post("/api/feedback/", json=payload)

    assert response.status_code == 201
    assert response.json()["status"] == "success"
    memory.remember_correction.assert_called_once()


def test_feedback_summary(client, authenticated_user):
    memory = MagicMock()
    memory.get_memory_summary.return_value = {"corrections": {"title": 3}}

    with patch("app.routers.feedback.memory", memory):
        response = client.get("/api/feedback/summary")

    assert response.status_code == 200
    assert response.json() == {"title": 3}


def test_feedback_requires_auth(client):
    payload = {
        "document_id": "doc-1",
        "field": "title",
        "original_value": "A",
        "corrected_value": "B",
    }
    response = client.post("/api/feedback/", json=payload)
    assert response.status_code in (401, 403)
