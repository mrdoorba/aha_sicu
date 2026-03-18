# CLAUDE.md
## Git Workflow
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
---

## Test-Driven Development

**Cycle:** Red → Green → Refactor. AAA structure: Arrange → Act → Assert. One assert per test.

**Naming:** `test_<expected>_when_<condition>` (backend) / `should <expected> when <condition>` (frontend)

**Runners & tools:**
- Backend: **pytest** + pytest-asyncio. Tests in `backend/tests/`.
- Frontend: **vitest** + Testing Library + jsdom. Test files colocated (`*.test.tsx`).

**Known gotchas:**
- Rules query function is `get_rules_by_template_and_marketplace` (renamed from `get_rules_by_template`) — mocks must use the new name
- `generate_score` passes `marketplace` as a **positional** arg — mock assertions must match: `(conn, "default", "TH")` not `(conn, "default", marketplace="TH")`
- `ScoringResponse` required string fields (`marketing_estimation`, `marketing_percentage`, `marketing_budget`, `closing_message`, `email_subject`, `email_body`) must be `""` not `None` when mocking

---

## SOLID Principles

Apply SOLID where it reduces complexity — not as ritual. Prefer composition over inheritance.

---

## Code Style & Conventions

### General Principles

Prioritize: simplicity, robustness, performance, correctness. Avoid over-engineering. Stay consistent with existing patterns unless they're clearly suboptimal — then improve and flag the change.

### Backend

- Type hints on all function signatures

### Frontend

- TypeScript strict mode

### Python Tooling

- Use **`uv`** for all Python-related tasks: dependency management, virtual environments, running scripts, and installing packages
- `uv run` to execute scripts, `uv add` / `uv remove` for dependencies, `uv sync` to install, `uv venv` for environments

---

## Key Paths

- Scoring engine: `backend/app/calculators/scoring/`
- Marketplace constants: `backend/app/core/marketplace.py`
- Email templates: `backend/app/modules/email/template.py`
- DB migrations: `backend/alembic/versions/`
- i18n locales: `frontend/src/locales/{id,en,th}.json`
- Translation utility: `frontend/src/utils/renderTranslatable.ts`
- Category mapping: `frontend/src/lib/categoryMap.ts`

---

## Running

- Backend tests: `cd backend && uv run pytest tests/ -x`
- Frontend tests: `cd frontend && npm test` (vitest in watch mode) / `npm run test:run` (single run)
- Dev stack: `docker-compose up`
- Backend lint: `cd backend && uv run ruff check .`
- Frontend lint: `cd frontend && npm run lint`

---

## Error Handling

### Backend

- Custom `AppException(code, detail, status_code)` in `app/core/exceptions.py` — caught by global handler in `app/core/middleware.py`, returns structured JSON: `{ code, detail, timestamp }`
- Use `raise AppException(...)` for domain/business errors, not raw `HTTPException`
- Pydantic `ValueError` in schemas for validation — FastAPI converts to 422 automatically

### Frontend

- Sonner toasts (`toast.success()` / `toast.error()`) for user-facing feedback on mutations
- React Query `onError` callbacks for API mutation failures
- No global ErrorBoundary — errors are handled per-component/per-hook
