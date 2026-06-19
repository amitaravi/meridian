import logging
from datetime import date

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

from app.ai.generate import generate_narrative
from app.db.logs import create_log, get_latest_log
from app.db.profiles import get_profile_by_user_id
from app.db.streaks import get_streak
from app.services.blocks import generate_blocks

logger = logging.getLogger(__name__)

FRAMING_SEQUENCE = ["fear", "aspiration", "accomplishment", "urgency"]

# Fallback brief for demo/testing when AI generation fails
FALLBACK_NARRATIVE = """\
You woke up today with a choice. Right now, two paths diverge.

Path A is comfortable: same body, same energy level, another day where you're just getting by. Facing the same health struggles, the same low energy that makes it hard to focus on anything that matters. A year from now, you'll wish you'd started today.

Path B is within reach: a stronger body, the energy to show up for your goals and your family every single day. You've done this before—six months of consistent strength training proved you have it in you. Today is the day you become that person again.

You don't need to be perfect today. You need to be present. One strong decision at 16:18, and you're back on the path.
"""

FALLBACK_BLOCKS = [
    {
        "index": 0,
        "goal_area": "Fitness",
        "color_emoji": "🟦",
        "task": "Complete a 50-minute full-body strength session: 5 min warm-up, 40 min compound lifts (squats, bench, rows), 5 min cool-down.",
        "duration_mins": 50,
    },
    {
        "index": 1,
        "goal_area": "Fitness",
        "color_emoji": "🟦",
        "task": "Prepare and consume a protein-rich recovery meal. Focus on hydration and one source of lean protein.",
        "duration_mins": 25,
    },
    {
        "index": 2,
        "goal_area": "Fitness",
        "color_emoji": "🟦",
        "task": "Foam roll major muscle groups (legs, back, shoulders) for 10 minutes, then plan tomorrow's session.",
        "duration_mins": 25,
    },
]


def _block_keyboard(block_index: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✓ Done", callback_data=f"done:{block_index}"),
        InlineKeyboardButton("→ Skip", callback_data=f"skip:{block_index}"),
    ]])


def _next_framing(last_log: dict | None) -> str:
    if not last_log:
        return "fear"
    try:
        idx = FRAMING_SEQUENCE.index(last_log["framing_type"])
        return FRAMING_SEQUENCE[(idx + 1) % len(FRAMING_SEQUENCE)]
    except (ValueError, KeyError):
        return "fear"


async def send_fallback_brief(user_id: str, telegram_id: int, bot: Bot) -> None:
    """Send a static fallback brief when AI generation fails. Good for demos."""
    today = date.today().isoformat()
    last_log = get_latest_log(user_id)
    framing_type = _next_framing(last_log)

    create_log(user_id, today, FALLBACK_BLOCKS, framing_type)
    logger.info(
        "Fallback brief sent for user=%s (demo mode)",
        user_id,
    )

    await bot.send_message(chat_id=telegram_id, text=FALLBACK_NARRATIVE)

    for block in FALLBACK_BLOCKS:
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

    try:
        narrative = await generate_narrative(profile, framing_type, current_streak)
        blocks = await generate_blocks(user_id, n=3)

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
    except Exception as e:
        logger.warning(
            "AI generation failed for user=%s, falling back to static brief: %s",
            user_id, e
        )
        await send_fallback_brief(user_id, telegram_id, bot)
