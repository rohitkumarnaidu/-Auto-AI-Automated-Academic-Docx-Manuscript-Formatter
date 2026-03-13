from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional


@dataclass
class RealtimeEvent:
    event_type: str
    job_id: Optional[str] = None
    session_id: Optional[str] = None
    stage: Optional[str] = None
    progress: Optional[int] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    payload: Dict[str, Any] = field(default_factory=dict)


def make_event(event_type: str, **kwargs: Any) -> Dict[str, Any]:
    timestamp = kwargs.pop("timestamp", None)
    payload = kwargs.pop("payload", None)
    event = RealtimeEvent(event_type=event_type, payload=payload or {}, **kwargs)
    if timestamp is not None:
        event.timestamp = timestamp
    data = asdict(event)
    data["timestamp"] = event.timestamp.isoformat()
    return data
