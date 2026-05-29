from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.dependencies import OpenRouterServiceDep
from app.models.openrouter_models import (
    OpenRouterChatRequest,
    OpenRouterChatResponse,
)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/openrouter", response_model=OpenRouterChatResponse)
async def chat_with_openrouter(
    chat_request: OpenRouterChatRequest,
    service: OpenRouterServiceDep,
):
    return await service.chat(chat_request)


@router.post("/openrouter/stream")
def stream_chat_with_openrouter(
    chat_request: OpenRouterChatRequest,
    service: OpenRouterServiceDep,
):
    return StreamingResponse(
        service.stream_chat(chat_request),
        media_type="text/event-stream",
    )


@router.post("/openrouter/claude", response_model=OpenRouterChatResponse)
async def chat_with_openrouter_claude(
    chat_request: OpenRouterChatRequest,
    service: OpenRouterServiceDep,
):
    return await service.chat_with_claude(chat_request)


@router.post("/openrouter/claude/stream")
def stream_chat_with_openrouter_claude(
    chat_request: OpenRouterChatRequest,
    service: OpenRouterServiceDep,
):
    return StreamingResponse(
        service.stream_chat_with_claude(chat_request),
        media_type="text/event-stream",
    )
