# Architecture - Backend

**Generated:** 2026-02-16 | **Scan Level:** Exhaustive | **Part:** backend | **Type:** backend

## Overview

The backend is a FastAPI REST API running on Python 3.14. It provides authentication, brand data management, evaluation scoring, file processing, Google Sheets sync, and real-time events. The scoring engine implements a 75-row scoring system with configurable rules.

## Technology Stack

| Category | Technology | Version |
|----------|-----------|---------|
| Language | Python | 3.14 |
| Framework | FastAPI | 0.115+ |
| ASGI Server | Uvicorn | 0.32+ |
| Config | Pydantic Settings | 2.6+ |
| Database | PostgreSQL (Neon) | - |
| DB Driver | asyncpg | 0.30+ |
| DB Migrations | Alembic | 1.13+ |
| Auth | Firebase Admin SDK | 6.0+ |
| Data Processing | Polars | 1.0+ |
| Excel Parsing | fastexcel | 0.12+ |
| Cloud Storage | google-cloud-storage | 2.18+ |
| Google Sheets | google-api-python-client | 2.150+ |
| SSE | sse-starlette | 3.2+ |
| Testing | Pytest + pytest-asyncio | 8.0+ |
| Linting | Ruff | 0.11+ |
| Package Manager | UV | latest |

## Architecture Pattern

**Modular service-based API** with domain-driven module organization:

```
app/
├── main.py              # App factory, router registration
├── config.py            # Environment configuration
├── core/                # Cross-cutting concerns
├── db/                  # Data access layer
├── modules/             # Domain modules (feature-based)
├── calculators/         # Pure function business logic
└── services/            # Shared services
```

## Module Architecture

Each domain module follows a consistent structure:

```
module/
├── router.py     # FastAPI route handlers (controllers)
├── service.py    # Business logic layer
└── schemas.py    # Pydantic request/response models
```

### Modules

| Module | Endpoints | Purpose |
|--------|-----------|---------|
| `auth` | 1 | User authentication, auto-registration |
| `brands` | 2 | Brand data retrieval (VP + meeting data) |
| `evaluations` | 12 | Evaluation CRUD, calculators, scoring, save |
| `rules` | 2 | Scoring rules management (leader/admin) |
| `sync` | 2 | Google Sheets → PostgreSQL sync |
| `upload` | 3-4 | File upload via GCS signed URLs |
| `events` | 1 | Server-Sent Events stream |

## Authentication Architecture

### Dual-Mode Auth

1. **Firebase Auth** (user requests):
   - Bearer token in `Authorization` header
   - `core/security.py` verifies via Firebase Admin SDK
   - Auto-creates user record on first login

2. **OIDC Auth** (Cloud Scheduler):
   - Google OIDC token verification
   - Validates audience matches Cloud Run URL
   - Optional allow-list for service account emails
   - Used for scheduled sync triggers

### Dependency Injection

```python
# core/dependencies.py
async def get_db() -> asyncpg.Connection    # DB connection from pool
async def get_current_user() -> dict        # Firebase token verification
async def require_role(*roles) -> Depends   # Role-based access check
```

## Database Architecture

### Connection Management
- `asyncpg` connection pool (5-20 connections)
- Pool created on app startup, closed on shutdown
- Per-request connection via `get_db()` dependency

### Query Layer
Raw SQL queries in `db/queries/` modules — no ORM:
- `users.py` — User CRUD
- `brands.py` — Brand queries with VP/meeting JOINs
- `evaluations.py` — Evaluation state + snapshot queries
- `rules.py` — Scoring rules CRUD with version increment
- `sync_status.py` — Sync operation tracking
- `uploads.py` — File upload metadata
- `calculator_results.py` — Calculator output storage
- `utils.py` — SQL escape helpers

### Migration Strategy
Alembic migrations in `db/migrations/`:
- 13 migrations total (001-013)
- Run via `alembic upgrade head`
- Schema evolved from generic brands → split VP/meeting tables
- Scoring rules unified from fashion/non_fashion → single default template

## Calculator Architecture

Calculators are **pure functions** (no I/O, no database access):

```
engine.py (orchestration)
├── check_calculator_readiness()     # Check file/input prerequisites
├── run_ready_calculators()          # Run all ready calculators
├── run_calculators_for_upload()     # Run affected calcs after upload
└── clear_dependent_results()       # Clear stale results on re-upload

scoring.py (final scoring)
└── calculate_score()                # 75-row scoring system

ads_keyword.py
└── calculate_ads_keyword()          # CPC Ad + Keyword analysis

top_sku.py
└── calculate_top_sku()              # Top SKU ranking by revenue

discount.py
└── calculate_discount()             # Discount check + fake detection
```

### Calculator Dependencies

```
ads_keyword ← cpc_ad_report + keyword_report + total_products (manual)
top_sku     ← order_export + mass_update
discount    ← order_export
```

### Scoring System

The scoring engine (`scoring.py`) implements an 11-category scoring framework:

| Category | Max Score | Data Source |
|----------|-----------|-------------|
| Operational | 0 (info) | Manual inputs |
| Business | 0 (info) | Manual inputs |
| Content | 0 (info) | Manual inputs |
| Visitors | 15 | Manual inputs |
| Promo Tools | 15 | Manual inputs |
| Products/Status | 10 | Manual inputs |
| Ads | 20 | Manual + calculator |
| Campaign | 10 | Manual inputs |
| Stock | 15 | Calculator (top_sku) |
| Discount | 15 | Calculator (discount) |
| **Total** | **100** | |

Verdicts: `✔️` (Approved), `❌` (Rejected), `❌ Non Mall`, `❌ No Brand`, `❌ Opex`, `⭕️` (Special)

## Event Broadcasting

### SSE Architecture
```
EventBroadcaster (singleton)
├── subscribers: set[asyncio.Queue]    # Per-client message queues
├── subscribe() → Queue                # Register client
├── unsubscribe(queue)                 # Deregister client
└── broadcast(event, data)             # Fan-out to all subscribers

Events Router
└── GET /api/v1/events?token=...       # SSE endpoint
    └── Yields events until client disconnect
```

- Max 64 messages per client queue
- Warning at 10 concurrent subscribers
- Auth via query param (EventSource API limitation)

## Upload Processing Pipeline

```
1. POST /upload/signed-url → Generate GCS signed URL (15-min expiry)
2. Client XHR PUT to GCS signed URL (with progress tracking)
3. POST /upload/process → Backend:
   a. Download from GCS (or local dev storage)
   b. Parse CSV/Excel via parser.py
   c. Validate and count rows
   d. Store parsed data in brand_uploads table
   e. Auto-run dependent calculators
   f. Return upload info + calculator results
```

### File Types

| File Type | Calculator Target | Format |
|-----------|------------------|--------|
| `cpc_ad_report` | ads_keyword | CSV/Excel |
| `keyword_report` | ads_keyword | CSV/Excel |
| `order_export` | discount, top_sku | CSV/Excel |
| `mass_update` | top_sku | CSV/Excel |

## Google Sheets Sync

```
POST /sync → Triggers background sync
  ├── Advisory lock (prevents concurrent syncs)
  ├── Fetch VP Sheet (Google Sheets API)
  ├── Fetch Meeting Sheet (Google Sheets API)
  ├── Upsert to brand_vp_data table
  ├── Upsert to brand_meeting_data table
  ├── Record sync_status
  └── Broadcast sync_status event via SSE
```

## Middleware

- **CORS**: Configurable origins (dev: localhost:5173, prod: Firebase Hosting URLs)
- **Request Logging**: Custom middleware logs request method, path, status, duration

## Error Handling

- `core/exceptions.py` — Custom exception handlers
- Standard HTTP error codes (401, 403, 404, 409, 422, 500)
- Consistent error response format: `{ "detail": "..." }`

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | Neon PostgreSQL connection string |
| `FIREBASE_CREDENTIALS_PATH` | One of | Path to Firebase service account JSON |
| `FIREBASE_CREDENTIALS_JSON` | One of | Firebase SA JSON as string |
| `CLOUD_RUN_URL` | Prod | Cloud Run URL for OIDC audience |
| `GCS_UPLOAD_BUCKET` | Prod | GCS bucket for file uploads |
| `GSHEETS_CREDENTIALS_PATH` | One of | Google Sheets SA credentials path |
| `GSHEETS_CREDENTIALS_JSON` | One of | Google Sheets SA JSON string |
| `GSHEETS_VP_SPREADSHEET_ID` | Yes | VP data Google Sheet ID |
| `GSHEETS_MEETING_SPREADSHEET_ID` | Yes | Meeting data Google Sheet ID |
| `DATABASE_POOL_MIN` | No | Min pool connections (default: 5) |
| `DATABASE_POOL_MAX` | No | Max pool connections (default: 20) |
| `ALLOWED_SCHEDULER_EMAILS` | No | Allowed OIDC service accounts |

## Testing

- **41 test files** total (16 integration + 13+ unit)
- `pytest --asyncio-mode=auto`
- Integration tests mock DB and Firebase auth
- Unit tests for calculators are pure function tests
- Coverage areas: auth, brands, calculators, evaluations, events, rules, scoring, sync, upload
