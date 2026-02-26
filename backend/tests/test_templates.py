from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.user import User
from app.utils.dependencies import get_optional_user


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def authenticated_user():
    user = User(id="user-123", email="user@example.com", role="authenticated")
    app.dependency_overrides[get_optional_user] = lambda: user
    yield user
    app.dependency_overrides.pop(get_optional_user, None)


def _mock_table_chain() -> MagicMock:
    table = MagicMock()
    table.select.return_value = table
    table.eq.return_value = table
    table.order.return_value = table
    table.insert.return_value = table
    table.update.return_value = table
    table.delete.return_value = table
    table.maybe_single.return_value = table
    return table


def test_list_custom_templates_requires_auth(client):
    response = client.get("/api/templates/custom")
    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required"


def test_custom_template_crud(client, authenticated_user):
    user_id = authenticated_user.id
    base_template = {
        "id": "tpl-1",
        "user_id": user_id,
        "name": "My Custom Template",
        "description": "test",
        "config": {"font_family": "Times New Roman", "font_size": 12},
        "created_at": "2026-02-26T10:00:00+00:00",
        "updated_at": "2026-02-26T10:00:00+00:00",
    }

    # Create
    create_table = _mock_table_chain()
    create_table.execute.return_value = SimpleNamespace(data=[base_template])
    create_sb = MagicMock()
    create_sb.table.return_value = create_table
    with patch("app.routers.templates.get_supabase_client", return_value=create_sb):
        response = client.post(
            "/api/templates/custom",
            json={"template": {"name": "My Custom Template", "settings": {"font_family": "Times New Roman"}}},
        )
    assert response.status_code == 200
    assert response.json()["template"]["name"] == "My Custom Template"

    # List
    list_table = _mock_table_chain()
    list_table.execute.return_value = SimpleNamespace(data=[base_template])
    list_sb = MagicMock()
    list_sb.table.return_value = list_table
    with patch("app.routers.templates.get_supabase_client", return_value=list_sb):
        response = client.get("/api/templates/custom")
    assert response.status_code == 200
    assert len(response.json()["templates"]) == 1

    # Update
    updated_template = dict(base_template)
    updated_template["name"] = "Updated Template"
    update_table = _mock_table_chain()
    update_table.execute.return_value = SimpleNamespace(data=[updated_template])
    update_sb = MagicMock()
    update_sb.table.return_value = update_table
    with patch("app.routers.templates.get_supabase_client", return_value=update_sb):
        response = client.put(
            "/api/templates/custom/tpl-1",
            json={"template": {"name": "Updated Template", "settings": {"font_family": "Cambria"}}},
        )
    assert response.status_code == 200
    assert response.json()["template"]["name"] == "Updated Template"

    # Delete
    delete_table = _mock_table_chain()
    delete_table.execute.side_effect = [
        SimpleNamespace(data={"id": "tpl-1"}),
        SimpleNamespace(data=[{"id": "tpl-1"}]),
    ]
    delete_sb = MagicMock()
    delete_sb.table.return_value = delete_table
    with patch("app.routers.templates.get_supabase_client", return_value=delete_sb):
        response = client.delete("/api/templates/custom/tpl-1")
    assert response.status_code == 200
    assert response.json()["status"] == "deleted"


def test_custom_template_validation(client, authenticated_user):
    sb = MagicMock()
    with patch("app.routers.templates.get_supabase_client", return_value=sb):
        response = client.post(
            "/api/templates/custom",
            json={"template": {"name": "Invalid Config", "settings": ["not", "an", "object"]}},
        )
    assert response.status_code == 422
    assert "config" in response.json()["detail"].lower()
