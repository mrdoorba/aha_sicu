# Story 2.5: Daily Automatic Sync

Status: review

## Story

As a **system**,
I want **to automatically sync brand data daily via Cloud Scheduler**,
So that **the BD team always has fresh data without manual intervention**.

## Acceptance Criteria

1. **Cloud Scheduler Terraform Resource**
   - **Given** the Terraform configuration in `infrastructure/terraform/`
   - **When** `terraform apply` is run
   - **Then** a Cloud Scheduler job `aha_sicu_daily_sync` is created
   - **And** it triggers at 06:00 WIB (23:00 UTC previous day) daily
   - **And** it targets the Cloud Run service URL `POST /api/v1/sync`
   - **And** it uses `aha-sicu-scheduler-sa` service account for authentication

2. **Scheduler Service Account & IAM**
   - **Given** the Terraform configuration
   - **When** resources are provisioned
   - **Then** service account `aha-sicu-scheduler-sa` exists
   - **And** it has `roles/run.invoker` on the Cloud Run service
   - **And** it has no other permissions (least privilege)

3. **Backend Accepts Scheduler Requests (OIDC Token Auth)**
   - **Given** Cloud Scheduler sends a request with an OIDC token (not a Firebase token)
   - **When** the request hits `POST /api/v1/sync`
   - **Then** the backend validates the OIDC token using Google's public JWKS
   - **And** identifies the caller as a service account (not a user)
   - **And** proceeds with the sync (no user record needed for scheduler)

4. **Sync Execution and SSE Broadcast**
   - **Given** the scheduled sync triggers successfully
   - **When** the sync completes (success or failure)
   - **Then** results are recorded in `sync_status` table (reuses existing `run_sync`)
   - **And** SSE broadcasts status to connected clients (reuses existing broadcaster)
   - **And** connected frontends see real-time update of the daily sync

5. **Scheduler Retry on Failure**
   - **Given** the Cloud Scheduler job fires and the sync endpoint returns an error (5xx)
   - **When** Cloud Scheduler detects the failure
   - **Then** it retries up to 3 times with exponential backoff
   - **And** failures are logged in Cloud Logging

6. **Backend Tests for Dual Auth**
   - **Given** the sync endpoint now supports both Firebase tokens and OIDC tokens
   - **When** running the test suite
   - **Then** existing user-auth sync tests still pass (no regression)
   - **And** new tests verify OIDC token acceptance on the sync endpoint
   - **And** new tests verify rejection of invalid OIDC tokens

## Tasks / Subtasks

- [x] Task 1: Backend — Add OIDC token validation for service-to-service auth (AC: #3)
  - [x] 1.1 Add `google-auth>=2.38.0` dependency to `pyproject.toml` (provides `google.oauth2.id_token`, `google.auth.transport.requests`)
  - [x] 1.2 Create `app/core/oidc.py` — `verify_oidc_token(token: str) -> dict` using `google.oauth2.id_token.verify_oauth2_token()` with Google's public JWKS
  - [x] 1.3 Update `app/core/dependencies.py` — modify `get_current_user` to detect token type: try Firebase first, fallback to OIDC validation; OIDC returns a synthetic service-account user dict `{"id": None, "email": sa_email, "role": "scheduler", "firebase_uid": None}`
  - [x] 1.4 Verify sync router works with the synthetic scheduler user (no DB write for scheduler calls)

- [x] Task 2: Backend — Tests for OIDC auth path (AC: #6)
  - [x] 2.1 Create `backend/tests/unit/core/test_oidc.py` — unit tests for `verify_oidc_token`: valid token, expired, invalid, wrong audience
  - [x] 2.2 Add integration tests in `backend/tests/integration/api/test_sync.py` — test sync endpoint with mocked OIDC token (scheduler auth path)
  - [x] 2.3 Verify existing Firebase auth tests still pass (regression check)

- [x] Task 3: Infrastructure — Cloud Scheduler Terraform resources (AC: #1, #2, #5)
  - [x] 3.1 Create `infrastructure/terraform/scheduler.tf` with:
    - `google_cloud_scheduler_job.daily_sync` — cron `0 23 * * *` (= 06:00 WIB), target: Cloud Run URL + `/api/v1/sync`, HTTP POST, OIDC auth
    - Retry config: max 3 retries, min backoff 30s, max backoff 300s
  - [x] 3.2 Create `infrastructure/terraform/iam.tf` (or add to existing main.tf):
    - `google_service_account.scheduler` — `aha-sicu-scheduler-sa`
    - `google_cloud_run_service_iam_member.scheduler_invoker` — `roles/run.invoker`
  - [x] 3.3 Add `variable "cloud_run_url"` to `variables.tf` for the Cloud Run service URL (needed before Cloud Run is deployed; output it later)
  - [x] 3.4 Enable Cloud Scheduler API: `google_project_service.scheduler_api`

- [x] Task 4: Infrastructure — Terraform validation (AC: #1, #2)
  - [x] 4.1 Run `terraform validate` to verify HCL syntax
  - [x] 4.2 Run `terraform plan` (dry run) to verify resource creation graph
  - [x] 4.3 Document apply instructions in PR description

## Dev Notes

### Architecture: Cloud Scheduler → Cloud Run OIDC Auth

Cloud Scheduler authenticates to Cloud Run using **OIDC tokens**, NOT Firebase tokens. This is the standard GCP service-to-service authentication pattern:

```
Cloud Scheduler (aha-sicu-scheduler-sa)
    ↓ OIDC token in Authorization header
POST /api/v1/sync (Cloud Run: aha_sicu_api)
    ↓ verify OIDC token
run_sync() → sync_status table → SSE broadcast
```

**Why OIDC, not Firebase?**
- Cloud Scheduler generates OIDC tokens natively (built-in feature)
- Firebase tokens are for human users authenticated via Firebase Auth SDK
- Service accounts use Google OIDC — different signing authority
- Architecture doc specifies `aha-sicu-scheduler-sa` with `run.invoker` role

### Backend Auth Strategy: Dual Token Support

The sync endpoint currently requires a Firebase user token via `get_current_user`. For scheduler support, modify `get_current_user` to support both token types:

1. **Try Firebase validation first** (existing path — handles user requests)
2. **On Firebase failure, try OIDC validation** (new path — handles scheduler requests)
3. **If both fail, return 401**

This approach:
- Preserves all existing behavior (zero regression risk)
- Requires NO changes to the sync router or service
- Centralizes auth logic in `dependencies.py`

### OIDC Token Validation Implementation

Use `google-auth` library (Google's official Python auth library):

```python
# app/core/oidc.py
from google.oauth2 import id_token
from google.auth.transport import requests

async def verify_oidc_token(token: str) -> dict:
    """Verify Google OIDC token from Cloud Scheduler."""
    claims = await asyncio.to_thread(
        id_token.verify_oauth2_token,
        token,
        requests.Request(),
        # audience = Cloud Run service URL
    )
    return {
        "email": claims.get("email", ""),
        "issuer": claims.get("iss", ""),
    }
```

**Audience check:** The OIDC token's `audience` field must match the Cloud Run service URL. This is automatically set by Cloud Scheduler when `oidc_token.audience` is configured. In local/test environments, use a configurable setting.

### Config Addition

Add to `app/config.py`:
```python
# Cloud Run service URL (for OIDC audience validation)
# Set in production; empty in local dev (disables OIDC)
cloud_run_url: str = ""
```

### Terraform Resource Details

**Cloud Scheduler Job:**
```hcl
resource "google_cloud_scheduler_job" "daily_sync" {
  name        = "aha_sicu_daily_sync"
  description = "Daily brand data sync from Google Sheets"
  schedule    = "0 23 * * *"  # 06:00 WIB = 23:00 UTC (day before)
  time_zone   = "Asia/Jakarta"  # Alternative: use WIB timezone directly

  http_target {
    http_method = "POST"
    uri         = "${var.cloud_run_url}/api/v1/sync"

    oidc_token {
      service_account_email = google_service_account.scheduler.email
      audience              = var.cloud_run_url
    }
  }

  retry_config {
    retry_count          = 3
    min_backoff_duration = "30s"
    max_backoff_duration = "300s"
  }
}
```

**Key detail:** `time_zone = "Asia/Jakarta"` makes the cron `0 6 * * *` (06:00 local) instead of needing UTC conversion. Choose whichever approach is clearer.

**Service Account:**
```hcl
resource "google_service_account" "scheduler" {
  account_id   = "aha-sicu-scheduler-sa"
  display_name = "Store ICU Scheduler Service Account"
}

resource "google_cloud_run_service_iam_member" "scheduler_invoker" {
  service  = google_cloud_run_v2_service.api.name
  location = var.region
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.scheduler.email}"
}
```

**Note:** Cloud Run service resource (`google_cloud_run_v2_service.api`) doesn't exist in Terraform yet. Use `var.cloud_run_url` for the scheduler target and reference the Cloud Run service name via variable until Cloud Run Terraform is added in a deployment story.

### Existing Sync Infrastructure — DO NOT MODIFY

The sync pipeline is fully implemented and working. This story only adds:
1. A new auth path (OIDC) to the existing `get_current_user` dependency
2. Terraform resources for Cloud Scheduler + IAM

**Existing flow (unchanged):**
- `POST /api/v1/sync` → advisory lock check → create sync_status → `run_sync()` background task
- `run_sync()` → fetch VP sheet → fetch Meeting sheet → upsert brands → update sync_status → broadcast SSE
- SSE events → connected frontends auto-refresh

### Previous Story (2.4) Learnings — MUST FOLLOW

1. **Tests use `AsyncClient` + `patch(...)` MagicMock** for db context manager
2. **Backend test pattern**: Mock external dependencies at the service boundary
3. **Sync service imports `sync_broadcaster`** — scheduler-triggered syncs will also broadcast SSE events (no change needed)
4. **Advisory lock on sync** prevents concurrent syncs — Cloud Scheduler hitting during a manual sync returns 409 (correct behavior, scheduler retry handles it)
5. **`uv.lock` must be included** in File List when adding Python dependencies
6. **Story File List must include ALL files** changed on the feature branch

### Code Review Findings from Previous Stories — Pre-Apply

- Always use `apiClient.ts` middleware for auth on frontend — NO frontend changes in this story
- Backend auth must never accept empty/null tokens — OIDC path must validate token presence before attempting verification
- Test mock assertions must verify actual parameters passed

### NFR Compliance

- **NFR1**: No impact on page load (backend-only + infrastructure changes)
- **NFR5**: Real-time propagation still < 500ms (SSE broadcaster unchanged)
- **NFR11**: Google Sheets rate limiting handled by existing `sheets_client.py` retry logic
- **NFR12**: Sync failures logged with actionable error messages (existing behavior)

### Project Structure Notes

No new modules or directories needed. This story adds files within existing structure:

```
backend/app/core/oidc.py          ← NEW: OIDC token verification
backend/tests/unit/core/          ← NEW directory
backend/tests/unit/core/__init__.py  ← NEW
backend/tests/unit/core/test_oidc.py ← NEW
infrastructure/terraform/scheduler.tf ← NEW
infrastructure/terraform/iam.tf      ← NEW (or extend main.tf)
```

Alignment with architecture: `core/` directory holds shared infrastructure (security, dependencies). OIDC validation is cross-cutting auth infrastructure → belongs in `core/`.

### References

- [Source: _bmad-output/planning-artifacts/architecture.md — Infrastructure: `scheduler.tf`, `iam.tf`, service accounts]
- [Source: _bmad-output/planning-artifacts/architecture.md — Service Accounts: `aha-sicu-scheduler-sa` with `run.invoker`]
- [Source: _bmad-output/planning-artifacts/architecture.md — Cloud Scheduler: `aha_sicu_daily_sync`]
- [Source: _bmad-output/planning-artifacts/architecture.md — Region: `asia-southeast1`]
- [Source: _bmad-output/planning-artifacts/epics.md — Epic 2, Story 2.5 acceptance criteria]
- [Source: _bmad-output/planning-artifacts/prd.md — FR1: Auto sync daily, NFR11: Rate limit handling]
- [Source: _bmad-output/implementation-artifacts/2-4-real-time-sync-status-via-sse.md — SSE broadcast patterns, sync service integration]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6 (claude-opus-4-6)

### Debug Log References

- No debug issues encountered during implementation.

### Completion Notes List

- **Task 1:** Implemented dual-auth support in `get_current_user` — tries Firebase first, falls back to OIDC. Created `app/core/oidc.py` with `verify_oidc_token()` using `google.oauth2.id_token.verify_oauth2_token()`. OIDC path returns synthetic scheduler user dict (no DB access). Added `cloud_run_url` config setting for audience validation. Updated `google-auth` minimum from 2.35.0 to 2.38.0.
- **Task 2:** Created 7 unit tests for `verify_oidc_token` (valid, expired, invalid, wrong audience, empty token, audience passing, no-audience-when-empty-url). Added 2 integration tests for OIDC scheduler path (202 response, no DB user lookup). Updated 3 existing "invalid token" tests across auth/sync/sync_trigger to mock both Firebase and OIDC failure. All 76 tests pass (67 existing + 9 new).
- **Task 3:** Created `scheduler.tf` with Cloud Scheduler job (`aha_sicu_daily_sync`, cron `0 6 * * *` Asia/Jakarta, POST /api/v1/sync, OIDC auth, 3 retries). Created `iam.tf` with scheduler service account and `roles/run.invoker` IAM binding. Added `cloud_run_url` and `cloud_run_service_name` variables. Enabled Cloud Scheduler API.
- **Task 4:** `terraform validate` passes. `terraform plan` shows correct 4 new resources (scheduler job, service account, IAM member, API enablement).

### File List

- backend/pyproject.toml (modified — google-auth version bump to >=2.38.0)
- backend/uv.lock (modified — lock file updated)
- backend/app/config.py (modified — added cloud_run_url setting)
- backend/app/core/oidc.py (new — OIDC token verification)
- backend/app/core/dependencies.py (modified — dual auth: Firebase + OIDC fallback)
- backend/tests/unit/core/__init__.py (new — test package init)
- backend/tests/unit/core/test_oidc.py (new — 7 OIDC unit tests)
- backend/tests/integration/api/test_sync_trigger.py (modified — added 2 OIDC integration tests, updated invalid token test)
- backend/tests/integration/api/test_sync.py (modified — updated invalid token test for dual auth)
- backend/tests/integration/api/test_auth.py (modified — updated invalid token test for dual auth)
- infrastructure/terraform/scheduler.tf (new — Cloud Scheduler job + API enablement)
- infrastructure/terraform/iam.tf (new — scheduler service account + IAM binding)
- infrastructure/terraform/variables.tf (modified — added cloud_run_url, cloud_run_service_name variables)

## Change Log

- 2026-02-06: Story 2.5 implementation complete — added OIDC dual-auth support for Cloud Scheduler, Terraform infrastructure for daily sync schedule, and comprehensive test coverage (76 tests, 0 regressions)

