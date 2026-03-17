import time
from unittest.mock import patch

import jwt
import pytest
from fastapi.testclient import TestClient

# Import app - adjust import based on your actual structure
from app.main import app
from app.config.settings import settings

client = TestClient(app)

def test_rate_limiting_upload():
    """
    Verify that the upload endpoint enforces the 10 uploads/minute limit.
    """
    import uuid
    # Mock authentication to simulate a specific user
    # Use random token to avoid rate limit collision from previous test runs
    payload = {
        "sub": "test-user",
        "email": "test@example.com",
        "aud": "authenticated",
        "iss": f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1",
        "exp": int(time.time()) + 3600,
    }
    token = jwt.encode(payload, settings.SUPABASE_JWT_SECRET, algorithm=settings.ALGORITHM)
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a dummy file
    files = {'file': ('test.docx', b'test content', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
    
    # Make 10 allowed requests
    for i in range(10):
        response = client.post("/api/documents/upload", files=files, headers=headers)
        if response.status_code == 429:
            print(f"FAILED at request {i+1}: Got 429 too early. Body: {response.json()}")
            assert response.status_code != 429, f"Request {i+1} failed with 429"
        assert response.status_code in [200, 400, 422, 500, 503], f"Unexpected status {response.status_code}"

    # Make the 11th request - should fail
    response = client.post("/api/documents/upload", files=files, headers=headers)
    print(f"11th Request Status: {response.status_code}")
    if response.status_code != 429:
         print(f"Body: {response.text}")
    assert response.status_code == 429, f"11th request should be 429, got {response.status_code}"
    data = response.json()
    assert "rate limit exceeded" in data["error"].lower()

def test_file_size_limit(monkeypatch):
    """
    Verify that uploads larger than the configured limit are rejected.
    """
    monkeypatch.setattr(settings, "MAX_FILE_SIZE", 4)
    files = {"file": ("test.txt", b"12345", "text/plain")}

    with patch("app.routers.documents._require_db", return_value=None):
        with patch("app.routers.documents.DocumentService.create_document") as mock_create:
            response = client.post("/api/documents/upload", files=files)

    assert response.status_code == 413
    assert "Maximum size" in response.json()["detail"]
    mock_create.assert_not_called()

def test_cors_headers():
    """
    Verify CORS headers are present.
    """
    headers = {
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "POST",
    }
    response = client.options("/api/documents/upload", headers=headers)
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert "POST" in response.headers["access-control-allow-methods"]
