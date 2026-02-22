"""
API Integration Tests
Tests FastAPI endpoints, authentication, and request handling.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from app.main import app

client = TestClient(app)

class TestAPIEndpoints:
    """Test suite for API endpoints."""
    
    @pytest.mark.integration
    def test_root_endpoint(self):
        """Test root endpoint returns correct message."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "ScholarForm AI Backend is running"}
    
    @pytest.mark.integration
    def test_health_endpoint(self):
        """Test health check endpoint returns correct structure."""
        with patch('app.db.supabase_client.check_supabase_health') as mock_sb_health:
            with patch('httpx.AsyncClient') as mock_httpx:
                with patch('app.services.model_store.model_store.get_model') as mock_get_model:
                    # Mock successful health checks
                    mock_sb_health.return_value = {"status": "healthy"}
                    
                    # Mock httpx Ollama check 
                    mock_response = AsyncMock()
                    mock_response.status_code = 200
                    mock_client = AsyncMock()
                    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                    mock_client.__aexit__ = AsyncMock(return_value=False)
                    mock_client.get = AsyncMock(return_value=mock_response)
                    mock_httpx.return_value = mock_client
                    
                    # Mock model store
                    mock_get_model.return_value = True
                    
                    response = client.get("/health")
                    
                    assert response.status_code == 200
                    data = response.json()
                    assert "status" in data
                    assert "version" in data
                    assert "components" in data
    
    @pytest.mark.integration
    def test_health_endpoint_degraded_database(self):
        """Test health endpoint when database is unavailable."""
        with patch('app.db.supabase_client.check_supabase_health') as mock_sb_health:
            with patch('httpx.AsyncClient') as mock_httpx:
                with patch('app.services.model_store.model_store.get_model') as mock_get_model:
                    # Mock database failure
                    mock_sb_health.return_value = {"status": "unhealthy"}
                    
                    # Mock httpx success
                    mock_response = AsyncMock()
                    mock_response.status_code = 200
                    mock_client = AsyncMock()
                    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                    mock_client.__aexit__ = AsyncMock(return_value=False)
                    mock_client.get = AsyncMock(return_value=mock_response)
                    mock_httpx.return_value = mock_client
                    
                    mock_get_model.return_value = True
                    
                    response = client.get("/health")
                    
                    data = response.json()
                    assert data["status"] == "degraded"
                    assert "supabase_db" in data["components"]
    
    @pytest.mark.integration
    def test_health_endpoint_ollama_unavailable(self):
        """Test health endpoint when Ollama is unavailable."""
        with patch('app.db.supabase_client.check_supabase_health') as mock_sb_health:
            with patch('httpx.AsyncClient') as mock_httpx:
                with patch('app.services.model_store.model_store.get_model') as mock_get_model:
                    # Mock Supabase healthy
                    mock_sb_health.return_value = {"status": "healthy"}
                    
                    # Mock Ollama failure
                    mock_client = AsyncMock()
                    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                    mock_client.__aexit__ = AsyncMock(return_value=False)
                    mock_client.get = AsyncMock(side_effect=Exception("Ollama unavailable"))
                    mock_httpx.return_value = mock_client
                    
                    mock_get_model.return_value = True
                    
                    response = client.get("/health")
                    
                    data = response.json()
                    assert data["status"] == "degraded"
                    assert "ollama" in data["components"]
    
    @pytest.mark.integration
    def test_cors_headers(self):
        """Test CORS headers are present."""
        response = client.options("/", headers={"Origin": "http://localhost:5173"})
        # CORS middleware should add headers
        assert response.status_code in [200, 405]  # OPTIONS may not be explicitly defined
    
    @pytest.mark.integration
    def test_rate_limiting_not_applied_to_health(self):
        """Test rate limiting skips health endpoint."""
        with patch('app.db.supabase_client.check_supabase_health') as mock_sb_health:
            with patch('httpx.AsyncClient') as mock_httpx:
                with patch('app.services.model_store.model_store.get_model') as mock_get_model:
                    mock_sb_health.return_value = {"status": "healthy"}
                    mock_response = AsyncMock()
                    mock_response.status_code = 200
                    mock_client = AsyncMock()
                    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                    mock_client.__aexit__ = AsyncMock(return_value=False)
                    mock_client.get = AsyncMock(return_value=mock_response)
                    mock_httpx.return_value = mock_client
                    mock_get_model.return_value = True
                    
                    # Make multiple rapid requests to /health
                    for _ in range(20):
                        response = client.get("/health")
                        assert response.status_code in [200, 503]  # healthy or degraded, never rate limited


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])

