# Story 2.1: Google Sheets Sync Backend

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **system**,
I want **to sync brand data from the Brand Database Google Sheet**,
So that **the BD team has up-to-date brand information to evaluate**.

## Acceptance Criteria

1. **Given** the Google Sheets API credentials are configured (service account)
   **When** the sync service is triggered (manual or scheduled)
   **Then** connect to the configured spreadsheets (VP and Meeting) using the configured Sheet IDs
   **And** read all brand rows from the designated ranges
   **And** for each brand row, upsert into `brand_vp_data` and `brand_meeting_data` tables (match by brand name)
   **And** record sync timestamp and per-sheet breakdown in `sync_status` table
   **And** return sync summary (brands synced count per sheet, errors if any)

2. **Given** the Google Sheets API returns a rate limit error
   **When** the sync is in progress
   **Then** implement exponential backoff retry (max 3 attempts)
   **And** log the retry attempts with `SYNC_RATE_LIMITED` code

3. **Given** the sync fails after retries
   **When** recording the result
   **Then** store error details in `sync_status` with `success: false`
   **And** log error with `SYNC_FAILED` code and actionable message

## Tasks / Subtasks

- [x] Task 1: Create Database Migrations (AC: #1)
  - [x] Create migration 002 for initial `brands` table
  - [x] Create migration 003 for `sync_status` table
  - [x] Create migration 004 to replace `brands` with `brand_vp_data` + `brand_meeting_data` (two-sheet model)
  - [x] Create migration 005 to add `sync_details` JSONB to `sync_status` (per-sheet breakdown)
  - [x] Add indexes for performance (brand name search, sync timestamp)
  - [x] Run migrations and verify schema

- [x] Task 2: Implement Database Queries (AC: #1, #3)
  - [x] Create `backend/app/db/queries/brands.py` with brand data CRUD queries (supports both VP and Meeting tables)
  - [x] Create `backend/app/db/queries/sync_status.py` with sync status queries
  - [x] Implement `upsert_brand_data()` using `ON CONFLICT DO UPDATE` with table name validation
  - [x] Implement `get_brand_data()` with pagination
  - [x] Implement `create_sync_status()` and `update_sync_status()` (with `sync_details` JSONB)

- [x] Task 3: Implement Google Sheets Client (AC: #1, #2)
  - [x] Create `backend/app/modules/sync/sheets_client.py`
  - [x] Configure Google Sheets API with service account credentials
  - [x] Implement `fetch_sheet_data()` generic method with retry logic
  - [x] Implement `fetch_vp_data()` and `fetch_meeting_data()` convenience methods
  - [x] Add exponential backoff retry logic for rate limits (max 3 attempts)
  - [x] Parse sheet data into structured format (header row becomes keys)

- [x] Task 4: Implement Sync Service (AC: #1, #2, #3)
  - [x] Create `backend/app/modules/sync/service.py`
  - [x] Implement `run_sync()` orchestration function
  - [x] Handle partial failures (continue with other brands if one fails)
  - [x] Track sync progress and status
  - [x] Return sync summary with counts and errors

- [x] Task 5: Create Sync Module Schema (AC: #1, #3)
  - [x] Create `backend/app/modules/sync/schemas.py`
  - [x] Define `SyncStatusResponse` model (with `sync_details` JSONB for per-sheet breakdown)
  - [x] Define `SyncResult` model with VP/Meeting results
  - [x] Define `SheetSyncResult` model per sheet
  - [x] Define `SyncError` model for row-level failures

- [x] Task 6: Create Sync API Router (AC: #1, #3)
  - [x] Create `backend/app/modules/sync/router.py`
  - [x] Implement `GET /api/v1/sync/status` endpoint
  - [x] Add authentication middleware (requires valid JWT)
  - [x] Register router in main.py

- [x] Task 7: Add Configuration for Google Sheets (AC: #1)
  - [x] Add environment variables to `.env.example`
  - [x] Add settings to `backend/app/config.py`
  - [x] Document required Google Sheets setup

- [x] Task 8: Write Tests (AC: #1, #2, #3)
  - [x] Unit tests for sheets_client with mocked Google API
  - [x] Unit tests for sync service with mocked sheets client
  - [x] Integration tests for sync endpoints
  - [x] Test exponential backoff retry logic
  - [x] Test error handling and status recording

## Dev Notes

### Database Schema

**`brand_vp_data` table (VP sheet data):**
```sql
CREATE TABLE brand_vp_data (
    id SERIAL PRIMARY KEY,
    brand_name VARCHAR(255) NOT NULL,
    raw_data JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_brand_vp_data_brand_name UNIQUE (brand_name)
);

CREATE INDEX idx_brand_vp_data_brand_name ON brand_vp_data(brand_name);
CREATE INDEX idx_brand_vp_data_updated_at ON brand_vp_data(updated_at DESC);
```

**`brand_meeting_data` table (1st Meeting sheet data):**
```sql
CREATE TABLE brand_meeting_data (
    id SERIAL PRIMARY KEY,
    brand_name VARCHAR(255) NOT NULL,
    raw_data JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_brand_meeting_data_brand_name UNIQUE (brand_name)
);

CREATE INDEX idx_brand_meeting_data_brand_name ON brand_meeting_data(brand_name);
CREATE INDEX idx_brand_meeting_data_updated_at ON brand_meeting_data(updated_at DESC);
```

**`sync_status` table:**
```sql
CREATE TABLE sync_status (
    id SERIAL PRIMARY KEY,
    started_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ,
    success BOOLEAN,
    brands_synced INTEGER DEFAULT 0,
    error_message TEXT,
    sync_details JSONB,  -- per-sheet VP/Meeting breakdown
    CONSTRAINT sync_status_completed_has_success CHECK (
        completed_at IS NULL OR success IS NOT NULL
    )
);

CREATE INDEX idx_sync_status_started_at ON sync_status(started_at DESC);
```

### Google Sheets Client Implementation

**sheets_client.py:**
```python
import asyncio
from typing import Any
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.config import settings
from app.core.exceptions import SyncError

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

class GoogleSheetsClient:
    def __init__(self):
        self._service = None

    def _get_service(self):
        """Lazy initialization of Google Sheets service."""
        if self._service is None:
            creds = service_account.Credentials.from_service_account_file(
                settings.GSHEETS_CREDENTIALS_PATH,
                scopes=SCOPES
            )
            self._service = build('sheets', 'v4', credentials=creds)
        return self._service

    async def fetch_brands_from_sheet(self) -> list[dict[str, Any]]:
        """Fetch brand data from Google Sheet with retry logic."""
        max_retries = 3
        base_delay = 1.0  # seconds

        for attempt in range(max_retries):
            try:
                # Run synchronous Google API call in thread pool
                service = self._get_service()
                result = await asyncio.to_thread(
                    lambda: service.spreadsheets().values().get(
                        spreadsheetId=settings.GSHEETS_SPREADSHEET_ID,
                        range=settings.GSHEETS_RANGE
                    ).execute()
                )

                rows = result.get('values', [])
                if not rows:
                    return []

                # First row is header
                headers = rows[0]
                brands = []
                for row in rows[1:]:
                    brand_data = dict(zip(headers, row + [''] * (len(headers) - len(row))))
                    brands.append(brand_data)

                return brands

            except HttpError as e:
                if e.resp.status == 429:  # Rate limit
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)  # Exponential backoff
                        # Log: SYNC_RATE_LIMITED
                        await asyncio.sleep(delay)
                        continue
                raise SyncError(
                    code="SYNC_FAILED",
                    detail=f"Google Sheets API error: {str(e)}"
                )

        raise SyncError(
            code="SYNC_RATE_LIMITED",
            detail="Max retries exceeded due to rate limiting"
        )
```

### Sync Service Implementation

**service.py:**
```python
import logging
from datetime import datetime, timezone
from typing import Any

from app.db.connection import get_db_pool
from app.db.queries.brands import upsert_brand
from app.db.queries.sync_status import create_sync_status, update_sync_status
from app.modules.sync.sheets_client import GoogleSheetsClient
from app.modules.sync.schemas import SyncResult

logger = logging.getLogger(__name__)

async def run_sync() -> SyncResult:
    """Execute full brand sync from Google Sheets."""
    pool = await get_db_pool()
    sheets_client = GoogleSheetsClient()

    # Create sync record
    async with pool.acquire() as conn:
        sync_id = await create_sync_status(
            conn,
            started_at=datetime.now(timezone.utc)
        )

    try:
        # Fetch from Google Sheets
        brand_rows = await sheets_client.fetch_brands_from_sheet()

        synced_count = 0
        errors = []

        # Upsert each brand
        async with pool.acquire() as conn:
            for brand_data in brand_rows:
                try:
                    await upsert_brand(
                        conn,
                        external_id=brand_data.get('ID'),
                        name=brand_data.get('Brand Name'),
                        category=brand_data.get('Category'),
                        marketplace=brand_data.get('Marketplace'),
                        raw_data=brand_data
                    )
                    synced_count += 1
                except Exception as e:
                    errors.append({
                        'brand': brand_data.get('Brand Name'),
                        'error': str(e)
                    })
                    logger.warning(f"Failed to sync brand: {brand_data.get('Brand Name')}: {e}")

        # Update sync status
        async with pool.acquire() as conn:
            await update_sync_status(
                conn,
                sync_id=sync_id,
                completed_at=datetime.now(timezone.utc),
                success=len(errors) == 0,
                brands_synced=synced_count,
                error_message=str(errors) if errors else None
            )

        return SyncResult(
            sync_id=sync_id,
            brands_synced=synced_count,
            errors=errors,
            success=len(errors) == 0
        )

    except Exception as e:
        # Update sync status with failure
        async with pool.acquire() as conn:
            await update_sync_status(
                conn,
                sync_id=sync_id,
                completed_at=datetime.now(timezone.utc),
                success=False,
                brands_synced=0,
                error_message=str(e)
            )
        logger.error(f"SYNC_FAILED: {e}")
        raise
```

### API Router

**router.py:**
```python
from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.modules.sync.schemas import SyncStatusResponse
from app.modules.sync.service import get_latest_sync_status

router = APIRouter(prefix="/api/v1/sync", tags=["sync"])

@router.get("/status", response_model=SyncStatusResponse)
async def get_sync_status(current_user = Depends(get_current_user)):
    """Get the latest sync status."""
    status = await get_latest_sync_status()
    return status
```

### Project Structure Notes

**Files to Create:**
| File | Purpose |
|------|---------|
| `backend/app/db/migrations/versions/002_add_brands_table.py` | Brands table migration |
| `backend/app/db/migrations/versions/003_add_sync_status_table.py` | Sync status table migration |
| `backend/app/db/queries/brands.py` | Brand CRUD queries |
| `backend/app/db/queries/sync_status.py` | Sync status queries |
| `backend/app/modules/sync/__init__.py` | Module init |
| `backend/app/modules/sync/router.py` | API endpoints |
| `backend/app/modules/sync/schemas.py` | Pydantic models |
| `backend/app/modules/sync/service.py` | Business logic |
| `backend/app/modules/sync/sheets_client.py` | Google Sheets integration |

**Files to Modify:**
| File | Changes |
|------|---------|
| `backend/app/main.py` | Register sync router |
| `backend/app/config.py` | Add Google Sheets settings |
| `backend/.env.example` | Add environment variables |
| `backend/pyproject.toml` | Add google-api-python-client dependency |

### Environment Variables

**Add to `.env.example`:**
```env
# Google Sheets API - Credentials
GSHEETS_CREDENTIALS_PATH=./credentials/gsheets-service-account.json

# VP Sheet (brand_vp_data)
GSHEETS_VP_SPREADSHEET_ID=your-vp-spreadsheet-id
GSHEETS_VP_RANGE=VP!A:Y
GSHEETS_VP_BRAND_COLUMN=Nama Brand

# 1st Meeting Sheet (brand_meeting_data)
GSHEETS_MEETING_SPREADSHEET_ID=your-meeting-spreadsheet-id
GSHEETS_MEETING_RANGE=ZAP: 1st Meeting!A:D
GSHEETS_MEETING_BRAND_COLUMN=Brand
```

### Configuration Settings

**Add to `config.py`:**
```python
class Settings(BaseSettings):
    # ... existing settings ...

    # Google Sheets API - Credentials
    gsheets_credentials_path: str | None = None

    # VP Sheet (brand_vp_data)
    gsheets_vp_spreadsheet_id: str | None = None
    gsheets_vp_range: str = "VP!A:Y"
    gsheets_vp_brand_column: str = "Nama Brand"

    # 1st Meeting Sheet (brand_meeting_data)
    gsheets_meeting_spreadsheet_id: str | None = None
    gsheets_meeting_range: str = "ZAP: 1st Meeting!A:D"
    gsheets_meeting_brand_column: str = "Brand"
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `SYNC_RATE_LIMITED` | 429 | Google Sheets API rate limit hit |
| `SYNC_FAILED` | 500 | General sync failure |
| `SYNC_CREDENTIALS_MISSING` | 500 | Service account credentials not configured |
| `SYNC_SHEET_NOT_FOUND` | 404 | Spreadsheet ID invalid or not accessible |
| `SYNC_PERMISSION_DENIED` | 403 | Service account lacks sheet access |

### Naming Conventions (MUST FOLLOW)

| Element | Pattern | Example |
|---------|---------|---------|
| Python files | `snake_case.py` | `sheets_client.py` |
| Python functions | `snake_case` | `fetch_brands_from_sheet()` |
| Python classes | `PascalCase` | `GoogleSheetsClient` |
| Database tables | `snake_case` plural | `brand_vp_data`, `brand_meeting_data`, `sync_status` |
| Database columns | `snake_case` | `external_id`, `created_at` |
| API endpoints | `/kebab-case` | `/api/v1/sync/status` |
| Error codes | `UPPER_SNAKE` prefix | `SYNC_RATE_LIMITED` |

### Dependencies to Add

**pyproject.toml:**
```toml
dependencies = [
    # ... existing ...
    "google-api-python-client>=2.150.0",
    "google-auth>=2.35.0",
]
```

### Testing Strategy

**Unit Tests:**
```python
# tests/unit/sync/test_sheets_client.py
import pytest
from unittest.mock import MagicMock, patch
from app.modules.sync.sheets_client import GoogleSheetsClient

@pytest.fixture
def mock_sheets_service():
    with patch('app.modules.sync.sheets_client.build') as mock_build:
        yield mock_build

async def test_fetch_brands_returns_parsed_data(mock_sheets_service):
    """Test that sheet data is correctly parsed into brand dictionaries."""
    mock_service = MagicMock()
    mock_sheets_service.return_value = mock_service
    mock_service.spreadsheets().values().get().execute.return_value = {
        'values': [
            ['ID', 'Brand Name', 'Category'],
            ['1', 'Nike', 'Fashion'],
            ['2', 'Samsung', 'Non-Fashion'],
        ]
    }

    client = GoogleSheetsClient()
    brands = await client.fetch_brands_from_sheet()

    assert len(brands) == 2
    assert brands[0]['Brand Name'] == 'Nike'
    assert brands[1]['Category'] == 'Non-Fashion'

async def test_exponential_backoff_on_rate_limit(mock_sheets_service):
    """Test that rate limit triggers exponential backoff retry."""
    from googleapiclient.errors import HttpError

    mock_service = MagicMock()
    mock_sheets_service.return_value = mock_service

    # Fail twice with rate limit, succeed on third
    rate_limit_error = HttpError(
        resp=MagicMock(status=429),
        content=b'Rate limit exceeded'
    )
    mock_service.spreadsheets().values().get().execute.side_effect = [
        rate_limit_error,
        rate_limit_error,
        {'values': [['ID', 'Name'], ['1', 'Brand']]}
    ]

    client = GoogleSheetsClient()
    brands = await client.fetch_brands_from_sheet()

    assert len(brands) == 1
```

**Integration Tests:**
```python
# tests/integration/api/test_sync.py
import pytest
from httpx import AsyncClient

async def test_get_sync_status_requires_auth(client: AsyncClient):
    """Test that sync status endpoint requires authentication."""
    response = await client.get("/api/v1/sync/status")
    assert response.status_code == 401
    assert response.json()["code"] == "AUTH_TOKEN_MISSING"

async def test_get_sync_status_returns_latest(
    authenticated_client: AsyncClient,
    seed_sync_status
):
    """Test that sync status returns the most recent sync."""
    response = await authenticated_client.get("/api/v1/sync/status")
    assert response.status_code == 200
    data = response.json()
    assert "last_sync" in data
    assert "status" in data
```

### Anti-Patterns to Avoid

1. **DO NOT** store Google Sheets credentials in code or commit to git
2. **DO NOT** make synchronous Google API calls in async handlers (use `asyncio.to_thread`)
3. **DO NOT** process all brands in a single transaction (use individual upserts for resilience)
4. **DO NOT** swallow exceptions silently — always log with error code
5. **DO NOT** hardcode spreadsheet IDs or ranges — use configuration
6. **DO NOT** skip retry logic for rate limits — Google Sheets has strict quotas

### Previous Story Intelligence

**From Story 1.1 (Project Structure):**
- Backend uses Python 3.14 with FastAPI
- UV for package management (`uv add` to install dependencies)
- Database connection uses asyncpg pool in `db/connection.py`
- Alembic for migrations in `db/migrations/`
- Module structure: `modules/{feature}/router.py, schemas.py, service.py`

**From Story 1.2 (Firebase Auth Backend):**
- `get_current_user` dependency available for authentication
- Error response format: `{ "code": "...", "detail": "...", "timestamp": "..." }`
- AppException pattern for raising structured errors
- Users table exists with `firebase_uid`, `email`, `role`

**From Story 1.3 (Frontend Login Flow):**
- Frontend auth context and API client with auth token injection exist
- Ready to consume authenticated endpoints

### Git Intelligence Summary

Recent commits show Epic 1 is complete:
- Project structure initialized with FastAPI + React
- Firebase Auth working on both backend and frontend
- Code follows established patterns and conventions

### Important Notes for This Story

1. **No API endpoint to trigger sync yet** — This story only creates the backend sync infrastructure. Story 2.2 will add the `POST /api/v1/sync` endpoint.

2. **Credentials handling** — Service account JSON file should be stored securely. In production, use Secret Manager; in development, use local file path.

3. **Sheet structure assumption** — Assumes first row is headers. VP sheet uses `Nama Brand` column, Meeting sheet uses `Brand` column. Column names are configurable via environment variables.

4. **Partial sync tolerance** — If one brand fails to upsert, continue with others and report errors at the end.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 2.1: Google Sheets Sync Backend]
- [Source: _bmad-output/planning-artifacts/architecture.md#Data Architecture]
- [Source: _bmad-output/planning-artifacts/architecture.md#Implementation Patterns & Consistency Rules]
- [Source: _bmad-output/planning-artifacts/prd.md#Brand Data Management]
- [Source: _bmad-output/implementation-artifacts/1-1-initialize-project-structure.md#Dev Notes]
- [Source: _bmad-output/implementation-artifacts/1-2-firebase-auth-backend-integration.md#Dev Notes]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- All 31 tests pass (pytest): 10 unit tests for sheets_client, 9 unit tests for sync service, 5 integration tests for sync API, existing tests preserved

### Completion Notes List

- **Task 1**: Created migrations 002 (brands), 003 (sync_status), 004 (replace brands with brand_vp_data + brand_meeting_data), and 005 (add sync_details JSONB to sync_status)
- **Task 2**: Implemented brand queries with `upsert_brand_data()` (ON CONFLICT DO UPDATE), `get_brand_data()` with pagination, centralized table validation via `_validate_table()` helper
- **Task 3**: Implemented GoogleSheetsClient with lazy service initialization, `fetch_sheet_data()` generic method, `fetch_vp_data()` and `fetch_meeting_data()` convenience methods, exponential backoff retry (max 3 attempts, 1s/2s/4s delays), error handling for rate limits (429), not found (404), permission denied (403), and credentials issues
- **Task 4**: Implemented `run_sync()` orchestration with two-sheet support (VP + Meeting), partial failure tolerance per sheet and per row, per-sheet breakdown persisted to `sync_details` JSONB
- **Task 5**: Created Pydantic schemas: SyncError, SheetSyncResult, SyncResult (VP + Meeting results), SyncStatusResponse (with sync_details)
- **Task 6**: Created sync router with `GET /api/v1/sync/status` endpoint, requires authentication via `get_current_user` dependency
- **Task 7**: Added per-sheet config (VP: `gsheets_vp_spreadsheet_id`, `gsheets_vp_range`, `gsheets_vp_brand_column`; Meeting: `gsheets_meeting_spreadsheet_id`, `gsheets_meeting_range`, `gsheets_meeting_brand_column`) to Settings; updated .env.example
- **Task 8**: Comprehensive test coverage - 12 unit tests for sheets_client, 9 unit tests for sync service, 5 integration tests for sync API

### Change Log

- 2026-02-05: Implemented Google Sheets sync backend (Story 2.1) - all 8 tasks completed
- 2026-02-05: Added Terraform configuration for Google Sheets Service Account (Epic 2 Critical Path Items #3, #4)
- 2026-02-05: Expanded to two-sheet model (VP + Meeting) with migration 004
- 2026-02-06: Code review fixes - added migration 005 (sync_details JSONB), centralized table validation, fixed Terraform SA naming to `aha-sicu-sheets-sa`, fixed lambda closure in sheets_client, removed unused `delete_all_brand_data()`, updated all documentation

### File List

**New Files:**
- backend/app/db/migrations/versions/002_create_brands_table.py
- backend/app/db/migrations/versions/003_create_sync_status_table.py
- backend/app/db/migrations/versions/004_replace_brands_with_vp_and_meeting.py
- backend/app/db/migrations/versions/005_add_sync_details_to_sync_status.py
- backend/app/db/queries/brands.py
- backend/app/db/queries/sync_status.py
- backend/app/modules/sync/__init__.py
- backend/app/modules/sync/router.py
- backend/app/modules/sync/schemas.py
- backend/app/modules/sync/service.py
- backend/app/modules/sync/sheets_client.py
- backend/tests/unit/sync/__init__.py
- backend/tests/unit/sync/test_sheets_client.py
- backend/tests/unit/sync/test_service.py
- backend/tests/integration/api/test_sync.py
- infrastructure/terraform/README.md (setup documentation)

**Modified Files:**
- backend/app/main.py (added sync router import and registration)
- backend/app/config.py (added Google Sheets settings for VP and Meeting sheets)
- backend/app/core/exceptions.py (added SyncException class)
- backend/.env.example (added Google Sheets environment variables for both sheets)
- backend/pyproject.toml (added google-api-python-client and google-auth dependencies)
- infrastructure/terraform/main.tf (added Google Sheets API and Service Account `aha-sicu-sheets-sa`)
- infrastructure/terraform/variables.tf (added environment variable)
- .gitignore (added credentials directory pattern)

## Senior Developer Review (AI)

**Reviewer:** Mr. Door on 2026-02-06
**Outcome:** Changes Requested (10 issues found, all fixed)

### Findings Summary

| ID | Severity | Issue | Resolution |
|----|----------|-------|------------|
| H1 | HIGH | Story ACs/Dev Notes referenced stale `brands` table instead of `brand_vp_data`/`brand_meeting_data` | Updated story documentation to reflect two-sheet model |
| H2 | HIGH | Task 2 claimed `upsert_brand()` but actual function is `upsert_brand_data()` | Updated task descriptions to match implementation |
| H3 | HIGH | `sync_status` table lost VP/Meeting granularity on persistence | Added migration 005 with `sync_details` JSONB column; updated queries, service, and schemas |
| H4 | HIGH | Terraform SA named `store-icu-gsheets-sync` instead of `aha-sicu-sheets-sa`; SA key in state without warning | Renamed SA, added security warning comments |
| M1 | MEDIUM | Lambda closure in `sheets_client.py` `asyncio.to_thread()` could capture stale reference | Replaced lambda with explicit `request.execute` pattern |
| M2 | MEDIUM | Integration tests use sync TestClient instead of async | Acknowledged as valid — FastAPI's sync TestClient is standard testing approach |
| M3 | MEDIUM | File List missing migration 004 and variables.tf; migration filenames wrong | Updated File List with all files and correct names |
| M4 | MEDIUM | f-string SQL in `brands.py` with per-function validation guards | Centralized validation into `_validate_table()` helper with `_VALID_TABLES` frozenset |
| L1 | LOW | Terraform README showed single-sheet `.env` config | Updated README with two-sheet VP/Meeting config |
| L2 | LOW | Unused `delete_all_brand_data()` function with no tests | Removed function |

### Files Changed in Review

- `backend/app/db/migrations/versions/005_add_sync_details_to_sync_status.py` (new)
- `backend/app/db/queries/brands.py` (centralized validation, removed unused function)
- `backend/app/db/queries/sync_status.py` (added sync_details parameter and column)
- `backend/app/modules/sync/schemas.py` (added sync_details to SyncStatusResponse)
- `backend/app/modules/sync/service.py` (persist per-sheet breakdown, include sync_details in response)
- `backend/app/modules/sync/sheets_client.py` (replaced lambda with explicit request pattern)
- `infrastructure/terraform/main.tf` (renamed SA to `aha-sicu-sheets-sa`, added security warnings)
- `infrastructure/terraform/README.md` (updated to two-sheet config)
- `_bmad-output/implementation-artifacts/2-1-google-sheets-sync-backend.md` (comprehensive documentation update)

