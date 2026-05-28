import json
from collections.abc import AsyncIterator
from typing import Any

import httpx
from fastapi import HTTPException

from app.config import Settings
from app.models.deepseek_models import DeepSeekChatRequest, DeepSeekChatResponse


class DeepSeekService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def chat(self, chat_request: DeepSeekChatRequest) -> DeepSeekChatResponse:
        if not self.settings.deepseek_api_key:
            raise HTTPException(
                status_code=500,
                detail="DEEPSEEK_API_KEY is not configured",
            )

        payload = self._build_payload(chat_request, stream=False)
        data = await self._send_chat_request(payload)
        return self._parse_chat_response(data)

    def stream_chat(self, chat_request: DeepSeekChatRequest) -> AsyncIterator[str]:
        if not self.settings.deepseek_api_key:
            raise HTTPException(
                status_code=500,
                detail="DEEPSEEK_API_KEY is not configured",
            )

        payload = self._build_payload(chat_request, stream=True)
        return self._stream_chat_request(payload)

    def _build_payload(
        self,
        chat_request: DeepSeekChatRequest,
        stream: bool,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": chat_request.model or self.settings.deepseek_model,
            "messages": [
                message.model_dump() for message in chat_request.messages
            ],
            "stream": stream,
        }

        if chat_request.max_tokens is not None:
            payload["max_tokens"] = chat_request.max_tokens
        if chat_request.temperature is not None:
            payload["temperature"] = chat_request.temperature
        if chat_request.thinking_enabled is not None:
            payload["thinking"] = {
                "type": "enabled" if chat_request.thinking_enabled else "disabled"
            }
        if chat_request.reasoning_effort is not None:
            payload["reasoning_effort"] = chat_request.reasoning_effort
        if stream:
            payload["stream_options"] = {"include_usage": True}

        return payload

    async def _send_chat_request(self, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(
                timeout=self.settings.deepseek_timeout_seconds
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
                detail=f"DeepSeek API error: {detail}",
            ) from exc
        except httpx.TimeoutException as exc:
            raise HTTPException(
                status_code=504,
                detail="DeepSeek API request timed out",
            ) from exc
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"DeepSeek API request failed: {exc}",
            ) from exc
        except ValueError as exc:
            raise HTTPException(
                status_code=502,
                detail="DeepSeek API returned invalid JSON",
            ) from exc

    async def _stream_chat_request(
        self,
        payload: dict[str, Any],
    ) -> AsyncIterator[str]:
        try:
            async with httpx.AsyncClient(
                timeout=self.settings.deepseek_timeout_seconds
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
            yield self._format_sse_error(f"DeepSeek API error: {detail}")
        except httpx.TimeoutException:
            yield self._format_sse_error("DeepSeek API request timed out")
        except httpx.RequestError as exc:
            yield self._format_sse_error(f"DeepSeek API request failed: {exc}")

    def _parse_chat_response(self, data: dict[str, Any]) -> DeepSeekChatResponse:
        choices = data.get("choices") or []
        if not choices:
            raise HTTPException(
                status_code=502,
                detail="DeepSeek API returned no choices",
            )

        choice = choices[0]
        message = choice.get("message") or {}
        content = message.get("content")
        if content is None:
            raise HTTPException(
                status_code=502,
                detail="DeepSeek API returned no assistant content",
            )

        return DeepSeekChatResponse(
            id=data.get("id"),
            model=data.get("model"),
            role=message.get("role") or "assistant",
            content=content,
            reasoning_content=message.get("reasoning_content"),
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
        return f"{self.settings.deepseek_base_url.rstrip('/')}/chat/completions"

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.settings.deepseek_api_key}",
            "Content-Type": "application/json",
        }

    def _format_sse_error(self, detail: str) -> str:
        data = json.dumps({"detail": detail}, ensure_ascii=False)
        return f"event: error\ndata: {data}\n\n"
