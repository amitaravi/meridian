import logging
from datetime import date

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

from app.ai.generate import generate_narrative, generate_time_blocks
from app.db.logs import create_log, get_latest_log
from app.db.profiles import get_profile_by_user_id
from app.db.streaks import get_streak

logger = logging.getLogger(__name__)

FRAMING_SEQUENCE = ["fear", "aspiration", "accomplishment", "urgency"]


def _next_framing(last_log: dict | None) -> str:
    if not last_log:
        return "fear"
    try:
        idx = FRAMING_SEQUENCE.index(last_log["framing_type"])
        return FRAMING_SEQUENCE[(idx + 1) % len(FRAMING_SEQUENCE)]
    except (ValueError, KeyError):
        return "fear"


def _block_keyboard(block_index: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✓ Done", callback_data=f"done:{block_index}"),
        InlineKeyboardButton("→ Skip", callback_data=f"skip:{block_index}"),
    ]])


async def send_brief(user_id: str, telegram_id: int, bot: Bot) -> None:
    """Generate and deliver the daily brief for one user."""
    profile = get_profile_by_user_id(user_id)
    if not profile:
        logger.warning("send_brief: no profile for user_id=%s, skipping", user_id)
        return

    streak_row = get_streak(user_id)
    current_streak = streak_row["current_streak"] if streak_row else 0

    last_log = get_latest_log(user_id)
    framing_type = _next_framing(last_log)
    today = date.today().isoformat()

    narrative = await generate_narrative(profile, framing_type, current_streak)
    blocks = await generate_time_blocks(profile, n=3)

    create_log(user_id, today, blocks, framing_type)
    logger.info(
        "Brief generated for user=%s framing=%s blocks=%d",
        user_id, framing_type, len(blocks),
    )

    await bot.send_message(chat_id=telegram_id, text=narrative)

    for block in blocks:
        text = (
            f"{block['color_emoji']} *{block['goal_area']}*  {block['duration_mins']} min\n"
            f"{block['task']}"
        )
        await bot.send_message(
            chat_id=telegram_id,
            text=text,
            parse_mode="Markdown",
            reply_markup=_block_keyboard(block["index"]),
        )
