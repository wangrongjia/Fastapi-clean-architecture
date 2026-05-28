from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.dependencies import DeepSeekServiceDep
from app.models.deepseek_models import DeepSeekChatRequest, DeepSeekChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/deepseek", response_model=DeepSeekChatResponse)
async def chat_with_deepseek(
    chat_request: DeepSeekChatRequest,
    service: DeepSeekServiceDep,
):
    return await service.chat(chat_request)


@router.post("/deepseek/stream")
def stream_chat_with_deepseek(
    chat_request: DeepSeekChatRequest,
    service: DeepSeekServiceDep,
):
    return StreamingResponse(
        service.stream_chat(chat_request),
        media_type="text/event-stream",
    )
