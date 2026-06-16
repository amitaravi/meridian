# ADR-001: Telegram Bot as Primary Delivery Mechanism

**Status:** Accepted  
**Date:** 2026-06-16

## Context

Meridian's core product loop requires a daily morning trigger that gets users into their first work block within 5 minutes. Multiple delivery mechanisms were evaluated: native mobile app, web app, email, SMS, WhatsApp, Telegram, browser extension, Slack, Discord.

The critical constraint: the trigger must attach to an existing morning behaviour with zero installation friction. The target user (ambitious professional, 23–32, India) checks messages on their phone within minutes of waking.

## Decision

Use Telegram Bot as the primary daily interaction surface, with a minimal Next.js web app for onboarding (where rich forms are needed) and the weekly scoreboard (where visual display is needed).

## Rationale

1. **Existing morning habit:** Telegram is part of the target user's morning phone-check routine, especially in India.
2. **Zero installation friction:** No app store, no approval, no new app to remember. Lives inside an app they already have.
3. **Sufficient interactivity:** Inline keyboard buttons handle block completion (`[✓ Done]`, `[→ Skip]`) — the only interaction needed.
4. **Build speed:** A Telegram bot MVP is achievable in days, not weeks. No app store approval.
5. **Right medium for the message:** The daily Path A/B contrast arrives as a personal message — not an app screen — which matches the "message from a mentor" framing.

## Rejected alternatives

- **Native app:** Superior UX ceiling, but 4–6 weeks to build, app store approval required, high app fatigue risk. Planned for V3.
- **WhatsApp:** Highest penetration, but Business API requires Meta approval (weeks), template restrictions, per-message cost. Planned for V3.
- **Email:** No interaction mechanic possible. Open rates collapse after week 2 for daily sends.
- **Web app:** No reliable morning trigger. Requires intentional navigation — too many failure points before value is delivered.
- **SMS:** 98% open rate, but no UI for the completion mechanic.

## Consequences

- Bot must use webhook mode (not polling) to work on Render free tier
- Render free tier spins down after inactivity — cron-job.org required to warm the instance before scheduled sends
- Onboarding requires a web app (Telegram forms are too limited for 5-step onboarding)
- Weekly scoreboard requires a web page (visual grid not possible in Telegram)
- Long-term: migrate to WhatsApp or native app once revenue and team size allow
