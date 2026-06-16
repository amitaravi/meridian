"""
Unit tests for block generation service.

Mocks Supabase and Groq — no real API calls are made.
Run with: pytest bot/tests/test_blocks.py
"""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.blocks import _available_window, generate_blocks


# ── Fixtures ──────────────────────────────────────────────────────────────────

PROFILE = {
    "user_id": "abc-123",
    "brief_hour": 7,
    "brief_minute": 0,
    "goal_areas": [
        {"name": "Career Transition", "color_emoji": "🟦", "description": "Pivot to startups", "weekly_hours": 10},
        {"name": "Side Project",      "color_emoji": "🟩", "description": "Build Meridian",    "weekly_hours": 5},
    ],
    "path_a": "Still at the bank at 34.",
    "path_b": "Shipped the product.",
    "accomplishments": ["Topped school exams"],
    "why_text": "Want to build.",
    "timezone": "Asia/Kolkata",
}

BLOCKS_JSON = '[{"index":0,"goal_area":"Career Transition","color_emoji":"🟦","task":"Write 3 LinkedIn bullets.","duration_mins":25}]'


# ── _available_window ─────────────────────────────────────────────────────────

def test_available_window_derives_from_brief_hour():
    start, end = _available_window({"brief_hour": 6, "brief_minute": 30})
    assert start == "06:30"
    assert end == "22:00"


def test_available_window_zero_padding():
    start, end = _available_window({"brief_hour": 7, "brief_minute": 0})
    assert start == "07:00"


def test_available_window_defaults_when_fields_missing():
    start, end = _available_window({})
    assert start == "07:00"
    assert end == "22:00"


# ── generate_blocks ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_generate_blocks_passes_window_to_groq():
    """start_time and end_time derived from brief_hour must reach the Groq prompt."""
    mock_choice = MagicMock()
    mock_choice.message.content = BLOCKS_JSON

    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    with (
        patch("app.services.blocks.get_profile_by_user_id", return_value=PROFILE),
        patch("app.services.blocks.get_weekly_hours_by_area", return_value={}),
        patch("app.ai.generate.groq_client") as mock_groq,
    ):
        mock_groq.chat.completions.create = AsyncMock(return_value=mock_response)
        blocks = await generate_blocks("abc-123", n=1)

    assert len(blocks) == 1
    # Verify the prompt sent to Groq contained the correct window
    call_kwargs = mock_groq.chat.completions.create.call_args
    prompt_sent = call_kwargs[1]["messages"][0]["content"]
    assert "07:00" in prompt_sent
    assert "22:00" in prompt_sent


@pytest.mark.asyncio
async def test_generate_blocks_marks_behind_areas():
    """Areas behind on weekly target should be flagged as 'behind' in the prompt."""
    mock_choice = MagicMock()
    mock_choice.message.content = BLOCKS_JSON
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    # Career Transition: 1h worked out of 10h target → behind
    # Side Project: 4.5h worked out of 5h target → on track
    weekly = {"Career Transition": 1.0, "Side Project": 4.5}

    with (
        patch("app.services.blocks.get_profile_by_user_id", return_value=PROFILE),
        patch("app.services.blocks.get_weekly_hours_by_area", return_value=weekly),
        patch("app.ai.generate.groq_client") as mock_groq,
    ):
        mock_groq.chat.completions.create = AsyncMock(return_value=mock_response)
        await generate_blocks("abc-123", n=1)

    prompt_sent = mock_groq.chat.completions.create.call_args[1]["messages"][0]["content"]
    assert "behind" in prompt_sent
    assert "on track" in prompt_sent


@pytest.mark.asyncio
async def test_generate_blocks_normalises_indices():
    """Block indices must always be 0-based regardless of what Groq returns."""
    scrambled = '[{"index":5,"goal_area":"Side Project","color_emoji":"🟩","task":"Do X.","duration_mins":25}]'
    mock_choice = MagicMock()
    mock_choice.message.content = scrambled
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    with (
        patch("app.services.blocks.get_profile_by_user_id", return_value=PROFILE),
        patch("app.services.blocks.get_weekly_hours_by_area", return_value={}),
        patch("app.ai.generate.groq_client") as mock_groq,
    ):
        mock_groq.chat.completions.create = AsyncMock(return_value=mock_response)
        blocks = await generate_blocks("abc-123", n=1)

    assert blocks[0]["index"] == 0


@pytest.mark.asyncio
async def test_generate_blocks_raises_on_missing_profile():
    with patch("app.services.blocks.get_profile_by_user_id", return_value=None):
        with pytest.raises(ValueError, match="No profile found"):
            await generate_blocks("missing-user")


@pytest.mark.asyncio
async def test_generate_blocks_json_fallback_parsing():
    """Should extract JSON from a response wrapped in markdown fences."""
    wrapped = '```json\n[{"index":0,"goal_area":"Career Transition","color_emoji":"🟦","task":"Write.","duration_mins":50}]\n```'
    mock_choice = MagicMock()
    mock_choice.message.content = wrapped
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    with (
        patch("app.services.blocks.get_profile_by_user_id", return_value=PROFILE),
        patch("app.services.blocks.get_weekly_hours_by_area", return_value={}),
        patch("app.ai.generate.groq_client") as mock_groq,
    ):
        mock_groq.chat.completions.create = AsyncMock(return_value=mock_response)
        blocks = await generate_blocks("abc-123", n=1)

    assert blocks[0]["goal_area"] == "Career Transition"
