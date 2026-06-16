# Meridian — Data Schema

> Load this file when: reading or writing Supabase data, modifying tables, writing queries, or adding new fields.

**Always check this file before writing any Supabase query. Column names and JSON shapes are the source of truth.**

---

## Tables

### `users`

Minimal identity record. Created on first `/start` command.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `uuid` | PK, default `gen_random_uuid()` | Internal primary key |
| `telegram_id` | `bigint` | UNIQUE, NOT NULL | Telegram user ID (from `message.from.id`) |
| `created_at` | `timestamptz` | default `now()` | Account creation time |
| `is_active` | `boolean` | default `true` | False when user runs `/pause` |

**RLS policy:** User can only read/update their own row (`telegram_id` must match auth context). Bot service uses `SUPABASE_ANON_KEY` with `telegram_id` as the filter — no auth token required for bot operations.

---

### `profiles`

Full user configuration. Created when onboarding form is submitted.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `user_id` | `uuid` | PK, FK → `users.id` | One profile per user |
| `goal_areas` | `jsonb` | NOT NULL | Array of goal area objects (see shape below) |
| `why_text` | `text` | NOT NULL | Raw "why" captured in onboarding step 2 |
| `path_a` | `text` | NOT NULL | Comfortable future description (Path A) |
| `path_b` | `text` | NOT NULL | Ambitious future description (Path B) |
| `accomplishments` | `jsonb` | NOT NULL | Array of accomplishment strings |
| `brief_hour` | `integer` | NOT NULL, 0–23 | Hour for daily brief delivery (user's local time) |
| `brief_minute` | `integer` | NOT NULL, default 0 | Minute for daily brief delivery |
| `timezone` | `text` | NOT NULL, default `'Asia/Kolkata'` | IANA timezone string |
| `updated_at` | `timestamptz` | default `now()` | Last profile update |

**`goal_areas` JSON shape:**
```json
[
  {
    "name": "Career Transition",
    "description": "Move from corporate SWE to startup product engineer",
    "weekly_hours": 10,
    "color_emoji": "🟦"
  },
  {
    "name": "Side Project",
    "description": "Build Meridian MVP",
    "weekly_hours": 5,
    "color_emoji": "🟩"
  }
]
```

**`accomplishments` JSON shape:**
```json
[
  "Studied 10 hours daily for board exams and topped the school",
  "Built and deployed a full-stack app in 2 weeks from scratch"
]
```

**RLS policy:** User can only read/update their own profile.

---

### `daily_logs`

One row per user per calendar day. Created when the daily brief is sent.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `uuid` | PK, default `gen_random_uuid()` | Row ID |
| `user_id` | `uuid` | NOT NULL, FK → `users.id` | Owner |
| `date` | `date` | NOT NULL | Calendar date (user's local date, not UTC) |
| `blocks` | `jsonb` | NOT NULL | Array of generated block objects |
| `completed_block_indices` | `integer[]` | default `{}` | Indices of blocks marked ✓ Done |
| `skipped_block_indices` | `integer[]` | default `{}` | Indices of blocks marked → Skip |
| `framing_type` | `text` | NOT NULL | One of: `fear`, `aspiration`, `accomplishment`, `urgency` |
| `brief_sent_at` | `timestamptz` | | When the brief was delivered |

**Unique constraint:** `(user_id, date)` — one log per user per day.

**`blocks` JSON shape:**
```json
[
  {
    "index": 0,
    "goal_area": "Career Transition",
    "color_emoji": "🟦",
    "task": "Write 3 bullet points summarising what you learned at your last job that a startup needs now. These become your first LinkedIn draft.",
    "duration_mins": 50
  },
  {
    "index": 1,
    "goal_area": "Side Project",
    "color_emoji": "🟩",
    "task": "Set up the FastAPI project skeleton with a /health endpoint and /webhook route. Run it locally and confirm it responds.",
    "duration_mins": 25
  }
]
```

**RLS policy:** User can only read/update their own logs.

---

### `streaks`

One row per user. Updated on every block completion.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `user_id` | `uuid` | PK, FK → `users.id` | Owner |
| `current_streak` | `integer` | default `0` | Consecutive active days |
| `longest_streak` | `integer` | default `0` | Historical best streak |
| `last_active_date` | `date` | | Last date a block was completed |

**Streak logic:**
- On block completion: compare `last_active_date` to today
  - If `last_active_date` = yesterday → `current_streak += 1`
  - If `last_active_date` = today → no change (already counted)
  - If gap > 1 day → `current_streak = 1` (re-entry)
- Update `longest_streak` if `current_streak > longest_streak`
- On re-entry (3+ day gap): reset `current_streak = 1` on first completion

**RLS policy:** User can only read/update their own streak row.

---

## Migrations

SQL migration files live in `/bot/migrations/`. Naming convention:

```
001_initial_schema.sql
002_add_skipped_block_indices.sql
```

Run migrations manually via Supabase SQL editor or `supabase db push` (if using Supabase CLI).

**Never modify a deployed migration file.** Always create a new numbered migration.

---

## Framing Type Rotation

The `framing_type` in `daily_logs` determines the tone of the next day's brief. Rotation order:

```
fear → aspiration → accomplishment → urgency → fear → ...
```

On brief generation:
1. Query the last `daily_logs` row for the user
2. Read its `framing_type`
3. Use the next in sequence for today's brief
4. Store today's `framing_type` in the new `daily_logs` row

If no previous log exists (first brief), start with `fear`.

---

## Common Query Patterns

**Get full user context for brief generation (Python):**
```python
result = supabase.table("profiles").select("*").eq("user_id", user_id).single().execute()
profile = result.data
```

**Record block completion (Python):**
```python
supabase.table("daily_logs").update({
    "completed_block_indices": supabase.raw(f"array_append(completed_block_indices, {block_index})")
}).eq("user_id", user_id).eq("date", today_date).execute()
```

**Check gap for re-entry detection (Python):**
```python
result = supabase.table("streaks").select("last_active_date").eq("user_id", user_id).single().execute()
last_active = result.data["last_active_date"]
gap = (today - date.fromisoformat(last_active)).days
```

**Get scoreboard data for web (TypeScript):**
```typescript
const { data } = await supabase
  .from("daily_logs")
  .select("date, blocks, completed_block_indices")
  .eq("user_id", userId)
  .gte("date", sevenDaysAgo)
  .order("date", { ascending: true });
```

---

## Schema Change Protocol

1. Write a new migration file in `/bot/migrations/`
2. Apply it via Supabase SQL editor
3. Update this file (`data-schema.md`) to reflect the new column/table
4. Update any affected query patterns in `/bot` and `/web`
5. Update `.env.example` if new env vars are needed
