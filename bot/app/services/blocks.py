"""
Service-level block generation.

generate_blocks(user_id, n) is the public API used by brief.py and the
manual CLI. It fetches the user's profile, this-week's completion data,
and available hours window, then delegates to the AI layer.
"""
import logging

from app.ai.generate import generate_time_blocks
from app.db.logs import get_weekly_hours_by_area
from app.db.profiles import get_profile_by_user_id

logger = logging.getLogger(__name__)

_DEFAULT_END_HOUR = 22


def _available_window(profile: dict) -> tuple[str, str]:
    """Derive the user's available work window from their brief delivery time.

    Start = the moment the brief arrives (user is awake and ready).
    End   = 22:00 local time (hardcoded for V1; no separate field in schema).
    """
    hour = profile.get("brief_hour", 7)
    minute = profile.get("brief_minute", 0)
    return f"{hour:02d}:{minute:02d}", f"{_DEFAULT_END_HOUR:02d}:00"


async def generate_blocks(user_id: str, n: int = 3) -> list[dict]:
    """
    Fetch profile + weekly context + available window, then call Groq for n blocks.

    Goal areas behind on their weekly target are flagged for prioritisation.
    Only blocks that fit within the user's available hours window are requested.
    n defaults to 3; pass 1 for re-entry scenarios.
    """
    profile = get_profile_by_user_id(user_id)
    if not profile:
        raise ValueError(f"No profile found for user_id={user_id}")

    weekly_hours = get_weekly_hours_by_area(user_id)
    start_time, end_time = _available_window(profile)

    logger.debug(
        "Generating %d blocks for user=%s window=%s–%s",
        n, user_id, start_time, end_time,
    )

    return await generate_time_blocks(
        profile,
        n=n,
        weekly_hours_by_area=weekly_hours,
        start_time=start_time,
        end_time=end_time,
    )
