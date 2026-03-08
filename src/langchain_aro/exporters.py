from __future__ import annotations

import json
from pathlib import Path

from .schemas import Artifact


def export_artifact(artifact: Artifact, output_dir: str | Path) -> Path:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    artifact_path = output_path / "run.json"
    artifact_path.write_text(
        json.dumps(artifact.to_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return artifact_path


def export_jsonl(artifact: Artifact, output_dir: str | Path) -> Path:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    artifact_path = output_path / "run.jsonl"
    lines = [json.dumps(event, sort_keys=True) for event in artifact.events]
    artifact_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return artifact_path
