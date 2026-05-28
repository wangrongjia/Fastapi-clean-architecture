from fastapi.testclient import TestClient

from app.dependencies import get_deepseek_service
from app.main import app
from app.models.deepseek_models import DeepSeekChatResponse


class FakeDeepSeekService:
    async def chat(self, chat_request):
        return DeepSeekChatResponse(
            id="chatcmpl-test",
            model=chat_request.model or "deepseek-v4-flash",
            content="你好！",
            finish_reason="stop",
            usage={"total_tokens": 8},
        )


def test_chat_with_deepseek(client: TestClient):
    app.dependency_overrides[get_deepseek_service] = lambda: FakeDeepSeekService()

    response = client.post(
        "/chat/deepseek",
        json={"messages": [{"role": "user", "content": "你好"}]},
    )

    data = response.json()

    assert response.status_code == 200
    assert data["id"] == "chatcmpl-test"
    assert data["model"] == "deepseek-v4-flash"
    assert data["role"] == "assistant"
    assert data["content"] == "你好！"
    assert data["finish_reason"] == "stop"
    assert data["usage"] == {"total_tokens": 8}
