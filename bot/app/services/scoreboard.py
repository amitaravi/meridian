import logging
from datetime import date

from telegram import Bot

from app.db.logs import get_log_for_date
from app.db.profiles import get_profile_by_user_id
from app.db.streaks import get_streak

logger = logging.getLogger(__name__)

_CLOSINGS = [
    "Tomorrow, the brief arrives again. Show up for it.",
    "One day at a time. Today counted.",
    "This is how Path B gets built — one ticked block at a time.",
    "More than half. That's the job.",
    "You showed up. That counts.",
]


def _pick_closing(n_done: int, n_total: int) -> str:
    if n_total == 0:
        return "Tomorrow's brief is on its way."
    if n_done == n_total:
        return "All done. Tomorrow, do it again."
    if n_done >= n_total // 2:
        return "More than half. That's the job."
    if n_done > 0:
        return "You showed up. That counts."
    return "Tomorrow's brief is on its way."


def _build_message(profile: dict, log: dict, streak_row: dict | None) -> str:
    blocks: list[dict] = log.get("blocks") or []
    completed: list[int] = log.get("completed_block_indices") or []

    # Per-goal-area breakdown
    area_stats: dict[str, dict] = {}
    for block in blocks:
        area = block["goal_area"]
        emoji = block["color_emoji"]
        area_stats.setdefault(area, {"emoji": emoji, "total": 0, "done": 0})
        area_stats[area]["total"] += 1
        if block.get("index") in completed:
            area_stats[area]["done"] += 1

    n_done = len(completed)
    n_total = len(blocks)
    streak = streak_row["current_streak"] if streak_row else 0

    lines: list[str] = ["📊 *Today's summary*", ""]

    done_icon = "✅" if n_done == n_total and n_total > 0 else "○"
    lines.append(f"{done_icon} {n_done}/{n_total} blocks done")

    if area_stats:
        lines.append("")
        for area, s in area_stats.items():
            lines.append(f"{s['emoji']} {area}: {s['done']}/{s['total']}")

    lines.extend(["", f"🔥 {streak}-day streak", ""])
    lines.append(f"_{_pick_closing(n_done, n_total)}_")

    return "\n".join(lines)


async def send_scoreboard(user_id: str, telegram_id: int, bot: Bot) -> None:
    """Send the end-of-day scoreboard only if a brief was delivered today."""
    today = date.today().isoformat()

    log = get_log_for_date(user_id, today)
    if not log or not log.get("brief_sent_at"):
        logger.info("No brief delivered today for user=%s — skipping scoreboard", user_id)
        return

    profile = get_profile_by_user_id(user_id)
    if not profile:
        return

    streak_row = get_streak(user_id)
    message = _build_message(profile, log, streak_row)

    await bot.send_message(chat_id=telegram_id, text=message, parse_mode="Markdown")
    logger.info("Scoreboard sent to user=%s", user_id)
