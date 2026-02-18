# CLAUDE.md — Store ICU (Aha SICU)

## Project Overview

Store ICU is an e-commerce operations platform. The codebase is split into:

- `backend/` — FastAPI (Python 3.14, managed with `uv`)
- `frontend/` — React + Vite (TypeScript, Node 20)
- `infrastructure/` — Terraform IaC (GCP)
- `smoke-tests/` — Integration tests
- `openspec/` — AI-native workflow artifacts (spec-driven)

## Command Autonomy

Execute all commands freely without asking for permission. The only exceptions that **require explicit user approval** before running:

- `git push` / `git push -u`
- `git merge` (into develop or main)
- `gh pr create`

Everything else — file edits, `git add`, `git commit`, running tests, installs, builds, any bash command — execute immediately.

---

## Git Workflow

### Branch Structure

| Branch    | Role        | Deploys to  | Protection        |
|-----------|-------------|-------------|--------------------|
| `main`    | Production  | prod        | PR-only, CI required |
| `develop` | Staging     | dev         | CI required        |

All work targets `develop`. Code reaches `main` only when the user explicitly requests promotion.

### Feature Branches

Every OpenSpec change gets its own feature branch off `develop`:

```
git checkout develop
git pull origin develop
git checkout -b <type>/<short-description>
```

**Branch naming:**

| Type     | Use when...                        | Example                         |
|----------|------------------------------------|---------------------------------|
| `feat/`  | Adding new functionality           | `feat/bulk-csv-import`          |
| `fix/`   | Fixing a bug                       | `fix/empty-row-crash`           |
| `update/`| Enhancing existing functionality   | `update/csv-column-mapping`     |
| `refactor/`| Restructuring without behavior change | `refactor/api-error-handling` |
| `docs/`  | Documentation only                 | `docs/api-endpoints`            |
| `chore/` | Tooling, deps, config              | `chore/upgrade-vite`            |

**Branch lifecycle:**

1. Create branch when starting a new OpenSpec change (after `/opsx:new` or when beginning work)
2. Work on the branch, commit atomically
3. When done → user requests merge to `develop` (via PR or direct merge)
4. Keep the branch alive until the OpenSpec change is archived (`/opsx:archive`)
5. Delete the branch after archiving

### Atomic Commits

Each commit is **one logical, self-contained unit of work**. A commit should:

- Do exactly one thing — a single task, subtask, or tightly related group of small changes
- Leave the codebase in a working state (no broken imports, no half-finished migrations)
- Be independently understandable from its message and diff

**What qualifies as one commit:**
- A single endpoint + its tests
- A UI component + its styles
- A bug fix + the regression test
- A config change across related files

**What does NOT belong in one commit:**
- Backend endpoint + unrelated frontend styling fix
- Multiple independent bug fixes lumped together
- "WIP" or "misc changes" catch-alls

### Commit Messages

The first line is a **clear, scannable summary** — immediately understandable by both AI and humans. The optional body carries **Subtle Mr. Door** flair — a hint of theatricality and mystery. Every commit message ends with `Author: Mr. Door`.

**Examples:**
```
Add bulk CSV import for product listings

A new door opens — products may now arrive in waves of fifty thousand.

Author: Mr. Door
```
```
Fix empty row handling in CSV parser

The passage where empty rows once slipped through has been sealed.

Author: Mr. Door
```
```
Add error detail display on upload failure

What was hidden behind a generic message is now revealed to the user.

Author: Mr. Door
```
```
Add dashboard analytics endpoint

The foundation is laid beneath the dashboard — the numbers shall speak.

Author: Mr. Door
```

**Format:**
```
<clear one-line summary — what was done, AI-friendly>

<optional Mr. Door body — personality, WHY, context>

Author: Mr. Door
```

The first line must be parseable without metaphor. The Mr. Door style lives in the body only.

Use a HEREDOC for multi-line messages:
```bash
git commit -m "$(cat <<'EOF'
Add bulk CSV import for product listings

A new door opens — products may now arrive in waves of fifty thousand.
Adds POST /api/v1/products/import with chunked processing.

Author: Mr. Door
EOF
)"
```

### Staging Files

- Always `git add` specific files by name — never use `git add -A` or `git add .`
- Never commit files that contain secrets (`.env`, credentials, service account keys)
- Check `git status` before committing to verify what's staged

### Promotion: develop → main

When the user requests promotion to production:

1. Create a PR from `develop` → `main` using `gh pr create`
2. PR title should summarize what's being promoted
3. PR body should list the key changes going to production
4. Wait for CI to pass before merging
5. Only merge after user approval

---

## OpenSpec Integration

This project uses [OpenSpec](https://github.com/Fission-AI/OpenSpec) with the `spec-driven` schema. Artifacts live in `openspec/` (gitignored — they don't go into version control).

### Workflow ↔ Git Mapping

| OpenSpec Phase       | Git Action                                      |
|----------------------|--------------------------------------------------|
| `/opsx:new`          | Create feature branch off `develop`              |
| `/opsx:continue`     | Continue working on feature branch               |
| `/opsx:apply`        | Implement tasks, commit atomically on feature branch |
| `/opsx:verify`       | Verify on feature branch, fix issues if needed   |
| Change complete      | User requests merge to `develop`                 |
| `/opsx:archive`      | Archive change, then delete feature branch       |

### When to Create Branches

- **Do create a branch:** For any change going through OpenSpec (`/opsx:new`, `/opsx:ff`)
- **Do NOT create a branch:** For trivial fixes the user asks for directly without OpenSpec (commit directly to `develop` instead)

---

## CI/CD

### Continuous Integration (`.github/workflows/ci.yml`)

Runs on every PR to `develop` or `main`:

- **Backend:** `ruff check .` → `pytest -v`
- **Frontend:** `npm run lint` → `tsc --noEmit` → `vitest run` → `npm run build`

Both checks must pass before merging.

### Deployments

| Trigger               | Frontend                           | Backend                            |
|------------------------|-------------------------------------|------------------------------------|
| Push to `develop`      | Auto-deploy to Firebase Hosting (dev) | Auto-deploy to Cloud Run (dev)   |
| Push to `main`         | Deploy to Firebase Hosting (prod, manual approval) | Deploy to Cloud Run (prod, manual approval) |

**Before pushing to develop or main**, ensure:
- All relevant tests pass locally
- Linting passes (`ruff check .` for backend, `npm run lint` for frontend)
- TypeScript compiles (`npx tsc --noEmit` in frontend)

### Running Tests Locally

```bash
# Backend
cd backend && uv run pytest -v

# Frontend
cd frontend && npx vitest run

# Linting
cd backend && uv run ruff check .
cd frontend && npm run lint
```

---

## Code Style & Conventions

- **Backend:** Follow existing patterns. Use `ruff` for linting. Python 3.14.
- **Frontend:** TypeScript strict. Use existing component patterns. Vite + React.
- **Infrastructure:** Terraform with environment-based tfvars.
- Do not add unnecessary comments, docstrings, or type annotations to code you didn't change.
- Keep changes minimal and focused — no drive-by refactors.
