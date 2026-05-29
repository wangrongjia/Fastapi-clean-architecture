from typing import Any, Literal

from pydantic import BaseModel, Field


class OpenRouterChatMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str = Field(min_length=1)


class OpenRouterChatRequest(BaseModel):
    messages: list[OpenRouterChatMessage] = Field(min_length=1)
    model: str | None = None
    max_tokens: int | None = Field(default=None, gt=0)
    temperature: float | None = Field(default=None, ge=0, le=2)
    top_p: float | None = Field(default=None, ge=0, le=1)
    stop: list[str] | None = None
    response_format: dict[str, Any] | None = None
    tools: list[dict[str, Any]] | None = None
    tool_choice: str | dict[str, Any] | None = None
    reasoning: dict[str, Any] | None = None
    reasoning_effort: Literal[
        "xhigh",
        "high",
        "medium",
        "low",
        "minimal",
        "none",
    ] | None = None
    include_reasoning: bool | None = None


class OpenRouterChatResponse(BaseModel):
    id: str | None = None
    model: str | None = None
    role: str = "assistant"
    content: str
    reasoning: str | None = None
    finish_reason: str | None = None
    usage: dict[str, Any] | None = None
