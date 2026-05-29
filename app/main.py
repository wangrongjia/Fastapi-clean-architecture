from fastapi import FastAPI

from app.db import create_db_and_tables
from app.logging_config import get_logger, setup_logging
from app.routers import (
    deepseek_router,
    hero_router,
    openrouter_router,
    recruitment_router,
)

# Initialize logging and create logger for this module
setup_logging()
logger = get_logger(__name__)

app = FastAPI()
logger.info("API is ready.")

app.include_router(hero_router.router)
app.include_router(deepseek_router.router)
app.include_router(openrouter_router.router)
app.include_router(recruitment_router.router)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    logger.info("Connected database and created tables.")
