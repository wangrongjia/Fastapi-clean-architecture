import asyncio

import httpx
import pytest

from app.config import Settings
from app.models.deepseek_models import DeepSeekChatMessage, DeepSeekChatRequest
from app.services.deepseek_service import DeepSeekService


def test_chat_requires_api_key():
    settings = Settings(deepseek_api_key=None)
    service = DeepSeekService(settings=settings)
    request = DeepSeekChatRequest(
        messages=[DeepSeekChatMessage(role="user", content="Hello")]
    )

    with pytest.raises(Exception) as excinfo:
        asyncio.run(service.chat(request))

    assert excinfo.type.__name__ == "HTTPException"
    assert getattr(excinfo.value, "status_code") == 500
    assert getattr(excinfo.value, "detail") == "DEEPSEEK_API_KEY is not configured"


def test_chat_sends_request_and_returns_assistant_response(mocker):
    settings = Settings(
        deepseek_api_key="test-key",
        deepseek_base_url="https://api.deepseek.com",
        deepseek_model="deepseek-v4-flash",
    )
    service = DeepSeekService(settings=settings)
    request = DeepSeekChatRequest(
        messages=[DeepSeekChatMessage(role="user", content="Hello")],
        max_tokens=64,
        temperature=0.2,
        thinking_enabled=False,
    )

    response = httpx.Response(
        200,
        json={
            "id": "chatcmpl-test",
            "model": "deepseek-v4-flash",
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {
                        "role": "assistant",
                        "content": "Hi there!",
                    },
                }
            ],
            "usage": {"total_tokens": 12},
        },
        request=httpx.Request("POST", "https://api.deepseek.com/chat/completions"),
    )

    async_client = mocker.AsyncMock()
    async_client.post.return_value = response
    async_client_context = mocker.MagicMock()
    async_client_context.__aenter__ = mocker.AsyncMock(return_value=async_client)
    async_client_context.__aexit__ = mocker.AsyncMock(return_value=None)
    async_client_class = mocker.patch(
        "app.services.deepseek_service.httpx.AsyncClient",
        return_value=async_client_context,
    )

    result = asyncio.run(service.chat(request))

    async_client_class.assert_called_once_with(timeout=60.0)
    async_client.post.assert_awaited_once_with(
        "https://api.deepseek.com/chat/completions",
        json={
            "model": "deepseek-v4-flash",
            "messages": [{"role": "user", "content": "Hello"}],
            "stream": False,
            "max_tokens": 64,
            "temperature": 0.2,
            "thinking": {"type": "disabled"},
        },
        headers={
            "Authorization": "Bearer test-key",
            "Content-Type": "application/json",
        },
    )
    assert result.id == "chatcmpl-test"
    assert result.content == "Hi there!"
    assert result.finish_reason == "stop"
    assert result.usage == {"total_tokens": 12}
