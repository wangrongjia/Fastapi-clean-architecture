import json
from collections.abc import AsyncIterator
from typing import Any

import httpx
from fastapi import HTTPException

from app.config import Settings
from app.models.openrouter_models import (
    OpenRouterChatRequest,
    OpenRouterChatResponse,
)


class OpenRouterService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def chat(
        self,
        chat_request: OpenRouterChatRequest,
    ) -> OpenRouterChatResponse:
        return await self._chat(chat_request, default_model=self.settings.openrouter_model)

    async def chat_with_claude(
        self,
        chat_request: OpenRouterChatRequest,
    ) -> OpenRouterChatResponse:
        return await self._chat(
            chat_request,
            default_model=self.settings.openrouter_claude_model,
        )

    async def _chat(
        self,
        chat_request: OpenRouterChatRequest,
        default_model: str,
    ) -> OpenRouterChatResponse:
        if not self.settings.openrouter_api_key:
            raise HTTPException(
                status_code=500,
                detail="OPENROUTER_API_KEY is not configured",
            )

        payload = self._build_payload(
            chat_request,
            stream=False,
            default_model=default_model,
        )
        data = await self._send_chat_request(payload)
        return self._parse_chat_response(data)

    def stream_chat(
        self,
        chat_request: OpenRouterChatRequest,
    ) -> AsyncIterator[str]:
        return self._stream_chat(
            chat_request,
            default_model=self.settings.openrouter_model,
        )

    def stream_chat_with_claude(
        self,
        chat_request: OpenRouterChatRequest,
    ) -> AsyncIterator[str]:
        return self._stream_chat(
            chat_request,
            default_model=self.settings.openrouter_claude_model,
        )

    def _stream_chat(
        self,
        chat_request: OpenRouterChatRequest,
        default_model: str,
    ) -> AsyncIterator[str]:
        if not self.settings.openrouter_api_key:
            raise HTTPException(
                status_code=500,
                detail="OPENROUTER_API_KEY is not configured",
            )

        payload = self._build_payload(
            chat_request,
            stream=True,
            default_model=default_model,
        )
        return self._stream_chat_request(payload)

    def _build_payload(
        self,
        chat_request: OpenRouterChatRequest,
        stream: bool,
        default_model: str,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": chat_request.model or default_model,
            "messages": [
                message.model_dump() for message in chat_request.messages
            ],
            "stream": stream,
        }

        optional_fields = (
            "max_tokens",
            "temperature",
            "top_p",
            "stop",
            "response_format",
            "tools",
            "tool_choice",
            "reasoning",
            "reasoning_effort",
            "include_reasoning",
        )
        request_data = chat_request.model_dump(exclude_none=True)
        for field in optional_fields:
            if field in request_data:
                payload[field] = request_data[field]

        if stream:
            payload["stream_options"] = {"include_usage": True}

        return payload

    async def _send_chat_request(self, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(
                timeout=self.settings.openrouter_timeout_seconds
            ) as client:
                response = await client.post(
                    self._chat_url(),
                    json=payload,
                    headers=self._headers(),
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as exc:
            detail = self._extract_error_detail(exc.response)
            raise HTTPException(
                status_code=502,
                detail=f"OpenRouter API error: {detail}",
            ) from exc
        except httpx.TimeoutException as exc:
            raise HTTPException(
                status_code=504,
                detail="OpenRouter API request timed out",
            ) from exc
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"OpenRouter API request failed: {exc}",
            ) from exc
        except ValueError as exc:
            raise HTTPException(
                status_code=502,
                detail="OpenRouter API returned invalid JSON",
            ) from exc

    async def _stream_chat_request(
        self,
        payload: dict[str, Any],
    ) -> AsyncIterator[str]:
        try:
            async with httpx.AsyncClient(
                timeout=self.settings.openrouter_timeout_seconds
            ) as client:
                async with client.stream(
                    "POST",
                    self._chat_url(),
                    json=payload,
                    headers=self._headers(),
                ) as response:
                    response.raise_for_status()
                    async for chunk in response.aiter_text():
                        if chunk:
                            yield chunk
        except httpx.HTTPStatusError as exc:
            detail = self._extract_error_detail(exc.response)
            yield self._format_sse_error(f"OpenRouter API error: {detail}")
        except httpx.TimeoutException:
            yield self._format_sse_error("OpenRouter API request timed out")
        except httpx.RequestError as exc:
            yield self._format_sse_error(f"OpenRouter API request failed: {exc}")

    def _parse_chat_response(self, data: dict[str, Any]) -> OpenRouterChatResponse:
        choices = data.get("choices") or []
        if not choices:
            raise HTTPException(
                status_code=502,
                detail="OpenRouter API returned no choices",
            )

        choice = choices[0]
        message = choice.get("message") or {}
        content = message.get("content")
        if content is None:
            raise HTTPException(
                status_code=502,
                detail="OpenRouter API returned no assistant content",
            )

        return OpenRouterChatResponse(
            id=data.get("id"),
            model=data.get("model"),
            role=message.get("role") or "assistant",
            content=content,
            reasoning=message.get("reasoning"),
            finish_reason=choice.get("finish_reason"),
            usage=data.get("usage"),
        )

    def _extract_error_detail(self, response: httpx.Response) -> str:
        try:
            data = response.json()
        except ValueError:
            return response.text

        error = data.get("error") if isinstance(data, dict) else None
        if isinstance(error, dict):
            return str(error.get("message") or error)
        return str(data)

    def _chat_url(self) -> str:
        return f"{self.settings.openrouter_base_url.rstrip('/')}/chat/completions"

    def _headers(self) -> dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self.settings.openrouter_api_key}",
            "Content-Type": "application/json",
        }
        if self.settings.openrouter_site_url:
            headers["HTTP-Referer"] = self.settings.openrouter_site_url
        if self.settings.openrouter_app_name:
            headers["X-Title"] = self.settings.openrouter_app_name
        return headers

    def _format_sse_error(self, detail: str) -> str:
        data = json.dumps({"detail": detail}, ensure_ascii=False)
        return f"event: error\ndata: {data}\n\n"
