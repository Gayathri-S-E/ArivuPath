"""Lesson understanding + teaching contracts (Agents 1 and 2)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class RetrievedPassage(BaseModel):
    concept_id: str
    title: str
    text: str


class LessonContext(BaseModel):
    """Output of the Lesson Understanding Agent — grounded, retrieved material."""

    chapter_id: str
    question: str
    matched_concepts: list[str] = Field(default_factory=list)
    passages: list[RetrievedPassage] = Field(default_factory=list)
    source_label: str
    found: bool = Field(description="False when no approved content matched.")


class ExplanationStep(BaseModel):
    order: int
    text: str


class Explanation(BaseModel):
    """Output of the Tamil Teaching Agent. Always marked ai_generated."""

    language: Literal["ta", "en"]
    concept: str
    steps: list[ExplanationStep]
    examples: list[str] = Field(default_factory=list)
    grounded_concept_ids: list[str] = Field(default_factory=list)
    ai_generated: Literal[True] = True


class AskRequest(BaseModel):
    chapter_id: str
    question: str = Field(min_length=1, max_length=1000)
    language: Literal["ta", "en"] = "ta"
    want_example: bool = True


class AskResponse(BaseModel):
    lesson_context: LessonContext
    explanation: Explanation | None = None
    # Human-readable note surfaced to the UI (e.g. grounding / AI-label notice).
    notice: str
