"""
Unit tests for scheduler job management.

Tests ensure_user_job idempotency — no DB or APScheduler daemon needed.
Run with: pytest bot/tests/test_scheduler.py
"""
from unittest.mock import MagicMock, patch

import app.services.scheduler as sched

PROFILE = {
    "brief_hour": 7,
    "brief_minute": 0,
    "timezone": "Asia/Kolkata",
}


def _mock_bot():
    """Set a fake bot so register functions don't assert-fail."""
    sched._bot = MagicMock()


def _clear_bot():
    sched._bot = None


# ── ensure_user_job — no existing job ────────────────────────────────────────

def test_ensure_registers_all_three_jobs_when_none_exist():
    _mock_bot()
    mock_scheduler = MagicMock()
    mock_scheduler.get_job.return_value = None  # brief job not scheduled yet

    with patch.object(sched, "_scheduler", mock_scheduler):
        sched.ensure_user_job("user-1", 111, PROFILE)

    # brief + evening scoreboard + weekly = 3 add_job calls
    assert mock_scheduler.add_job.call_count == 3
    _clear_bot()


def test_ensure_checks_brief_job_id():
    _mock_bot()
    mock_scheduler = MagicMock()
    mock_scheduler.get_job.return_value = None

    with patch.object(sched, "_scheduler", mock_scheduler):
        sched.ensure_user_job("user-abc", 222, PROFILE)

    mock_scheduler.get_job.assert_called_once_with("brief_user-abc")
    _clear_bot()


# ── ensure_user_job — job already exists (idempotent) ────────────────────────

def test_ensure_noop_when_brief_job_already_scheduled():
    _mock_bot()
    mock_scheduler = MagicMock()
    mock_scheduler.get_job.return_value = MagicMock()  # job exists

    with patch.object(sched, "_scheduler", mock_scheduler):
        sched.ensure_user_job("user-1", 111, PROFILE)

    mock_scheduler.add_job.assert_not_called()
    _clear_bot()


def test_ensure_safe_to_call_twice():
    """Second call must not duplicate jobs."""
    _mock_bot()
    mock_scheduler = MagicMock()
    # First call: no job. Second call: job exists.
    mock_scheduler.get_job.side_effect = [None, MagicMock()]

    with patch.object(sched, "_scheduler", mock_scheduler):
        sched.ensure_user_job("user-1", 111, PROFILE)  # registers
        sched.ensure_user_job("user-1", 111, PROFILE)  # no-op

    assert mock_scheduler.add_job.call_count == 3  # only from first call
    _clear_bot()


# ── remove_user_job ───────────────────────────────────────────────────────────

def test_remove_clears_all_three_job_ids():
    mock_scheduler = MagicMock()
    mock_scheduler.get_job.return_value = MagicMock()  # all jobs exist

    with patch.object(sched, "_scheduler", mock_scheduler):
        sched.remove_user_job("user-1")

    removed = [call.args[0] for call in mock_scheduler.remove_job.call_args_list]
    assert "brief_user-1" in removed
    assert "scoreboard_user-1" in removed
    assert "weekly_user-1" in removed


def test_remove_skips_missing_jobs():
    mock_scheduler = MagicMock()
    mock_scheduler.get_job.return_value = None  # no jobs exist

    with patch.object(sched, "_scheduler", mock_scheduler):
        sched.remove_user_job("user-1")

    mock_scheduler.remove_job.assert_not_called()
