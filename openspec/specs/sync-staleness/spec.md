## ADDED Requirements

### Requirement: Sync staleness timeout
The system SHALL treat any sync record that has been in progress for more than 10 minutes as timed out. A timed-out sync record MUST NOT block new sync operations and MUST be displayed as failed in the UI.

#### Scenario: Stale sync record does not block new sync
- **WHEN** a sync record has `completed_at IS NULL` and `started_at` is older than 10 minutes
- **THEN** `is_sync_in_progress()` SHALL return `False`, allowing a new sync to be triggered

#### Scenario: Stale sync record shown as failed in UI
- **WHEN** the latest sync record has `completed_at IS NULL` and `started_at` is older than 10 minutes
- **THEN** `get_latest_sync_status()` SHALL return `status: "failed"` with error message indicating the sync timed out

#### Scenario: Active sync within timeout window is not affected
- **WHEN** a sync record has `completed_at IS NULL` and `started_at` is less than 10 minutes ago
- **THEN** the system SHALL treat it as genuinely in progress (existing behavior preserved)
