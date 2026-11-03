"""Personalized learning path contracts (Agent 5)."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class ActivityType(str, Enum):
    understand = "understand"
    tamil_explanation = "tamil_explanation"
    example = "example"
    practice = "practice"
    review = "review"
    assessment = "assessment"


class PathStep(BaseModel):
    order: int
    activity: ActivityType
    concept_id: str
    title: str
    detail: str
    completed: bool = False


class LearningPath(BaseModel):
    """Output of the Personalized Learning Path Agent."""

    user_id: str
    chapter_id: str
    steps: list[PathStep] = Field(default_factory=list)
    rationale: str
    # Cross-session improvement signal (e.g. mastery delta since last session).
    improvement_note: str = ""
