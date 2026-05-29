from fastapi.testclient import TestClient

from app.dependencies import get_recruitment_service
from app.main import app
from app.models.recruitment_models import RecruitmentParseResponse


class FakeRecruitmentService:
    async def parse(self, request):
        return RecruitmentParseResponse(
            provider=request.provider,
            model="openai/gpt-oss-120b:free",
            job_title="Backend Engineer",
            salary={"raw": "20k-30k", "min_amount": 20000, "max_amount": 30000},
            skills=["Python", "FastAPI"],
            experience={"raw": "3年以上", "min_years": 3},
            company="Example Inc",
            match_score=88,
            match_reason="关键信息较完整。",
            usage={"total_tokens": 80},
        )


def test_parse_recruitment_text(client: TestClient):
    app.dependency_overrides[get_recruitment_service] = lambda: FakeRecruitmentService()

    response = client.post(
        "/recruitment/parse",
        json={
            "provider": "openrouter_gpt",
            "text": "Example Inc 招聘 Backend Engineer，20k-30k，3年以上经验。",
        },
    )

    data = response.json()

    assert response.status_code == 200
    assert data["provider"] == "openrouter_gpt"
    assert data["model"] == "openai/gpt-oss-120b:free"
    assert data["job_title"] == "Backend Engineer"
    assert data["salary"]["min_amount"] == 20000
    assert data["skills"] == ["Python", "FastAPI"]
    assert data["experience"]["min_years"] == 3
    assert data["company"] == "Example Inc"
    assert data["match_score"] == 88
