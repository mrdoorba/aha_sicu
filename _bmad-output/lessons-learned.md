# Lessons Learned

Accumulated knowledge from code reviews, retrospectives, and implementation experience.

## Project Stack

- Backend: FastAPI + asyncpg, Neon PostgreSQL
- Frontend: React + Vite + TanStack Query
- Backend modules: `modules/{feature}/{router,schemas,service}.py`
- Frontend: hooks in `hooks/`, components in `components/{feature}/`, pages in `pages/`
- API client: `openapi-fetch` with auth middleware in `services/apiClient.ts`

## Running Tests

- Backend: `cd backend && uv run python -m pytest -v`
- Frontend: `cd frontend && npx vitest run --reporter=verbose`
- Python not on PATH directly — must use `uv run python -m pytest`

## Common Code Review Findings

### Backend (Python / FastAPI)

- ILIKE queries MUST include `ESCAPE '\'` when using `_escape_like()` helper
- Search parameters need `max_length` validation on Query params
- Exception chaining: always `raise ... from e` — never lose original traceback
- Never bare `except` that swallows errors — always log or re-raise
- Table name validation: use `_VALID_TABLES` frozenset + `_validate_table()` helper for dynamic table names
- Response schemas must match ACs field-by-field (names, types, structure) — verify before marking done

### Frontend (React / TypeScript)

- Frontend hooks must use `apiClient.ts` (openapi-fetch), never raw `fetch()`
- Error handling in TanStack Query queryFn: throw errors, don't swallow them
- Type definitions exist in both `apiClient.ts` (paths) and hooks — keep them in sync

### Process

- Story File List must include ALL files changed on the feature branch (check git diff)

## Epic 2 Retrospective Insights (2026-02-06)

- 56 code review issues across 5 stories (19H, 22M, 15L) — all caught before production
- Recurring patterns: AC schema mismatch (3 stories), error handling gaps (3 stories), File List gaps (3 stories)
- Story 2.3 needed 2 full reviews (20 issues) — first full-stack story, established frontend patterns
- Code review issue count decreased over epic: 10 → 8 → 20 → 10 → 8 (2.3 spike was first full-stack)
- Updated docs in retro: architecture.md (SQL safety, error handling, review checklist), dev-story checklist, code-review checklist
