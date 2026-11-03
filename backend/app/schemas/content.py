"""Curriculum content schemas (approved lesson material)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Concept(BaseModel):
    concept_id: str
    title_en: str
    title_ta: str
    difficulty: int = Field(ge=1, le=5)
    passages: list[str] = Field(default_factory=list)
    passages_ta: list[str] = Field(default_factory=list)


class Chapter(BaseModel):
    chapter_id: str
    class_level: int
    subject: str
    chapter_title_en: str
    chapter_title_ta: str
    summary_en: str
    summary_ta: str
    content_label: str
    concepts: list[Concept] = Field(default_factory=list)


class ChapterSummary(BaseModel):
    """Lightweight listing entry (no full passages)."""

    chapter_id: str
    class_level: int
    subject: str
    chapter_title_en: str
    chapter_title_ta: str


class ChapterListResponse(BaseModel):
    chapters: list[ChapterSummary]


class ChapterResponse(BaseModel):
    chapter: Chapter
