import asyncio

from app.models.deepseek_models import DeepSeekChatResponse
from app.models.recruitment_models import RecruitmentParseRequest
from app.services.recruitment_service import RecruitmentService


class FakeDeepSeekService:
    async def chat(self, chat_request):
        return DeepSeekChatResponse(
            id="chat-test",
            model="deepseek-v4-flash",
            content="""
            {
              "job_title": "Python Backend Engineer",
              "salary": {
                "raw": "20k-30k/month",
                "min_amount": 20000,
                "max_amount": 30000,
                "currency": "CNY",
                "period": "month"
              },
              "skills": ["Python", "FastAPI", "PostgreSQL"],
              "experience": {
                "raw": "3+ years",
                "min_years": 3,
                "max_years": null
              },
              "company": "Example Inc",
              "match_score": 92,
              "match_reason": "岗位、薪资、技能和经验要求都很清晰。"
            }
            """,
            usage={"total_tokens": 100},
        )


class FakeOpenRouterService:
    async def chat(self, chat_request):
        raise AssertionError("openrouter_gpt should not be called in this test")

    async def chat_with_claude(self, chat_request):
        raise AssertionError("openrouter_claude should not be called in this test")


def test_parse_recruitment_with_deepseek():
    service = RecruitmentService(
        deepseek_service=FakeDeepSeekService(),
        openrouter_service=FakeOpenRouterService(),
    )
    request = RecruitmentParseRequest(
        provider="deepseek",
        text="Example Inc 招聘 Python Backend Engineer，20k-30k，3年以上经验。",
    )

    result = asyncio.run(service.parse(request))

    assert result.provider == "deepseek"
    assert result.model == "deepseek-v4-flash"
    assert result.job_title == "Python Backend Engineer"
    assert result.salary.min_amount == 20000
    assert result.skills == ["Python", "FastAPI", "PostgreSQL"]
    assert result.experience.min_years == 3
    assert result.company == "Example Inc"
    assert result.match_score == 92
    assert result.usage == {"total_tokens": 100}
