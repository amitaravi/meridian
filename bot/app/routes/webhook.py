import logging
from typing import Any

from fastapi import APIRouter, Request
from telegram import Update

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/webhook")
async def webhook(request: Request) -> dict[str, str]:
    data: dict[str, Any] = await request.json()
    bot_app = request.app.state.bot_app
    update = Update.de_json(data, bot_app.bot)
    await bot_app.process_update(update)
    return {"status": "ok"}
