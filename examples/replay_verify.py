from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from langchain_aro import verify_artifact


def main() -> None:
    artifact_path = ROOT / "artifacts" / "run.json"
    report = verify_artifact(artifact_path)

    print(f"Artifact: {report.path}")
    print(f"Verified: {report.ok}")

    if report.expected_hash:
        print(f"Stored hash: {report.expected_hash}")
    if report.actual_hash:
        print(f"Computed hash: {report.actual_hash}")
    if report.errors:
        print("Errors:")
        for error in report.errors:
            print(f"  - {error}")


if __name__ == "__main__":
    main()
