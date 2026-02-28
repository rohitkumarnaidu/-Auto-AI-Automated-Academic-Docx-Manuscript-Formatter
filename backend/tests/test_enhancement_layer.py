from types import SimpleNamespace
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.pipeline.ocr import pdf_ocr
from app.utils.dependencies import get_current_user


client = TestClient(app)


def test_metrics_enhancements_endpoint_returns_profile_for_admin():
    admin_user = SimpleNamespace(role="admin", app_metadata={"role": "admin"})
    app.dependency_overrides[get_current_user] = lambda: admin_user
    try:
        response = client.get("/api/metrics/enhancements")
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "success"
    assert "profile" in payload
    assert "ocr_backends" in payload
    assert "queue_mode" in payload


def test_pdf_ocr_backend_normalization_filters_unavailable_backends():
    with patch.object(pdf_ocr, "TESSERACT_AVAILABLE", False), \
         patch.object(pdf_ocr, "PADDLE_AVAILABLE", True), \
         patch.object(pdf_ocr, "NUMPY_AVAILABLE", True):
        ocr = pdf_ocr.PdfOCR()
        normalized = ocr._normalize_backends(["tesseract", "paddle", "unknown", "paddle"])
        assert normalized == ["paddle"]
