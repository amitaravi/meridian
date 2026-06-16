import logging
from datetime import date

from telegram import Bot

logger = logging.getLogger(__name__)


def detect_gap(user_id: str) -> int | None:
    """Return days since last_active_date, or None if no streak row exists.

    Imported lazily so detect_gap is testable without supabase.
    """
    from app.db.streaks import get_streak

    streak_row = get_streak(user_id)
    if not streak_row or not streak_row.get("last_active_date"):
        return None
    last_active = date.fromisoformat(streak_row["last_active_date"])
    return (date.today() - last_active).days


async def send_reentry_brief(user_id: str, telegram_id: int, bot: Bot) -> None:
    """Send a shorter, acknowledgement-first brief after a 3+ day gap."""
    from app.ai.generate import generate_reentry_blocks, generate_reentry_narrative
    from app.db.logs import create_log, get_latest_log
    from app.db.profiles import get_profile_by_user_id
    from app.services.brief import _block_keyboard, _next_framing

    profile = get_profile_by_user_id(user_id)
    if not profile:
        logger.warning("send_reentry_brief: no profile for user_id=%s", user_id)
        return

    gap = detect_gap(user_id) or 3
    today = date.today().isoformat()
    last_log = get_latest_log(user_id)
    framing_type = _next_framing(last_log)

    narrative = await generate_reentry_narrative(profile, gap)
    blocks = await generate_reentry_blocks(profile, n=1)

    create_log(user_id, today, blocks, framing_type)
    logger.info("Re-entry brief sent for user=%s (gap=%d days)", user_id, gap)

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
