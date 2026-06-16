import logging

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram import Bot

logger = logging.getLogger(__name__)

_scheduler = AsyncIOScheduler()
_bot: Bot | None = None


def init(bot: Bot) -> None:
    """Store the bot reference used by all scheduled jobs."""
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
    """Add or replace the morning brief job for one user."""
    assert _bot is not None, "Call scheduler.init(bot) before registering jobs"
    tz = pytz.timezone(timezone)
    _scheduler.add_job(
        _send_brief_job,
        trigger=CronTrigger(hour=hour, minute=minute, timezone=tz),
        id=f"brief_{user_id}",
        args=[user_id, telegram_id],
        replace_existing=True,
    )
    logger.info("Brief job: user=%s at %02d:%02d %s", user_id, hour, minute, timezone)


def register_evening_job(
    user_id: str,
    telegram_id: int,
    brief_hour: int,
    timezone: str,
) -> None:
    """Add or replace the evening scoreboard job for one user.

    Fires at min(brief_hour + 14, 21):00 so a 7am user gets a 9pm scoreboard.
    """
    assert _bot is not None, "Call scheduler.init(bot) before registering jobs"
    evening_hour = min(brief_hour + 14, 21)
    tz = pytz.timezone(timezone)
    _scheduler.add_job(
        _send_scoreboard_job,
        trigger=CronTrigger(hour=evening_hour, minute=0, timezone=tz),
        id=f"scoreboard_{user_id}",
        args=[user_id, telegram_id],
        replace_existing=True,
    )
    logger.info("Scoreboard job: user=%s at %02d:00 %s", user_id, evening_hour, timezone)


def remove_user_job(user_id: str) -> None:
    job_id = f"brief_{user_id}"
    if _scheduler.get_job(job_id):
        _scheduler.remove_job(job_id)
        logger.info("Removed brief job for user=%s", user_id)


def remove_evening_job(user_id: str) -> None:
    job_id = f"scoreboard_{user_id}"
    if _scheduler.get_job(job_id):
        _scheduler.remove_job(job_id)
        logger.info("Removed scoreboard job for user=%s", user_id)


def load_all_jobs() -> None:
    """On startup, register morning + evening jobs for every active user."""
    from app.db.users import get_all_active_users_with_profiles

    users = get_all_active_users_with_profiles()
    for user in users:
        profiles: list[dict] = user.get("profiles") or []
        if not profiles:
            continue
        p = profiles[0]
        tz = p.get("timezone", "Asia/Kolkata")
        register_user_job(
            user_id=user["id"],
            telegram_id=user["telegram_id"],
            hour=p["brief_hour"],
            minute=p["brief_minute"],
            timezone=tz,
        )
        register_evening_job(
            user_id=user["id"],
            telegram_id=user["telegram_id"],
            brief_hour=p["brief_hour"],
            timezone=tz,
        )
    logger.info("Loaded %d user job pairs on startup", len(users))


async def _send_brief_job(user_id: str, telegram_id: int) -> None:
    """Fires each morning: detects re-entry gap and routes to the right brief."""
    assert _bot is not None
    from app.services.reentry import detect_gap, send_reentry_brief
    from app.services.brief import send_brief

    try:
        gap = detect_gap(user_id)
        if gap is not None and gap >= 3:
            logger.info("Re-entry detected for user=%s (gap=%d days)", user_id, gap)
            await send_reentry_brief(user_id, telegram_id, _bot)
        else:
            await send_brief(user_id, telegram_id, _bot)
    except Exception as e:
        logger.error("Brief send failed for user=%s: %s", user_id, e, exc_info=True)


async def _send_scoreboard_job(user_id: str, telegram_id: int) -> None:
    assert _bot is not None
    from app.services.scoreboard import send_scoreboard

    try:
        await send_scoreboard(user_id, telegram_id, _bot)
    except Exception as e:
        logger.error("Scoreboard send failed for user=%s: %s", user_id, e, exc_info=True)
