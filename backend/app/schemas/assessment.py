"""Assessment contracts (Agent 3)."""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class QuestionType(str, Enum):
    mcq = "mcq"
    true_false = "true_false"
    fill_blank = "fill_blank"
    short_answer = "short_answer"
    concept = "concept"


class Question(BaseModel):
    id: str
    type: QuestionType
    concept_id: str
    prompt: str
    options: list[str] = Field(default_factory=list)  # for mcq / true_false
    answer_key: str = Field(description="Canonical correct answer (not sent to UI during attempt).")
    difficulty: int = Field(ge=1, le=5)
    hint: str = ""


class Assessment(BaseModel):
    assessment_id: str
    chapter_id: str
    questions: list[Question]


class GenerateRequest(BaseModel):
    chapter_id: str
    concept_ids: list[str] = Field(default_factory=list)
    count: int = Field(default=5, ge=1, le=15)
    language: Literal["ta", "en"] = "ta"
    # Target difficulty, used to adapt generation to the student's level.
    target_difficulty: int = Field(default=2, ge=1, le=5)


class SubmittedAnswer(BaseModel):
    question_id: str
    answer: str


class AnswerEvaluation(BaseModel):
    question_id: str
    concept_id: str
    correct: bool
    rationale: str = Field(description="Why the answer is right/wrong, in the student's language.")
    concept_understood: bool = Field(
        description="Whether the response reflects conceptual understanding vs memorization/guess."
    )
    suggested_hint: str = ""


class EvaluateRequest(BaseModel):
    assessment_id: str
    chapter_id: str
    language: Literal["ta", "en"] = "ta"
    answers: list[SubmittedAnswer]
    # The questions being answered (carried from generate so eval is stateless).
    questions: list[Question]


class EvaluateResponse(BaseModel):
    evaluations: list[AnswerEvaluation]
    score: int
    total: int
    # Difficulty recommendation for the next round (adaptive).
    next_difficulty: int = Field(ge=1, le=5)
