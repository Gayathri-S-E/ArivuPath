"""Authentication and user schemas."""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class Role(str, Enum):
    student = "student"
    teacher = "teacher"


class Medium(str, Enum):
    tamil = "ta"
    english = "en"


class RegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    class_level: int = Field(ge=6, le=10, description="School class (6-10)")
    medium: Medium = Medium.tamil
    subject: str = Field(default="science", max_length=40)
    # Students self-register only as 'student'. Teacher accounts are provisioned.
    preferences: dict[str, str] = Field(default_factory=dict)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class PublicUser(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: Role
    class_level: int
    medium: Medium
    subject: str
    preferences: dict[str, str] = Field(default_factory=dict)


class TokenResponse(BaseModel):
    token: str
    token_type: Literal["bearer"] = "bearer"
    user: PublicUser


class TokenPayload(BaseModel):
    sub: str          # user id
    role: Role
    exp: int
