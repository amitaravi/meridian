import logging
import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from app.db.profiles import get_profile_by_telegram_id
from app.db.users import create_user_if_not_exists

logger = logging.getLogger(__name__)


async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    assert update.effective_user is not None
    assert update.message is not None

    telegram_id = update.effective_user.id

    try:
        user = create_user_if_not_exists(telegram_id)
        profile = get_profile_by_telegram_id(telegram_id)
    except Exception as e:
        logger.error("DB error in /start for %d: %s", telegram_id, e, exc_info=True)
        await update.message.reply_text(
            "Something went wrong setting up your account. Please try again in a moment."
        )
        return

    if profile:
        # Ensure scheduler jobs are live for this user. Covers the gap between
        # completing web onboarding and the next bot restart.
        try:
            from app.services import scheduler
            scheduler.ensure_user_job(user["id"], telegram_id, profile)
        except Exception as e:
            logger.warning("Could not register scheduler job for %d: %s", telegram_id, e)

        await update.message.reply_text(
            "Welcome back. Your daily brief keeps arriving.\n\n"
            "Use /status to see your streak, or /pause to take a break."
        )
        return

    web_app_url = os.environ.get("WEB_APP_URL", "https://meridian.app")
    onboarding_url = f"{web_app_url}/onboarding?tid={telegram_id}"
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Begin Onboarding →", url=onboarding_url)]]
    )
    await update.message.reply_text(
        "Welcome to Meridian.\n\n"
        "You're one setup away from a daily brief that keeps you on your ambitious path — "
        "not your comfortable one.\n\n"
        "Take 5 minutes to tell me about your two futures.",
        reply_markup=keyboard,
    )
