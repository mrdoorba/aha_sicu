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
- React keys must use stable identifiers (e.g., `kode_variasi`), never array indices — breaks on sort/filter
- Cache invalidation must be explicit across all mutation points (run, upload, run-all)
- State machine reset logic must be explicit — `useEffect` with dependencies to re-enable buttons after data changes

### Process

- Story File List must include ALL files changed on the feature branch (check git diff)
- Dev self-check before review: (1) Is every AC tested? (2) Are error paths handled with structured codes?

### Data Conventions

- Percentage values: stored as `0.5` = 0.5% (NOT fractions like 0.005) — applies across manual data, calculators, and scoring
- Indonesian number formatting: comma for thousands in output text (e.g., `IDR 26,433,781`), dot separator in input must be cleaned
- Category name mapping: Indonesian internally (scoring data), English in UI display labels — use CATEGORY_MAP constant
- Correct-course workflow must verify data format conventions between shared components (not just logic changes)

## Epic 2 Retrospective Insights (2026-02-06)

- 56 code review issues across 5 stories (19H, 22M, 15L) — all caught before production
- Recurring patterns: AC schema mismatch (3 stories), error handling gaps (3 stories), File List gaps (3 stories)
- Story 2.3 needed 2 full reviews (20 issues) — first full-stack story, established frontend patterns
- Code review issue count decreased over epic: 10 → 8 → 20 → 10 → 8 (2.3 spike was first full-stack)
- Updated docs in retro: architecture.md (SQL safety, error handling, review checklist), dev-story checklist, code-review checklist

## Epic 4 Retrospective Insights (2026-02-12)

- ~42 code review issues across 6 stories (~7/story) — slight increase from Epic 3's ~6/story
- Forward-compatible API design: Story 4.1 accepted query params (search, date_from, date_to, category) before wiring them — Stories 4.2-4.4 plugged in with zero API contract changes
- Extract shared helpers early: `_build_filter_clauses()` for conditional WHERE clauses, `escape_like()` in `db/queries/utils.py` — reduces duplication across filter stories
- Type precision: use `Literal` types (not `str`) for constrained values like sort direction, order_by fields — caught in multiple reviews
- File List in story specs often incomplete — devs discover mid-implementation that unlisted files need changes
- Accessibility gaps persist: ARIA labels, keyboard navigation still caught in reviews despite checklist
- SSE pattern reusable: `new_evaluation` event in Story 4.6 cleanly reused Epic 2's SSE infrastructure
- Epic 3 retro self-check habit (AC coverage + error handling) did not fully stick — same patterns still flagged

## Epic 3 Retrospective Insights (2026-02-11)

- ~60 code review issues across 10 stories — issue rate improved from ~11/story (Epic 2) to ~6/story
- 100% follow-through on Epic 2 retro action items (7/7) — correct-course, accessibility retrofit, all doc updates
- Recurring HIGH patterns: missing error handling (4 stories), missing AC test coverage (4 stories), state management reset bugs (2 stories)
- Pure function calculator pattern proven across all 3 calculators — easy to test, validate, maintain
- Test suite grew from 138 to 695+ (5x increase), zero regressions
- Only MND was real test data — KYPSO and SUKA were spec reference examples. Real-world validation deferred to post-deployment
- Percentage convention (0.5 = 0.5%) and category name mapping (Indonesian vs English) were gaps not caught by correct-course
- Team agreement: lightweight dev self-check (2 questions) preferred over heavy formal gates
- Epic 6 (Production Deployment & Launch) created as new epic for post-Epic 5 deployment
