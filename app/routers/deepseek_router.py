from fastapi import APIRouter

from app.dependencies import DeepSeekServiceDep
from app.models.deepseek_models import DeepSeekChatRequest, DeepSeekChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/deepseek", response_model=DeepSeekChatResponse)
async def chat_with_deepseek(
    chat_request: DeepSeekChatRequest,
    service: DeepSeekServiceDep,
):
    return await service.chat(chat_request)
