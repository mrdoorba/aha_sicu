## Why

Cloud Run's CPU Always-on mode (`cpu-throttling: false`) costs ~$11.50/month for dev — 76% of total Cloud Run spend — mostly from idle CPU time between requests. Switching to on-demand CPU (`cpu-throttling: true`) would cut this by ~94%, but the SSE endpoint (`GET /api/v1/events`) maintains persistent connections that are incompatible with on-demand CPU mode. Replacing SSE with polling removes this blocker.

## What Changes

- **BREAKING**: Remove the SSE endpoint `GET /api/v1/events` and the `EventBroadcaster` service
- Replace real-time SSE notifications with short-interval polling on existing `GET /api/v1/sync/status` (reduce `refetchInterval` from 60s to ~5s when sync is active)
- Add a new polling hook for evaluations to replace the SSE `new_evaluation` event (periodic query invalidation)
- Remove the `useSSE` hook and SSE connection state indicators (Live/Connecting/Reconnecting/Offline) from `SyncStatus` component
- Remove `sse-starlette` dependency from backend
- Switch Cloud Run to on-demand CPU via CI/CD deploy flags

## Capabilities

### New Capabilities
- `sync-polling`: Polling-based sync status updates replacing SSE real-time stream

### Modified Capabilities
_None — no existing spec-level requirements change. The sync and evaluation features retain the same user-facing behavior (status visibility, notifications), only the delivery mechanism changes._

## Impact

- **Backend**: Remove `app/modules/events/` router, `app/services/event_broadcaster.py`, all `sync_broadcaster.broadcast()` calls in sync and evaluation services. Remove `sse-starlette` from `pyproject.toml`.
- **Frontend**: Remove `useSSE` hook and tests. Update `SyncStatus` component to remove connection state UI. Enhance `useSync` polling interval. Add evaluation polling.
- **Tests**: Remove SSE-related tests (backend: `test_event_broadcaster.py`, `test_evaluation_save_broadcast.py`; frontend: `useSSE.test.ts`). Update `SyncStatus.test.tsx`, `BrandsPage.test.tsx`, `EvaluationPage.test.tsx` to remove SSE mocks.
- **CI/CD**: Add `--cpu-throttling` flag to `deploy-cloudrun` action in `deploy-backend.yml`.
- **Dependencies**: Remove `sse-starlette` package.
