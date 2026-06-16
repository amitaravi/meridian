import logging

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram import Bot

logger = logging.getLogger(__name__)

_scheduler = AsyncIOScheduler()
_bot: Bot | None = None


def init(bot: Bot) -> None:
    """Store the bot reference used by scheduled jobs."""
    global _bot
    _bot = bot


def start() -> None:
    _scheduler.start()
    logger.info("Scheduler started")


def stop() -> None:
    if _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")


def register_user_job(
    user_id: str,
    telegram_id: int,
    hour: int,
    minute: int,
    timezone: str,
) -> None:
    """Add or replace a daily brief job for one user."""
    assert _bot is not None, "Call scheduler.init(bot) before registering jobs"
    tz = pytz.timezone(timezone)
    job_id = f"brief_{user_id}"
    _scheduler.add_job(
        _send_brief_job,
        trigger=CronTrigger(hour=hour, minute=minute, timezone=tz),
        id=job_id,
        args=[user_id, telegram_id],
        replace_existing=True,
    )
    logger.info(
        "Registered brief job user=%s at %02d:%02d %s",
        user_id, hour, minute, timezone,
    )


def remove_user_job(user_id: str) -> None:
    job_id = f"brief_{user_id}"
    if _scheduler.get_job(job_id):
        _scheduler.remove_job(job_id)
        logger.info("Removed brief job for user=%s", user_id)


def load_all_jobs() -> None:
    """On startup, register jobs for every active user with a profile."""
    from app.db.users import get_all_active_users_with_profiles

    users = get_all_active_users_with_profiles()
    for user in users:
        profiles: list[dict] = user.get("profiles") or []
        if not profiles:
            continue
        profile = profiles[0]
        register_user_job(
            user_id=user["id"],
            telegram_id=user["telegram_id"],
            hour=profile["brief_hour"],
            minute=profile["brief_minute"],
            timezone=profile.get("timezone", "Asia/Kolkata"),
        )
    logger.info("Loaded %d brief jobs on startup", len(users))


async def _send_brief_job(user_id: str, telegram_id: int) -> None:
    assert _bot is not None
    from app.services.brief import send_brief

    try:
        await send_brief(user_id, telegram_id, _bot)
    except Exception as e:
        logger.error(
            "Scheduled brief failed for user=%s: %s", user_id, e, exc_info=True
        )
