import logging

from app.db.client import get_supabase

logger = logging.getLogger(__name__)


def create_user_if_not_exists(telegram_id: int) -> dict:
    """Upsert a user row by telegram_id and return it."""
    supabase = get_supabase()
    result = (
        supabase.table("users")
        .upsert({"telegram_id": telegram_id}, on_conflict="telegram_id")
        .execute()
    )
    return result.data[0]


def get_user_by_telegram_id(telegram_id: int) -> dict | None:
    """Return the user row for this telegram_id, or None if not found."""
    supabase = get_supabase()
    result = (
        supabase.table("users")
        .select("*")
        .eq("telegram_id", telegram_id)
        .execute()
    )
    return result.data[0] if result.data else None


def get_user_by_id(user_id: str) -> dict | None:
    """Return the user row for this internal UUID, or None."""
    supabase = get_supabase()
    result = (
        supabase.table("users")
        .select("*")
        .eq("id", user_id)
        .execute()
    )
    return result.data[0] if result.data else None
def normalize_user(user):
    profiles = user.get("profiles")

    # CASE 1: Supabase returns list (sometimes happens with joins)
    if isinstance(profiles, list):
        profiles = profiles[0] if len(profiles) > 0 else None

    # CASE 2: already dict → keep as is
    user["profiles"] = profiles
    return user

def get_all_active_users_with_profiles() -> list[dict]:
    """Return all active users that have a completed profile."""
    supabase = get_supabase()

    result = (
        supabase.table("users")
        .select("id, telegram_id, profiles(*)")
        .eq("is_active", True)
        .execute()
    )

    users = result.data or []

    normalized_users = []

    for u in users:
        profiles = u.get("profiles")

        # normalize Supabase join shape
        if isinstance(profiles, list):
            profiles = profiles[0] if len(profiles) > 0 else None

        u["profiles"] = profiles

        # keep only users with valid profile
        if profiles:
            normalized_users.append(u)

    return normalized_users

def set_user_active(telegram_id: int, *, active: bool) -> None:
    """Set is_active for a user (used by /pause and /resume)."""
    supabase = get_supabase()
    supabase.table("users").update({"is_active": active}).eq(
        "telegram_id", telegram_id
    ).execute()
