import logging
import os

from fastapi import APIRouter, HTTPException, Request

from app.services import scheduler

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/internal/register-job")
async def register_job(request: Request) -> dict[str, str]:
    """Called by the web app after a profile is saved to hot-reload the scheduler."""
    key = request.headers.get("X-Internal-Key", "")
    if not key or key != os.environ.get("INTERNAL_API_KEY", ""):
        raise HTTPException(status_code=401, detail="Unauthorized")

    body: dict = await request.json()
    try:
        scheduler.register_user_job(
            user_id=body["user_id"],
            telegram_id=int(body["telegram_id"]),
            hour=int(body["brief_hour"]),
            minute=int(body["brief_minute"]),
            timezone=body["timezone"],
        )
        scheduler.register_evening_job(
            user_id=body["user_id"],
            telegram_id=int(body["telegram_id"]),
            brief_hour=int(body["brief_hour"]),
            timezone=body["timezone"],
        )
    except Exception as e:
        logger.error("Failed to register job from internal call: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to register job")

    return {"status": "ok"}
