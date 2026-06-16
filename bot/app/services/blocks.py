"""
Service-level block generation.

generate_blocks(user_id, n) is the public API used by brief.py and the
manual CLI. It fetches the user's profile and this-week's completion data,
then delegates to the AI layer.
"""
import logging

from app.ai.generate import generate_time_blocks
from app.db.logs import get_weekly_hours_by_area
from app.db.profiles import get_profile_by_user_id

logger = logging.getLogger(__name__)


async def generate_blocks(user_id: str, n: int = 3) -> list[dict]:
    """
    Fetch profile + weekly context, then call Groq for n time blocks.

    Goal areas behind on their weekly target are flagged in the prompt
    so Groq can prioritise them. n defaults to 3; pass 1 for re-entry.
    """
    profile = get_profile_by_user_id(user_id)
    if not profile:
        raise ValueError(f"No profile found for user_id={user_id}")

    weekly_hours = get_weekly_hours_by_area(user_id)
    logger.debug("Weekly hours for user=%s: %s", user_id, weekly_hours)

    return await generate_time_blocks(profile, n=n, weekly_hours_by_area=weekly_hours)
