import logging

from app.db.client import get_supabase

logger = logging.getLogger(__name__)


def get_profile_by_telegram_id(telegram_id: int) -> dict | None:
    """Return the profile for this telegram_id, or None if not onboarded."""
    supabase = get_supabase()
    result = (
        supabase.table("users")
        .select("id, profiles(*)")
        .eq("telegram_id", telegram_id)
        .execute()
    )
    if not result.data:
        return None
    profiles = result.data[0].get("profiles") or []
    return profiles[0] if profiles else None


def get_profile_by_user_id(user_id: str) -> dict | None:
    """Return the profile for this internal user_id, or None."""
    supabase = get_supabase()
    result = (
        supabase.table("profiles")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )
    return result.data[0] if result.data else None
