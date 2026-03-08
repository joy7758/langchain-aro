from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ARTIFACT_VERSION = "0.1.0"


@dataclass(slots=True)
class Artifact:
    version: str
    project: str
    run_id: str
    created_at: str
    events: list[dict[str, Any]]
    execution_hash: str
    path: Path | None = field(default=None, compare=False, repr=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "project": self.project,
            "run_id": self.run_id,
            "created_at": self.created_at,
            "events": self.events,
            "execution_hash": self.execution_hash,
        }


@dataclass(slots=True)
class VerificationReport:
    ok: bool
    path: Path
    errors: list[str] = field(default_factory=list)
    expected_hash: str | None = None
    actual_hash: str | None = None
    event_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "path": str(self.path),
            "errors": self.errors,
            "expected_hash": self.expected_hash,
            "actual_hash": self.actual_hash,
            "event_count": self.event_count,
        }
