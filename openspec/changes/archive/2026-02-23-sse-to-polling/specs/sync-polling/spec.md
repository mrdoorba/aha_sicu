## ADDED Requirements

### Requirement: Adaptive sync status polling
The frontend SHALL poll `GET /api/v1/sync/status` at an interval that adapts based on the current sync state. When sync status is `in_progress`, the poll interval SHALL be 3 seconds. When sync status is `success`, `failed`, or `null`, the poll interval SHALL be 30 seconds.

#### Scenario: Poll interval during active sync
- **WHEN** the sync status is `in_progress`
- **THEN** the frontend polls `GET /api/v1/sync/status` every 3 seconds

#### Scenario: Poll interval during idle
- **WHEN** the sync status is `success`, `failed`, or no sync has ever run
- **THEN** the frontend polls `GET /api/v1/sync/status` every 30 seconds

#### Scenario: Transition from active to idle polling
- **WHEN** a sync completes (status changes from `in_progress` to `success` or `failed`)
- **THEN** the poll interval changes from 3 seconds to 30 seconds on the next cycle

### Requirement: Evaluation list periodic refresh
The frontend SHALL periodically refetch the evaluations list to pick up evaluations created by other users. The refetch interval SHALL be 30 seconds.

#### Scenario: New evaluation by another user
- **WHEN** another user saves an evaluation
- **THEN** the evaluations list refreshes within 30 seconds without page reload

### Requirement: SSE endpoint removal
The backend SHALL NOT expose the `GET /api/v1/events` SSE endpoint. The `EventBroadcaster` service and all broadcast calls SHALL be removed.

#### Scenario: SSE endpoint returns not found
- **WHEN** a client requests `GET /api/v1/events`
- **THEN** the server returns HTTP 404 (or the route does not exist)

### Requirement: SSE connection state UI removal
The frontend SHALL NOT display SSE connection state indicators (Live, Connecting, Reconnecting, Disconnected, Offline) in the `SyncStatus` component.

#### Scenario: SyncStatus without connection indicators
- **WHEN** the SyncStatus component renders
- **THEN** it displays sync status badge and Sync Now button without any connection state indicator

### Requirement: Cloud Run on-demand CPU
The CI/CD pipeline SHALL deploy Cloud Run with CPU throttling enabled (`--cpu-throttling`) for the dev environment, so that CPU is only allocated during request processing.

#### Scenario: Dev deployment uses on-demand CPU
- **WHEN** the backend deploys to dev environment via CI/CD
- **THEN** the Cloud Run service runs with `cpu-throttling: true`
