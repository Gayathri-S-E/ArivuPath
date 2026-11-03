"""Abstract storage interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.schemas.content import Chapter, ChapterSummary


class UserRecord:
    """Internal user row (includes password hash — never serialized to clients)."""

    def __init__(
        self,
        id: str,
        name: str,
        email: str,
        password_hash: str,
        role: str,
        class_level: int,
        medium: str,
        subject: str,
        preferences: dict[str, str],
        teacher_id: str | None = None,
    ) -> None:
        self.id = id
        self.name = name
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.class_level = class_level
        self.medium = medium
        self.subject = subject
        self.preferences = preferences
        self.teacher_id = teacher_id


class Repository(ABC):
    """Users, learning progress, and assessment records."""

    # --- users ---
    @abstractmethod
    def create_user(self, user: UserRecord) -> None: ...

    @abstractmethod
    def get_user_by_email(self, email: str) -> UserRecord | None: ...

    @abstractmethod
    def get_user(self, user_id: str) -> UserRecord | None: ...

    @abstractmethod
    def list_students_for_teacher(self, teacher_id: str) -> list[UserRecord]: ...

    # --- assessment records (one row per answered question) ---
    @abstractmethod
    def record_answer(
        self,
        user_id: str,
        chapter_id: str,
        concept_id: str,
        question_id: str,
        correct: bool,
        concept_understood: bool,
        ts: float,
    ) -> None: ...

    @abstractmethod
    def get_answers(self, user_id: str, chapter_id: str | None = None) -> list[dict[str, Any]]: ...

    @abstractmethod
    def get_answers_for_users(self, user_ids: list[str]) -> list[dict[str, Any]]: ...


class ContentStore(ABC):
    """Approved curriculum content access."""

    @abstractmethod
    def list_chapters(self) -> list[ChapterSummary]: ...

    @abstractmethod
    def get_chapter(self, chapter_id: str) -> Chapter | None: ...
