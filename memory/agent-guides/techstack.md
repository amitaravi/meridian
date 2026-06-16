# Meridian — Tech Stack

> Load this file when: choosing libraries, adding dependencies, or making hosting decisions.

---

## Architecture Overview

Two independently deployed services sharing one Supabase database.

```
┌─────────────────────────────────────────────┐
│  Telegram User                              │
└────────────┬────────────────────────────────┘
             │ webhook / sends
┌────────────▼────────────────────────────────┐
│  /bot  (Python, Render free tier)           │
│  FastAPI + python-telegram-bot v21          │
│  APScheduler (daily sends)                 │
│  Groq API (brief + block generation)       │
└────────────┬────────────────────────────────┘
             │ supabase-py
┌────────────▼────────────────────────────────┐
│  Supabase (PostgreSQL + RLS)                │
└────────────┬────────────────────────────────┘
             │ @supabase/supabase-js
┌────────────▼────────────────────────────────┐
│  /web  (Next.js 14, Vercel free tier)       │
│  Onboarding form + scoreboard page          │
└─────────────────────────────────────────────┘

External: cron-job.org pings /health on Render before each send window
```

---

## Bot Service (`/bot`)

| Technology | Version | Purpose | Rationale |
|---|---|---|---|
| Python | 3.11 | Runtime | Stable, excellent async support, best bot ecosystem |
| FastAPI | 0.111+ | HTTP server / webhook endpoint | Async-native, minimal boilerplate, auto-docs |
| python-telegram-bot | 21.x | Telegram Bot API wrapper | Best Python Telegram library; async, webhook support, inline keyboards |
| APScheduler | 3.10+ | In-process cron scheduling | Schedules per-user sends at configured times; in-process avoids external scheduler cost |
| supabase-py | 2.x | Supabase client | Official Python client; wraps REST API + auth |
| groq | Latest | Groq API client | Official SDK; used for brief and block generation |
| python-dotenv | Latest | Environment variable loading | Dev-only; Render injects env vars in production |
| uvicorn | Latest | ASGI server | Production server for FastAPI on Render |

### Bot dependencies to never add without discussion
- Do not add SQLAlchemy or any ORM — use Supabase client directly
- Do not add Celery — APScheduler is sufficient for this scale
- Do not add Redis — no caching layer needed in V1

---

## Web Service (`/web`)

| Technology | Version | Purpose | Rationale |
|---|---|---|---|
| Next.js | 14 (App Router) | Framework | Team knows React; App Router gives server components for DB calls |
| TypeScript | 5.x | Language | Type safety across components and API routes |
| Tailwind CSS | 3.x | Styling | Rapid UI development; no custom CSS files |
| @supabase/supabase-js | 2.x | Supabase client | Official JS client; used in server components and API routes |
| @supabase/ssr | Latest | Supabase SSR helpers | Correct cookie handling for server-side Supabase in Next.js |

### Web dependencies to never add without discussion
- Do not add a state management library (Zustand, Redux) — React state is sufficient for the onboarding form
- Do not add a UI component library (shadcn, MUI) without discussing first — use Tailwind primitives
- Do not add an ORM — use Supabase JS client directly

---

## Database

| Technology | Purpose | Rationale |
|---|---|---|
| Supabase | PostgreSQL database + auth + RLS | Free tier (500MB, unlimited API requests), managed, built-in Row Level Security, Python and JS clients |

- Connection: via Supabase REST API (through clients) — no direct PostgreSQL connection string used
- RLS must be enabled on every table — see `data-schema.md`

---

## AI / LLM

| Provider | Model | Purpose | Rationale |
|---|---|---|---|
| Groq | llama-3.1-70b-versatile | Brief narrative + block generation | Free tier: ~14,400 req/day; excellent quality; fastest inference available |

**Fallback:** If Groq is down or rate-limited, fail gracefully — log the error and skip that user's send for the day. Do not use a different model silently.

**Groq API key:** `GROQ_API_KEY` in `/bot/.env`

---

## Hosting & Infrastructure

| Service | What it hosts | Cost | Key constraint |
|---|---|---|---|
| Render (free tier) | `/bot` Python FastAPI app | $0 | Spins down after 15 min inactivity; wake-up via cron-job.org |
| Vercel (free tier) | `/web` Next.js app | $0 | 100GB bandwidth/month; serverless functions 10s timeout |
| Supabase (free tier) | PostgreSQL database | $0 | 500MB storage; 2 projects max |
| cron-job.org (free) | HTTP ping to wake Render | $0 | Configure to hit `/health` 5 min before earliest user brief time |

### Render free tier workaround
The bot uses **webhook mode** (not polling). Telegram pushes updates to the Render URL. For outgoing sends (daily briefs), APScheduler fires at the right time, but the process must be awake. cron-job.org pings `/health` 5 minutes before the earliest daily send to ensure the instance is warm.

---

## Environment Variables

### `/bot/.env.example`
```
TELEGRAM_BOT_TOKEN=
SUPABASE_URL=
SUPABASE_ANON_KEY=
GROQ_API_KEY=
WEBHOOK_URL=https://your-app.onrender.com
```

### `/web/.env.example`
```
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
NEXT_PUBLIC_BOT_USERNAME=MeridianBot
```

**Rules:**
- `.env` files are gitignored
- `.env.example` files are committed with placeholder values
- Never log or expose env var values in code
- `SUPABASE_SERVICE_ROLE_KEY` is used only in server-side Next.js code (never in client components)

---

## Local Development

```bash
# Bot
cd bot
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env      # fill in values
uvicorn app.main:app --reload --port 8000

# Web
cd web
npm install
cp .env.example .env.local   # fill in values
npm run dev
```

For local Telegram webhook testing, use `ngrok` to expose the local port:
```bash
ngrok http 8000
# Then register webhook: POST https://api.telegram.org/bot{TOKEN}/setWebhook?url={ngrok_url}/webhook
```
