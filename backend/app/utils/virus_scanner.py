from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict

from app.config.settings import settings

logger = logging.getLogger(__name__)

try:
    import clamd  # type: ignore
except Exception:  # pragma: no cover - optional dependency in some test environments
    clamd = None


def scan_file(file_path: str) -> Dict[str, str | bool]:
    """
    Scan a file with ClamAV.

    Returns:
        {
          "clean": bool,
          "engine": "clamav" | "unavailable",
          "result": "clean" | "scan_skipped" | "<threat_name>"
        }
    """
    candidate = str(Path(file_path))

    if clamd is None:
        logger.warning("ClamAV client library unavailable. Skipping malware scan for %s", candidate)
        return {"clean": True, "engine": "unavailable", "result": "scan_skipped"}

    host = settings.CLAMAV_HOST
    port = int(settings.CLAMAV_PORT)

    try:
        client = clamd.ClamdNetworkSocket(host=host, port=port)
        client.ping()
    except Exception as exc:
        logger.warning("ClamAV unavailable at %s:%s. Skipping malware scan (%s).", host, port, exc)
        return {"clean": True, "engine": "unavailable", "result": "scan_skipped"}

    try:
        result = client.scan(candidate) or {}
    except Exception as exc:
        logger.warning("ClamAV scan failed for %s. Skipping scan (%s).", candidate, exc)
        return {"clean": True, "engine": "unavailable", "result": "scan_skipped"}

    if not result:
        return {"clean": True, "engine": "clamav", "result": "clean"}

    status, details = result.get(candidate, ("OK", "clean"))
    if str(status).upper() == "FOUND":
        threat_name = str(details or "unknown_threat")
        return {"clean": False, "engine": "clamav", "result": threat_name}

    return {"clean": True, "engine": "clamav", "result": "clean"}
