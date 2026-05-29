from fastapi.testclient import TestClient

from app.dependencies import get_openrouter_service
from app.main import app
from app.models.openrouter_models import OpenRouterChatResponse


class FakeOpenRouterService:
    async def chat(self, chat_request):
        return OpenRouterChatResponse(
            id="gen-test",
            model=chat_request.model or "openai/gpt-oss-120b:free",
            content="Hello!",
            finish_reason="stop",
            usage={"total_tokens": 8},
        )

    async def chat_with_claude(self, chat_request):
        return OpenRouterChatResponse(
            id="gen-claude-test",
            model=chat_request.model or "anthropic/claude-3-haiku",
            content="Hello from Claude!",
            finish_reason="stop",
            usage={"total_tokens": 9},
        )

    async def stream_chat(self, chat_request):
        yield 'data: {"choices":[{"delta":{"content":"Hello"}}]}\n\n'
        yield "data: [DONE]\n\n"

    async def stream_chat_with_claude(self, chat_request):
        yield 'data: {"choices":[{"delta":{"content":"Claude"}}]}\n\n'
        yield "data: [DONE]\n\n"


def test_chat_with_openrouter(client: TestClient):
    app.dependency_overrides[get_openrouter_service] = lambda: FakeOpenRouterService()

    response = client.post(
        "/chat/openrouter",
        json={"messages": [{"role": "user", "content": "Hello"}]},
    )

    data = response.json()

    assert response.status_code == 200
    assert data["id"] == "gen-test"
    assert data["model"] == "openai/gpt-oss-120b:free"
    assert data["role"] == "assistant"
    assert data["content"] == "Hello!"
    assert data["finish_reason"] == "stop"
    assert data["usage"] == {"total_tokens": 8}


def test_stream_chat_with_openrouter(client: TestClient):
    app.dependency_overrides[get_openrouter_service] = lambda: FakeOpenRouterService()

    with client.stream(
        "POST",
        "/chat/openrouter/stream",
        json={"messages": [{"role": "user", "content": "Hello"}]},
    ) as response:
        data = response.read().decode()

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert 'data: {"choices":[{"delta":{"content":"Hello"}}]}' in data
    assert "data: [DONE]" in data


def test_chat_with_openrouter_claude(client: TestClient):
    app.dependency_overrides[get_openrouter_service] = lambda: FakeOpenRouterService()

    response = client.post(
        "/chat/openrouter/claude",
        json={"messages": [{"role": "user", "content": "Hello"}]},
    )

    data = response.json()

    assert response.status_code == 200
    assert data["id"] == "gen-claude-test"
    assert data["model"] == "anthropic/claude-3-haiku"
    assert data["role"] == "assistant"
    assert data["content"] == "Hello from Claude!"
    assert data["finish_reason"] == "stop"
    assert data["usage"] == {"total_tokens": 9}


def test_stream_chat_with_openrouter_claude(client: TestClient):
    app.dependency_overrides[get_openrouter_service] = lambda: FakeOpenRouterService()

    with client.stream(
        "POST",
        "/chat/openrouter/claude/stream",
        json={"messages": [{"role": "user", "content": "Hello"}]},
    ) as response:
        data = response.read().decode()

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert 'data: {"choices":[{"delta":{"content":"Claude"}}]}' in data
    assert "data: [DONE]" in data
