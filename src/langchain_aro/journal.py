from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any
from uuid import uuid4


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def make_json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, BaseException):
        return {"type": type(value).__name__, "message": str(value)}
    if is_dataclass(value):
        return make_json_safe(asdict(value))
    if isinstance(value, dict):
        return {str(key): make_json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [make_json_safe(item) for item in value]
    return repr(value)


@dataclass(slots=True)
class JournalEvent:
    event_type: str
    timestamp: str
    payload: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.event_type,
            "timestamp": self.timestamp,
            "payload": make_json_safe(self.payload),
        }


@dataclass(slots=True)
class RunJournal:
    project: str
    run_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=utc_now_iso)
    events: list[JournalEvent] = field(default_factory=list)

    def append(
        self,
        event_type: str,
        payload: dict[str, Any] | None = None,
        *,
        timestamp: str | None = None,
    ) -> JournalEvent:
        event = JournalEvent(
            event_type=event_type,
            timestamp=timestamp or utc_now_iso(),
            payload=make_json_safe(payload or {}),
        )
        self.events.append(event)
        return event

    def to_dict(self) -> dict[str, Any]:
        return {
            "project": self.project,
            "run_id": self.run_id,
            "created_at": self.created_at,
            "events": [event.to_dict() for event in self.events],
        }

    def serialize(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, indent=2)
