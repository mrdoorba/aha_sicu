# Story 2.2: Manual Sync Trigger API

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **BD team member**,
I want **to trigger a manual sync of brand data**,
so that **I can get the latest brands without waiting for the daily auto-sync**.

## Acceptance Criteria

1. **Given** I am authenticated
   **When** I call `POST /api/v1/sync`
   **Then** the sync process starts asynchronously
   **And** return `{"status": "started", "sync_id": <id>}` immediately with HTTP 202

2. **Given** a sync is already in progress
   **When** I call `POST /api/v1/sync`
   **Then** return 409 Conflict with `{"code": "SYNC_IN_PROGRESS", "detail": "A sync is already running"}`

3. **Given** I call `GET /api/v1/sync/status`
   **When** authenticated
   **Then** return the latest sync status:
   ```json
   {
     "last_sync": "2026-02-04T10:30:00Z",
     "status": "success" | "failed" | "in_progress",
     "brands_synced": 150,
     "error_message": null,
     "sync_details": {
       "vp_sheet": { "rows_synced": 120, "status": "success" },
       "meeting_sheet": { "rows_synced": 30, "status": "success" }
     }
   }
   ```

## Tasks / Subtasks

- [x] Task 1: Add concurrent sync guard query (AC: #2)
  - [x] Add `is_sync_in_progress()` query to `backend/app/db/queries/sync_status.py`
  - [x] Query checks for any `sync_status` row where `completed_at IS NULL` (started but not finished)

- [x] Task 2: Add sync trigger schema and error code (AC: #1, #2)
  - [x] Add `SyncTriggerResponse` schema to `backend/app/modules/sync/schemas.py` with fields: `status: str`, `sync_id: int`
  - [x] Add `SYNC_IN_PROGRESS` error code to `backend/app/core/exceptions.py`

- [x] Task 3: Implement POST /api/v1/sync endpoint (AC: #1, #2)
  - [x] Add `POST /sync` route to `backend/app/modules/sync/router.py`
  - [x] Require authentication via `get_current_user` dependency
  - [x] Check for in-progress sync using `is_sync_in_progress()` — return 409 if active
  - [x] Create initial `sync_status` record (sets `started_at`, `completed_at=NULL`)
  - [x] Dispatch `run_sync()` as a FastAPI `BackgroundTask` passing the `sync_id`
  - [x] Return 202 Accepted with `{"status": "started", "sync_id": <id>}` immediately

- [x] Task 4: Refactor run_sync to accept pre-created sync_id (AC: #1)
  - [x] Modify `run_sync()` in `service.py` to accept an optional `sync_id` parameter
  - [x] When `sync_id` is provided, skip creating a new sync_status record and use the existing one
  - [x] Ensure `run_sync()` still works standalone (for future scheduler use in Story 2.5)

- [x] Task 5: Write tests (AC: #1, #2, #3)
  - [x] Unit test: `is_sync_in_progress()` returns True when incomplete sync exists
  - [x] Unit test: `is_sync_in_progress()` returns False when no active sync
  - [x] Integration test: `POST /api/v1/sync` returns 202 with sync_id
  - [x] Integration test: `POST /api/v1/sync` returns 409 when sync already in progress
  - [x] Integration test: `POST /api/v1/sync` requires authentication (401 without token)
  - [x] Integration test: `GET /api/v1/sync/status` returns updated status after sync completes

## Dev Notes

### Architecture Compliance

**API Conventions (MUST follow):**
- REST with raw responses (no wrapper) — [Source: architecture.md#API & Communication]
- Error format: `{"code": "SYNC_IN_PROGRESS", "detail": "A sync is already running", "timestamp": "..."}`
- Error codes use `SYNC_` prefix for sync operations
- All endpoints under `/api/v1/` require Bearer token authentication

**Module Pattern (MUST follow):**
- All sync code lives in `backend/app/modules/sync/` — router, schemas, service
- Router uses `APIRouter(prefix="/api/v1/sync", tags=["sync"])`
- Authentication via `Depends(get_current_user)` on every endpoint
- Business logic in `service.py`, not in router

**Async Background Processing:**
- Use FastAPI's `BackgroundTasks` for running sync asynchronously
- The `POST /sync` endpoint must return immediately (202) before sync completes
- The sync process updates `sync_status` table as it progresses
- Client polls `GET /sync/status` to check progress (SSE will be added in Story 2.4)

### Technical Implementation Details

**Concurrent Sync Guard:**
```python
# In db/queries/sync_status.py
async def is_sync_in_progress(conn) -> bool:
    """Check if any sync is currently running (started but not completed)."""
    row = await conn.fetchrow(
        "SELECT id FROM sync_status WHERE completed_at IS NULL LIMIT 1"
    )
    return row is not None
```

**POST /sync Endpoint Pattern:**
```python
# In modules/sync/router.py
@router.post("", status_code=202, response_model=SyncTriggerResponse)
async def trigger_sync(
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user),
    pool=Depends(get_db_pool),
):
    async with pool.acquire() as conn:
        if await is_sync_in_progress(conn):
            raise AppException(
                code="SYNC_IN_PROGRESS",
                detail="A sync is already running",
                status_code=409,
            )
        sync_id = await create_sync_status(conn, started_at=datetime.now(timezone.utc))

    background_tasks.add_task(run_sync, sync_id=sync_id)
    return SyncTriggerResponse(status="started", sync_id=sync_id)
```

**run_sync Refactor:**
- Current `run_sync()` creates its own sync_status record internally
- Refactor to accept optional `sync_id: int | None = None`
- If `sync_id` provided: skip creation, use existing record
- If `sync_id` not provided: create record as before (backward compatible for Story 2.5 scheduler)

### Existing Code Context (from Story 2.1)

**What already exists — DO NOT recreate:**
| Component | File | Status |
|-----------|------|--------|
| `run_sync()` orchestration | `modules/sync/service.py` | Exists — needs minor refactor for sync_id param |
| `get_latest_sync_status()` | `modules/sync/service.py` | Exists — works as-is |
| `GET /sync/status` endpoint | `modules/sync/router.py` | Exists — works as-is |
| `create_sync_status()` | `db/queries/sync_status.py` | Exists — works as-is |
| `update_sync_status()` | `db/queries/sync_status.py` | Exists — works as-is |
| `SyncStatusResponse` schema | `modules/sync/schemas.py` | Exists — already includes `sync_details` |
| `GoogleSheetsClient` | `modules/sync/sheets_client.py` | Exists — no changes needed |

**What needs to be created/modified:**
| Component | File | Action |
|-----------|------|--------|
| `is_sync_in_progress()` | `db/queries/sync_status.py` | **Add** new query function |
| `SyncTriggerResponse` | `modules/sync/schemas.py` | **Add** new schema |
| `POST /sync` endpoint | `modules/sync/router.py` | **Add** new route |
| `run_sync()` sync_id param | `modules/sync/service.py` | **Modify** to accept optional sync_id |
| `SYNC_IN_PROGRESS` code | `core/exceptions.py` | **Add** if not already handled by AppException |

### Library & Framework Requirements

| Library | Version | Usage in This Story |
|---------|---------|---------------------|
| FastAPI | existing | `BackgroundTasks`, `APIRouter`, `Depends` |
| asyncpg | existing | Database queries via connection pool |
| Pydantic | existing | `SyncTriggerResponse` schema |

**No new dependencies required** — this story uses only what is already installed.

### File Structure Requirements

**Files to modify:**
```
backend/app/modules/sync/router.py     ← Add POST /sync endpoint
backend/app/modules/sync/schemas.py    ← Add SyncTriggerResponse
backend/app/modules/sync/service.py    ← Refactor run_sync for sync_id param
backend/app/db/queries/sync_status.py  ← Add is_sync_in_progress()
```

**Files to create (tests only):**
```
backend/tests/unit/sync/test_sync_status_queries.py    ← Unit tests for is_sync_in_progress
backend/tests/integration/api/test_sync_trigger.py     ← Integration tests for POST /sync
```

**No new module directories needed** — all work is within the existing `modules/sync/` module.

### Testing Requirements

**Test Framework:** pytest (backend standard)

**Unit Tests:**
- Test `is_sync_in_progress()` with mock database connection
- Test that it returns `True` when an incomplete sync exists
- Test that it returns `False` when all syncs are completed

**Integration Tests:**
- Test `POST /api/v1/sync` returns 202 with valid auth token
- Test `POST /api/v1/sync` returns 401 without auth token
- Test `POST /api/v1/sync` returns 409 when sync is in progress
- Test response body matches `SyncTriggerResponse` schema
- Test `GET /api/v1/sync/status` reflects sync state after trigger

**Test Patterns (from Story 2.1):**
- Use `AsyncClient` (httpx) for integration tests
- Mock `GoogleSheetsClient` to avoid real API calls
- Use test database fixtures from `conftest.py`
- Authentication mocking via `get_current_user` override

### Naming Conventions (MUST FOLLOW)

| Element | Pattern | Example |
|---------|---------|---------|
| Python functions | `snake_case` | `is_sync_in_progress()`, `trigger_sync()` |
| Python classes | `PascalCase` | `SyncTriggerResponse` |
| API endpoints | plural nouns, kebab-case | `POST /api/v1/sync` |
| Error codes | `UPPER_SNAKE` with prefix | `SYNC_IN_PROGRESS` |
| JSON response fields | `snake_case` | `sync_id`, `sync_details` |
| Test files | `test_*.py` | `test_sync_trigger.py` |

### Anti-Patterns to Avoid

1. **DO NOT** run `run_sync()` synchronously in the request handler — it must be a background task
2. **DO NOT** create a new module or service file — extend existing `modules/sync/` files
3. **DO NOT** duplicate the sync orchestration logic — reuse `run_sync()` from service.py
4. **DO NOT** add polling/SSE logic — that belongs to Story 2.4
5. **DO NOT** add a frontend "Sync Now" button — that belongs to Story 2.3
6. **DO NOT** add Cloud Scheduler integration — that belongs to Story 2.5
7. **DO NOT** wrap responses in extra envelopes — use raw response format per architecture

### Previous Story Intelligence

**From Story 2.1 (Google Sheets Sync Backend):**
- `run_sync()` already handles dual-sheet orchestration (VP + Meeting) with partial failure tolerance
- `sync_status` table has `sync_details` JSONB column for per-sheet breakdown (added in migration 005)
- Error handling uses `AppException` pattern with structured codes
- All 31 tests pass — ensure no regressions
- Code review fixed: lambda closure in sheets_client, centralized table validation in brands.py, SA naming to `aha-sicu-sheets-sa`
- `get_current_user` dependency is available and tested for authentication

**From Story 1.2 (Firebase Auth Backend):**
- Auth middleware validates Firebase JWT tokens
- `get_current_user` returns user context with uid, email, role
- 401 errors use `AUTH_TOKEN_MISSING` and `AUTH_TOKEN_INVALID` codes

### Git Intelligence Summary

Recent commits show:
- Story 2.1 complete with code review fixes merged (`6075489`, `3d10803`)
- shadcn/ui setup complete for frontend (`abf2d68`, `e8b8b9b`, `063fc29`)
- Sprint change proposal architecture updates merged (`b254162`, `f41fc95`)
- All code follows established patterns and naming conventions
- Test suite is green — 31 existing sync tests to preserve

### Project Structure Notes

- This story is **backend-only** — no frontend changes
- Fully aligned with the module structure: `modules/sync/{router,schemas,service}.py`
- Database queries go in `db/queries/sync_status.py` (existing file)
- Tests follow established pattern: `tests/unit/sync/` and `tests/integration/api/`
- No infrastructure/Terraform changes needed

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 2.2: Manual Sync Trigger API]
- [Source: _bmad-output/planning-artifacts/architecture.md#API & Communication]
- [Source: _bmad-output/planning-artifacts/architecture.md#Implementation Patterns & Consistency Rules]
- [Source: _bmad-output/planning-artifacts/architecture.md#Module Boundaries]
- [Source: _bmad-output/planning-artifacts/prd.md#Brand Data Management — FR2]
- [Source: _bmad-output/implementation-artifacts/2-1-google-sheets-sync-backend.md#Dev Notes]
- [Source: _bmad-output/implementation-artifacts/2-1-google-sheets-sync-backend.md#Dev Agent Record]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6 (claude-opus-4-6)

### Debug Log References

No debug issues encountered. All tasks implemented cleanly following red-green-refactor cycle.

### Completion Notes List

- **Task 1:** Added `is_sync_in_progress()` query to `sync_status.py` — checks for rows with `completed_at IS NULL`. 2 unit tests added and passing.
- **Task 2:** Added `SyncTriggerResponse` Pydantic schema with `status: str` and `sync_id: int` fields. `SYNC_IN_PROGRESS` error code handled via existing `SyncException` class (no changes to exceptions.py needed).
- **Task 3:** Implemented `POST /api/v1/sync` endpoint in router.py — uses `get_current_user` for auth, `is_sync_in_progress()` for 409 guard, creates sync_status record, dispatches `run_sync` as `BackgroundTask`, returns 202 with sync_id. 6 integration tests added and passing.
- **Task 4:** Refactored `run_sync()` to accept optional `sync_id: int | None = None`. When provided, skips creating a new sync_status record. Backward compatible — standalone calls still create their own record (for Story 2.5 scheduler). 2 unit tests added for both paths.
- **Task 5:** All specified tests written inline with Tasks 1-4 using TDD. Total: 2 unit tests + 6 integration tests + 2 service tests = 10 new tests. Full suite: 44 tests, 0 failures, 0 regressions.

### Change Log

- 2026-02-06: Implemented Story 2.2 — Manual Sync Trigger API. Added POST /sync endpoint (202/409), is_sync_in_progress() guard query, SyncTriggerResponse schema, run_sync() sync_id refactor. 10 new tests, 44 total passing.

### File List

**Files Modified:**
- `backend/app/modules/sync/router.py` — Added `POST /sync` endpoint with auth, sync guard, and background task dispatch
- `backend/app/modules/sync/schemas.py` — Added `SyncTriggerResponse` schema
- `backend/app/modules/sync/service.py` — Refactored `run_sync()` to accept optional `sync_id` parameter
- `backend/app/db/queries/sync_status.py` — Added `is_sync_in_progress()` query function

**Files Created:**
- `backend/tests/unit/sync/test_sync_status_queries.py` — Unit tests for `is_sync_in_progress()`
- `backend/tests/integration/api/test_sync_trigger.py` — Integration tests for `POST /sync` and schema validation
