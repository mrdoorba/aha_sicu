# GEMINI.md — Store ICU (Aha SICU)

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
git checkout develop && git pull origin develop
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

Each commit is **one logical, self-contained unit of work** — does exactly one thing, leaves the codebase working, and is independently understandable from its message and diff.

### Commit Messages

The first line is a **clear, scannable summary** — no metaphor, immediately parseable. The optional body carries **Subtle Mr. Door** flair. Every commit ends with `Author: Mr. Door`.

**Format:**
```
<clear one-line summary — what was done>

<optional Mr. Door body — personality, WHY, context>

Author: Mr. Door
```

**Example:**
```
Add bulk CSV import for product listings

A new door opens — products may now arrive in waves of fifty thousand.
Adds POST /api/v1/products/import with chunked processing.

Author: Mr. Door
```

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

### Running Tests Locally

```bash
# Backend (from backend/)
uv run pytest -v
uv run ruff check .

# Frontend (from frontend/)
npx vitest run
npm run lint
```

---

## Code Style & Conventions

- **Backend:** Follow existing patterns. Use `ruff` for linting. Python 3.14.
- **Frontend:** TypeScript strict. Use existing component patterns. Vite + React.
- **Infrastructure:** Terraform with environment-based tfvars.
