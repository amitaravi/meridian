import logging
from datetime import date, timedelta

logger = logging.getLogger(__name__)


def calculate_new_streak(
    current: int,
    last_active: date | None,
    today: date,
) -> int:
    """Pure function — returns the new streak value given current state.

    Rules:
    - No previous activity → start at 1
    - Already counted today → no change
    - Yesterday → increment
    - Any larger gap → reset to 1
    """
    if last_active is None:
        return 1
    if last_active == today:
        return current
    if last_active == today - timedelta(days=1):
        return current + 1
    return 1


def handle_block_completion(user_id: str) -> int:
    """Update streak for today's first completion; return new streak value."""
    # Imported here so that importing calculate_new_streak alone (e.g. in tests)
    # does not pull in the supabase dependency chain.
    from app.db.streaks import get_streak, upsert_streak

    today = date.today()
    row = get_streak(user_id)

    current = row["current_streak"] if row else 0
    longest = row["longest_streak"] if row else 0
    last_active_str: str | None = row["last_active_date"] if row else None
    last_active = date.fromisoformat(last_active_str) if last_active_str else None

    new_streak = calculate_new_streak(current, last_active, today)
    new_longest = max(new_streak, longest)

    upsert_streak(user_id, new_streak, new_longest, today)
    return new_streak
