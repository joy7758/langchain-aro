from langchain_aro.hashing import execution_hash_for_artifact


def test_execution_hash_is_stable_for_identical_payloads() -> None:
    artifact = {
        "version": "0.1.0",
        "project": "demo",
        "run_id": "run-1",
        "created_at": "2026-03-08T00:00:00Z",
        "events": [
            {
                "type": "run_started",
                "timestamp": "2026-03-08T00:00:00Z",
                "payload": {"value": {"input": "hello"}},
            }
        ],
    }

    assert execution_hash_for_artifact(artifact) == execution_hash_for_artifact(dict(artifact))


def test_execution_hash_ignores_field_order() -> None:
    first = {
        "version": "0.1.0",
        "project": "demo",
        "run_id": "run-1",
        "created_at": "2026-03-08T00:00:00Z",
        "events": [
            {
                "type": "run_started",
                "timestamp": "2026-03-08T00:00:00Z",
                "payload": {"a": 1, "b": 2},
            }
        ],
    }
    second = {
        "events": [
            {
                "payload": {"b": 2, "a": 1},
                "timestamp": "2026-03-08T00:00:00Z",
                "type": "run_started",
            }
        ],
        "created_at": "2026-03-08T00:00:00Z",
        "run_id": "run-1",
        "project": "demo",
        "version": "0.1.0",
    }

    assert execution_hash_for_artifact(first) == execution_hash_for_artifact(second)
