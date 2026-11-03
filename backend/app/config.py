"""Application configuration, loaded entirely from the environment.

No secrets or credentials are hardcoded here. Values come from environment
variables (and an optional local `.env` file during development).
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # App
    app_env: str = "development"
    jwt_secret: str = "change-me-to-a-long-random-string"
    jwt_expire_minutes: int = 720
    jwt_algorithm: str = "HS256"
    cors_origins: str = "http://localhost:5173"

    # Storage
    storage_backend: str = "local"  # "local" | "aws"
    sqlite_path: str = "./arivupath.db"
    content_dir: str = "./content"

    # Bedrock / AI
    aws_region: str = "us-east-1"
    bedrock_model_id: str = ""
    bedrock_enabled: bool = False

    # AWS storage (only when storage_backend == "aws")
    ddb_users_table: str = "ArivuPathUsers"
    ddb_progress_table: str = "ArivuPathProgress"
    ddb_assessments_table: str = "ArivuPathAssessments"
    s3_content_bucket: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def content_path(self) -> Path:
        return Path(self.content_dir).resolve()

    @property
    def ai_available(self) -> bool:
        """True only when Bedrock is explicitly enabled AND a model id is set.

        When False, AI endpoints return an explicit 'AI unavailable' error.
        We never fabricate an AI response in place of a real agent call.
        """
        return self.bedrock_enabled and bool(self.bedrock_model_id.strip())


@lru_cache
def get_settings() -> Settings:
    return Settings()
