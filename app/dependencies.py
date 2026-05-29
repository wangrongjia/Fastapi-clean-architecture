from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from app.db import engine
from app.repositories.hero_repository import HeroRepository
from app.services.deepseek_service import DeepSeekService
from app.services.hero_service import HeroService
from app.services.openrouter_service import OpenRouterService


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def get_hero_repository(session: SessionDep) -> HeroRepository:
    return HeroRepository(session=session)


HeroRepoDep = Annotated[HeroRepository, Depends(get_hero_repository)]


def get_hero_service(repo: HeroRepoDep) -> HeroService:
    return HeroService(repo=repo)


HeroServiceDep = Annotated[HeroService, Depends(get_hero_service)]


def get_deepseek_service() -> DeepSeekService:
    from app.db import get_settings

    return DeepSeekService(settings=get_settings())


DeepSeekServiceDep = Annotated[DeepSeekService, Depends(get_deepseek_service)]


def get_openrouter_service() -> OpenRouterService:
    from app.db import get_settings

    return OpenRouterService(settings=get_settings())


OpenRouterServiceDep = Annotated[OpenRouterService, Depends(get_openrouter_service)]
