import json

from langchain_aro import ARORecorder, verify_artifact


def test_verify_artifact_passes_for_valid_artifact(tmp_path) -> None:
    recorder = ARORecorder(project="demo", output_dir=tmp_path / "artifacts")
    handler = recorder.callback_handler()

    handler.on_chain_start({"name": "MockChain"}, {"input": "hello"})
    handler.on_chain_end({"output": "HELLO"})

    artifact = recorder.finalize()
    report = verify_artifact(artifact.path)

    assert report.ok is True
    assert report.errors == []
    assert report.event_count == 4


def test_verify_artifact_fails_for_tampered_artifact(tmp_path) -> None:
    recorder = ARORecorder(project="demo", output_dir=tmp_path / "artifacts")
    handler = recorder.callback_handler()

    handler.on_chain_start({"name": "MockChain"}, {"input": "hello"})
    handler.on_chain_end({"output": "HELLO"})

    artifact = recorder.finalize()

    payload = json.loads(artifact.path.read_text(encoding="utf-8"))
    payload["project"] = "tampered"
    artifact.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    report = verify_artifact(artifact.path)

    assert report.ok is False
    assert "Execution hash mismatch." in report.errors
