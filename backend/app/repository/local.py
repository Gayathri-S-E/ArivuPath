"""Local storage: SQLite for users/progress, JSON files for content."""

from __future__ import annotations

import json
import sqlite3
import threading
from pathlib import Path
from typing import Any

from app.repository.base import ContentStore, Repository, UserRecord
from app.schemas.content import Chapter, ChapterSummary


class LocalRepository(Repository):
    def __init__(self, sqlite_path: str) -> None:
        self._path = sqlite_path
        self._lock = threading.Lock()
        # check_same_thread=False + a lock keeps it safe under FastAPI's threadpool.
        self._conn = sqlite3.connect(sqlite_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._create_schema()

    def _create_schema(self) -> None:
        with self._lock:
            self._conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL CHECK (role IN ('student','teacher')),
                    class_level INTEGER NOT NULL,
                    medium TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    preferences TEXT NOT NULL DEFAULT '{}',
                    teacher_id TEXT
                );
                CREATE TABLE IF NOT EXISTS answers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL REFERENCES users(id),
                    chapter_id TEXT NOT NULL,
                    concept_id TEXT NOT NULL,
                    question_id TEXT NOT NULL,
                    correct INTEGER NOT NULL,
                    concept_understood INTEGER NOT NULL,
                    ts REAL NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_answers_user ON answers(user_id);
                """
            )
            self._conn.commit()

    # --- users ---
    def create_user(self, user: UserRecord) -> None:
        with self._lock:
            self._conn.execute(
                """INSERT INTO users
                   (id,name,email,password_hash,role,class_level,medium,subject,preferences,teacher_id)
                   VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (
                    user.id,
                    user.name,
                    user.email,
                    user.password_hash,
                    user.role,
                    user.class_level,
                    user.medium,
                    user.subject,
                    json.dumps(user.preferences),
                    user.teacher_id,
                ),
            )
            self._conn.commit()

    def _row_to_user(self, row: sqlite3.Row) -> UserRecord:
        return UserRecord(
            id=row["id"],
            name=row["name"],
            email=row["email"],
            password_hash=row["password_hash"],
            role=row["role"],
            class_level=row["class_level"],
            medium=row["medium"],
            subject=row["subject"],
            preferences=json.loads(row["preferences"] or "{}"),
            teacher_id=row["teacher_id"],
        )

    def get_user_by_email(self, email: str) -> UserRecord | None:
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM users WHERE email = ?", (email.lower(),)
            ).fetchone()
        return self._row_to_user(row) if row else None

    def get_user(self, user_id: str) -> UserRecord | None:
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM users WHERE id = ?", (user_id,)
            ).fetchone()
        return self._row_to_user(row) if row else None

    def list_students_for_teacher(self, teacher_id: str) -> list[UserRecord]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT * FROM users WHERE role = 'student' AND (teacher_id = ? OR teacher_id IS NULL)",
                (teacher_id,),
            ).fetchall()
        return [self._row_to_user(r) for r in rows]

    # --- answers ---
    def record_answer(
        self,
        user_id: str,
        chapter_id: str,
        concept_id: str,
        question_id: str,
        correct: bool,
        concept_understood: bool,
        ts: float,
    ) -> None:
        with self._lock:
            self._conn.execute(
                """INSERT INTO answers
                   (user_id,chapter_id,concept_id,question_id,correct,concept_understood,ts)
                   VALUES (?,?,?,?,?,?,?)""",
                (user_id, chapter_id, concept_id, question_id, int(correct), int(concept_understood), ts),
            )
            self._conn.commit()

    def _rows_to_answers(self, rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
        return [
            {
                "user_id": r["user_id"],
                "chapter_id": r["chapter_id"],
                "concept_id": r["concept_id"],
                "question_id": r["question_id"],
                "correct": bool(r["correct"]),
                "concept_understood": bool(r["concept_understood"]),
                "ts": r["ts"],
            }
            for r in rows
        ]

    def get_answers(self, user_id: str, chapter_id: str | None = None) -> list[dict[str, Any]]:
        with self._lock:
            if chapter_id:
                rows = self._conn.execute(
                    "SELECT * FROM answers WHERE user_id = ? AND chapter_id = ? ORDER BY ts",
                    (user_id, chapter_id),
                ).fetchall()
            else:
                rows = self._conn.execute(
                    "SELECT * FROM answers WHERE user_id = ? ORDER BY ts", (user_id,)
                ).fetchall()
        return self._rows_to_answers(rows)

    def get_answers_for_users(self, user_ids: list[str]) -> list[dict[str, Any]]:
        if not user_ids:
            return []
        placeholders = ",".join("?" for _ in user_ids)
        with self._lock:
            rows = self._conn.execute(
                f"SELECT * FROM answers WHERE user_id IN ({placeholders}) ORDER BY ts",
                tuple(user_ids),
            ).fetchall()
        return self._rows_to_answers(rows)


class LocalContentStore(ContentStore):
    """Reads approved content from JSON files under content_dir."""

    def __init__(self, content_dir: Path) -> None:
        self._dir = Path(content_dir)

    def _iter_lesson_files(self) -> list[Path]:
        if not self._dir.exists():
            return []
        return sorted(self._dir.rglob("lesson.json"))

    def list_chapters(self) -> list[ChapterSummary]:
        out: list[ChapterSummary] = []
        for f in self._iter_lesson_files():
            data = json.loads(f.read_text(encoding="utf-8"))
            out.append(
                ChapterSummary(
                    chapter_id=data["chapter_id"],
                    class_level=data["class_level"],
                    subject=data["subject"],
                    chapter_title_en=data["chapter_title_en"],
                    chapter_title_ta=data["chapter_title_ta"],
                )
            )
        return out

    def get_chapter(self, chapter_id: str) -> Chapter | None:
        for f in self._iter_lesson_files():
            data = json.loads(f.read_text(encoding="utf-8"))
            if data.get("chapter_id") == chapter_id:
                return Chapter.model_validate(data)
        return None
