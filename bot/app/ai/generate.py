import json
import logging
import re
from datetime import datetime

from app.ai.client import groq_client
from app.ai.prompts import BLOCKS_PROMPT, BRIEF_PROMPT, REENTRY_BLOCKS_PROMPT, REENTRY_PROMPT

logger = logging.getLogger(__name__)

MODEL = "llama-3.1-70b-versatile"


def _format_goal_areas(goal_areas: list[dict]) -> str:
    return "\n".join(
        f"- {a['name']} ({a['color_emoji']}): {a['description']} "
        f"[{a['weekly_hours']}h/week target]"
        for a in goal_areas
    )


def _format_accomplishments(accomplishments: list[str]) -> str:
    return "; ".join(accomplishments)


async def generate_narrative(
    profile: dict,
    framing_type: str,
    streak: int,
) -> str:
    """Call Groq to produce a 150–200 word contrast narrative."""
    prompt = BRIEF_PROMPT.format(
        path_a=profile["path_a"],
        path_b=profile["path_b"],
        accomplishments=_format_accomplishments(profile.get("accomplishments") or []),
        framing_type=framing_type,
        day_of_week=datetime.now().strftime("%A"),
        streak=streak,
    )
    response = await groq_client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=350,
        temperature=0.8,
    )
    return response.choices[0].message.content.strip()


def _format_weekly_hours(
    goal_areas: list[dict],
    weekly_hours_by_area: dict[str, float] | None,
) -> str:
    if not weekly_hours_by_area:
        return "No data yet this week."
    lines = []
    for area in goal_areas:
        worked = weekly_hours_by_area.get(area["name"], 0.0)
        target = area.get("weekly_hours", 0)
        status = "behind" if worked < target * 0.7 else "on track"
        lines.append(f"- {area['name']}: {worked}h / {target}h target ({status})")
    return "\n".join(lines) if lines else "No data yet this week."


async def generate_time_blocks(
    profile: dict,
    n: int = 3,
    weekly_hours_by_area: dict[str, float] | None = None,
) -> list[dict]:
    """Call Groq to produce n time blocks as a parsed list of dicts."""
    goal_areas = profile.get("goal_areas") or []
    prompt = BLOCKS_PROMPT.format(
        n=n,
        goal_areas_formatted=_format_goal_areas(goal_areas),
        weekly_hours_summary=_format_weekly_hours(goal_areas, weekly_hours_by_area),
        day_of_week=datetime.now().strftime("%A"),
    )
    response = await groq_client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=600,
        temperature=0.5,
    )
    raw = response.choices[0].message.content.strip()

    try:
        blocks = json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\[.*\]", raw, re.DOTALL)
        if not match:
            raise ValueError(f"Groq returned non-JSON blocks response: {raw[:200]}")
        blocks = json.loads(match.group())

    # Ensure indices are set correctly regardless of what the model returned
    for i, block in enumerate(blocks):
        block["index"] = i

    return blocks


async def generate_reentry_narrative(profile: dict, gap: int) -> str:
    """Short (~80-100 word) re-entry narrative that acknowledges the absence."""
    prompt = REENTRY_PROMPT.format(
        path_b=profile["path_b"],
        gap=gap,
    )
    response = await groq_client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()


async def generate_reentry_blocks(profile: dict, n: int = 1) -> list[dict]:
    """Generate n low-friction re-entry blocks (25 min each)."""
    # Sort goal areas by weekly_hours ascending so the easiest area is first
    goal_areas = sorted(
        profile.get("goal_areas") or [],
        key=lambda a: a.get("weekly_hours", 99),
    )
    reentry_profile = {**profile, "goal_areas": goal_areas}

    prompt = REENTRY_BLOCKS_PROMPT.format(
        n=n,
        goal_areas_formatted=_format_goal_areas(reentry_profile["goal_areas"]),
    )
    response = await groq_client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0.4,
    )
    raw = response.choices[0].message.content.strip()

    try:
        blocks = json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\[.*\]", raw, re.DOTALL)
        if not match:
            raise ValueError(f"Groq returned non-JSON re-entry blocks: {raw[:200]}")
        blocks = json.loads(match.group())

    for i, block in enumerate(blocks):
        block["index"] = i
        block["duration_mins"] = 25  # enforce 25 min on re-entry regardless of model output

    return blocks
