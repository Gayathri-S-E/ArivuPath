"""Agent runtime helpers.

We standardise on Strands' structured-output protocol: every specialist agent asks
its model for a typed Pydantic object. The `run_structured` helper drives a Strands
Model's async `structured_output` generator to completion and returns the final
typed object. This works identically for the real BedrockModel and for the
deterministic FakeModel used in tests.
"""

from __future__ import annotations

import asyncio
from typing import TypeVar

from pydantic import BaseModel

from strands.models.model import Model
from strands.types.content import Message

T = TypeVar("T", bound=BaseModel)


async def _drive(model: Model, output_model: type[T], prompt: str, system_prompt: str) -> T:
    messages: list[Message] = [{"role": "user", "content": [{"text": prompt}]}]
    result: T | None = None
    async for event in model.structured_output(output_model, messages, system_prompt=system_prompt):
        if isinstance(event, dict) and "output" in event:
            result = event["output"]
    if result is None:
        raise RuntimeError("Model produced no structured output.")
    return result


def run_structured(model: Model, output_model: type[T], prompt: str, system_prompt: str = "") -> T:
    """Synchronously run a structured-output request against a Strands model."""
    return asyncio.run(_drive(model, output_model, prompt, system_prompt))
