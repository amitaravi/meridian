"""
Unit tests for streak calculation logic.

Tests the pure calculate_new_streak() function in isolation — no DB or
Telegram calls. Run with: pytest bot/tests/test_streak.py
"""
from datetime import date

from app.services.streak import calculate_new_streak


# ── First completion ──────────────────────────────────────────────────────────

def test_first_completion_returns_1():
    result = calculate_new_streak(current=0, last_active=None, today=date(2026, 6, 16))
    assert result == 1


def test_first_completion_ignores_current_value():
    # Even if somehow current > 0 with no last_active, treat it as a fresh start
    result = calculate_new_streak(current=5, last_active=None, today=date(2026, 6, 16))
    assert result == 1


# ── Consecutive day ───────────────────────────────────────────────────────────

def test_consecutive_day_increments_streak():
    result = calculate_new_streak(
        current=5,
        last_active=date(2026, 6, 15),
        today=date(2026, 6, 16),
    )
    assert result == 6


def test_consecutive_day_from_1():
    result = calculate_new_streak(
        current=1,
        last_active=date(2026, 6, 15),
        today=date(2026, 6, 16),
    )
    assert result == 2


# ── Same day (idempotent) ─────────────────────────────────────────────────────

def test_same_day_no_change():
    result = calculate_new_streak(
        current=5,
        last_active=date(2026, 6, 16),
        today=date(2026, 6, 16),
    )
    assert result == 5


def test_same_day_does_not_inflate_streak():
    result = calculate_new_streak(
        current=10,
        last_active=date(2026, 6, 16),
        today=date(2026, 6, 16),
    )
    assert result == 10


# ── Gap resets to 1 ──────────────────────────────────────────────────────────

def test_gap_resets_streak():
    result = calculate_new_streak(
        current=5,
        last_active=date(2026, 6, 10),
        today=date(2026, 6, 16),
    )
    assert result == 1


def test_two_day_gap_resets_streak():
    result = calculate_new_streak(
        current=3,
        last_active=date(2026, 6, 14),
        today=date(2026, 6, 16),
    )
    assert result == 1


def test_exactly_one_day_gap_is_consecutive():
    # last_active yesterday → consecutive, should increment not reset
    result = calculate_new_streak(
        current=7,
        last_active=date(2026, 6, 15),
        today=date(2026, 6, 16),
    )
    assert result == 8


def test_large_gap_still_resets_to_1():
    result = calculate_new_streak(
        current=100,
        last_active=date(2026, 1, 1),
        today=date(2026, 6, 16),
    )
    assert result == 1
