"""
Unit tests for the end-of-day scoreboard message.

_build_message and _pick_closing are pure functions — no mocking needed.
send_scoreboard tests mock the DB layer.
Run with: pytest bot/tests/test_scoreboard.py
"""
from unittest.mock import AsyncMock, patch

import pytest

from app.services.scoreboard import _build_message, _pick_closing, send_scoreboard


# ── Fixtures ──────────────────────────────────────────────────────────────────

PROFILE = {
    "goal_areas": [
        {"name": "Career Transition", "color_emoji": "🟦", "weekly_hours": 10},
        {"name": "Side Project",      "color_emoji": "🟩", "weekly_hours": 5},
    ]
}

BLOCKS = [
    {"index": 0, "goal_area": "Career Transition", "color_emoji": "🟦", "duration_mins": 50},
    {"index": 1, "goal_area": "Side Project",      "color_emoji": "🟩", "duration_mins": 25},
    {"index": 2, "goal_area": "Career Transition", "color_emoji": "🟦", "duration_mins": 25},
]

STREAK_ROW = {"current_streak": 7, "longest_streak": 14}


# ── _pick_closing ─────────────────────────────────────────────────────────────

def test_pick_closing_all_done():
    assert _pick_closing(3, 3) == "All done. Tomorrow, do it again."

def test_pick_closing_majority_done():
    # 2/3 is strictly more than half (2*2=4 > 3)
    assert _pick_closing(2, 3) == "More than half. That's the job."

def test_pick_closing_minority_done():
    # 1/3 is NOT more than half (1*2=2 < 3)
    assert _pick_closing(1, 3) == "You showed up. That counts."

def test_pick_closing_exactly_half():
    # 1/2 is NOT strictly more than half
    assert _pick_closing(1, 2) == "You showed up. That counts."

def test_pick_closing_zero_done():
    assert _pick_closing(0, 3) == "Tomorrow's brief is on its way."

def test_pick_closing_no_blocks():
    assert _pick_closing(0, 0) == "Tomorrow's brief is on its way."


# ── _build_message — header and counts ───────────────────────────────────────

def test_build_message_all_done_uses_checkmark():
    log = {"blocks": BLOCKS, "completed_block_indices": [0, 1, 2]}
    msg = _build_message(PROFILE, log, STREAK_ROW)
    assert "✅ 3/3 blocks done" in msg

def test_build_message_partial_uses_circle():
    log = {"blocks": BLOCKS, "completed_block_indices": [0]}
    msg = _build_message(PROFILE, log, STREAK_ROW)
    assert "○ 1/3 blocks done" in msg

def test_build_message_zero_done():
    log = {"blocks": BLOCKS, "completed_block_indices": []}
    msg = _build_message(PROFILE, log, STREAK_ROW)
    assert "○ 0/3 blocks done" in msg


# ── _build_message — per-goal-area breakdown ─────────────────────────────────

def test_build_message_area_breakdown_correct():
    # blocks 0 and 2 are Career Transition; only block 0 completed
    log = {"blocks": BLOCKS, "completed_block_indices": [0]}
    msg = _build_message(PROFILE, log, STREAK_ROW)
    assert "🟦 Career Transition: 1/2" in msg
    assert "🟩 Side Project: 0/1" in msg

def test_build_message_all_areas_complete():
    log = {"blocks": BLOCKS, "completed_block_indices": [0, 1, 2]}
    msg = _build_message(PROFILE, log, STREAK_ROW)
    assert "🟦 Career Transition: 2/2" in msg
    assert "🟩 Side Project: 1/1" in msg


# ── _build_message — streak ───────────────────────────────────────────────────

def test_build_message_shows_streak():
    log = {"blocks": BLOCKS, "completed_block_indices": [0]}
    msg = _build_message(PROFILE, log, STREAK_ROW)
    assert "🔥 7-day streak" in msg

def test_build_message_zero_streak_when_no_row():
    log = {"blocks": BLOCKS, "completed_block_indices": [0]}
    msg = _build_message(PROFILE, log, streak_row=None)
    assert "🔥 0-day streak" in msg


# ── send_scoreboard — skip conditions ────────────────────────────────────────

@pytest.mark.asyncio
async def test_send_scoreboard_skips_when_no_log():
    mock_bot = AsyncMock()
    with patch("app.db.logs.get_log_for_date", return_value=None):
        await send_scoreboard("uid", 123, mock_bot)
    mock_bot.send_message.assert_not_called()


@pytest.mark.asyncio
async def test_send_scoreboard_skips_when_no_brief_sent_at():
    """Log exists but no brief_sent_at means the brief wasn't delivered today."""
    mock_bot = AsyncMock()
    log_no_brief = {"blocks": BLOCKS, "completed_block_indices": [], "brief_sent_at": None}
    with (
        patch("app.db.logs.get_log_for_date", return_value=log_no_brief),
        patch("app.db.profiles.get_profile_by_user_id", return_value=PROFILE),
        patch("app.db.streaks.get_streak", return_value=STREAK_ROW),
    ):
        await send_scoreboard("uid", 123, mock_bot)
    mock_bot.send_message.assert_not_called()


@pytest.mark.asyncio
async def test_send_scoreboard_sends_when_brief_delivered():
    """Brief was delivered → scoreboard message should be sent."""
    mock_bot = AsyncMock()
    log_with_brief = {
        "blocks": BLOCKS,
        "completed_block_indices": [0],
        "brief_sent_at": "2026-06-16T07:00:00+00:00",
    }
    with (
        patch("app.db.logs.get_log_for_date", return_value=log_with_brief),
        patch("app.db.profiles.get_profile_by_user_id", return_value=PROFILE),
        patch("app.db.streaks.get_streak", return_value=STREAK_ROW),
    ):
        await send_scoreboard("uid", 123, mock_bot)
    mock_bot.send_message.assert_called_once()
    assert "📊" in mock_bot.send_message.call_args[1]["text"]
