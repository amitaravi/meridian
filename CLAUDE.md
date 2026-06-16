# Meridian — Claude Code Operating Instructions

## Project Purpose

Meridian is a Telegram bot + Next.js web app that sends ambitious professionals a personalised daily brief reconnecting them to their future identity, then gives them today's pre-generated hourly time blocks. It eliminates both motivation fade and the blank-page planning problem.

**Two services. One repo.**
- `/bot` — Python 3.11, FastAPI, python-telegram-bot v21 (hosted on Render)
- `/web` — Next.js 14, TypeScript, Tailwind CSS (hosted on Vercel)

Full product spec: [`/PRD.md`](./PRD.md)

---

## Progressive Disclosure System

This file stays lean. All detailed guidance lives in `/memory/agent-guides/`. Load only what the task requires.

| Guide | Load when... |
|---|---|
| [`techstack.md`](./memory/agent-guides/techstack.md) | Choosing libraries, adding dependencies, hosting decisions |
| [`data-schema.md`](./memory/agent-guides/data-schema.md) | Reading/writing Supabase, modifying tables, writing queries |
| [`repository-structure.md`](./memory/agent-guides/repository-structure.md) | Creating files, deciding where new code lives |
| [`version-control.md`](./memory/agent-guides/version-control.md) | Branching, committing, creating PRs |
| [`project-skills.md`](./memory/agent-guides/project-skills.md) | Telegram bot patterns, Groq prompts, APScheduler, RLS |

---

## Core Agent Behaviour Rules

1. **Read before writing.** Before editing any file, read it first. Never overwrite without understanding current state.
2. **One issue, one branch.** Each GitHub issue gets its own branch. Never mix concerns.
3. **No scope creep.** Implement exactly what the issue describes. If you notice related work, open a new issue — do not fold it in.
4. **Check the schema first.** Before writing any Supabase query, read `data-schema.md` to confirm table/column names.
5. **Verify before claiming done.** Run the bot locally or check Telegram output before marking a task complete.
6. **Never hardcode secrets.** All API keys, tokens, and URLs go in `.env` files. `.env` is gitignored. Update `.env.example` when adding new variables.
7. **Ask before deleting.** If a file or function seems unused, confirm before removing.

---

## Code Quality Rules

- **Python (`/bot`):** PEP 8, type hints on all functions, no bare `except` clauses
- **TypeScript (`/web`):** strict mode enabled, no `any` types, components in `components/`, pages in `app/`
- **No dead code:** remove unused imports, variables, and commented-out blocks before committing
- **No print debugging:** use Python `logging` module in `/bot`; use `console.error` only in `/web` catch blocks
- **Function length:** if a function exceeds 40 lines, split it
- **Comments:** only when the *why* is non-obvious — never describe what the code does

---

## Git Workflow

```
main          ← production-ready only; never commit directly
feature/      ← feature/issue-{N}-short-description
fix/          ← fix/issue-{N}-short-description
```

- Branch from `main`
- PR required to merge to `main`
- Commit message format: `type(scope): description` — e.g. `feat(bot): add /start handler with onboarding link`
- Valid types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`
- Reference the issue in the PR body: `Closes #N`

Full branching rules: [`version-control.md`](./memory/agent-guides/version-control.md)

---

## Documentation Update Rules

- Update `data-schema.md` whenever a Supabase table or column changes
- Update `techstack.md` whenever a new library is added or removed
- Update `repository-structure.md` whenever a new top-level directory or significant module is added
- Update `/PRD.md` if product scope changes (add a changelog entry at the bottom)
- Never update `CLAUDE.md` to add implementation detail — push it to the appropriate guide

---

## Keeping Root Context Small

- This file must stay under 150 lines
- If you are tempted to add detail here, add it to the relevant `/memory/agent-guides/` file and link to it
- Do not copy-paste schema, code snippets, or long lists into this file
