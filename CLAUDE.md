# CLAUDE.md
## Git Workflow

### Branch Structure

| Branch    | Role        | Deploys to  | Protection        |
|-----------|-------------|-------------|--------------------|
| `main`    | Production  | prod        | PR-only, CI required |
| `develop` | Staging     | dev         | CI required        |

All work targets `develop`. Code reaches `main` only when the user explicitly requests promotion.

### Atomic Commits

Each commit is **one logical, self-contained unit of work** — does exactly one thing, leaves the codebase working, and is independently understandable from its message and diff.

### Commit Messages

The first line is a **clear, scannable summary** — no metaphor, immediately parseable. The optional body carries **Subtle Mr. Door** from the Lord of Mysteries series novel flair. Every commit ends with `Author: Mr. Door`.

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

### General Principles

Prioritize: simplicity, robustness, performance, correctness. Avoid over-engineering.

### Backend

- Type hints on all function signatures
- Stay consistent with existing patterns unless they're clearly suboptimal — then improve and flag the change

### Frontend

- TypeScript strict mode
- Stay consistent with existing patterns unless they're clearly suboptimal — then improve and flag the change
- Test files colocated with source (`*.test.tsx`)

### Infrastructure

- Stay consistent with existing patterns unless they're clearly suboptimal — then improve and flag the change
