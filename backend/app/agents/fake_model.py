"""Deterministic fake Strands Model for offline, repeatable tests.

This is ONLY used in automated tests (never in the running app). It implements the
Strands Model interface and returns pre-queued structured outputs or a callable that
builds output from the prompt, so agent logic and contracts can be verified without
calling Amazon Bedrock.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator, Callable
from typing import Any

from pydantic import BaseModel

from strands.models.model import Model


class FakeModel(Model):
    """A Model whose structured_output yields caller-supplied objects.

    Provide either:
      - `responses`: a list of BaseModel instances returned in FIFO order, or
      - `builder`: a callable (output_model, prompt) -> BaseModel instance.
    """

    def __init__(
        self,
        responses: list[BaseModel] | None = None,
        builder: Callable[[type[BaseModel], str], BaseModel] | None = None,
    ) -> None:
        self._responses = list(responses or [])
        self._builder = builder
        self._config: dict[str, Any] = {"model_id": "fake-model"}
        self.calls: list[str] = []  # prompts seen, for assertions

    # --- Model interface ---
    def get_config(self) -> Any:
        return self._config

    def update_config(self, **model_config: Any) -> None:
        self._config.update(model_config)

    async def stream(self, *args: Any, **kwargs: Any) -> AsyncGenerator[dict[str, Any], None]:
        # Agents here use structured_output exclusively; a minimal stream suffices.
        yield {"messageStart": {"role": "assistant"}}
        yield {"messageStop": {"stopReason": "end_turn"}}

    async def structured_output(
        self,
        output_model: type[BaseModel],
        prompt: Any,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> AsyncGenerator[dict[str, Any], None]:
        self.calls.append(_prompt_text(prompt))
        obj = self._next(output_model, _prompt_text(prompt))
        if not isinstance(obj, output_model):
            # Coerce via dict if the builder returned a compatible object.
            obj = output_model.model_validate(obj.model_dump())
        yield {"output": obj}

    # --- helpers ---
    def _next(self, output_model: type[BaseModel], prompt: str) -> BaseModel:
        if self._responses:
            return self._responses.pop(0)
        if self._builder is not None:
            return self._builder(output_model, prompt)
        raise AssertionError("FakeModel has no queued responses and no builder.")


def _prompt_text(prompt: Any) -> str:
    """Flatten a Strands message list (or string) into plain text for assertions."""
    if isinstance(prompt, str):
        return prompt
    parts: list[str] = []
    try:
        for msg in prompt:
            for block in msg.get("content", []):
                if "text" in block:
                    parts.append(block["text"])
    except (AttributeError, TypeError):
        return str(prompt)
    return "\n".join(parts)
