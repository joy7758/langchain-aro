from __future__ import annotations

from pathlib import Path
from typing import Any

from .exporters import export_artifact
from .hashing import execution_hash_for_artifact
from .journal import RunJournal, make_json_safe
from .schemas import ARTIFACT_VERSION, Artifact

try:
    from langchain_core.callbacks import BaseCallbackHandler as _BaseCallbackHandler
except ImportError:
    class _BaseCallbackHandler:
        """Fallback when langchain-core is not installed."""


class LangChainAROCallbackHandler(_BaseCallbackHandler):
    def __init__(self, recorder: "ARORecorder") -> None:
        super().__init__()
        self._recorder = recorder

    def on_chain_start(
        self,
        serialized: dict[str, Any] | None,
        inputs: dict[str, Any] | None,
        *,
        run_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        self._recorder.record_run_started(
            serialized=serialized,
            inputs=inputs,
            callback_run_id=run_id,
            metadata=kwargs or None,
        )

    def on_chain_end(
        self,
        outputs: dict[str, Any] | Any,
        *,
        run_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        self._recorder.record_run_finished(
            outputs=outputs,
            callback_run_id=run_id,
            metadata=kwargs or None,
        )

    def on_chain_error(
        self,
        error: BaseException,
        *,
        run_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        self._recorder.record_run_error(
            error=error,
            callback_run_id=run_id,
            metadata=kwargs or None,
        )

    def on_run_start(self, inputs: dict[str, Any] | None, **kwargs: Any) -> None:
        self._recorder.record_run_started(inputs=inputs, metadata=kwargs or None)

    def on_run_end(self, outputs: dict[str, Any] | Any, **kwargs: Any) -> None:
        self._recorder.record_run_finished(outputs=outputs, metadata=kwargs or None)

    def on_run_error(self, error: BaseException, **kwargs: Any) -> None:
        self._recorder.record_run_error(error=error, metadata=kwargs or None)


class ARORecorder:
    def __init__(self, project: str, output_dir: str | Path = "artifacts") -> None:
        self.project = project
        self.output_dir = Path(output_dir)
        self.journal = RunJournal(project=project)
        self._handler: LangChainAROCallbackHandler | None = None

    def callback_handler(self) -> LangChainAROCallbackHandler:
        if self._handler is None:
            self._handler = LangChainAROCallbackHandler(self)
        return self._handler

    def record_run_started(
        self,
        *,
        serialized: dict[str, Any] | None = None,
        inputs: dict[str, Any] | None = None,
        callback_run_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        payload: dict[str, Any] = {}
        if serialized is not None:
            payload["serialized"] = make_json_safe(serialized)
        if callback_run_id is not None:
            payload["callback_run_id"] = str(callback_run_id)
        if metadata:
            payload["metadata"] = make_json_safe(metadata)

        self.journal.append("run_started", payload)

        if inputs is not None:
            self.journal.append("input", {"value": make_json_safe(inputs)})

    def record_run_finished(
        self,
        *,
        outputs: dict[str, Any] | Any = None,
        callback_run_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        if outputs is not None:
            self.journal.append("output", {"value": make_json_safe(outputs)})

        payload: dict[str, Any] = {}
        if callback_run_id is not None:
            payload["callback_run_id"] = str(callback_run_id)
        if metadata:
            payload["metadata"] = make_json_safe(metadata)

        self.journal.append("run_finished", payload)

    def record_run_error(
        self,
        *,
        error: BaseException,
        callback_run_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        payload: dict[str, Any] = {"error": make_json_safe(error)}
        if callback_run_id is not None:
            payload["callback_run_id"] = str(callback_run_id)
        if metadata:
            payload["metadata"] = make_json_safe(metadata)

        self.journal.append("run_error", payload)

    def finalize(self) -> Artifact:
        artifact_payload = {
            "version": ARTIFACT_VERSION,
            "project": self.project,
            "run_id": self.journal.run_id,
            "created_at": self.journal.created_at,
            "events": [event.to_dict() for event in self.journal.events],
        }

        artifact = Artifact(
            **artifact_payload,
            execution_hash=execution_hash_for_artifact(artifact_payload),
        )
        artifact.path = export_artifact(artifact, self.output_dir)
        return artifact
