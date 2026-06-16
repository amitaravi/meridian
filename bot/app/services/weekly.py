import logging
import os

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(__name__)


async def send_weekly_summary(user_id: str, telegram_id: int, bot: Bot) -> None:
    """Send the Sunday evening message linking to the weekly scoreboard."""
    web_app_url = os.environ.get("WEB_APP_URL", "https://meridian.app")
    scoreboard_url = f"{web_app_url}/scoreboard/{user_id}"

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("View your week →", url=scoreboard_url)]]
    )
    await bot.send_message(
        chat_id=telegram_id,
        text=(
            "📊 *Your week in review.*\n\n"
            "See every block, every goal area, and your current streak — "
            "all in one place."
        ),
        parse_mode="Markdown",
        reply_markup=keyboard,
    )
    logger.info("Weekly summary sent to user=%s", user_id)
