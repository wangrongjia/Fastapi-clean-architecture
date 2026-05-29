import json
import re
from typing import Any

from fastapi import HTTPException
from pydantic import ValidationError

from app.models.deepseek_models import DeepSeekChatMessage, DeepSeekChatRequest
from app.models.openrouter_models import OpenRouterChatMessage, OpenRouterChatRequest
from app.models.recruitment_models import (
    RecruitmentParseRequest,
    RecruitmentParseResponse,
    RecruitmentProvider,
)
from app.services.deepseek_service import DeepSeekService
from app.services.openrouter_service import OpenRouterService


class RecruitmentService:
    def __init__(
        self,
        deepseek_service: DeepSeekService,
        openrouter_service: OpenRouterService,
    ) -> None:
        self.deepseek_service = deepseek_service
        self.openrouter_service = openrouter_service

    async def parse(
        self,
        request: RecruitmentParseRequest,
    ) -> RecruitmentParseResponse:
        system_prompt = self._system_prompt()
        user_prompt = self._user_prompt(request.text)

        if request.provider == "deepseek":
            chat_response = await self.deepseek_service.chat(
                DeepSeekChatRequest(
                    messages=[
                        DeepSeekChatMessage(role="system", content=system_prompt),
                        DeepSeekChatMessage(role="user", content=user_prompt),
                    ],
                    max_tokens=1200,
                    temperature=0,
                    response_format={"type": "json_object"},
                    thinking_enabled=False,
                )
            )
        else:
            chat_request = OpenRouterChatRequest(
                messages=[
                    OpenRouterChatMessage(role="system", content=system_prompt),
                    OpenRouterChatMessage(role="user", content=user_prompt),
                ],
                max_tokens=1200,
                temperature=0,
                response_format={"type": "json_object"},
            )
            if request.provider == "openrouter_gpt":
                chat_response = await self.openrouter_service.chat(chat_request)
            else:
                chat_response = await self.openrouter_service.chat_with_claude(
                    chat_request
                )

        return self._parse_model_json(
            content=chat_response.content,
            provider=request.provider,
            model=chat_response.model,
            usage=chat_response.usage,
        )

    def _parse_model_json(
        self,
        content: str,
        provider: RecruitmentProvider,
        model: str | None,
        usage: dict[str, Any] | None,
    ) -> RecruitmentParseResponse:
        try:
            data = json.loads(self._strip_json_fence(content))
        except json.JSONDecodeError as exc:
            raise HTTPException(
                status_code=502,
                detail="LLM returned invalid recruitment JSON",
            ) from exc

        if not isinstance(data, dict):
            raise HTTPException(
                status_code=502,
                detail="LLM returned non-object recruitment JSON",
            )

        data["provider"] = provider
        data["model"] = model
        data["usage"] = usage

        try:
            return RecruitmentParseResponse.model_validate(data)
        except ValidationError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"LLM returned invalid recruitment schema: {exc.errors()}",
            ) from exc

    def _strip_json_fence(self, content: str) -> str:
        text = content.strip()
        match = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", text, flags=re.DOTALL)
        if match:
            return match.group(1).strip()
        return text

    def _system_prompt(self) -> str:
        return (
            "你是招聘信息结构化抽取助手。只返回合法 JSON，不要返回 Markdown、解释、"
            "前后缀文本。无法确定的字段使用 null 或空数组。"
        )

    def _user_prompt(self, text: str) -> str:
        return f"""
请从下面的招聘文本中抽取结构化信息，并严格返回这个 JSON 结构：
{{
  "job_title": "岗位名称，无法确定则为 null",
  "salary": {{
    "raw": "原始薪资文本，无法确定则为 null",
    "min_amount": "数字，无法确定则为 null",
    "max_amount": "数字，无法确定则为 null",
    "currency": "币种，如 CNY/USD，无法确定则为 null",
    "period": "薪资周期，如 month/year/day/hour，无法确定则为 null"
  }},
  "skills": ["技能关键词，按重要性排序"],
  "experience": {{
    "raw": "原始经验要求文本，无法确定则为 null",
    "min_years": "数字，无法确定则为 null",
    "max_years": "数字，无法确定则为 null"
  }},
  "company": "公司名称，无法确定则为 null",
  "match_score": "0-100 的整数。只基于招聘文本本身，表示岗位画像清晰度和信息完整度，不是候选人匹配分",
  "match_reason": "一句话说明 match_score 的依据"
}}

招聘文本：
{text}
""".strip()
