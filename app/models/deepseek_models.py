from typing import Any, Literal

from pydantic import BaseModel, Field


class DeepSeekChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1)


class DeepSeekChatRequest(BaseModel):
    messages: list[DeepSeekChatMessage] = Field(min_length=1)
    model: str | None = None
    max_tokens: int | None = Field(default=None, gt=0)
    temperature: float | None = Field(default=None, ge=0, le=2)
    response_format: dict[str, Any] | None = None
    thinking_enabled: bool | None = None
    reasoning_effort: Literal["high", "max"] | None = None


class DeepSeekChatResponse(BaseModel):
    id: str | None = None
    model: str | None = None
    role: str = "assistant"
    content: str
    reasoning_content: str | None = None
    finish_reason: str | None = None
    usage: dict[str, Any] | None = None
