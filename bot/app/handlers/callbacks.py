import logging
from datetime import date

from telegram import Update
from telegram.ext import ContextTypes

from app.db.logs import append_completed_block, append_skipped_block, get_log_for_date
from app.db.users import get_user_by_telegram_id
from app.services.streak import handle_block_completion

logger = logging.getLogger(__name__)


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    assert query is not None
    assert query.from_user is not None

    await query.answer()  # always answer first — removes loading spinner

    try:
        action, block_index_str = query.data.split(":")
        block_index = int(block_index_str)
    except (ValueError, AttributeError):
        logger.warning("Unexpected callback_data: %s", query.data)
        return

    telegram_id = query.from_user.id
    today = date.today().isoformat()

    try:
        user = get_user_by_telegram_id(telegram_id)
        if not user:
            await query.answer("Could not find your account.")
            return

        user_id: str = user["id"]
        log = get_log_for_date(user_id, today)
        block = _find_block(log, block_index)

        if action == "done":
            append_completed_block(user_id, today, block_index)
            new_streak = handle_block_completion(user_id)

            updated_log = get_log_for_date(user_id, today)
            n_done = len(updated_log.get("completed_block_indices") or []) if updated_log else 0
            n_total = len(updated_log.get("blocks") or []) if updated_log else 0

            area = block["goal_area"] if block else f"Block {block_index + 1}"
            emoji = block["color_emoji"] if block else "✓"
            await query.edit_message_text(
                f"{emoji} *{area}* — done ✓\n"
                f"_{n_done}/{n_total} today · {new_streak} day streak_",
                parse_mode="Markdown",
            )

        elif action == "skip":
            append_skipped_block(user_id, today, block_index)
            area = block["goal_area"] if block else f"Block {block_index + 1}"
            emoji = block["color_emoji"] if block else "→"
            await query.edit_message_text(
                f"{emoji} ~~{area}~~ — skipped",
            )

    except Exception as e:
        logger.error("Callback error for telegram_id=%d: %s", telegram_id, e, exc_info=True)


def _find_block(log: dict | None, block_index: int) -> dict | None:
    if not log:
        return None
    blocks: list[dict] = log.get("blocks") or []
    return next((b for b in blocks if b.get("index") == block_index), None)
