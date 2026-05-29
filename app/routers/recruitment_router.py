from fastapi import APIRouter

from app.dependencies import RecruitmentServiceDep
from app.models.recruitment_models import (
    RecruitmentParseRequest,
    RecruitmentParseResponse,
)

router = APIRouter(prefix="/recruitment", tags=["recruitment"])


@router.post("/parse", response_model=RecruitmentParseResponse)
async def parse_recruitment_text(
    request: RecruitmentParseRequest,
    service: RecruitmentServiceDep,
):
    return await service.parse(request)
