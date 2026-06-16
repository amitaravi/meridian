# Meridian — Product Requirements Document

**Version:** 1.0  
**Status:** Active  
**Last updated:** 2026-06-16

---

## Product Vision

A daily 5-minute morning ritual that reconnects ambitious professionals to their future identity and generates their exact hourly work plan for the day — eliminating both the motivation fade and the blank page simultaneously.

**The one job:** Get the right person working on the right thing within 5 minutes of opening the app, every morning.

**Delivery mechanism:** Telegram bot (primary daily interaction) + Next.js web app (onboarding and scoreboard only).

---

## Problem Statement

Ambitious professionals in unfulfilling jobs know what they want to build toward. They have the capability (proven by past performance). They have the time (evenings, weekends). But they repeatedly lose the thread connecting today's actions to their future self.

The core loop that breaks:
1. Strong motivation → execute well for days or weeks
2. Disruption (travel, exhausting work period, holiday) → momentum lost
3. Reconnecting to "why" feels heavy → defer → drift
4. Default habits fill the gap (YouTube, passive consumption)
5. Weeks pass without meaningful progress

The solution is not a new productivity system. It is a daily mechanism that keeps the thread alive — making the cost of reconnection zero, and the first action of the day pre-decided.

---

## Target Users

### Primary Persona — "The Drifting High-Performer"

| Attribute | Detail |
|---|---|
| Age | 23–32 |
| Role | SWE, analyst, or professional at a corporate MNC |
| Goal | Startup transition, entrepreneurship, or major career pivot |
| History | Peak performer when external structure existed (exams, school, trainer) |
| Current reality | Executing in short bursts separated by drift periods |
| Motivation type | Fear of mediocrity + identity ("built for more") |
| Accountability | Sparse — no reliable daily accountability structure |
| Content habits | Ali Abdaal, Sahil Bloom, startup Twitter/LinkedIn |
| Tool relationship | Won't pay for "productivity apps"; will pay for "career investments" |

### Anti-User

- Someone who just wants a simple habit tracker
- Someone without defined goals
- Someone seeking human-to-human accountability
- Someone satisfied with their current trajectory

---

## User Stories

### Onboarding

- As a new user, I want to input my goals, "why," past accomplishments, and two-path contrast in one guided session, so the product knows me well enough to be personal from day one.
- As a new user, I want onboarding to feel like a meaningful reflection exercise, not a form, so I leave with clarity rather than fatigue.

### Daily Morning Brief

- As a returning user, I want to receive a vivid, varied daily contrast between my comfortable future (Path A) and my ambitious one (Path B), so I feel the urgency to act today rather than later.
- As a user, I want the motivation narrative to feel fresh and different each day, so it never becomes background noise I tune out.
- As a user, I want to be reminded of something I have already accomplished that proves I am capable, so I start the day from identity strength, not self-doubt.

### Time Blocks

- As a user, I want today's specific time blocks pre-generated from my goals, so I never have to decide what to work on — I just execute.
- As a user, I want each block to contain a concrete task I can start immediately without any setup or additional planning.
- As a user, I want to tap to mark blocks complete and see visible progress, so completion feels satisfying and worth repeating.

### Re-entry

- As a user who has been away for several days, I want a re-entry ritual that makes today feel small and manageable, so I do not feel I have to catch up — just restart.

### Settings & Profile

- As a user, I want to update my goals, Path A/B descriptions, and brief delivery time without repeating the full onboarding flow.
- As a user, I want to pause and resume my daily sends via a simple bot command.

---

## Success Metrics

| Metric | V1 Target |
|---|---|
| Day 7 retention | > 40% |
| Day 30 retention | > 20% |
| Morning open rate (before 10am) | > 55% of active users |
| Time block completion rate | > 50% of generated blocks |
| Re-entry rate after 3+ day gap | > 35% |
| NPS at Day 30 | > 50 |
| Free → paid conversion | > 15% |

The single metric that signals V1 is working: **30% of users open the bot before 9am on Day 14.** That means a morning ritual is forming.

---

## Features

### Feature 1: Onboarding (one-time, ~15 minutes)

A guided 5-step web flow that feels like a meaningful reflection session.

**Step 1 — Goal Areas**
Up to 3 life areas (e.g. Career Transition, Side Project, Fitness). Each has: name, one-line description, target hours per week, colour.

**Step 2 — The "Why" Capture**
Three prompted questions:
- What are you ultimately trying to build or become?
- What does your life look like at age 40 if you stay on your current path?
- What does taking the hard path unlock for your life?

**Step 3 — Path A vs Path B**
Two free-text fields. Path A: the comfortable, average future in specific detail. Path B: the ambitious future in specific detail. These are the AI's source material for every daily brief.

**Step 4 — Past Accomplishments**
2–3 specific things the user has already done that prove they are capable (e.g. "Studied 10 hours a day for board exams"). Used to counter self-doubt in daily briefs.

**Step 5 — Availability**
Days with office/job commitments, preferred working hours for personal goals, preferred brief delivery time, timezone.

On completion: profile saved to Supabase, confirmation screen shown with Telegram deep link.

---

### Feature 2: Daily Morning Brief

Delivered via Telegram at the user's configured time. Two sequential messages.

**Message 1 — The Contrast Narrative**
- 150–200 words of flowing prose
- Generated fresh each day by Groq API
- Framing type rotates daily: Fear → Aspiration → Accomplishment → Urgency → repeat
- Always references the user's specific Path A/B details — never generic
- Ends with one sentence creating urgency for today specifically

**Message 2 — Today's Time Blocks**
- 3–4 blocks generated by a second Groq call
- Each block: goal area (colour emoji), concrete task, duration (25 or 50 min)
- Displayed with inline keyboard: `[✓ Done]` `[→ Skip]`

---

### Feature 3: Time Block Completion

- Tapping `[✓ Done]`: records completion in Supabase, updates message to reflect done state, sends confirmation
- Tapping `[→ Skip]`: records skip without affecting streak
- Streak logic: completing ≥1 block on a new calendar day increments streak; gap of >1 day resets to 1

---

### Feature 4: Daily Scoreboard Message

Sent each evening (~9pm or configured evening time).

- Blocks completed vs planned (per goal area)
- Current streak count
- One-line motivational close

Only sent if a brief was delivered that day.

---

### Feature 5: Re-entry Ritual

Triggered when `last_active_date` gap ≥ 3 days.

- Opens with acknowledgement ("You've been away. That's okay.")
- Shorter contrast narrative (80–100 words)
- Only 1–2 blocks (lowest-friction goal area prioritised)
- Closing: "You don't need to catch up. Just one block today puts you back on Path B."
- Streak resets to 1 on first re-entry completion
- Standard brief resumes next morning

---

### Feature 6: Weekly Scoreboard Web Page

Available at `/scoreboard/[userId]` — linked from a Sunday evening Telegram message.

- 7-day grid: one column per day, one row per goal area
- Cell states: empty / partial / complete (colour-coded)
- Weekly hours worked vs target per area
- Current streak displayed prominently
- Publicly shareable by URL (no login required) — enables building-in-public posts

---

### Feature 7: User Profile Management

**Web:** Settings page at `/settings?tid={telegram_id}` — all profile fields editable, saves to Supabase.

**Bot commands:**
- `/pause` — stops daily sends, sets `is_active = false`
- `/resume` — restarts sends, re-registers scheduler job
- `/status` — shows current streak, goal areas, next brief time

---

## Non-Goals (V1)

These are explicitly out of scope. They are V2+ roadmap items.

- Social features, sharing, or community
- Human accountability partner pairing
- Calendar integrations (Google Calendar, Notion, etc.)
- Weekly or monthly planning sessions (guided)
- Push notifications (web notifications only to start)
- Native mobile app (mobile-responsive web only)
- Audio briefs
- Habit tracking beyond time blocks
- Analytics dashboards for users
- Team or group features
- Stripe / payment processing

---

## User Flows

### Flow 1: New User Onboarding
```
User sends /start to Meridian bot on Telegram
→ Bot saves telegram_id to Supabase users table
→ Bot replies with welcome message + [Begin Onboarding] button (link to web)
→ User completes 5-step web form
→ Profile saved to Supabase profiles table
→ Confirmation screen shown with [Return to Telegram] deep link
→ User returns to bot → bot confirms setup + shows brief delivery time
```

### Flow 2: Daily Morning (Returning User)
```
Scheduled send fires at user's configured time
→ Groq generates contrast narrative (framing type rotated)
→ Groq generates 3–4 time blocks
→ Telegram: Message 1 (narrative) sent
→ Telegram: Message 2+ (blocks with inline keyboards) sent
→ User taps [✓ Done] on first block
→ Completion recorded in Supabase, streak updated, confirmation sent
→ User works through remaining blocks
→ Evening: scoreboard message sent
```

### Flow 3: Re-entry After Gap
```
Scheduled send fires → gap detection: last_active_date ≥ 3 days ago
→ Re-entry brief generated (shorter narrative, 1–2 blocks)
→ Re-entry message delivered to Telegram
→ User completes 1 block → streak resets to 1
→ Standard flow resumes next morning
```

---

## Technical Architecture

### Stack

| Layer | Technology | Rationale |
|---|---|---|
| Bot | Python 3.11 + python-telegram-bot v21 + FastAPI | Best-in-class bot library, webhook support, free to operate |
| Web | Next.js 14 + TypeScript + Tailwind CSS | Team knows React; fast deployment on Vercel |
| Database | Supabase (PostgreSQL) | Free tier, managed, built-in RLS, JS + Python clients |
| AI | Groq API — llama-3.1-70b-versatile | Free tier, 14,400+ req/day, excellent quality |
| Bot hosting | Render (free tier, webhook mode) | Free, persistent enough for webhook handling |
| Web hosting | Vercel (free tier) | Zero-config Next.js deployment |
| Cron wake-up | cron-job.org (free) | Keeps Render instance warm at send time |
| Payments | Stripe | V2 only |

### AI Prompt Architecture

**Brief generation prompt (Groq):**
- Input: Path A, Path B, accomplishments, framing type, day of week, current streak
- Output: 150–200 word contrast narrative
- Framing rotation: fear → aspiration → accomplishment → urgency (stored in `daily_logs`)

**Block generation prompt (Groq):**
- Input: goal areas + weekly targets, available hours today, day of week, hours worked this week per area
- Output: JSON array of `{area, task, duration_mins}`
- Task specificity rule: completable within stated duration, no setup required, references user's specific context

### Data Model Summary

See `/memory/agent-guides/data-schema.md` for full schema.

Core tables: `users`, `profiles`, `daily_logs`, `streaks`

---

## Pricing

| Tier | Price | Included |
|---|---|---|
| Free | $0 | 7-day full trial |
| Pro | $15/month | Unlimited daily briefs, all features |
| Annual | $120/year | 2 months free |

**Positioning:** Not a productivity app. A career investment. Framed as: "Less than one coffee a week to stay on the path to the life you actually want."

---

## Future Roadmap

### V2 (Month 2–3) — Weekly Layer
- Sunday evening guided weekly planning session (10 min, prompted)
- Weekly scoreboard: visual contribution graph by goal area
- Web push notifications for morning activation
- "This week you worked X hours on career transition" weekly summary email

### V3 (Month 4–6) — Accountability Layer
- Async daily check-in with AI mentor persona
- Optional accountability pairs (two users share weekly scoreboards)
- Monthly trajectory report: "Based on this month's execution, you are N months ahead of / behind your Path B timeline"

### V4+ (Month 7–12) — Community & Depth
- Founder transition cohorts (SWE→startup, corporate→founder)
- Goal area templates with milestone tracking
- Native mobile app (React Native)
- Calendar integration for smart block scheduling
- "Hard mode" — more demanding AI persona

---

## Implementation Phases

### Phase 1 — Dogfood (Week 1–2, ~6 hours)
Single-user Python script. Reads config file, calls Groq, sends brief to Telegram. No database. Validates that the daily brief actually changes behaviour before building infrastructure.

### Phase 2 — First Users (Week 3–4, ~8 hours)
Multi-user bot with Supabase, web onboarding, block completion tracking, 3–5 friends onboarded.

### Phase 3 — Launch (Week 5–6, ~6 hours)
Weekly scoreboard, re-entry ritual, landing page, ready to post publicly on LinkedIn.

**The one rule:** Do not touch Phase 2 until Phase 1 has been used personally for 7 consecutive days.
