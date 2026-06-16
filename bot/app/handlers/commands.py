import logging
from datetime import timedelta

from telegram import Update
from telegram.ext import ContextTypes

from app.db.profiles import get_profile_by_telegram_id
from app.db.streaks import get_streak
from app.db.users import get_user_by_telegram_id, set_user_active
from app.services import scheduler

logger = logging.getLogger(__name__)


async def handle_pause(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    assert update.effective_user and update.message

    telegram_id = update.effective_user.id
    try:
        user = get_user_by_telegram_id(telegram_id)
        if not user:
            await update.message.reply_text("Couldn't find your account. Try /start first.")
            return
        set_user_active(telegram_id, active=False)
        scheduler.remove_user_job(user["id"])
        scheduler.remove_evening_job(user["id"])
    except Exception as e:
        logger.error("Error in /pause for %d: %s", telegram_id, e, exc_info=True)
        await update.message.reply_text("Something went wrong. Please try again.")
        return

    await update.message.reply_text(
        "Paused. Your daily brief will stop arriving.\n\n"
        "Send /resume whenever you're ready to pick back up."
    )


async def handle_resume(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    assert update.effective_user and update.message

    telegram_id = update.effective_user.id
    try:
        user = get_user_by_telegram_id(telegram_id)
        if not user:
            await update.message.reply_text("Couldn't find your account. Try /start first.")
            return
        profile = get_profile_by_telegram_id(telegram_id)
        if not profile:
            await update.message.reply_text(
                "Your profile isn't set up yet. Use /start to begin onboarding."
            )
            return
        set_user_active(telegram_id, active=True)
        scheduler.register_user_job(
            user_id=user["id"],
            telegram_id=telegram_id,
            hour=profile["brief_hour"],
            minute=profile["brief_minute"],
            timezone=profile.get("timezone", "Asia/Kolkata"),
        )
        scheduler.register_evening_job(
            user_id=user["id"],
            telegram_id=telegram_id,
            brief_hour=profile["brief_hour"],
            timezone=profile.get("timezone", "Asia/Kolkata"),
        )
    except Exception as e:
        logger.error("Error in /resume for %d: %s", telegram_id, e, exc_info=True)
        await update.message.reply_text("Something went wrong. Please try again.")
        return

    hour = profile["brief_hour"]
    minute = profile["brief_minute"]
    tz = profile.get("timezone", "Asia/Kolkata")
    await update.message.reply_text(
        f"Resumed. Your daily brief will arrive at "
        f"{hour:02d}:{minute:02d} {tz} each morning."
    )


async def handle_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    assert update.effective_user and update.message

    telegram_id = update.effective_user.id
    try:
        user = get_user_by_telegram_id(telegram_id)
        if not user:
            await update.message.reply_text("Couldn't find your account. Try /start first.")
            return
        profile = get_profile_by_telegram_id(telegram_id)
        if not profile:
            await update.message.reply_text(
                "You haven't completed onboarding yet. Use /start to begin."
            )
            return
        streak_row = get_streak(user["id"])
    except Exception as e:
        logger.error("Error in /status for %d: %s", telegram_id, e, exc_info=True)
        await update.message.reply_text("Something went wrong. Please try again.")
        return

    streak = streak_row["current_streak"] if streak_row else 0
    last_active = streak_row.get("last_active_date") if streak_row else None
    areas = profile.get("goal_areas") or []
    active = user.get("is_active", True)

    area_lines = "\n".join(
        f"{a['color_emoji']} {a['name']} ({a['weekly_hours']}h/week)"
        for a in areas
    )
    status_tag = "Active" if active else "Paused — /resume to restart"

    await update.message.reply_text(
        f"📊 *Your Meridian*\n\n"
        f"🔥 Streak: {streak} day{'s' if streak != 1 else ''}\n"
        f"Last active: {last_active or 'never'}\n\n"
        f"*Goal areas:*\n{area_lines}\n\n"
        f"⏰ Brief: {profile['brief_hour']:02d}:{profile['brief_minute']:02d} "
        f"{profile.get('timezone', 'Asia/Kolkata')}\n"
        f"Status: {status_tag}",
        parse_mode="Markdown",
    )
