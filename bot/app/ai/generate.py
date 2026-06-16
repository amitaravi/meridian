import json
import logging
import re
from datetime import datetime

from app.ai.client import groq_client
from app.ai.prompts import BLOCKS_PROMPT, BRIEF_PROMPT

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


async def generate_time_blocks(profile: dict, n: int = 3) -> list[dict]:
    """Call Groq to produce n time blocks as a parsed list of dicts."""
    prompt = BLOCKS_PROMPT.format(
        n=n,
        goal_areas_formatted=_format_goal_areas(profile.get("goal_areas") or []),
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
