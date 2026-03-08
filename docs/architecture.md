# Architecture

## Design Goals

`langchain-aro` is designed as a small execution-integrity layer for LangChain-style runs.

The current MVP goals are:

* capture a minimal set of runtime events
* produce a portable artifact on the local filesystem
* compute a stable execution hash
* verify the artifact later without the original runtime

## Why Middleware-First

The middleware-first approach keeps the LangChain-facing surface narrow. The recorder only needs to observe a minimal callback stream and write a journal. This keeps the integration small, testable, and easier to evolve before broader protocol coverage is added.

Starting from middleware also avoids prematurely building a tracing backend, database layer, or web interface. The first problem to solve is artifact integrity, not platform infrastructure.

## Separation of Concerns

### LangChain Event Capture

The callback handler captures a small event set:

* `run_started`
* `input`
* `output`
* `run_finished`
* `run_error`

It does not attempt full tracing coverage in the MVP.

### ARO Artifact Generation

The recorder owns the run journal, turns events into a stable in-memory structure, computes the execution hash, and exports the result to `artifacts/run.json`.

### ARO Verification

Verification is separate from capture. The verifier reads an artifact from disk, validates the required fields and event structure, recomputes the execution hash, and reports whether the artifact is intact.

## Data Flow

`chain run -> callbacks -> journal -> artifact -> verify`

1. A chain invocation emits callback events.
2. The callback handler forwards those events to `ARORecorder`.
3. The recorder appends normalized events to a `RunJournal`.
4. `finalize()` builds and exports an artifact with a stable hash.
5. `verify_artifact(path)` validates and verifies the exported artifact.

## Future Extension Points

* richer callback coverage for tools, models, and agents
* additional artifact formats such as JSONL
* signatures and stronger provenance fields
* adapters for other frameworks beyond LangChain
