# Story 4.6: Real-Time New Evaluation Notifications

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **BD team member**,
I want **to see when new evaluations are saved by teammates**,
so that **I stay informed without refreshing**.

## Acceptance Criteria

1. **Backend broadcasts `new_evaluation` SSE event after save**
   **Given** a user saves a new evaluation via `POST /api/v1/evaluations/brands/{brand_id}/save`
   **When** the evaluation is successfully inserted into the database
   **Then** the server broadcasts `event: new_evaluation` via the existing `sync_broadcaster` with data:
   ```json
   {
     "evaluation_id": 123,
     "brand_name": "Nike",
     "score": 78.0,
     "evaluator": "rina@company.com",
     "created_at": "2026-02-04T10:30:00Z"
   }
   ```
   **And** the broadcast does NOT block the save response (fire-and-forget after successful insert)
   **And** the broadcast is NOT sent if the save fails (brand not found, DB error)

2. **Frontend shows toast notification for new evaluations from other users**
   **Given** I am connected to the SSE endpoint (`GET /api/v1/events`)
   **When** a `new_evaluation` event is received
   **Then** if the evaluator is NOT the current logged-in user, show a toast notification:
   `"New evaluation: {brand_name} ({score}) by {evaluator_first_name}"`
   **And** the toast auto-dismisses after 5 seconds
   **And** if the evaluator IS the current user, skip the toast (they already have save confirmation)

3. **Frontend invalidates evaluation history queries on new_evaluation event**
   **Given** a `new_evaluation` event is received (from any user, including self)
   **When** the SSE hook processes the event
   **Then** invalidate all TanStack Query keys matching `['evaluations', ...]`
   **And** if the user is on the History page, the list auto-refreshes with the new evaluation

## Tasks / Subtasks

- [x] Task 1: Add SSE broadcast to save_evaluation service (AC: #1)
  - [x] 1.1 Import `sync_broadcaster` from `app.services.event_broadcaster` in `modules/evaluations/service.py`
  - [x] 1.2 Add `evaluator_email: str` parameter to `save_evaluation()` function signature
  - [x] 1.3 Extract `brand_name` from the existing `brand` dict returned by `brand_queries.get_brand_by_id()` (already called for validation at line 269)
  - [x] 1.4 After the transaction block succeeds (line 287), broadcast `new_evaluation` event with: evaluation_id, brand_name, score, evaluator, created_at
  - [x] 1.5 Wrap broadcast in try/except to prevent broadcast failures from affecting save response

- [x] Task 2: Pass evaluator_email from router to service (AC: #1)
  - [x] 2.1 Update the `save_evaluation_endpoint()` in `router.py` (line 292) to pass `evaluator_email=current_user["email"]`

- [x] Task 3: Write backend tests (AC: #1)
  - [x] 3.1 Test that `save_evaluation` broadcasts `new_evaluation` event on success
  - [x] 3.2 Test that broadcast payload includes all required fields (evaluation_id, brand_name, score, evaluator, created_at)
  - [x] 3.3 Test that broadcast is NOT called when brand_id doesn't exist (404 path)
  - [x] 3.4 Test that broadcast failure does not prevent save response from returning

- [x] Task 4: Add `new_evaluation` event listener in useSSE.ts (AC: #2, #3)
  - [x] 4.1 Add `addEventListener('new_evaluation', ...)` in the `connect()` function (after the existing `sync_status` listener at line 66)
  - [x] 4.2 Parse `event.data` as JSON to extract `brand_name`, `score`, `evaluator`
  - [x] 4.3 Invalidate queries with key prefix `['evaluations']` to refresh history list
  - [x] 4.4 Accept an optional `currentUserEmail` parameter (or use a ref) to compare against event `evaluator`
  - [x] 4.5 If evaluator !== currentUserEmail, call `toast.info(...)` with notification message
  - [x] 4.6 Import `toast` from `sonner` (already installed and mounted in App.tsx)

- [x] Task 5: Pass current user email to useSSE hook (AC: #2)
  - [x] 5.1 In the component that mounts `useSSE()` (e.g., `App.tsx` or layout), pass the current user's email from AuthContext
  - [x] 5.2 Store email in a ref inside useSSE to avoid stale closures (follow existing `queryClientRef` pattern)

- [x] Task 6: Write frontend tests (AC: #2, #3)
  - [x] 6.1 Test that useSSE registers a `new_evaluation` event listener
  - [x] 6.2 Test that evaluations queries are invalidated when new_evaluation event fires
  - [x] 6.3 Test that toast notification appears for events from other users
  - [x] 6.4 Test that toast does NOT appear for events from the current user
  - [x] 6.5 Test that malformed event data is handled gracefully (no crash)

## Dev Notes

### Story Context — Final Story of Epic 4 (Evaluation History & Search)

This is the last story in Epic 4. It adds real-time notifications when teammates save new evaluations, completing the collaborative experience. The SSE infrastructure is **already fully operational** from Story 2.4 — this story reuses it with a new event type.

**Cross-story context within Epic 4:**
- Story 4.1 (done): Base history list with pagination + sorting
- Story 4.2 (done): Brand name search
- Story 4.3 (done): Date range filter
- Story 4.4 (done): Category filter
- Story 4.5 (done): Evaluation detail view at `/history/:id`
- **Story 4.6 (this): SSE `new_evaluation` event — toast notification + auto-refresh history list**

**Scope is intentionally small.** The entire SSE pipeline exists. We're adding:
1. One `broadcast()` call in the backend save path
2. One `addEventListener()` in the frontend SSE hook
3. One `toast.info()` call

### Backend — Broadcast in save_evaluation()

**File:** `backend/app/modules/evaluations/service.py`

The `save_evaluation()` function (lines 247-296) already:
- Validates brand exists via `brand_queries.get_brand_by_id()` → the returned `brand` dict has `brand_name`
- Inserts the evaluation → the returned `row` dict has `id` and `created_at`

**Add broadcast AFTER the transaction block succeeds:**

```python
from app.services.event_broadcaster import sync_broadcaster

async def save_evaluation(
    brand_id: int,
    user_id: int,
    template: str,
    final_score: float,
    verdict: str,
    score_breakdown: list[dict],
    calculator_results: dict,
    manual_inputs: dict,
    rule_version: int = 1,
    email_output: str | None = None,
    evaluator_email: str = "",  # NEW — passed from router
) -> SaveEvaluationResponse:
    async with db.connection() as conn:
        async with conn.transaction():
            brand = await brand_queries.get_brand_by_id(conn, brand_id)
            if not brand:
                raise AppException(...)

            row = await eval_queries.insert_evaluation(conn, ...)

    # Broadcast OUTSIDE the transaction — save already committed
    try:
        await sync_broadcaster.broadcast(
            "new_evaluation",
            {
                "evaluation_id": row["id"],
                "brand_name": brand["brand_name"],
                "score": final_score,
                "evaluator": evaluator_email,
                "created_at": row["created_at"].isoformat(),
            },
        )
    except Exception:
        logging.getLogger(__name__).warning(
            "Failed to broadcast new_evaluation event", exc_info=True
        )

    return SaveEvaluationResponse(...)
```

**Critical: Broadcast OUTSIDE the transaction.** If broadcast fails, the save is already committed. Wrapping in try/except ensures broadcast errors never affect the user's save operation.

**`brand["brand_name"]` availability:** `brand_queries.get_brand_by_id()` returns `dict | None` with the full row. Check the return includes `brand_name` — it should, since `brand_vp_data` has `brand_name` as a column.

### Backend — Router Change

**File:** `backend/app/modules/evaluations/router.py` (lines 277-303)

Only change: pass `evaluator_email` from `current_user`:

```python
return await save_evaluation(
    brand_id=brand_id,
    user_id=current_user["id"],
    evaluator_email=current_user["email"],  # NEW
    template=body.template,
    ...
)
```

### Frontend — useSSE.ts Modification

**File:** `frontend/src/hooks/useSSE.ts`

**Approach:** Add `new_evaluation` event listener alongside the existing `sync_status` listener. The hook needs the current user's email to suppress self-notifications.

**Option A (recommended): Add `currentUserEmail` parameter:**

```typescript
export function useSSE(currentUserEmail?: string) {
  // ...existing code...
  const currentUserEmailRef = useRef(currentUserEmail);
  currentUserEmailRef.current = currentUserEmail;

  // Inside connect(), after the sync_status listener:
  es.addEventListener('new_evaluation', (event: MessageEvent) => {
    // Always invalidate — history list should refresh for any new evaluation
    queryClientRef.current.invalidateQueries({ queryKey: ['evaluations'] });

    // Show toast only for OTHER users' evaluations
    try {
      const data = JSON.parse(event.data);
      if (data.evaluator && data.evaluator !== currentUserEmailRef.current) {
        const name = data.evaluator.split('@')[0]; // "rina" from "rina@company.com"
        toast.info(`New evaluation: ${data.brand_name} (${data.score}) by ${name}`);
      }
    } catch {
      // Malformed event data — ignore, query invalidation already fired
    }
  });
}
```

**Caller update:** Where `useSSE()` is mounted (likely `SyncStatus.tsx` or a layout component), pass the current user's email:

```typescript
const { user } = useAuth();
const { connectionState } = useSSE(user?.email);
```

**Why this approach:** Minimal change. The hook already uses refs for mutable state. Adding one more ref for email follows the existing pattern. The toast fires immediately from the SSE event data — no additional API call needed.

**Query invalidation key:** Use `{ queryKey: ['evaluations'] }` which invalidates ALL evaluation queries (list with any filter combination). The `useEvaluationHistory` hook uses `['evaluations', page, limit, ...]` — TanStack Query's `invalidateQueries` with a prefix key matches all of these.

### Frontend — Toast Library

**Already installed and configured:**
- Library: `sonner` (toast notifications)
- Global mount: `<Toaster />` in `App.tsx` (line 70)
- Import: `import { toast } from 'sonner'`
- Auto-dismiss: Default 4 seconds, can override with `{ duration: 5000 }`
- Used elsewhere: clipboard copy in EvaluationDetailPage

### Frontend — useSSE Mount Location

The `useSSE()` hook is currently called in components that need SSE. Check where it's mounted:
- Likely in `SyncStatus.tsx` (which uses `connectionState`)
- The hook needs to be mounted on any page where notifications are desired

**Recommendation:** Keep the existing mount point. Since `SyncStatus` is rendered in the Header/Layout (visible on all authenticated pages), the SSE connection is active app-wide. The `new_evaluation` listener will fire on any page.

### Existing Code to Integrate With

**Backend (modify):**
- `backend/app/modules/evaluations/service.py` — Add broadcaster import, add `evaluator_email` param, add broadcast call after save
- `backend/app/modules/evaluations/router.py` — Pass `evaluator_email=current_user["email"]` to save_evaluation

**Frontend (modify):**
- `frontend/src/hooks/useSSE.ts` — Add `new_evaluation` listener, add `currentUserEmail` param, add toast
- Component mounting `useSSE()` — Pass current user email

**No new files needed.** All changes are additions to existing files.

### Architecture Compliance

**Backend Pattern (MUST follow):**
- `sync_broadcaster.broadcast("new_evaluation", {...})` — follows the `sync_status` event pattern exactly
- Broadcast outside transaction — save is committed before broadcast attempt
- Try/except around broadcast — never fail the save operation due to SSE
- `evaluator_email` as function param — router has the data, passes it down (follows existing pattern of passing user_id)
- Use logging for broadcast failures — `logger.warning(...)` with `exc_info=True`

**Frontend Pattern (MUST follow):**
- `es.addEventListener('new_evaluation', ...)` — follows existing `sync_status` pattern
- `queryClientRef.current.invalidateQueries(...)` — uses ref to avoid stale closures
- `toast.info(...)` from `sonner` — already used in the codebase
- Parse event data in try/catch — malformed data must not crash the app
- Compare evaluator email to suppress self-notifications

### Library & Framework Requirements

| Library | Version | Usage in This Story | Status |
|---------|---------|---------------------|--------|
| `app.services.event_broadcaster` | internal | `sync_broadcaster.broadcast()` | Exists |
| `sse-starlette` | existing | SSE endpoint (no changes) | Installed |
| `sonner` | existing | `toast.info()` for notifications | Installed |
| `@tanstack/react-query` | v5 (existing) | `invalidateQueries()` | Installed |

**No new dependencies required.**

### Project Structure Notes

**Modified files only:**
```
backend/app/modules/evaluations/service.py   -- Add broadcast after save_evaluation
backend/app/modules/evaluations/router.py    -- Pass evaluator_email to save_evaluation
frontend/src/hooks/useSSE.ts                 -- Add new_evaluation listener + toast
```

**Test files (new or modified):**
```
backend/tests/integration/api/test_evaluation_save_broadcast.py  -- New: broadcast tests
frontend/src/hooks/useSSE.test.ts                                -- New or modified: SSE listener tests
```

**Alignment with unified project structure:**
- No structural changes — modifications only to existing module files
- Backend follows service-layer broadcast pattern (same as sync module)
- Frontend follows SSE hook event listener pattern (same as sync_status)

### Testing Requirements

**Backend Tests (pytest):**

| Test | AC | Description |
|------|-----|-------------|
| `test_save_evaluation_broadcasts_new_evaluation` | #1 | After successful save, sync_broadcaster.broadcast is called with "new_evaluation" event |
| `test_broadcast_payload_fields` | #1 | Broadcast data includes evaluation_id, brand_name, score, evaluator, created_at |
| `test_no_broadcast_on_brand_not_found` | #1 | When brand doesn't exist (404), no broadcast call |
| `test_broadcast_failure_does_not_block_save` | #1 | When broadcast raises, save still returns successfully |

**Testing approach:** Mock `sync_broadcaster.broadcast` in the test to verify it's called with correct args. The unit/integration tests for `save_evaluation` should patch the broadcaster.

**Frontend Tests (vitest):**

| Test | AC | Description |
|------|-----|-------------|
| `registers new_evaluation event listener` | #2, #3 | EventSource has addEventListener called with 'new_evaluation' |
| `invalidates evaluations queries on event` | #3 | queryClient.invalidateQueries called with ['evaluations'] key |
| `shows toast for other user event` | #2 | toast.info called when evaluator !== current user |
| `skips toast for self event` | #2 | toast.info NOT called when evaluator === current user |
| `handles malformed event data` | #2 | No crash when event.data is not valid JSON |

**Run commands:**
- Backend: `cd backend && uv run python -m pytest tests/integration/api/test_evaluation_save_broadcast.py -v`
- Frontend: `cd frontend && npx vitest run src/hooks/useSSE.test.ts --reporter=verbose`

### Previous Story Intelligence

**From Story 4.5 (Evaluation Detail View) — Direct predecessor:**
- Detail view accessible at `/history/:id` — toast can deep-link to new evaluation
- All Epic 4 features operational: list, search, date filter, category filter, detail view
- 522 backend tests, 258 frontend tests — all passing
- Sprint status: all 4.1-4.5 done, 4.6 is backlog (will update to ready-for-dev)

**From Story 4.5 Dev Notes — forward guidance:**
> "The SSE `new_evaluation` event should include the evaluation `id` so the toast can link to `/history/{id}` for quick navigation to the new evaluation's detail view."

**From Story 2.4 (SSE infrastructure) — Foundation:**
- `EventBroadcaster` singleton at `backend/app/services/event_broadcaster.py`
- SSE endpoint at `backend/app/modules/events/router.py` — auth via query param token
- Frontend `useSSE.ts` hook with reconnection, exponential backoff, query invalidation pattern
- `sync_status` event fully operational — `new_evaluation` follows the exact same pattern

**From Lessons Learned:**
- Response schemas must match ACs field-by-field
- File List must include ALL changed files
- Backend tests: `uv run python -m pytest` (not `pytest` directly)
- Frontend hooks MUST use existing patterns (refs for mutable state, try/catch for data parsing)
- Cache invalidation must be explicit across all mutation points

### Git Intelligence

**Recent commits (Story 4.5 completed and merged to develop):**
```
da27316 Merge feature/4-5-evaluation-detail-view into develop
06b9ed2 Fix code review findings: Literal types, empty state message, None check (Story 4.5)
27304cc Mark Story 4.5 complete — all tasks done, status → review
d68ec23 Add frontend evaluation detail page with tests (Tasks 6-9)
198bc27 Add backend evaluation detail endpoint with tests (Tasks 1-5)
```

**Patterns to follow:**
- Feature branch: `feature/4-6-real-time-new-evaluation-notifications`
- Branch from `develop` (current branch)
- Atomic commits: backend changes first, then frontend changes
- Tests committed alongside implementation

### How This Completes Epic 4

Story 4.6 is the **final story in Epic 4**. After this:
1. Epic 4 retrospective can be completed
2. Epic 4 status should move from `in-progress` to `done` in sprint-status.yaml (manual step after retrospective)
3. Epic 5 (Rule Configuration) becomes the next active epic

| Story | Status | What It Delivered |
|-------|--------|-------------------|
| 4.1 | done | Evaluation history list with pagination |
| 4.2 | done | Search by brand name |
| 4.3 | done | Filter by date range |
| 4.4 | done | Filter by category |
| 4.5 | done | Evaluation detail view |
| **4.6** | **this** | **Real-time notifications for new evaluations** |

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-4.6 — Story ACs, FR35: display new evaluations without page refresh]
- [Source: _bmad-output/planning-artifacts/architecture.md#API-Communication — SSE endpoint `/api/v1/events`, event types: sync_status, new_evaluation]
- [Source: _bmad-output/planning-artifacts/architecture.md#Real-Time — Server-Sent Events for one-way server→client push]
- [Source: _bmad-output/planning-artifacts/prd.md — FR35: System can display new evaluations to other users without page refresh, NFR5: Real-time update propagation <500ms]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Feedback-Patterns — Toast notifications: bottom-right, 3-5s auto-dismiss, non-blocking]
- [Source: backend/app/services/event_broadcaster.py — EventBroadcaster singleton, broadcast(event, data) API]
- [Source: backend/app/modules/events/router.py — SSE endpoint with Firebase token auth via query param]
- [Source: backend/app/modules/sync/service.py:106-110,221-231,256-264 — sync_status broadcast pattern (import, call placement, payload structure)]
- [Source: backend/app/modules/evaluations/service.py:247-296 — save_evaluation() current implementation (no broadcast yet)]
- [Source: backend/app/modules/evaluations/router.py:277-303 — save_evaluation_endpoint() with current_user dict containing email]
- [Source: frontend/src/hooks/useSSE.ts — SSE hook with sync_status listener, queryClientRef pattern, reconnection logic]
- [Source: frontend/src/components/ui/sonner.tsx — Toaster component, already mounted in App.tsx]
- [Source: _bmad-output/implementation-artifacts/4-5-evaluation-detail-view.md — Forward guidance: include evaluation_id in SSE event for deep-linking]
- [Source: _bmad-output/lessons-learned.md — Cache invalidation must be explicit, error handling required]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

None — clean implementation with no blocking issues.

### Completion Notes List

- **Task 1-2 (Backend):** Added `sync_broadcaster.broadcast("new_evaluation", ...)` call after the transaction in `save_evaluation()`. Broadcast is wrapped in try/except so failures never block the save response. Added `evaluator_email` parameter passed from router via `current_user["email"]`.
- **Task 3 (Backend Tests):** 4 tests covering: broadcast on success, payload field validation, no broadcast on 404, and broadcast failure resilience. All pass.
- **Task 4-5 (Frontend):** Added `new_evaluation` event listener in `useSSE.ts` that invalidates `['evaluations']` queries for auto-refresh and shows `toast.info()` for other users' evaluations (5s auto-dismiss). Self-notifications suppressed by comparing evaluator email. `SyncStatus.tsx` passes current user email from `useAuth()`.
- **Task 6 (Frontend Tests):** 5 tests covering: listener registration, query invalidation, toast for other users, no toast for self, and malformed data handling. All pass.
- **Regressions:** 526 backend tests pass (0 failures). 263 frontend tests pass. 2 pre-existing Firebase config failures (unrelated to this story).

### Change Log

- 2026-02-12: Implemented Story 4.6 — Real-time new evaluation notifications via SSE

### File List

**Modified:**
- `backend/app/modules/evaluations/service.py` — Added sync_broadcaster import, evaluator_email param, broadcast call after save
- `backend/app/modules/evaluations/router.py` — Pass evaluator_email=current_user["email"] to save_evaluation
- `frontend/src/hooks/useSSE.ts` — Added new_evaluation event listener, toast import, currentUserEmail param
- `frontend/src/hooks/useSSE.test.ts` — Added 5 new tests for new_evaluation event handling
- `frontend/src/components/sync/SyncStatus.tsx` — Pass current user email to useSSE hook
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — Updated 4-6 status to review

**New:**
- `backend/tests/integration/api/test_evaluation_save_broadcast.py` — 4 backend tests for SSE broadcast after save
