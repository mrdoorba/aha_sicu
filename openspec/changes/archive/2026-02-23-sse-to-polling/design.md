## Context

The backend currently uses Server-Sent Events (SSE) via `sse-starlette` to push real-time updates to the frontend for two event types:
1. **`sync_status`** — sync started/completed/failed notifications
2. **`new_evaluation`** — when another user saves an evaluation

The SSE endpoint (`GET /api/v1/events`) maintains persistent HTTP connections, which requires Cloud Run's CPU Always-on mode. This mode bills for CPU during idle time, making it the dominant cost driver (~76% of Cloud Run spend).

The frontend already has a fallback polling mechanism (`refetchInterval: 60_000` in `useSync.ts`), but at 60s intervals it's too slow to serve as the primary update mechanism during active syncs.

The app serves ~5 concurrent users (internal business tool).

## Goals / Non-Goals

**Goals:**
- Remove SSE dependency so Cloud Run can use on-demand CPU (`cpu-throttling: true`)
- Maintain responsive sync status updates during active sync operations
- Maintain cross-user evaluation notifications
- Clean removal of all SSE infrastructure (backend, frontend, tests, dependency)

**Non-Goals:**
- Changing the sync mechanism itself (Cloud Scheduler, background tasks)
- Adding WebSocket support or any other push technology
- Optimizing polling beyond what's needed for ~5 users
- Changing prod Cloud Run configuration (only dev for now)

## Decisions

### 1. Adaptive polling interval for sync status

**Decision**: Use a short interval (3s) when sync is `in_progress`, fall back to long interval (30s) otherwise.

**Why not fixed 5s?** A fixed 5s poll would be too frequent during idle (wasteful) and could be sluggish during active sync. Adaptive polling gives responsive UX during the ~30s sync window and minimal overhead the rest of the time.

**Why not 60s idle like current?** 30s provides a reasonable balance — catches completed syncs (e.g., Cloud Scheduler daily 06:00) within half a minute without excessive requests.

**Implementation**: Leverage `react-query`'s `refetchInterval` as a function that reads current `data.status`.

### 2. Evaluation notifications via periodic invalidation

**Decision**: Add `refetchInterval: 30_000` to evaluation queries to periodically pick up new evaluations from other users.

**Why 30s?** Evaluations are not time-critical — a 30s delay in seeing another user's evaluation is acceptable for this internal tool. The toast notification for other users' evaluations will be removed (requires tracking "seen" state which adds complexity for minimal value).

**Alternative considered**: A dedicated "last evaluation timestamp" endpoint that the frontend polls, then triggers invalidation only when changed. Rejected — adds backend complexity for ~5 users; periodic invalidation is simpler and sufficient.

### 3. Remove SSE infrastructure entirely (not just disable)

**Decision**: Delete the events module, EventBroadcaster, and all broadcast calls rather than leaving them dormant.

**Why?** Dead code increases maintenance burden. The broadcast calls in sync and evaluation services add visual noise and import dependencies. Clean removal is preferred over commenting out or feature-flagging.

### 4. CPU throttling via CI/CD deploy flags

**Decision**: Add `--cpu-throttling` flag to the `deploy-cloudrun` GitHub Action for dev environment.

**Why not Terraform?** The current Terraform `google_cloud_run_v2_service` resource doesn't manage CPU throttling — the service is deployed via `google-github-actions/deploy-cloudrun@v3` in CI/CD. Adding the flag there is the path of least resistance and matches existing deployment patterns.

### 5. Remove connection state UI entirely

**Decision**: Remove the Live/Connecting/Reconnecting/Disconnected/Offline indicators from `SyncStatus`.

**Why?** These indicators only make sense for a persistent connection. With polling, the "connection" is implicit — if the API returns data, it's working. Error states are already handled by react-query's `isError` state.

## Risks / Trade-offs

- **[Slightly delayed sync feedback]** → Users see sync completion ~3s after it finishes instead of instantly. Acceptable for ~5 internal users.
- **[No more cross-user evaluation toasts]** → Users won't get instant pop-up notifications when another user saves an evaluation. Mitigated by 30s evaluation polling which refreshes the list. If this becomes a pain point, toasts can be re-added with a "last seen" tracking mechanism later.
- **[Cold start on daily sync]** → Cloud Scheduler triggers at 06:00 WIB. With on-demand CPU and `min_instances=0`, there's a 3-5s cold start. The sync still completes well within timeout. No user impact (no one uses the app at 06:00).
- **[Increased polling load]** → 5 users × 1 request every 3-30s is negligible (~15 req/min peak). Far below any concern threshold.
