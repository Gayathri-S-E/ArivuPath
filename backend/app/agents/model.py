"""Bedrock model construction for the Strands agents.

The model is built from environment-driven settings only. No credentials are
hardcoded; boto3 resolves them from the environment or an IAM role. When Bedrock is
not enabled/configured, build_model() raises AIUnavailableError so callers return an
explicit error instead of a fabricated AI response.
"""

from __future__ import annotations

from app.config import Settings


class AIUnavailableError(RuntimeError):
    """Raised when a live AI call is requested but Bedrock is not configured."""


def build_model(settings: Settings):
    """Construct a Strands BedrockModel from settings.

    Raises AIUnavailableError when AI is not available so we never silently fall
    back to a fake/canned answer in the running application.
    """
    if not settings.ai_available:
        raise AIUnavailableError(
            "Amazon Bedrock is not configured. Set BEDROCK_ENABLED=1, BEDROCK_MODEL_ID "
            "and valid AWS credentials to enable live AI features."
        )

    import boto3
    from strands.models import BedrockModel

    session = boto3.Session(region_name=settings.aws_region)
    return BedrockModel(
        model_id=settings.bedrock_model_id,
        boto_session=session,
        temperature=0.3,
    )
