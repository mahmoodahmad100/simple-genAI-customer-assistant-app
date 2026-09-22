from typing import Any

from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    user_id: str = Field(min_length=1)
    message: str = Field(min_length=1)

    @field_validator("user_id", "message")
    @classmethod
    def must_not_be_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("must not be blank")
        return stripped


class ChatResponse(BaseModel):
    response: str
    sources: list[str]
    tool_calls: list[dict[str, Any]]


class HealthResponse(BaseModel):
    status: str
