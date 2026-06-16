"""
Unit tests for re-entry ritual gap detection.

detect_gap is the critical pure-logic function: it reads last_active_date
from the DB and returns the day count. All tests mock get_streak so no
supabase connection is needed.
Run with: pytest bot/tests/test_reentry.py
"""
from datetime import date, timedelta
from unittest.mock import patch

from app.services.reentry import detect_gap


def _make_streak(last_active: date | None) -> dict | None:
    if last_active is None:
        return None
    return {
        "current_streak": 3,
        "longest_streak": 10,
        "last_active_date": last_active.isoformat(),
    }


# ── No data → returns None ────────────────────────────────────────────────────

def test_detect_gap_returns_none_when_no_streak_row():
    with patch("app.db.streaks.get_streak", return_value=None):
        assert detect_gap("user-1") is None


def test_detect_gap_returns_none_when_last_active_missing():
    row_no_date = {"current_streak": 0, "longest_streak": 0, "last_active_date": None}
    with patch("app.db.streaks.get_streak", return_value=row_no_date):
        assert detect_gap("user-1") is None


# ── Gap values ────────────────────────────────────────────────────────────────

def test_detect_gap_zero_when_active_today():
    today = date.today()
    with patch("app.db.streaks.get_streak", return_value=_make_streak(today)):
        assert detect_gap("user-1") == 0


def test_detect_gap_one_when_active_yesterday():
    yesterday = date.today() - timedelta(days=1)
    with patch("app.db.streaks.get_streak", return_value=_make_streak(yesterday)):
        assert detect_gap("user-1") == 1


def test_detect_gap_three_triggers_reentry():
    three_days_ago = date.today() - timedelta(days=3)
    with patch("app.db.streaks.get_streak", return_value=_make_streak(three_days_ago)):
        gap = detect_gap("user-1")
    assert gap is not None and gap >= 3


def test_detect_gap_large_gap():
    long_ago = date.today() - timedelta(days=30)
    with patch("app.db.streaks.get_streak", return_value=_make_streak(long_ago)):
        assert detect_gap("user-1") == 30


# ── Scheduler routing (boundary) ─────────────────────────────────────────────

def test_gap_exactly_two_does_not_trigger_reentry():
    """Gap of 2 days should not trigger re-entry (threshold is ≥3)."""
    two_days_ago = date.today() - timedelta(days=2)
    with patch("app.db.streaks.get_streak", return_value=_make_streak(two_days_ago)):
        gap = detect_gap("user-1")
    assert gap is not None and gap < 3


def test_gap_exactly_three_triggers_reentry():
    """Gap of exactly 3 days is the boundary — must trigger re-entry."""
    three_days_ago = date.today() - timedelta(days=3)
    with patch("app.db.streaks.get_streak", return_value=_make_streak(three_days_ago)):
        gap = detect_gap("user-1")
    assert gap is not None and gap >= 3
