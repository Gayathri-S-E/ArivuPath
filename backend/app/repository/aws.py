"""AWS storage implementation (DynamoDB + S3).

NOTE: This is a documented placeholder for Phase 9. It is NOT yet implemented or
tested. Per project rule C7 we do not claim a working AWS integration until it has
been verified against real AWS resources. Selecting STORAGE_BACKEND=aws will raise
until this is completed, so the app never silently pretends AWS is wired up.
"""

from __future__ import annotations

from typing import Any

from app.config import Settings
from app.repository.base import ContentStore, Repository, UserRecord
from app.schemas.content import Chapter, ChapterSummary

_NOT_READY = (
    "AWS storage backend is not implemented/tested yet (Phase 9). "
    "Use STORAGE_BACKEND=local for now."
)


class AwsRepository(Repository):
    def __init__(self, settings: Settings) -> None:
        raise NotImplementedError(_NOT_READY)

    def create_user(self, user: UserRecord) -> None: ...
    def get_user_by_email(self, email: str) -> UserRecord | None: ...
    def get_user(self, user_id: str) -> UserRecord | None: ...
    def list_students_for_teacher(self, teacher_id: str) -> list[UserRecord]: ...
    def record_answer(self, *a: Any, **k: Any) -> None: ...
    def get_answers(self, user_id: str, chapter_id: str | None = None) -> list[dict[str, Any]]: ...
    def get_answers_for_users(self, user_ids: list[str]) -> list[dict[str, Any]]: ...


class AwsContentStore(ContentStore):
    def __init__(self, settings: Settings) -> None:
        raise NotImplementedError(_NOT_READY)

    def list_chapters(self) -> list[ChapterSummary]: ...
    def get_chapter(self, chapter_id: str) -> Chapter | None: ...
