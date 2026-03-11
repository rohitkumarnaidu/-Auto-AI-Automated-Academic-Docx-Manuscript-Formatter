from __future__ import annotations

import os
import socket

import pytest


def _service_reachable(host: str, port: int, timeout: float = 0.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _docker_service_matrix() -> list[tuple[str, str, int]]:
    return [
        ("Redis", os.getenv("REDIS_HOST", "127.0.0.1"), int(os.getenv("REDIS_PORT", "6379"))),
        ("GROBID", os.getenv("GROBID_HOST", "127.0.0.1"), int(os.getenv("GROBID_PORT", "8070"))),
    ]


@pytest.fixture(autouse=True)
def ensure_docker_services_available():
    missing = [
        name
        for name, host, port in _docker_service_matrix()
        if not _service_reachable(host, port)
    ]
    if missing:
        pytest.skip(f"Service {', '.join(missing)} not available")


def pytest_collection_modifyitems(items):
    for item in items:
        path = str(item.fspath).replace("\\", "/")
        if "/tests/integration/" in path:
            item.add_marker(pytest.mark.integration)

