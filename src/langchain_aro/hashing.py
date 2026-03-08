from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def canonical_json_bytes(value: Any) -> bytes:
    return canonical_json(value).encode("utf-8")


def sha256_digest(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def artifact_hash_payload(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "version": artifact["version"],
        "project": artifact["project"],
        "run_id": artifact["run_id"],
        "created_at": artifact["created_at"],
        "events": artifact["events"],
    }


def execution_hash_for_artifact(artifact: dict[str, Any]) -> str:
    return sha256_digest(artifact_hash_payload(artifact))
