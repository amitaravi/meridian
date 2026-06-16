# Meridian

Meridian sends ambitious professionals a personalised daily brief reconnecting them to their future identity, then delivers pre-generated hourly time blocks for the day.

**Two services. One repo.**

| Service | Stack | Hosting |
|---------|-------|---------|
| [`/bot`](./bot) | Python 3.11, FastAPI, python-telegram-bot v21 | Render (free tier) |
| [`/web`](./web) | Next.js 14, TypeScript, Tailwind CSS | Vercel (free tier) |

Both services share a single **Supabase** PostgreSQL database.

---

## Local Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- A Telegram bot token (from [@BotFather](https://t.me/botfather))
- A Supabase project ([supabase.com](https://supabase.com))

### Bot

```bash
cd bot
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env           # fill in values
uvicorn app.main:app --reload --port 8000
```

For local Telegram webhook testing, expose port 8000 with [ngrok](https://ngrok.com):

```bash
ngrok http 8000
# Then register the webhook:
curl -X POST "https://api.telegram.org/bot{TOKEN}/setWebhook?url={NGROK_URL}/webhook"
```

### Web

```bash
cd web
npm install
cp .env.example .env.local     # fill in values
npm run dev
```

App runs at `http://localhost:3000`.

---

## Deployment

### Bot → Render

1. Connect this GitHub repo in Render; set root directory to `bot`
2. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Add env vars from [`bot/.env.example`](./bot/.env.example)
4. Set `WEBHOOK_URL` to your Render service URL (e.g. `https://meridian-bot.onrender.com`)

See [`docs/runbooks/deploy-bot.md`](./docs/runbooks/deploy-bot.md) for the full runbook.

### Web → Vercel

1. Connect this GitHub repo in Vercel; set root directory to `web`
2. Add env vars from [`web/.env.example`](./web/.env.example)

---

## Render free-tier cold start

Render's free tier spins down after 15 minutes of inactivity. Configure [cron-job.org](https://cron-job.org) to `GET /health` on your Render URL 5 minutes before the earliest daily brief send time to keep the instance warm.

---

## Product spec

Full product requirements: [`PRD.md`](./PRD.md)
