# Meridian — Repository Structure

> Load this file when: creating new files, deciding where code belongs, or adding a new module.

---

## Top-Level Structure

```
meridian/
├── CLAUDE.md                    # Agent operating instructions (keep lean)
├── PRD.md                       # Full product requirements document
├── README.md                    # Human-facing project overview
│
├── bot/                         # Python Telegram bot + FastAPI server
├── web/                         # Next.js web app (onboarding + scoreboard)
│
├── memory/
│   └── agent-guides/            # Progressive disclosure docs for Claude Code
│       ├── techstack.md
│       ├── data-schema.md
│       ├── repository-structure.md
│       ├── version-control.md
│       └── project-skills.md
│
└── docs/                        # Evolving product documentation
    ├── decisions/               # Architecture Decision Records (ADRs)
    └── runbooks/                # Operational guides (deploy, rollback, etc.)
```

---

## `/bot` — Python Service

```
bot/
├── app/
│   ├── main.py                  # FastAPI app entry point; mounts routes
│   ├── bot.py                   # python-telegram-bot Application setup
│   │
│   ├── handlers/                # Telegram update handlers
│   │   ├── __init__.py
│   │   ├── start.py             # /start command
│   │   ├── commands.py          # /pause, /resume, /status
│   │   └── callbacks.py         # Inline keyboard button callbacks (Done/Skip)
│   │
│   ├── services/                # Business logic (no Telegram or HTTP coupling)
│   │   ├── __init__.py
│   │   ├── brief.py             # generate_brief(user_id) → sends Telegram messages
│   │   ├── blocks.py            # generate_blocks(user_id, n) → list of block dicts
│   │   ├── scheduler.py         # APScheduler setup; register/remove user jobs
│   │   ├── streak.py            # update_streak(user_id, date) logic
│   │   └── reentry.py           # detect_gap(user_id) → bool; re-entry brief logic
│   │
│   ├── db/                      # Supabase client and query functions
│   │   ├── __init__.py
│   │   ├── client.py            # Supabase client singleton
│   │   ├── users.py             # get_user, create_user, set_active queries
│   │   ├── profiles.py          # get_profile, upsert_profile queries
│   │   ├── logs.py              # create_log, update_completion, get_recent queries
│   │   └── streaks.py           # get_streak, update_streak queries
│   │
│   ├── ai/                      # Groq API calls
│   │   ├── __init__.py
│   │   ├── client.py            # Groq client singleton
│   │   ├── prompts.py           # Prompt templates (brief + blocks)
│   │   └── generate.py          # generate_narrative(), generate_time_blocks()
│   │
│   └── routes/
│       ├── __init__.py
│       ├── webhook.py           # POST /webhook — receives Telegram updates
│       └── health.py            # GET /health — used by cron-job.org wake-up
│
├── migrations/                  # SQL migration files
│   └── 001_initial_schema.sql
│
├── tests/                       # Unit tests
│   ├── test_brief.py
│   ├── test_blocks.py
│   └── test_streak.py
│
├── requirements.txt
├── .env.example
├── .gitignore
└── Procfile                     # Render deployment: `web: uvicorn app.main:app --host 0.0.0.0 --port $PORT`
```

### `/bot` rules

- **Handlers** only handle Telegram events — they call services, never contain business logic
- **Services** are pure business logic — no Telegram imports, no HTTP imports
- **DB modules** contain only query functions — one module per table
- **AI modules** contain only Groq API calls — prompts live in `prompts.py` as constants
- Tests live in `/bot/tests/` and cover services and AI modules only (not handlers)

---

## `/web` — Next.js Service

```
web/
├── app/                         # Next.js 14 App Router
│   ├── layout.tsx               # Root layout
│   ├── page.tsx                 # Landing page (/)
│   │
│   ├── onboarding/
│   │   └── page.tsx             # 5-step onboarding form (/onboarding?tid=...)
│   │
│   ├── scoreboard/
│   │   └── [userId]/
│   │       └── page.tsx         # Weekly scoreboard (/scoreboard/[userId])
│   │
│   └── settings/
│       └── page.tsx             # Profile management (/settings?tid=...)
│
├── components/                  # Shared React components
│   ├── onboarding/              # Step components for onboarding form
│   │   ├── StepGoalAreas.tsx
│   │   ├── StepWhy.tsx
│   │   ├── StepPaths.tsx
│   │   ├── StepAccomplishments.tsx
│   │   └── StepAvailability.tsx
│   ├── scoreboard/              # Scoreboard grid components
│   │   ├── WeekGrid.tsx
│   │   └── GoalAreaRow.tsx
│   └── ui/                      # Generic UI primitives
│       ├── Button.tsx
│       ├── Input.tsx
│       └── ProgressBar.tsx
│
├── lib/                         # Shared utilities and clients
│   ├── supabase/
│   │   ├── client.ts            # Browser-side Supabase client
│   │   └── server.ts            # Server-side Supabase client (service role)
│   └── utils.ts                 # Date helpers, type utilities
│
├── types/                       # TypeScript type definitions
│   └── index.ts                 # Profile, GoalArea, DailyLog, Block types
│
├── public/                      # Static assets
│
├── next.config.ts
├── tailwind.config.ts
├── tsconfig.json
├── package.json
├── .env.example
└── .gitignore
```

### `/web` rules

- All database calls happen in **server components** or **API routes** — never in client components
- `SUPABASE_SERVICE_ROLE_KEY` is used only in server-side code (`lib/supabase/server.ts`)
- `NEXT_PUBLIC_SUPABASE_*` vars are used only in the browser client (`lib/supabase/client.ts`)
- Components in `components/ui/` are generic and reusable — no business logic
- Page components are thin — they fetch data and pass it to components

---

## `/docs` — Documentation

```
docs/
├── decisions/                   # Architecture Decision Records
│   └── ADR-001-telegram-bot-delivery.md
└── runbooks/
    ├── deploy-bot.md
    └── deploy-web.md
```

**ADR format:**
```markdown
# ADR-NNN: Title
Status: Accepted | Deprecated | Superseded by ADR-XXX
Context: Why this decision was needed
Decision: What was decided
Consequences: What changes as a result
```

Write an ADR for every significant architectural decision that is not obvious from the code.

---

## Naming Conventions

| Item | Convention | Example |
|---|---|---|
| Python files | `snake_case.py` | `brief.py`, `generate.py` |
| Python functions | `snake_case` | `generate_brief()` |
| Python classes | `PascalCase` | `BriefService` |
| TypeScript files | `PascalCase.tsx` for components | `StepGoalAreas.tsx` |
| TypeScript files | `camelCase.ts` for utilities | `utils.ts` |
| TypeScript functions | `camelCase` | `getProfile()` |
| TypeScript components | `PascalCase` | `WeekGrid` |
| Database tables | `snake_case` | `daily_logs` |
| Environment variables | `SCREAMING_SNAKE_CASE` | `GROQ_API_KEY` |
| Git branches | `kebab-case` | `feature/issue-6-daily-brief` |

---

## What Goes Where — Decision Guide

| Scenario | Location |
|---|---|
| New Telegram command handler | `bot/app/handlers/commands.py` |
| New button callback | `bot/app/handlers/callbacks.py` |
| New Groq prompt | `bot/app/ai/prompts.py` (as a constant) |
| New business logic function | `bot/app/services/` (new file if new domain) |
| New Supabase query | `bot/app/db/` (in the file matching the table) |
| New SQL migration | `bot/migrations/NNN_description.sql` |
| New Next.js page | `web/app/path/page.tsx` |
| New reusable component | `web/components/ui/` or domain subfolder |
| New server-side data fetch | Server component or `web/app/api/route.ts` |
| New TypeScript type | `web/types/index.ts` |
| Architecture decision | `docs/decisions/ADR-NNN-title.md` |
| Operational runbook | `docs/runbooks/topic.md` |
