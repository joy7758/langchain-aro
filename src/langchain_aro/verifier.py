from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .hashing import execution_hash_for_artifact
from .schemas import VerificationReport

REQUIRED_FIELDS = {
    "version",
    "project",
    "run_id",
    "created_at",
    "events",
    "execution_hash",
}

REQUIRED_EVENT_FIELDS = {"type", "timestamp", "payload"}


def _validate_artifact_shape(data: dict[str, Any], report: VerificationReport) -> None:
    missing_fields = sorted(REQUIRED_FIELDS - data.keys())
    if missing_fields:
        report.errors.append(f"Missing required fields: {', '.join(missing_fields)}")

    for field in ("version", "project", "run_id", "created_at", "execution_hash"):
        if field in data and not isinstance(data[field], str):
            report.errors.append(f"Field '{field}' must be a string.")
        elif field in data and not data[field]:
            report.errors.append(f"Field '{field}' must not be empty.")

    events = data.get("events")
    if events is None:
        return
    if not isinstance(events, list):
        report.errors.append("Field 'events' must be a list.")
        return

    report.event_count = len(events)

    for index, event in enumerate(events):
        if not isinstance(event, dict):
            report.errors.append(f"Event {index} must be an object.")
            continue

        missing_event_fields = sorted(REQUIRED_EVENT_FIELDS - event.keys())
        if missing_event_fields:
            report.errors.append(
                f"Event {index} missing fields: {', '.join(missing_event_fields)}"
            )

        if "type" in event and not isinstance(event["type"], str):
            report.errors.append(f"Event {index} field 'type' must be a string.")
        if "timestamp" in event and not isinstance(event["timestamp"], str):
            report.errors.append(f"Event {index} field 'timestamp' must be a string.")
        if "payload" in event and not isinstance(event["payload"], dict):
            report.errors.append(f"Event {index} field 'payload' must be an object.")


def verify_artifact(path: str | Path) -> VerificationReport:
    artifact_path = Path(path)
    report = VerificationReport(ok=False, path=artifact_path)

    if not artifact_path.exists():
        report.errors.append("Artifact file does not exist.")
        return report

    try:
        data = json.loads(artifact_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        report.errors.append(f"Artifact is not valid JSON: {error.msg}")
        return report

    if not isinstance(data, dict):
        report.errors.append("Artifact root must be a JSON object.")
        return report

    _validate_artifact_shape(data, report)

    if {"version", "project", "run_id", "created_at", "events"} <= data.keys():
        report.actual_hash = execution_hash_for_artifact(data)
    if "execution_hash" in data and isinstance(data["execution_hash"], str):
        report.expected_hash = data["execution_hash"]

    if report.expected_hash and report.actual_hash and report.expected_hash != report.actual_hash:
        report.errors.append("Execution hash mismatch.")

    report.ok = not report.errors
    return report
