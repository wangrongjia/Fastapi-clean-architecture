from typing import Literal

from pydantic import BaseModel, Field


RecruitmentProvider = Literal[
    "deepseek",
    "openrouter_gpt",
    "openrouter_claude",
]


class RecruitmentParseRequest(BaseModel):
    text: str = Field(min_length=1)
    provider: RecruitmentProvider = "deepseek"


class SalaryInfo(BaseModel):
    raw: str | None = None
    min_amount: float | None = None
    max_amount: float | None = None
    currency: str | None = None
    period: str | None = None


class ExperienceInfo(BaseModel):
    raw: str | None = None
    min_years: float | None = None
    max_years: float | None = None


class RecruitmentParseResponse(BaseModel):
    job_title: str | None = None
    salary: SalaryInfo = Field(default_factory=SalaryInfo)
    skills: list[str] = Field(default_factory=list)
    experience: ExperienceInfo = Field(default_factory=ExperienceInfo)
    company: str | None = None
    match_score: int = Field(ge=0, le=100)
    match_reason: str | None = None
    provider: RecruitmentProvider
    model: str | None = None
    usage: dict | None = None
