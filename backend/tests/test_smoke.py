import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch, AsyncMock

@pytest.fixture(autouse=True)
def mock_ai_models():
    """Mock AI model pre-loading to speed up tests."""
    with patch("app.pipeline.intelligence.semantic_parser.get_semantic_parser") as mock_parser, \
         patch("app.pipeline.intelligence.rag_engine.get_rag_engine") as mock_rag:
        
        parser_instance = MagicMock()
        mock_parser.return_value = parser_instance
        
        rag_instance = MagicMock()
        mock_rag.return_value = rag_instance
        yield

@pytest.fixture
def client():
    """Setup TestClient with dependency overrides and mocked service."""
    from app.main import app
    from app.utils.dependencies import get_current_user, get_optional_user
    from app.services.document_service import DocumentService
    
    mock_service = MagicMock(spec=DocumentService)
    
    mock_redis = AsyncMock()
    mock_redis.incr.return_value = 1
    mock_redis.expire.return_value = True
    
    mock_user = MagicMock()
    mock_user.id = "mock-user-123"
    
    app.dependency_overrides[get_optional_user] = lambda: mock_user
    app.dependency_overrides[get_current_user] = lambda: mock_user
    
    with patch("app.routers.documents.DocumentService", mock_service), \
         patch("app.routers.documents._require_db", return_value=None), \
         patch("app.middleware.rate_limit.redis", mock_redis):
        with TestClient(app) as c:
            c.mock_service = mock_service
            c.mock_user = mock_user
            yield c
            
    app.dependency_overrides = {}

@pytest.mark.contract
class TestAPISmokeEndpoints:
    
    def test_health_smoke(self, client):
        """2.3 Add API contract smoke: GET /health"""
        # Testing root health without requiring redis patch as it uses httpx internally
        response = client.get("/health")
        assert response.status_code in (200, 503)
        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "degraded", "unhealthy"]

    def test_templates_smoke(self, client):
        """Built-in template listing returns concrete template metadata."""
        response = client.get("/api/templates")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data.get("templates"), list)
        assert any(item["id"] == "ieee" for item in data["templates"])

    def test_deprecation_header_smoke(self, client):
        """Legacy public endpoints emit deprecation headers."""
        response = client.get("/api/templates")
        assert response.status_code == 200
        assert response.headers["Deprecation"] == "true"
        assert response.headers["Sunset"]
        assert 'successor-version' in response.headers["Link"]

    def test_signed_download_smoke(self, client, tmp_path):
        """Signed download flow returns a URL and serves the binary file."""
        job_id = "test-job-999"
        output_path = tmp_path / "demo.docx"
        output_path.write_bytes(b"PK\x03\x04demo-docx")
        client.mock_service.get_document.return_value = {
            "id": job_id,
            "filename": "demo.docx",
            "user_id": client.mock_user.id,
            "status": "COMPLETED",
            "output_path": str(output_path),
        }
        client.mock_service.generate_signed_download_url.return_value = {
            "url": f"http://testserver/api/v1/documents/{job_id}/download?format=docx&token=fake-token&expires=1234567890",
            "expires": 1234567890,
        }
        client.mock_service.verify_signed_download.return_value = True

        response = client.get(f"/api/v1/documents/{job_id}/download?format=docx")
        assert response.status_code == 200
        payload = response.json()
        assert payload["data"]["expires"] == 1234567890
        assert "token=fake-token" in payload["data"]["url"]

        signed_response = client.get(
            f"/api/v1/documents/{job_id}/download?format=docx&token=fake-token&expires=1234567890"
        )
        assert signed_response.status_code == 200
        assert (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            in signed_response.headers["content-type"]
        )
        
    def test_upload_smoke(self, client):
        """2.2 Add API contract smoke: POST /api/v1/documents/upload"""
        client.mock_service.create_document.return_value = {"id": "job-123"}
        with patch("app.routers.documents.enhancement_manager.dispatch_document_pipeline", return_value={"mode": "standard"}) as mock_pipeline:
            # Need valid PK magic bytes for .docx
            response = client.post(
                "/api/v1/documents/upload",
                files={"file": ("test.docx", b"\x50\x4b\x03\x04dummy content", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
                data={"template": "IEEE"}
            )
            assert response.status_code in (200, 201, 202)

    def test_generator_session_crud_smoke(self, client):
        """Agent session creation uses the current v1 generator API contract."""
        with patch("app.routers.v1.generator._require_celery_for_agent", return_value=None):
            with patch(
                "app.routers.v1.generator._session_service.create_session",
                new_callable=AsyncMock,
                return_value="sess-123",
            ):
                with patch("app.routers.v1.generator._session_service.add_message", new_callable=AsyncMock):
                    with patch("app.routers.v1.generator.audit_log_service.log", new_callable=AsyncMock):
                        with patch("app.tasks.celery_tasks.process_agent_pipeline_task.delay") as mock_delay:
                            response = client.post(
                                "/api/v1/generator/sessions",
                                json={
                                    "session_type": "agent",
                                    "prompt": "Draft an abstract about AI formatting",
                                    "template": "ieee",
                                },
                            )

        assert response.status_code == 202
        assert response.json() == {"session_id": "sess-123", "status": "started"}
        mock_delay.assert_called_once_with("sess-123", "Draft an abstract about AI formatting")
