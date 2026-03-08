import pytest

from langchain_aro import ARORecorder, verify_artifact

langchain_core = pytest.importorskip("langchain_core")
from langchain_core.runnables import RunnableLambda


def test_langchain_core_runnable_smoke(tmp_path) -> None:
    recorder = ARORecorder(project="smoke", output_dir=tmp_path / "artifacts")
    runnable = RunnableLambda(lambda value: {"output": str(value).upper()})

    result = runnable.invoke(
        "hello",
        config={"callbacks": [recorder.callback_handler()]},
    )
    artifact = recorder.finalize()
    report = verify_artifact(artifact.path)

    assert result == {"output": "HELLO"}
    assert report.ok is True
    assert [event["type"] for event in artifact.events] == [
        "run_started",
        "input",
        "output",
        "run_finished",
    ]
