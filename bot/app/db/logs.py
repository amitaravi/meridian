import logging
from datetime import datetime, timezone

from app.db.client import get_supabase

logger = logging.getLogger(__name__)


def get_latest_log(user_id: str) -> dict | None:
    """Return the most recent daily_log row for this user, or None."""
    supabase = get_supabase()
    result = (
        supabase.table("daily_logs")
        .select("*")
        .eq("user_id", user_id)
        .order("date", desc=True)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


def get_log_for_date(user_id: str, date: str) -> dict | None:
    """Return the daily_log row for a specific date (YYYY-MM-DD), or None."""
    supabase = get_supabase()
    result = (
        supabase.table("daily_logs")
        .select("*")
        .eq("user_id", user_id)
        .eq("date", date)
        .execute()
    )
    return result.data[0] if result.data else None


def create_log(
    user_id: str,
    date: str,
    blocks: list[dict],
    framing_type: str,
) -> dict:
    """Insert a new daily_log row and return it."""
    supabase = get_supabase()
    result = (
        supabase.table("daily_logs")
        .insert({
            "user_id": user_id,
            "date": date,
            "blocks": blocks,
            "framing_type": framing_type,
            "brief_sent_at": datetime.now(timezone.utc).isoformat(),
        })
        .execute()
    )
    return result.data[0]


def append_completed_block(user_id: str, date: str, block_index: int) -> None:
    """Add block_index to completed_block_indices if not already present."""
    supabase = get_supabase()
    log = get_log_for_date(user_id, date)
    if not log:
        logger.warning("No log found for user=%s date=%s", user_id, date)
        return
    current: list[int] = log.get("completed_block_indices") or []
    if block_index not in current:
        current.append(block_index)
        supabase.table("daily_logs").update(
            {"completed_block_indices": current}
        ).eq("user_id", user_id).eq("date", date).execute()


def append_skipped_block(user_id: str, date: str, block_index: int) -> None:
    """Add block_index to skipped_block_indices if not already present."""
    supabase = get_supabase()
    log = get_log_for_date(user_id, date)
    if not log:
        logger.warning("No log found for user=%s date=%s", user_id, date)
        return
    current: list[int] = log.get("skipped_block_indices") or []
    if block_index not in current:
        current.append(block_index)
        supabase.table("daily_logs").update(
            {"skipped_block_indices": current}
        ).eq("user_id", user_id).eq("date", date).execute()
