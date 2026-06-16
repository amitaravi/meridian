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


def register_weekly_job(
    user_id: str,
    telegram_id: int,
    timezone: str,
) -> None:
    """Add or replace the Sunday 8pm scoreboard link job for one user."""
    assert _bot is not None, "Call scheduler.init(bot) before registering jobs"
    tz = pytz.timezone(timezone)
    _scheduler.add_job(
        _send_weekly_job,
        trigger=CronTrigger(day_of_week="sun", hour=20, minute=0, timezone=tz),
        id=f"weekly_{user_id}",
        args=[user_id, telegram_id],
        replace_existing=True,
    )
    logger.info("Weekly job: user=%s Sundays 20:00 %s", user_id, timezone)


def remove_user_job(user_id: str) -> None:
    for job_id in (f"brief_{user_id}", f"weekly_{user_id}"):
        if _scheduler.get_job(job_id):
            _scheduler.remove_job(job_id)
            logger.info("Removed job %s", job_id)


def load_all_jobs() -> None:
    """On startup, register brief + weekly jobs for every active user."""
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
        register_weekly_job(
            user_id=user["id"],
            telegram_id=user["telegram_id"],
            timezone=tz,
        )
    logger.info("Loaded %d user job pairs on startup", len(users))


async def _send_brief_job(user_id: str, telegram_id: int) -> None:
    assert _bot is not None
    from app.services.brief import send_brief

    try:
        await send_brief(user_id, telegram_id, _bot)
    except Exception as e:
        logger.error("Scheduled brief failed for user=%s: %s", user_id, e, exc_info=True)


async def _send_weekly_job(user_id: str, telegram_id: int) -> None:
    assert _bot is not None
    from app.services.weekly import send_weekly_summary

    try:
        await send_weekly_summary(user_id, telegram_id, _bot)
    except Exception as e:
        logger.error("Weekly summary failed for user=%s: %s", user_id, e, exc_info=True)
