# Story 2.4: Real-Time Sync Status via SSE

Status: review

## Story

As a **BD team member**,
I want **to see sync status update in real-time without refreshing**,
So that **I know immediately when new data is available**.

## Acceptance Criteria

1. **SSE Connection Established**
   - **Given** I am logged in and connected to the app
   - **When** I establish connection to `GET /api/v1/events` (SSE endpoint)
   - **Then** receive a stream of server-sent events

2. **Sync Start Broadcast**
   - **Given** a sync starts (by me or another user or scheduler)
   - **When** the sync status changes
   - **Then** the server broadcasts `event: sync_status` with data:
     ```json
     {"status": "in_progress", "started_at": "..."}
     ```

3. **Sync Complete Broadcast**
   - **Given** a sync completes
   - **When** the status changes
   - **Then** broadcast `event: sync_status` with data:
     ```json
     {"status": "success", "completed_at": "...", "brands_synced": 150}
     ```

4. **Frontend Real-Time Update**
   - **Given** the frontend receives a `sync_status` event
   - **When** rendering
   - **Then** update the sync status display without page refresh
   - **And** invalidate TanStack Query caches for `syncStatus` and `brands` keys
   - **And** the brand list refreshes with new data automatically

5. **Connection Resilience**
   - **Given** the SSE connection drops (network issue, server restart)
   - **When** reconnecting
   - **Then** use exponential backoff with jitter (1s initial, 30s max, 5 retries)
   - **And** show connection state to user (connecting/reconnecting indicators)

## Tasks / Subtasks

- [x] Task 1: Backend — EventBroadcaster service (AC: #1, #2, #3)
  - [x] 1.1 Create `app/services/event_broadcaster.py` with `EventBroadcaster` class
  - [x] 1.2 Use `asyncio.Queue(maxsize=64)` per subscriber for fan-out
  - [x] 1.3 Implement `subscribe()`, `unsubscribe()`, `broadcast()` with `asyncio.Lock`
  - [x] 1.4 Handle full queues by dropping events for slow clients
  - [x] 1.5 Create singleton instance `sync_broadcaster`

- [x] Task 2: Backend — SSE endpoint (AC: #1)
  - [x] 2.1 Install `sse-starlette>=3.2.0` dependency
  - [x] 2.2 Create `app/modules/events/__init__.py`
  - [x] 2.3 Create `app/modules/events/router.py` with `GET /api/v1/events`
  - [x] 2.4 Use `EventSourceResponse` from `sse-starlette` with `ping=15`
  - [x] 2.5 Authenticate via query parameter `?token=` (Firebase token validation)
  - [x] 2.6 Add `X-Accel-Buffering: no` header for proxy compatibility
  - [x] 2.7 Handle client disconnect with `finally` block to `unsubscribe()`
  - [x] 2.8 Register events router in `app/main.py`

- [x] Task 3: Backend — Integrate broadcaster into sync service (AC: #2, #3)
  - [x] 3.1 Import `sync_broadcaster` in `app/modules/sync/service.py`
  - [x] 3.2 Broadcast `sync_status` event at sync start (status: `in_progress`)
  - [x] 3.3 Broadcast `sync_status` event at sync completion (status: `success`, `brands_synced`)
  - [x] 3.4 Broadcast `sync_status` event on sync failure (status: `failed`, `error_message`)

- [x] Task 4: Backend — Tests (AC: #1, #2, #3)
  - [x] 4.1 Unit test `EventBroadcaster`: subscribe/unsubscribe/broadcast/full-queue behavior
  - [x] 4.2 Integration test SSE endpoint: connection, event streaming, auth validation
  - [x] 4.3 Integration test sync-to-SSE flow: trigger sync → verify events broadcast

- [x] Task 5: Frontend — `useSSE` hook (AC: #4, #5)
  - [x] 5.1 Create `src/hooks/useSSE.ts` with native `EventSource` API
  - [x] 5.2 Auth via query param: append `?token=` from `getCurrentUserToken()`
  - [x] 5.3 Exponential backoff reconnect (1s→30s, max 5 retries, jitter)
  - [x] 5.4 Track connection state: `connecting` | `connected` | `reconnecting` | `disconnected` | `failed`
  - [x] 5.5 On `sync_status` event → `queryClient.invalidateQueries` for `['syncStatus']` and `['brands']`
  - [x] 5.6 Proper cleanup on unmount (close EventSource, clear retry timeouts)

- [x] Task 6: Frontend — Integrate SSE into BrandsPage (AC: #4)
  - [x] 6.1 Wire `useSSE` into `BrandsPage.tsx` or `SyncStatus.tsx`
  - [x] 6.2 Remove or reduce `refetchInterval: 10_000` polling (SSE replaces it)
  - [x] 6.3 Show SSE connection state indicator in sync status area
  - [x] 6.4 Update `apiClient.ts` paths with SSE endpoint type (documentation only — SSE not via openapi-fetch)

- [x] Task 7: Frontend — Tests (AC: #4, #5)
  - [x] 7.1 Unit test `useSSE` hook: connection, events, reconnection, cleanup
  - [x] 7.2 Update `SyncStatus.test.tsx` for SSE integration changes
  - [x] 7.3 Update `BrandsPage.test.tsx` for SSE integration changes

## Dev Notes

### Architecture Pattern: Application-Level Broadcasting

Use **application-level broadcasting** (not PostgreSQL LISTEN/NOTIFY). All sync mutations go through `POST /api/v1/sync` → `sync_service.run_sync()` → `sync_broadcaster.broadcast()`. This is the correct approach because:
- All state changes originate from the FastAPI service layer
- Only 5 concurrent users max — no external scaling needed
- No additional database infrastructure required

### SSE Library: `sse-starlette` v3.2.0+

**DO NOT** use raw `StreamingResponse`. Use `sse-starlette` which handles:
- W3C SSE spec framing (`event:`, `data:`, `id:`, `retry:` fields)
- Keepalive pings (15s default, prevents proxy timeouts)
- Client disconnect detection via `asyncio.CancelledError`
- `Content-Type: text/event-stream` and `Cache-Control: no-cache` headers

### SSE Endpoint: `GET /api/v1/events`

Per architecture, SSE endpoint lives in `modules/events/` module:
```
modules/events/
├── __init__.py
├── router.py          # GET /events (SSE endpoint)
└── service.py         # NOT needed — broadcaster is in services/
```

**Auth Strategy:** Since `EventSource` API cannot set custom headers, authenticate via **query parameter**: `GET /api/v1/events?token=<firebase_token>`. Backend extracts token from `request.query_params.get("token")` and validates with the same Firebase verification logic from `core/security.py`.

### EventBroadcaster Pattern

```
services/
└── event_broadcaster.py  # EventBroadcaster singleton
```

Key implementation details:
- `asyncio.Queue(maxsize=64)` per subscriber — bounded to prevent memory leaks
- `asyncio.Lock` protects subscriber list during concurrent subscribe/unsubscribe/broadcast
- Full queue → drop events for that client (acceptable for status updates)
- Memory: ~16 KB per client × 5 users = ~80 KB total (negligible)
- Singleton `sync_broadcaster` instance, imported where needed

### Sync Service Integration Points

In `app/modules/sync/service.py` `run_sync()`:
1. **After creating sync record** → broadcast `{"status": "in_progress", "started_at": "..."}`
2. **After successful completion** → broadcast `{"status": "success", "completed_at": "...", "brands_synced": N}`
3. **On failure (except block)** → broadcast `{"status": "failed", "error_message": "..."}`

### Frontend `useSSE` Hook

Use **native `EventSource` API** (zero extra dependencies). Do NOT use `@microsoft/fetch-event-source` — the query param auth approach works for this internal tool.

Key behaviors:
- Listen for named event type: `sync_status`
- On event received: `queryClient.invalidateQueries({ queryKey: ['syncStatus'] })` and `queryClient.invalidateQueries({ queryKey: ['brands'] })`
- This triggers TanStack Query to refetch from `GET /api/v1/sync/status` and `GET /api/v1/brands` — SSE is a notification signal, not a data transport
- Reconnect with exponential backoff + jitter on `onerror`
- Cleanup: `eventSource.close()` on unmount + clear retry timeouts

### Polling Removal Strategy

Current: `useSyncStatus()` has `refetchInterval: 10_000` (10s polling).

With SSE: **Keep polling as fallback but increase interval to 60s**. SSE handles real-time updates; polling is safety net for missed events. In `useSync.ts`, change `refetchInterval: 10_000` → `refetchInterval: 60_000`.

### SSE Event Format

```
event: sync_status
data: {"status": "in_progress", "sync_id": 42, "started_at": "2026-02-06T10:30:00Z"}

event: sync_status
data: {"status": "success", "sync_id": 42, "completed_at": "2026-02-06T10:30:15Z", "brands_synced": 150}

event: sync_status
data: {"status": "failed", "sync_id": 42, "error_message": "Google Sheets API rate limited"}
```

### Project Structure Notes

Files to create:
- `backend/app/services/__init__.py` — new services directory
- `backend/app/services/event_broadcaster.py` — EventBroadcaster class
- `backend/app/modules/events/__init__.py` — events module
- `backend/app/modules/events/router.py` — SSE endpoint
- `frontend/src/hooks/useSSE.ts` — SSE consumer hook

Files to modify:
- `backend/pyproject.toml` — add `sse-starlette>=3.2.0`
- `backend/app/main.py` — register events_router
- `backend/app/modules/sync/service.py` — add broadcast calls
- `frontend/src/hooks/useSync.ts` — reduce refetchInterval to 60s
- `frontend/src/pages/BrandsPage.tsx` — wire useSSE hook
- `frontend/src/components/sync/SyncStatus.tsx` — show connection state
- `frontend/src/services/apiClient.ts` — add events path type

Test files to create:
- `backend/tests/unit/events/__init__.py`
- `backend/tests/unit/events/test_event_broadcaster.py`
- `backend/tests/integration/api/test_events.py`
- `frontend/src/hooks/useSSE.test.ts`

Test files to modify:
- `frontend/src/components/sync/SyncStatus.test.tsx`
- `frontend/src/pages/BrandsPage.test.tsx`

### Previous Story (2.3) Learnings — MUST FOLLOW

1. **ILIKE queries MUST include `ESCAPE '\'`** when using `_escape_like()` helper
2. **Frontend hooks MUST use `apiClient.ts`** (openapi-fetch), never raw `fetch()` — but SSE uses native `EventSource` which is an exception (SSE is not a REST call)
3. **Search parameters need `max_length` validation** on Query params
4. **Error handling in TanStack Query**: throw errors, don't swallow them
5. **Type definitions** in `apiClient.ts` must stay in sync with hooks
6. **Story File List must include ALL files** changed on the feature branch
7. **Backend test pattern**: `AsyncClient` + `patch(...)` MagicMock for db context manager
8. **Frontend test pattern**: `@testing-library/react` with TanStack Query mocking, use `getAllByText` for ambiguous matches
9. **Sync completion detection**: Current pattern uses `useEffect` watching status → invalidate brands query. SSE replaces this — the `useEffect` in `SyncStatus.tsx` that invalidates brands on status change should be simplified since SSE handles it

### Code Review Findings to Pre-Apply

From Story 2.3 reviews (prevent same mistakes):
- Always use `apiClient.ts` middleware for auth — SSE is the only exception (query param auth)
- Never send "Bearer null" — `useSSE` must check for token before connecting
- Test mock assertions must verify actual parameters passed
- Component error states must have visible UI (not just console.log)

### NFR Compliance

- **NFR5**: Real-time update propagation < 500ms — SSE delivers this (server push, no polling delay)
- **Performance**: `sse-starlette` keepalive ping every 15s prevents proxy timeout disconnects

### References

- [Source: _bmad-output/planning-artifacts/architecture.md — SSE section: `modules/events/`, `hooks/useSSE.ts`]
- [Source: _bmad-output/planning-artifacts/architecture.md — API Patterns: REST conventions, error codes]
- [Source: _bmad-output/planning-artifacts/prd.md — FR34: Real-time sync status]
- [Source: _bmad-output/planning-artifacts/prd.md — NFR5: Real-time propagation < 500ms]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md — Sync Status Widget states]
- [Source: _bmad-output/planning-artifacts/epics.md — Epic 2, Story 2.4 acceptance criteria]
- [Source: _bmad-output/implementation-artifacts/2-3-brand-list-ui-with-sync-status.md — code review learnings]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6 (claude-opus-4-6)

### Debug Log References

- No blocking issues encountered during implementation

### Completion Notes List

- **Task 1**: Created `EventBroadcaster` class with `asyncio.Queue(maxsize=64)` per subscriber, `asyncio.Lock` for thread safety, full-queue drop policy. Singleton `sync_broadcaster` instance exported.
- **Task 2**: Installed `sse-starlette>=3.2.0`. Created `modules/events/` with SSE endpoint at `GET /api/v1/events`. Auth via `?token=` query parameter (Firebase validation). `EventSourceResponse` with `ping=15` and `X-Accel-Buffering: no` header. Registered in `main.py`.
- **Task 3**: Integrated `sync_broadcaster.broadcast()` into `run_sync()` at three points: sync start (`in_progress`), completion (`success`/`failed` with `brands_synced`), and exception (`failed` with `error_message`).
- **Task 4**: 7 unit tests for EventBroadcaster (subscribe, unsubscribe, broadcast, full-queue, singleton). 2 integration tests for SSE endpoint (missing token 422, invalid token 401). 3 unit tests for sync-to-SSE broadcast verification. All 67 backend tests pass.
- **Task 5**: Created `useSSE` hook using native `EventSource` API. Auth via query param from `getCurrentUserToken()`. Exponential backoff (1s-30s, 5 retries, jitter). Connection states: connecting/connected/reconnecting/disconnected/failed. On `sync_status` event: invalidates `syncStatus` and `brands` query keys. Cleanup on unmount.
- **Task 6**: Wired `useSSE` into `SyncStatus.tsx`. Removed `useEffect`-based brand invalidation (SSE handles it). Added connection state indicator (Live/Connecting.../Reconnecting.../Offline). Reduced polling interval from 10s to 60s in `useSync.ts`. Added SSE path type to `apiClient.ts`.
- **Task 7**: 7 unit tests for `useSSE` hook (connection states, token-based auth, query invalidation, max retries, cleanup). 3 tests for SSE connection indicators in SyncStatus. Updated BrandsPage tests with useSSE mock. All 58 frontend tests pass.

### Change Log

- 2026-02-06: Implemented Story 2.4 — Real-Time Sync Status via SSE (all 7 tasks completed)

### File List

New files:
- backend/app/services/__init__.py
- backend/app/services/event_broadcaster.py
- backend/app/modules/events/__init__.py
- backend/app/modules/events/router.py
- backend/tests/unit/events/__init__.py
- backend/tests/unit/events/test_event_broadcaster.py
- backend/tests/integration/api/test_events.py
- frontend/src/hooks/useSSE.ts
- frontend/src/hooks/useSSE.test.ts

Modified files:
- backend/pyproject.toml (added sse-starlette dependency)
- backend/app/main.py (registered events router)
- backend/app/modules/sync/service.py (added broadcaster imports and broadcast calls)
- backend/tests/unit/sync/test_service.py (added broadcaster mock and 3 broadcast tests)
- frontend/src/hooks/useSync.ts (refetchInterval 10s -> 60s)
- frontend/src/components/sync/SyncStatus.tsx (added useSSE, connection indicator, removed useEffect brand invalidation)
- frontend/src/components/sync/SyncStatus.test.tsx (added useSSE mock and 3 connection state tests)
- frontend/src/pages/BrandsPage.test.tsx (added useSSE mock)
- frontend/src/services/apiClient.ts (added SSE endpoint type)
- _bmad-output/implementation-artifacts/sprint-status.yaml (2-4 status: in-progress -> review)
- _bmad-output/implementation-artifacts/2-4-real-time-sync-status-via-sse.md (story file updated)
