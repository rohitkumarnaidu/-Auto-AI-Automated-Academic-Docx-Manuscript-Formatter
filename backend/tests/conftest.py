"""
conftest.py — shared pytest fixtures for ScholarForm AI backend tests.
"""
from __future__ import annotations

import os
import socket
import sys
from pathlib import Path
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
if Path.cwd() != BACKEND_ROOT:
    os.chdir(BACKEND_ROOT)

from app.services import health_checks


def _service_reachable(host: str, port: int, timeout: float = 0.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _integration_service_status() -> list[str]:
    service_matrix = [
        ("Redis", os.getenv("REDIS_HOST", "127.0.0.1"), int(os.getenv("REDIS_PORT", "6379"))),
        ("GROBID", os.getenv("GROBID_HOST", "127.0.0.1"), int(os.getenv("GROBID_PORT", "8070"))),
    ]
    return [name for name, host, port in service_matrix if not _service_reachable(host, port)]


@pytest.fixture(autouse=True)
def skip_integration_when_services_unavailable(request):
    if "integration" not in request.keywords:
        return
    missing = _integration_service_status()
    if missing:
        pytest.skip(f"Service {', '.join(missing)} not available")


@pytest.fixture(autouse=True)
def mock_redis():
    """Mock Redis globally for all tests."""
    with patch("app.routers.stream._pubsub.publish", new_callable=AsyncMock) as mock_stream_publish:
        with patch("app.middleware.rate_limit.redis") as mock_limit:
            with patch("app.cache.redis_cache.redis.Redis") as mock_cache:
                mock_limit.return_value = MagicMock()
                mock_cache.return_value = MagicMock()
                yield {
                    "stream_publish": mock_stream_publish,
                    "rate_limit": mock_limit,
                    "cache": mock_cache,
                }


@pytest.fixture(autouse=True)
def reset_health_check_caches():
    """Avoid cross-test contamination from cached /health and /ready payloads."""
    health_checks._reset_readiness_cache_for_tests()
    yield
    health_checks._reset_readiness_cache_for_tests()


from app.models import (
    Block,
    BlockType,
    DocumentMetadata,
    PipelineDocument,
    Reference,
    ReferenceType,
)


# ── Document fixtures ──────────────────────────────────────────────────────────

@pytest.fixture()
def minimal_doc() -> PipelineDocument:
    """Bare-minimum PipelineDocument with title + one body block."""
    doc = PipelineDocument(
        document_id="test-doc-001",
        metadata=DocumentMetadata(
            title="Test Manuscript",
            authors=["Jane Doe"],
            abstract="A short abstract.",
        ),
    )
    doc.blocks = [
        Block(block_id="b1", index=1, block_type=BlockType.TITLE,  text="Test Manuscript"),
        Block(block_id="b2", index=2, block_type=BlockType.HEADING_1, text="Introduction"),
        Block(block_id="b3", index=3, block_type=BlockType.BODY,   text="Body content here."),
    ]
    return doc


@pytest.fixture()
def full_doc(minimal_doc: PipelineDocument) -> PipelineDocument:
    """PipelineDocument with metadata, blocks, and a reference."""
    minimal_doc.metadata.keywords = ["formatting", "test"]
    minimal_doc.metadata.affiliations = ["Test University"]
    ref = Reference(
        reference_id="ref_1",
        citation_key="ref1",
        raw_text="[1] J. Doe, Testing, 2024.",
        reference_type=ReferenceType.JOURNAL_ARTICLE,
        authors=["Doe, J."],
        title="Testing",
        year=2024,
        index=0,
        formatted_text="[1] J. Doe, 'Testing,' 2024.",
    )
    minimal_doc.references = [ref]
    minimal_doc.blocks.append(
        Block(block_id="b4", index=4, block_type=BlockType.REFERENCE_ENTRY, text="[1] J. Doe, Testing, 2024.")
    )
    return minimal_doc
