import json

from langchain_aro import ARORecorder


def test_callback_handler_exports_artifact(tmp_path) -> None:
    recorder = ARORecorder(project="demo", output_dir=tmp_path / "artifacts")
    handler = recorder.callback_handler()

    assert hasattr(handler, "on_chain_start")
    assert hasattr(handler, "on_chain_end")
    assert hasattr(handler, "on_chain_error")

    handler.on_chain_start({"name": "MockChain"}, {"input": "hello"})
    handler.on_chain_end({"output": "HELLO"})

    artifact = recorder.finalize()

    assert artifact.path.exists()

    payload = json.loads(artifact.path.read_text(encoding="utf-8"))
    event_types = [event["type"] for event in payload["events"]]

    assert event_types == ["run_started", "input", "output", "run_finished"]
