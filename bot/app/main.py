import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from dotenv import load_dotenv
from fastapi import FastAPI

from app.bot import create_application
from app.routes.health import router as health_router
from app.routes.internal import router as internal_router
from app.routes.webhook import router as webhook_router
from app.services import scheduler

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    bot_app = create_application()
    await bot_app.initialize()
    await bot_app.start()

    webhook_url = os.environ["WEBHOOK_URL"]
    await bot_app.bot.set_webhook(url=f"{webhook_url}/webhook")
    logger.info("Webhook registered at %s/webhook", webhook_url)

    scheduler.init(bot_app.bot)
    scheduler.load_all_jobs()
    scheduler.start()

    app.state.bot_app = bot_app
    yield

    scheduler.stop()
    await bot_app.stop()
    await bot_app.shutdown()


app = FastAPI(lifespan=lifespan)
app.include_router(health_router)
app.include_router(webhook_router)
app.include_router(internal_router)
