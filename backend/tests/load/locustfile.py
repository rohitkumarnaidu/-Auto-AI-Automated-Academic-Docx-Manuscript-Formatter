"""
Locust load tests for ScholarForm backend.

Scenarios:
- Upload: 100 concurrent users uploading 1-page DOCX -> P99 ACK < 400ms
- Status poll: 100 concurrent GET /status -> P99 < 100ms
- Live preview: 50 concurrent WebSocket connections -> P99 RTT < 200ms
- Templates: 200 concurrent GET /templates -> P99 < 80ms
"""
from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from urllib.parse import urlparse

from locust import HttpUser, User, task, between, events

try:
    from websocket import create_connection
except Exception:  # pragma: no cover
    create_connection = None  # type: ignore[assignment]


SAMPLE_DOC_PATH = Path(__file__).resolve().parents[2] / "manual_tests" / "sample_inputs" / "sample.docx"
SAMPLE_DOC_BYTES = SAMPLE_DOC_PATH.read_bytes() if SAMPLE_DOC_PATH.exists() else b""


def _ws_base_url(http_base: str) -> str:
    parsed = urlparse(http_base)
    scheme = "wss" if parsed.scheme == "https" else "ws"
    return f"{scheme}://{parsed.netloc}"


class UploadUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def upload_document(self):
        if not SAMPLE_DOC_BYTES:
            events.request.fire(
                request_type="UPLOAD",
                name="upload_document",
                response_time=0,
                response_length=0,
                exception=RuntimeError("Sample DOCX missing."),
            )
            return
        files = {
            "file": (
                "sample.docx",
                SAMPLE_DOC_BYTES,
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        }
        with self.client.post("/api/v1/documents/upload", files=files, catch_response=True) as resp:
            if resp.status_code != 200:
                resp.failure(f"Upload failed: {resp.status_code}")


class StatusPollUser(HttpUser):
    wait_time = between(0.5, 1.5)
    job_id: str | None = None

    def on_start(self):
        self.job_id = None
        if not SAMPLE_DOC_BYTES:
            return
        files = {
            "file": (
                "sample.docx",
                SAMPLE_DOC_BYTES,
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        }
        resp = self.client.post("/api/v1/documents/upload", files=files)
        if resp.status_code == 200:
            try:
                self.job_id = resp.json().get("job_id")
            except Exception:
                self.job_id = None

    @task
    def poll_status(self):
        if not self.job_id:
            return
        self.client.get(f"/api/v1/documents/{self.job_id}/status")


class TemplatesUser(HttpUser):
    wait_time = between(0.2, 1.0)

    @task
    def list_templates(self):
        self.client.get("/api/v1/templates")


class PreviewWebSocketUser(User):
    wait_time = between(1, 3)

    @task
    def preview_ws_roundtrip(self):
        if create_connection is None:
            events.request.fire(
                request_type="WS",
                name="preview_ws",
                response_time=0,
                response_length=0,
                exception=RuntimeError("websocket-client not available"),
            )
            return
        session_id = uuid.uuid4().hex[:12]
        ws_url = f"{_ws_base_url(self.host)}/api/v1/ws/preview/{session_id}"
        payload = json.dumps({"content": "Sample content", "templateId": "none", "seq": 1})
        start = time.perf_counter()
        try:
            ws = create_connection(ws_url, timeout=10)
            ws.send(payload)
            ws.recv()
            ws.close()
            duration_ms = (time.perf_counter() - start) * 1000.0
            events.request.fire(
                request_type="WS",
                name="preview_ws",
                response_time=duration_ms,
                response_length=0,
                exception=None,
            )
        except Exception as exc:
            duration_ms = (time.perf_counter() - start) * 1000.0
            events.request.fire(
                request_type="WS",
                name="preview_ws",
                response_time=duration_ms,
                response_length=0,
                exception=exc,
            )
