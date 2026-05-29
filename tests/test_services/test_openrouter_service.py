import asyncio

import httpx
import pytest

from app.config import Settings
from app.models.openrouter_models import OpenRouterChatMessage, OpenRouterChatRequest
from app.services.openrouter_service import OpenRouterService


def test_chat_requires_api_key():
    settings = Settings(openrouter_api_key=None)
    service = OpenRouterService(settings=settings)
    request = OpenRouterChatRequest(
        messages=[OpenRouterChatMessage(role="user", content="Hello")]
    )

    with pytest.raises(Exception) as excinfo:
        asyncio.run(service.chat(request))

    assert excinfo.type.__name__ == "HTTPException"
    assert getattr(excinfo.value, "status_code") == 500
    assert getattr(excinfo.value, "detail") == "OPENROUTER_API_KEY is not configured"


def test_chat_sends_request_and_returns_assistant_response(mocker):
    settings = Settings(
        openrouter_api_key="test-key",
        openrouter_base_url="https://openrouter.ai/api/v1",
        openrouter_model="openai/gpt-oss-120b:free",
        openrouter_site_url="https://example.com",
        openrouter_app_name="Test App",
    )
    service = OpenRouterService(settings=settings)
    request = OpenRouterChatRequest(
        messages=[OpenRouterChatMessage(role="user", content="Hello")],
        max_tokens=64,
        temperature=0.2,
        reasoning_effort="low",
    )

    response = httpx.Response(
        200,
        json={
            "id": "gen-test",
            "model": "openai/gpt-oss-120b:free",
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {
                        "role": "assistant",
                        "content": "Hi there!",
                        "reasoning": "Short reasoning trace",
                    },
                }
            ],
            "usage": {"total_tokens": 12},
        },
        request=httpx.Request(
            "POST",
            "https://openrouter.ai/api/v1/chat/completions",
        ),
    )

    async_client = mocker.AsyncMock()
    async_client.post.return_value = response
    async_client_context = mocker.MagicMock()
    async_client_context.__aenter__ = mocker.AsyncMock(return_value=async_client)
    async_client_context.__aexit__ = mocker.AsyncMock(return_value=None)
    async_client_class = mocker.patch(
        "app.services.openrouter_service.httpx.AsyncClient",
        return_value=async_client_context,
    )

    result = asyncio.run(service.chat(request))

    async_client_class.assert_called_once_with(timeout=60.0)
    async_client.post.assert_awaited_once_with(
        "https://openrouter.ai/api/v1/chat/completions",
        json={
            "model": "openai/gpt-oss-120b:free",
            "messages": [{"role": "user", "content": "Hello"}],
            "stream": False,
            "max_tokens": 64,
            "temperature": 0.2,
            "reasoning_effort": "low",
        },
        headers={
            "Authorization": "Bearer test-key",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://example.com",
            "X-Title": "Test App",
        },
    )
    assert result.id == "gen-test"
    assert result.model == "openai/gpt-oss-120b:free"
    assert result.content == "Hi there!"
    assert result.reasoning == "Short reasoning trace"
    assert result.finish_reason == "stop"
    assert result.usage == {"total_tokens": 12}


def test_stream_payload_includes_usage_option():
    settings = Settings(openrouter_api_key="test-key")
    service = OpenRouterService(settings=settings)
    request = OpenRouterChatRequest(
        messages=[OpenRouterChatMessage(role="user", content="Hello")]
    )

    payload = service._build_payload(
        request,
        stream=True,
        default_model=settings.openrouter_model,
    )

    assert payload["model"] == "openai/gpt-oss-120b:free"
    assert payload["stream"] is True
    assert payload["stream_options"] == {"include_usage": True}


def test_claude_payload_uses_claude_default_model():
    settings = Settings(openrouter_api_key="test-key")
    service = OpenRouterService(settings=settings)
    request = OpenRouterChatRequest(
        messages=[OpenRouterChatMessage(role="user", content="Hello")]
    )

    payload = service._build_payload(
        request,
        stream=False,
        default_model=settings.openrouter_claude_model,
    )

    assert payload["model"] == "anthropic/claude-3-haiku"
    assert payload["stream"] is False
