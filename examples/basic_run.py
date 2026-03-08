from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from langchain_aro import ARORecorder


class MockChain:
    """Small stand-in for a LangChain-style invoke interface."""

    def invoke(self, payload: dict[str, Any], config: dict[str, Any] | None = None) -> dict[str, Any]:
        callbacks = (config or {}).get("callbacks", [])
        serialized = {"name": "MockChain"}

        try:
            for callback in callbacks:
                if hasattr(callback, "on_chain_start"):
                    callback.on_chain_start(serialized, payload)

            result = {"output": str(payload.get("input", "")).upper()}

            for callback in callbacks:
                if hasattr(callback, "on_chain_end"):
                    callback.on_chain_end(result)

            return result
        except Exception as error:
            for callback in callbacks:
                if hasattr(callback, "on_chain_error"):
                    callback.on_chain_error(error)
            raise


def main() -> None:
    recorder = ARORecorder(project="demo", output_dir=ROOT / "artifacts")
    chain = MockChain()

    result = chain.invoke(
        {"input": "hello"},
        config={"callbacks": [recorder.callback_handler()]},
    )

    artifact = recorder.finalize()

    print(f"Result: {result}")
    print(f"Artifact written to: {artifact.path}")


if __name__ == "__main__":
    main()
