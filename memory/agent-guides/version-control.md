# Meridian — Version Control Strategy

> Load this file when: creating branches, writing commits, opening PRs, or resolving conflicts.

---

## Branch Strategy

```
main
├── feature/issue-1-project-scaffolding
├── feature/issue-3-supabase-schema
├── feature/issue-6-daily-brief-generation
├── fix/issue-N-short-description
└── chore/update-dependencies
```

### Rules

- `main` is always production-ready. Never commit directly to `main`.
- Every GitHub issue gets exactly one branch.
- Branch from the latest `main` unless the issue is explicitly blocked by another branch (in which case, branch from that branch and note it in the PR).
- Delete branches after the PR is merged.

### Branch naming

```
{type}/issue-{N}-{short-description}
```

| Type | When to use |
|---|---|
| `feature/` | New functionality (most issues) |
| `fix/` | Bug fix on an existing feature |
| `chore/` | Dependency updates, config changes, no code change |
| `docs/` | Documentation only |
| `refactor/` | Code restructure with no behaviour change |

**Examples:**
```
feature/issue-4-bot-start-handoff
feature/issue-6-daily-brief-generation
fix/issue-7-streak-reset-on-reentry
chore/upgrade-python-telegram-bot-v21
```

---

## Commit Message Format

```
type(scope): short description in imperative mood

Optional longer description if the why is not obvious.
```

### Types

| Type | When to use |
|---|---|
| `feat` | New user-visible feature or behaviour |
| `fix` | Bug fix |
| `refactor` | Code change with no behaviour change |
| `test` | Adding or updating tests |
| `docs` | Documentation updates |
| `chore` | Build, deps, config — no production code change |

### Scopes

| Scope | What it covers |
|---|---|
| `bot` | Changes in `/bot` |
| `web` | Changes in `/web` |
| `db` | Schema migrations |
| `ai` | Groq prompt or generation changes |
| `scheduler` | APScheduler changes |
| `ci` | CI/CD config |

### Examples

```
feat(bot): add /start handler with onboarding link generation
feat(ai): implement daily brief generation with framing rotation
fix(bot): correct streak reset logic on re-entry day
feat(web): add 5-step onboarding form with Supabase save
refactor(db): extract streak queries into dedicated module
docs(memory): update data-schema with skipped_block_indices field
chore(bot): upgrade python-telegram-bot to 21.3
```

### Rules

- Subject line: max 72 characters, no trailing period
- Use imperative mood: "add", "fix", "update" — not "added", "fixed", "updates"
- Reference the issue at the bottom of longer commit messages: `Refs #6`
- Never use generic messages: "WIP", "fix bug", "update code", "changes"

---

## Pull Request Protocol

### PR title
Match the commit format: `feat(bot): add /start handler with onboarding link generation`

### PR body template

```markdown
## What this does
[One paragraph describing the end-to-end behaviour this PR delivers]

## How to test
1. Step one
2. Step two
3. Expected result

## Acceptance criteria
- [ ] Criterion from the issue (copy from issue body)
- [ ] Criterion two

Closes #N
```

### PR rules

- Every PR closes exactly one issue (reference with `Closes #N`)
- No PR is merged with failing tests
- PR author is responsible for resolving conflicts before requesting review
- For solo development: self-review is acceptable; create the PR anyway for the record

---

## Tagging & Releases

Releases are tagged on `main` after a working milestone:

```
v0.1.0 — Phase 1 complete (dogfood: single-user bot running locally)
v0.2.0 — Phase 2 complete (multi-user, Supabase, web onboarding)
v0.3.0 — Phase 3 complete (scoreboard, re-entry, landing page, live)
```

Tag format: `vMAJOR.MINOR.PATCH` following semver.

Create a release on GitHub with:
- What was shipped
- Known limitations
- How to deploy/update

---

## `.gitignore` Rules

Both `/bot` and `/web` must ignore:

```
# Secrets
.env
.env.local
.env.*.local

# Python
__pycache__/
*.pyc
venv/
.venv/

# Node
node_modules/
.next/

# Editor
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db
```

---

## Conflict Resolution

1. Never force-push to `main`
2. If a conflict arises on a feature branch, rebase onto `main`:
   ```bash
   git fetch origin
   git rebase origin/main
   ```
3. Resolve conflicts in the feature branch, not in `main`
4. If a migration file conflicts, always keep both migrations and ensure numbering is sequential
