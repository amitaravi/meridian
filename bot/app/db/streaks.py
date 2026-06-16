import logging
from datetime import date

from app.db.client import get_supabase

logger = logging.getLogger(__name__)


def get_streak(user_id: str) -> dict | None:
    """Return the streak row for this user, or None."""
    supabase = get_supabase()
    result = (
        supabase.table("streaks")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )
    return result.data[0] if result.data else None


def upsert_streak(
    user_id: str,
    current_streak: int,
    longest_streak: int,
    last_active_date: date,
) -> None:
    """Create or update the streak row for this user."""
    supabase = get_supabase()
    supabase.table("streaks").upsert({
        "user_id": user_id,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "last_active_date": last_active_date.isoformat(),
    }).execute()
