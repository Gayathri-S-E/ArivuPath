"""Storage abstraction: repository (users/progress/assessments) + content store.

Two implementations exist behind these interfaces: a local SQLite+JSON one for
development (no AWS needed) and an AWS one (DynamoDB + S3). The factory below
selects based on settings.storage_backend.
"""

from __future__ import annotations

from app.config import Settings

from .base import ContentStore, Repository
from .local import LocalContentStore, LocalRepository


def build_repository(settings: Settings) -> Repository:
    if settings.storage_backend == "aws":
        from .aws import AwsRepository  # imported lazily so boto3 DDB is optional

        return AwsRepository(settings)
    return LocalRepository(settings.sqlite_path)


def build_content_store(settings: Settings) -> ContentStore:
    if settings.storage_backend == "aws":
        from .aws import AwsContentStore

        return AwsContentStore(settings)
    return LocalContentStore(settings.content_path)


__all__ = [
    "ContentStore",
    "Repository",
    "LocalRepository",
    "LocalContentStore",
    "build_repository",
    "build_content_store",
]
