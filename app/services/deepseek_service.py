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

        payload = self._build_payload(chat_request)
        data = await self._send_chat_request(payload)
        return self._parse_chat_response(data)

    def _build_payload(self, chat_request: DeepSeekChatRequest) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": chat_request.model or self.settings.deepseek_model,
            "messages": [
                message.model_dump() for message in chat_request.messages
            ],
            "stream": False,
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

        return payload

    async def _send_chat_request(self, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.settings.deepseek_base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.settings.deepseek_api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(
                timeout=self.settings.deepseek_timeout_seconds
            ) as client:
                response = await client.post(url, json=payload, headers=headers)
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
