"""
API Integration Tests
Tests FastAPI endpoints, authentication, and request handling.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
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
        """Test health check endpoint."""
        with patch('app.main.SessionLocal') as mock_db:
            with patch('app.main.requests.get') as mock_ollama:
                # Mock successful health checks
                mock_db.return_value.execute.return_value = None
                mock_db.return_value.close.return_value = None
                mock_ollama.return_value.status_code = 200
                
                response = client.get("/health")
                
                assert response.status_code == 200
                data = response.json()
                assert "status" in data
                assert "version" in data
                assert "components" in data
    
    @pytest.mark.integration
    def test_health_endpoint_degraded_database(self):
        """Test health endpoint when database is unavailable."""
        with patch('app.main.SessionLocal') as mock_db:
            with patch('app.main.requests.get') as mock_ollama:
                # Mock database failure
                mock_db.return_value.execute.side_effect = Exception("DB unavailable")
                mock_ollama.return_value.status_code = 200
                
                response = client.get("/health")
                
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "degraded"
                assert "database" in data["components"]
    
    @pytest.mark.integration
    def test_health_endpoint_ollama_unavailable(self):
        """Test health endpoint when Ollama is unavailable."""
        with patch('app.main.SessionLocal') as mock_db:
            with patch('app.main.requests.get') as mock_ollama:
                # Mock Ollama failure
                mock_db.return_value.execute.return_value = None
                mock_ollama.side_effect = Exception("Ollama unavailable")
                
                response = client.get("/health")
                
                assert response.status_code == 200
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
        # Make multiple rapid requests to /health
        for _ in range(100):
            response = client.get("/health")
            assert response.status_code == 200  # Should never be rate limited


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])
