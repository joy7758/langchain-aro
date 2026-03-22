<!-- language-switch:start -->
<p>
  <a href="./README.md">
    <img src="https://img.shields.io/badge/English-Current-1f883d?style=for-the-badge" alt="English">
  </a>
  <a href="./README.zh-CN.md">
    <img src="https://img.shields.io/badge/Chinese-Switch-0f172a?style=for-the-badge" alt="Chinese">
  </a>
</p>
<!-- language-switch:end -->

# langchain-aro

LangChain middleware for execution integrity, audit trails, and verifiable agent runs.

## What It Is

`langchain-aro` is an early MVP for capturing a minimal callback stream from a LangChain-style run and turning it into a portable artifact that can be exported, hashed, and verified later.

It does not try to replace tracing systems or observability platforms. It focuses on execution integrity: producing portable run artifacts that can be exported, hashed, and verified.

The current MVP is validated against a real `langchain-core` callback flow.
Tested on Python 3.11 and 3.12 via GitHub Actions.

## Why Execution Integrity Matters

Agent traces are useful while a system is running, but traces alone do not give you a portable integrity artifact. If a run needs to be reviewed, replayed, or compared outside the original runtime, you need a stable representation of what happened and a way to verify that it has not been altered.

This project addresses that smaller and more specific problem:

* capture a minimal run journal
* serialize it into a portable artifact
* compute a stable execution hash
* verify the artifact later

## How It Fits the Stack

`POP -> AOP -> ARO -> Token Governor`

`langchain-aro` is the LangChain-facing entry point for the ARO layer, where execution artifacts are produced and verified.

## Architecture

```text
LangChain Runtime
       |
       v
ARO Middleware
       |
       v
Run Journal
       |
       v
Execution Hash
       |
       v
Verifiable Artifact
```

`langchain-aro` is complementary to observability systems. It does not replace tracing or runtime monitoring. It provides execution integrity artifacts.

## MVP Features

* run journal
* execution hash
* artifact export
* replay verification

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
python examples/basic_run.py
python examples/replay_verify.py
pytest
```

The examples use a small mock chain so the repository remains runnable even without a full LangChain installation.

## Minimal API Example

```python
from langchain_aro import ARORecorder, verify_artifact

recorder = ARORecorder(project="demo", output_dir="artifacts")

result = chain.invoke(
    {"input": "hello"},
    config={"callbacks": [recorder.callback_handler()]},
)

artifact = recorder.finalize()
report = verify_artifact(artifact.path)
```

## Artifact Format

Artifacts are exported to `artifacts/run.json` by default. The current MVP schema is intentionally small:

```json
{
  "version": "0.1.0",
  "project": "demo",
  "run_id": "8b7e0d6c-6fd8-4e2d-bf20-9ee73870c5f7",
  "created_at": "2026-03-08T00:00:00Z",
  "events": [
    {
      "type": "run_started",
      "timestamp": "2026-03-08T00:00:00Z",
      "payload": {
        "serialized": {
          "name": "MockChain"
        }
      }
    }
  ],
  "execution_hash": "..."
}
```

## Verification Flow

1. Capture a minimal callback sequence into a journal.
2. Export the journal as a `run.json` artifact.
3. Recompute the execution hash from canonical JSON.
4. Compare the stored hash and report whether the artifact is still valid.

## Roadmap

* broaden callback coverage without losing the minimal MVP shape
* add richer artifact export options such as JSONL
* support signatures and stronger provenance metadata
* add more framework adapters after the LangChain middleware path is stable
