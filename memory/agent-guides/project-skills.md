# Meridian — Project Skills & Patterns

> Load this file when: implementing bot handlers, writing Groq prompts, working with APScheduler, or using Telegram inline keyboards.

---

## Telegram Bot Patterns

### Webhook setup (FastAPI)

```python
# app/routes/webhook.py
from fastapi import Request
from app.bot import application

async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"ok": True}
```

Register the webhook on startup:
```python
# app/main.py — on_startup
await application.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")
```

### Command handler pattern

```python
# app/handlers/start.py
from telegram import Update
from telegram.ext import ContextTypes
from app.db.users import create_user_if_not_exists
from app.db.profiles import get_profile

async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    telegram_id = update.effective_user.id
    await create_user_if_not_exists(telegram_id)
    
    profile = await get_profile(telegram_id)
    if profile:
        # Returning user
        await update.message.reply_text("Welcome back! Use /status to see your progress.")
        return
    
    # New user — send onboarding link
    onboarding_url = f"https://meridian.app/onboarding?tid={telegram_id}"
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("Begin Onboarding →", url=onboarding_url)
    ]])
    await update.message.reply_text(
        "Welcome to Meridian. Let's build your daily brief.",
        reply_markup=keyboard
    )
```

### Inline keyboard (Done / Skip buttons)

```python
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def build_block_keyboard(block_index: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✓ Done", callback_data=f"done:{block_index}"),
        InlineKeyboardButton("→ Skip", callback_data=f"skip:{block_index}"),
    ]])
```

Callback handler:
```python
# app/handlers/callbacks.py
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()  # must always answer to remove loading state
    
    action, block_index = query.data.split(":")
    block_index = int(block_index)
    user_id = query.from_user.id
    
    if action == "done":
        await record_completion(user_id, block_index)
        await query.edit_message_text(f"✓ Block {block_index + 1} done.")
    elif action == "skip":
        await record_skip(user_id, block_index)
        await query.edit_message_text(f"→ Block {block_index + 1} skipped.")
```

**Rule:** Always call `await query.answer()` first in callback handlers — Telegram shows a loading spinner until it's called.

### Registering handlers

```python
# app/bot.py
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

def build_application(token: str) -> Application:
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", handle_start))
    app.add_handler(CommandHandler("pause", handle_pause))
    app.add_handler(CommandHandler("resume", handle_resume))
    app.add_handler(CommandHandler("status", handle_status))
    app.add_handler(CallbackQueryHandler(handle_callback))
    return app
```

---

## Groq API Patterns

### Client setup

```python
# app/ai/client.py
from groq import AsyncGroq
import os

groq_client = AsyncGroq(api_key=os.environ["GROQ_API_KEY"])
```

### Brief generation call

```python
# app/ai/generate.py
async def generate_narrative(profile: dict, framing_type: str, streak: int) -> str:
    prompt = build_brief_prompt(profile, framing_type, streak)
    
    response = await groq_client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=350,
        temperature=0.8,  # some variation, not too random
    )
    return response.choices[0].message.content.strip()
```

### Block generation call (structured output)

```python
async def generate_time_blocks(profile: dict, available_hours: dict, n: int = 3) -> list[dict]:
    prompt = build_blocks_prompt(profile, available_hours, n)
    
    response = await groq_client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=600,
        temperature=0.5,  # lower — consistency matters more than variety here
    )
    
    raw = response.choices[0].message.content.strip()
    # Parse JSON from response — wrap in try/except, retry once on failure
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Extract JSON array if model wrapped it in markdown
        match = re.search(r'\[.*\]', raw, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise ValueError(f"Could not parse blocks JSON from Groq response: {raw[:200]}")
```

### Prompt templates (stored in `prompts.py`)

```python
# app/ai/prompts.py

BRIEF_PROMPT = """You are a demanding, deeply caring mentor who knows this person intimately.

USER CONTEXT:
- Path A (comfortable, average future): {path_a}
- Path B (ambitious future they are building): {path_b}
- Past accomplishments that prove they are capable: {accomplishments}
- Today's framing: {framing_type}
  (fear = stark contrast, aspiration = vivid future, accomplishment = proud + challenging, urgency = direct)
- Day: {day_of_week}, Current streak: {streak} days

Write a 150-200 word contrast narrative as flowing prose (not bullet points).
Rules:
- Never generic. Always reference their specific details from Path A and Path B.
- End with exactly one sentence that creates urgency for TODAY specifically.
- Vary sentence rhythm. Do not start consecutive sentences the same way.
- Tone must match the framing type exactly."""


BLOCKS_PROMPT = """Generate {n} time blocks for today's work session.

USER GOALS:
{goal_areas_formatted}

AVAILABLE TODAY: {start_time} to {end_time}
DAY: {day_of_week}
HOURS WORKED THIS WEEK BY AREA: {weekly_hours_summary}

Return ONLY a valid JSON array. No explanation, no markdown fences.
Each block must follow this exact shape:
[
  {{
    "index": 0,
    "goal_area": "exact area name from above",
    "color_emoji": "matching emoji",
    "task": "specific task description",
    "duration_mins": 25 or 50
  }}
]

Task specificity rules:
- Must be completable within the stated duration with no setup required
- Must be specific enough that the user can start within 30 seconds of reading it
- Must reference the user's specific context, not generic advice
- Prioritise areas that are behind on their weekly hour target"""
```

---

## APScheduler Patterns

### Scheduler setup

```python
# app/services/scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

scheduler = AsyncIOScheduler()

def start_scheduler():
    scheduler.start()

def register_user_job(user_id: str, telegram_id: int, hour: int, minute: int, timezone: str):
    tz = pytz.timezone(timezone)
    job_id = f"brief_{user_id}"
    
    # Remove existing job if present (prevents duplicates on re-registration)
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
    
    scheduler.add_job(
        send_brief_job,
        trigger=CronTrigger(hour=hour, minute=minute, timezone=tz),
        id=job_id,
        args=[user_id, telegram_id],
        replace_existing=True,
    )

def remove_user_job(user_id: str):
    job_id = f"brief_{user_id}"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)

async def send_brief_job(user_id: str, telegram_id: int):
    """Called by scheduler. Detects re-entry, generates and sends brief."""
    try:
        gap = await detect_gap(user_id)
        if gap >= 3:
            await send_reentry_brief(user_id, telegram_id)
        else:
            await send_standard_brief(user_id, telegram_id)
    except Exception as e:
        logging.error(f"Brief send failed for user {user_id}: {e}")
```

### Load all jobs on startup

```python
# app/main.py — on_startup
async def on_startup():
    await application.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")
    
    active_users = await get_all_active_users_with_profiles()
    for user in active_users:
        register_user_job(
            user_id=user["id"],
            telegram_id=user["telegram_id"],
            hour=user["profile"]["brief_hour"],
            minute=user["profile"]["brief_minute"],
            timezone=user["profile"]["timezone"],
        )
    
    scheduler.start()
```

---

## Supabase Client Pattern (Python)

```python
# app/db/client.py
from supabase import create_client, Client
import os

_client: Client | None = None

def get_supabase() -> Client:
    global _client
    if _client is None:
        _client = create_client(
            os.environ["SUPABASE_URL"],
            os.environ["SUPABASE_ANON_KEY"],
        )
    return _client
```

Use `get_supabase()` in all db modules — never import the client directly.

---

## Supabase Client Pattern (TypeScript — Server)

```typescript
// web/lib/supabase/server.ts
import { createClient } from "@supabase/supabase-js";

export function createServerClient() {
  return createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!,  // service role for server-side writes
  );
}
```

Use `createServerClient()` only in server components and API routes — never in client components.

---

## Error Handling Conventions

### Bot (Python)

- Wrap all handler bodies in try/except
- Log errors with `logging.error(f"...: {e}", exc_info=True)`
- Never let an unhandled exception propagate to Telegram (it causes the webhook to retry infinitely)
- On Groq failure: log and skip the send for that user; do not crash the scheduler

### Web (TypeScript)

- Use `try/catch` around all Supabase calls in server components
- Return `{ error: string }` shapes from API routes on failure
- Never expose raw error messages to the client — log the full error server-side, return a generic message client-side

---

## Testing Conventions

### Bot unit tests (pytest)

```python
# tests/test_streak.py
import pytest
from datetime import date
from app.services.streak import calculate_new_streak

def test_consecutive_day_increments_streak():
    result = calculate_new_streak(current=5, last_active=date(2026, 6, 15), today=date(2026, 6, 16))
    assert result == 6

def test_gap_resets_streak():
    result = calculate_new_streak(current=5, last_active=date(2026, 6, 10), today=date(2026, 6, 16))
    assert result == 1

def test_same_day_no_change():
    result = calculate_new_streak(current=5, last_active=date(2026, 6, 16), today=date(2026, 6, 16))
    assert result == 5
```

- Test service functions in isolation (pure functions where possible)
- Mock Supabase and Groq in tests — do not make real API calls in the test suite
- Run tests with `pytest bot/tests/`

### Manual testing checklist (Telegram)

Before marking any bot issue complete:
1. Send `/start` → correct response
2. Complete onboarding via web link → profile appears in Supabase
3. Trigger a brief manually → both messages appear with correct formatting
4. Tap `[✓ Done]` → completion recorded in Supabase, message updated
5. Tap `[→ Skip]` → skip recorded, message updated
6. Check streak row in Supabase — values correct
