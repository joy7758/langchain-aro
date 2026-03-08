from langchain_aro.journal import RunJournal


def test_journal_append_and_serialize() -> None:
    journal = RunJournal(project="demo")

    journal.append("run_started", {"serialized": {"name": "MockChain"}})
    journal.append("input", {"value": {"input": "hello"}})

    payload = journal.to_dict()

    assert payload["project"] == "demo"
    assert len(payload["events"]) == 2
    assert payload["events"][0]["type"] == "run_started"
    assert payload["events"][1]["payload"]["value"]["input"] == "hello"

    serialized = journal.serialize()

    assert '"project": "demo"' in serialized
    assert '"type": "input"' in serialized
