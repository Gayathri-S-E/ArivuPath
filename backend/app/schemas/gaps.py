"""Learning gap detection contracts (Agent 4)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ConceptMastery(BaseModel):
    concept_id: str
    title: str
    attempts: int
    correct: int
    # 0.0-1.0 proportion correct; derived from real records only.
    mastery: float = Field(ge=0.0, le=1.0)
    status: str = Field(description="understood | needs_revision | not_started")


class RepeatedMistake(BaseModel):
    concept_id: str
    description: str
    occurrences: int


class GapReport(BaseModel):
    """Output of the Learning Gap Detection Agent."""

    user_id: str
    chapter_id: str
    understood: list[ConceptMastery] = Field(default_factory=list)
    needs_revision: list[ConceptMastery] = Field(default_factory=list)
    repeated_mistakes: list[RepeatedMistake] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    memorization_warning: str = Field(
        default="",
        description="Non-empty when answers look memorized rather than understood.",
    )
