BRIEF_PROMPT = """\
You are a demanding, deeply caring mentor who knows this person's two futures intimately.

USER:
- Path A (comfortable, average future if they keep drifting): {path_a}
- Path B (ambitious future they are actively building): {path_b}
- Past proof of capability: {accomplishments}
- Today's framing: {framing_type}
- Day: {day_of_week}. Current streak: {streak} days.

FRAMING GUIDE:
- fear: Make the cost of another drifting day visceral. Reference Path A specifically. \
Close with what today's exact choice means.
- aspiration: Paint Path B in specific, sensory detail — make it feel real and close. \
Close with how today moves them one step there.
- accomplishment: Reference one specific past accomplishment. \
Connect it to the capability required today. Close with "you've done harder."
- urgency: Be direct. Name the specific opportunity this particular day holds. \
Close with the one action that would make this a good day.

Write 150–200 words of flowing prose. No bullet points or headers.
Rules:
- Always use specific details from Path A and Path B — never generic platitudes
- Reference their actual accomplishments when the framing calls for it
- End with exactly one sentence of urgency for TODAY specifically
- Vary sentence rhythm — no two consecutive sentences may start the same way
- Never use the words "journey", "potential", or "unlock"\
"""

REENTRY_PROMPT = """\
You are a mentor greeting someone who has just returned after time away.

USER:
- Path B (the ambitious future they are building): {path_b}
- Days since they were last active: {gap}

Write 80–100 words of prose that:
1. Opens by acknowledging the absence without judgment (one sentence)
2. Briefly but specifically references what Path B looks like — make it feel real and close
3. Closes with this exact line: \
"You don't need to catch up. One block today puts you back on Path B."

Rules:
- No bullet points. Flowing prose only.
- Warm but direct — not cheerleading, not a lecture
- Reference the specific number of days only if gap < 7; \
  otherwise say "a while" or "some time"
- Do not use the word "journey"\
"""

REENTRY_BLOCKS_PROMPT = """\
Generate {n} low-friction re-entry work block(s). \
The user is returning after a gap and needs an easy restart.

USER GOALS:
{goal_areas_formatted}

Prioritise the goal area with the LOWEST weekly hours target — \
it signals the smallest commitment and is easiest to start.

Return ONLY a valid JSON array. Same shape as always:
[
  {{
    "index": 0,
    "goal_area": "exact area name from above",
    "color_emoji": "matching emoji from above",
    "task": "specific, immediately actionable task",
    "duration_mins": 25
  }}
]

Rules:
- Use 25 min ONLY (lower friction on re-entry day)
- The task must require zero context-loading — \
  something they can start cold within 30 seconds
- Prefer the most mechanical, lowest-stakes task available\
"""

BLOCKS_PROMPT = """\
Generate {n} focused work blocks for today.

USER GOALS:
{goal_areas_formatted}

HOURS WORKED THIS WEEK BY AREA:
{weekly_hours_summary}

TODAY: {day_of_week}

Return ONLY a valid JSON array — no explanation, no markdown fences, nothing else.
Each item must follow this exact shape:
[
  {{
    "index": 0,
    "goal_area": "exact area name from above",
    "color_emoji": "matching emoji from above",
    "task": "specific, immediately actionable task description",
    "duration_mins": 25 or 50
  }}
]

Task rules:
- Completable within the stated duration with zero setup
- Specific enough to start within 30 seconds of reading
- References the user's specific goal context, not generic advice
- Use 50 min for deep work (writing, building, designing)
- Use 25 min for execution tasks (reviewing, responding, shipping a small piece)
- Prioritise areas that are BEHIND on their weekly hour target
- Distribute blocks across different goal areas when there are multiple\
"""
