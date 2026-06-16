# Runbook: Deploy Bot to Render

## First-time setup

1. Push `/bot` to GitHub
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect the `meridian` repo, set root directory to `bot/`
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add all env vars from `bot/.env.example` under Environment tab
7. Deploy → copy the public URL (e.g. `https://meridian-bot.onrender.com`)
8. Set `WEBHOOK_URL` env var to that URL
9. Register Telegram webhook: `POST https://api.telegram.org/bot{TOKEN}/setWebhook?url={RENDER_URL}/webhook`

## Verify deployment

```bash
curl https://meridian-bot.onrender.com/health
# Expected: {"status": "ok"}
```

Send `/start` to the bot in Telegram — should receive a response within 30 seconds.

## Re-deploy after code changes

Render auto-deploys on push to `main`. No manual action required.

## Environment variable changes

Add/update in Render dashboard → Environment → restart the service.

## cron-job.org setup

1. Go to [cron-job.org](https://cron-job.org) → New Cron Job
2. URL: `https://meridian-bot.onrender.com/health`
3. Schedule: every day at the time 5 minutes before your earliest user's brief time
4. This keeps the Render instance warm for outgoing sends
