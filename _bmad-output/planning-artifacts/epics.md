---
stepsCompleted: ['step-01-validate-prerequisites', 'step-02-design-epics', 'step-03-create-stories', 'step-04-final-validation']
status: complete
completedAt: '2026-02-04'
inputDocuments:
  - '_bmad-output/planning-artifacts/prd.md'
  - '_bmad-output/planning-artifacts/architecture.md'
---

# Store ICU - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for Store ICU, decomposing the requirements from the PRD, UX Design if it exists, and Architecture requirements into implementable stories.

## Requirements Inventory

### Functional Requirements

**Brand Data Management (FR1-FR5)**
- FR1: System can sync brand data from Google Sheets Brand Database automatically (daily)
- FR2: BD team member can trigger manual sync of brand data on-demand
- FR3: BD team member can view current sync status (last synced timestamp)
- FR4: System can display sync errors when sync fails
- FR5: BD team member can browse and select a brand from the synced brand list to evaluate

**Data Input & Upload (FR6-FR11)**
- FR6: BD team member can upload Excel files for a specific brand's calculator processing
- FR7: System can parse uploaded Excel files using Polars
- FR8: BD team member can enter manual data values for a specific brand
- FR9: System can validate uploaded file format before processing
- FR10: BD team member can re-upload Excel files for a brand (upsert — replaces previous upload)
- FR11: BD team member can edit previously entered manual data for a brand

**Calculators (FR12-FR18)**
- FR12: System can execute Ads Keyword Calculator on a brand's uploaded data
- FR13: System can execute Discount Check Calculator on a brand's uploaded data
- FR14: System can execute Top SKU Calculator on a brand's uploaded data
- FR15: System can execute all calculators automatically after file upload for a brand
- FR16: BD team member can view individual calculator results for a brand
- FR17: System can combine calculator results with manual input data for a brand
- FR18: System can recalculate results when data is updated for a brand

**Final Scoring (FR19-FR22)**
- FR19: BD team member can select scoring template (Fashion or Non-Fashion) for a brand
- FR20: System can generate final score for a brand based on calculator results and manual inputs
- FR21: System can display final score with breakdown of contributing factors for a brand
- FR22: System can recalculate final score when underlying data changes

**Rule Configuration (FR23-FR26)**
- FR23: System owner can view current scoring thresholds and rules
- FR24: System owner can modify scoring thresholds without code deployment
- FR25: System can store rule configurations in database
- FR26: System can apply configured rules during score calculation

**Evaluation Storage & History (FR27-FR33)**
- FR27: System can save completed evaluations permanently (one evaluation per brand per session)
- FR28: BD team member can search evaluations by brand name (partial match)
- FR29: BD team member can filter evaluations by date range
- FR30: BD team member can filter evaluations by category (Fashion/Non-Fashion)
- FR31: BD team member can view full evaluation details (scores, inputs, who evaluated, when)
- FR32: System can track which user performed each evaluation
- FR33: System can maintain evaluation history (previous evaluations for same brand are preserved)

**Real-Time Updates (FR34-FR35)**
- FR34: System can update sync status in real-time without page refresh
- FR35: System can display new evaluations to other users without page refresh

**Authentication & Access (FR36-FR37)**
- FR36: BD team member can authenticate using Firebase Auth
- FR37: System can restrict access to authenticated users only

### NonFunctional Requirements

**Performance**
- NFR1: Page initial load < 3 seconds
- NFR2: Excel file upload + processing (2MB) < 5 seconds
- NFR3: Calculator execution < 2 seconds
- NFR4: Search results < 1 second
- NFR5: Real-time update propagation < 500ms

**Security**
- NFR6: Authentication required for all access (Firebase Auth)
- NFR7: API endpoints protected by JWT validation
- NFR8: Database credentials never exposed to frontend
- NFR9: HTTPS enforced for all connections
- NFR10: Google Sheets API credentials secured (service account)

**Integration**
- NFR11: Google Sheets sync handles API rate limits gracefully (retry with backoff)
- NFR12: Sync failures logged with actionable error messages
- NFR13: Excel file parsing handles .xlsx and .xls formats

**Reliability**
- NFR14: No data loss on evaluation save (database transaction integrity)
- NFR15: Sync status accurately reflects last successful sync
- NFR16: System recovers gracefully from temporary failures
- NFR17: Evaluation history is immutable (past evaluations cannot be accidentally deleted)

### Additional Requirements

**From Architecture Document:**

**Starter Template / Project Initialization:**
- Lean Modular Structure approach (no existing template - custom build)
- Backend: Python 3.14 with FastAPI, modular domain-driven structure
- Frontend: Vite + React + TypeScript with feature-organized structure
- Infrastructure: Terraform for GCP resources

**Infrastructure Requirements:**
- Cloud Run deployment for backend (`aha_sicu_api`)
- Firebase Hosting for frontend (`aha-sicu`)
- Neon PostgreSQL for database
- Resource prefix: `aha_sicu_`
- Region: `asia-southeast1` (Singapore)
- CI/CD via GitHub Actions

**Database Requirements:**
- asyncpg + parameterized SQL (no ORM)
- Alembic for migrations (raw SQL mode)
- Tables: `brands`, `evaluations`, `scoring_rules`, `users`

**API Requirements:**
- REST with raw responses (no wrapper)
- Offset-based pagination (`?page=1&limit=20`)
- Structured error codes (AUTH_, SYNC_, UPLOAD_, CALC_, RULE_)
- SSE for real-time updates (`/api/v1/events`)

**Frontend Requirements:**
- TanStack Query for server state
- React Context for auth state only
- React Hook Form for forms
- openapi-fetch for API client (typed from OpenAPI spec)
- Tailwind CSS for styling

**Security Requirements:**
- Firebase Auth with JWT validation middleware
- Role-based authorization (leader/admin for rule modification)
- Password re-confirmation for rule changes

**Calculator Implementation:**
- Pure functions with no I/O dependencies
- Isolated in `calculators/` module
- Called only by `modules/evaluations/`, never directly by API

### FR Coverage Map

| FR | Epic | Description |
|----|------|-------------|
| FR1 | Epic 2 | Auto sync from two Google Sheets (VP + Meeting) |
| FR2 | Epic 2 | Manual sync trigger |
| FR3 | Epic 2 | View sync status |
| FR4 | Epic 2 | Display sync errors |
| FR5 | Epic 2 | Browse/select brands |
| FR6 | Epic 3 | Upload Excel files |
| FR7 | Epic 3 | Parse Excel with Polars |
| FR8 | Epic 3 | Enter manual data |
| FR9 | Epic 3 | Validate file format |
| FR10 | Epic 3 | Re-upload (upsert) |
| FR11 | Epic 3 | Edit manual data |
| FR12 | Epic 3 | Ads Keyword Calculator |
| FR13 | Epic 3 | Discount Check Calculator |
| FR14 | Epic 3 | Top SKU Calculator |
| FR15 | Epic 3 | Auto-execute calculators |
| FR16 | Epic 3 | View calculator results |
| FR17 | Epic 3 | Combine results + manual input |
| FR18 | Epic 3 | Recalculate on data change |
| FR19 | Epic 3 | Select scoring template |
| FR20 | Epic 3 | Generate final score |
| FR21 | Epic 3 | Display score breakdown |
| FR22 | Epic 3 | Recalculate final score |
| FR23 | Epic 5 | View rules |
| FR24 | Epic 5 | Modify rules |
| FR25 | Epic 5 | Store rules in DB |
| FR26 | Epic 5 | Apply rules during calculation |
| FR27 | Epic 3 | Save evaluations |
| FR28 | Epic 4 | Search by brand name |
| FR29 | Epic 4 | Filter by date range |
| FR30 | Epic 4 | Filter by category |
| FR31 | Epic 4 | View full evaluation details |
| FR32 | Epic 4 | Track evaluator |
| FR33 | Epic 4 | Maintain evaluation history |
| FR34 | Epic 2 | Real-time sync status |
| FR35 | Epic 4 | Real-time new evaluations |
| FR36 | Epic 1 | Firebase Auth login |
| FR37 | Epic 1 | Restrict to authenticated users |

## Epic List

### Epic 1: Secure User Access
Users can securely log in and access the Store ICU application.
**FRs covered:** FR36, FR37
**Additional:** Project initialization (lean modular structure from Architecture)

### Epic 2: Brand Data Availability
BD team can view synced brand data from two Google Sheets (VP + Meeting) and see live sync status.
**FRs covered:** FR1, FR2, FR3, FR4, FR5, FR34

### Epic 3: Brand Evaluation Workflow
BD team can complete a full brand evaluation — upload data, run calculators, get final score, and save it.
**FRs covered:** FR6, FR7, FR8, FR9, FR10, FR11, FR12, FR13, FR14, FR15, FR16, FR17, FR18, FR19, FR20, FR21, FR22, FR27

### Epic 4: Evaluation History & Search
Team leader can search, filter, and review past evaluations with full details.
**FRs covered:** FR28, FR29, FR30, FR31, FR32, FR33, FR35

### Epic 5: Rule Configuration
System owner can view and modify scoring thresholds without code deployment.
**FRs covered:** FR23, FR24, FR25, FR26

---

## Epic 1: Secure User Access

Users can securely log in and access the Store ICU application.

### Story 1.1: Initialize Project Structure (Sprint 0)

> **Sprint 0 Context:** This is a technical enabler story required before user-facing stories can begin. Common pattern for greenfield projects.

As a **developer**,
I want **the project scaffolded with the lean modular structure**,
So that **all future development has a consistent foundation to build upon**.

**Acceptance Criteria:**

**Given** the project repository is empty
**When** the initialization is complete
**Then** the following backend structure exists:
- `backend/app/main.py` - FastAPI app with health check endpoint
- `backend/app/config.py` - Pydantic BaseSettings
- `backend/app/core/` - dependencies.py, exceptions.py, middleware.py, security.py
- `backend/app/db/` - connection.py, queries/, migrations/
- `backend/app/modules/` - placeholder __init__.py
- `backend/app/calculators/` - placeholder __init__.py
- `backend/pyproject.toml`, `backend/Dockerfile`, `backend/.env.example`
**And** the following frontend structure exists:
- `frontend/src/main.tsx`, `frontend/src/App.tsx`
- `frontend/src/components/`, `frontend/src/pages/`, `frontend/src/hooks/`
- `frontend/src/services/`, `frontend/src/firebase/`, `frontend/src/context/`
- `frontend/package.json`, `frontend/vite.config.ts`, `frontend/tailwind.config.js`
**And** the following infrastructure structure exists:
- `infrastructure/terraform/` with main.tf, variables.tf placeholder
- `.github/workflows/ci.yml` stub
**And** backend starts locally with `uvicorn app.main:app` returning `{"status": "healthy"}`
**And** frontend starts locally with `npm run dev` showing a placeholder page

---

### Story 1.2: Firebase Auth Backend Integration

As a **system**,
I want **to validate Firebase JWT tokens on API requests**,
So that **only authenticated users can access protected endpoints**.

**Acceptance Criteria:**

**Given** a request to any `/api/v1/*` endpoint
**When** the request has no `Authorization` header
**Then** return 401 Unauthorized with `{"code": "AUTH_TOKEN_MISSING", "detail": "Authorization header required"}`

**Given** a request with `Authorization: Bearer <invalid_token>`
**When** the backend validates the token via Firebase Admin SDK
**Then** return 401 Unauthorized with `{"code": "AUTH_TOKEN_INVALID", "detail": "Token validation failed"}`

**Given** a request with a valid Firebase JWT token
**When** the backend validates the token
**Then** extract user info (uid, email) from the token
**And** check if user exists in `users` table by `firebase_uid`
**And** if user doesn't exist, create record with role `member`
**And** update `last_login` timestamp
**And** attach user context to request for downstream handlers

**Database Migration:** Create `users` table:
- `id` SERIAL PRIMARY KEY
- `firebase_uid` VARCHAR(128) UNIQUE NOT NULL
- `email` VARCHAR(255) NOT NULL
- `role` VARCHAR(20) DEFAULT 'member' (values: member, leader, admin)
- `created_at` TIMESTAMPTZ DEFAULT NOW()
- `last_login` TIMESTAMPTZ

---

### Story 1.3: Frontend Login Flow

As a **BD team member**,
I want **to log in using my credentials**,
So that **I can access the Store ICU application securely**.

**Acceptance Criteria:**

**Given** I am not logged in
**When** I navigate to any protected page (e.g., `/dashboard`)
**Then** I am redirected to `/login`

**Given** I am on the login page
**When** I enter valid email/password and click "Login"
**Then** Firebase Auth authenticates me
**And** the app stores the auth token
**And** I am redirected to `/dashboard`
**And** the header shows my email and a logout button

**Given** I am logged in and refresh the page
**When** the page loads
**Then** my auth state persists (I remain logged in)
**And** I see the dashboard, not the login page

**Given** I am logged in
**When** I click "Logout"
**Then** Firebase Auth signs me out
**And** I am redirected to `/login`
**And** protected routes are no longer accessible

**Given** I enter invalid credentials
**When** I click "Login"
**Then** I see a user-friendly error message (e.g., "Invalid email or password")
**And** I remain on the login page

---

## Epic 2: Brand Data Availability

BD team can view synced brand data from Google Sheets and see live sync status.

### Story 2.1: Google Sheets Sync Backend

As a **system**,
I want **to sync brand data from two Google Sheets (VP and 1st Meeting)**,
So that **the BD team has up-to-date brand information to evaluate**.

**Acceptance Criteria:**

**Given** the Google Sheets API credentials are configured (service account)
**When** the sync service is triggered (manual or scheduled)
**Then** connect to the Brand Database spreadsheet using the configured Sheet ID
**And** read all brand rows from the designated range
**And** for each brand row, upsert into `brands` table (match by unique identifier)
**And** record sync timestamp in `sync_status` table
**And** return sync summary (brands synced count, errors if any)

**Given** the Google Sheets API returns a rate limit error
**When** the sync is in progress
**Then** implement exponential backoff retry (max 3 attempts)
**And** log the retry attempts with `SYNC_RATE_LIMITED` code

**Given** the sync fails after retries
**When** recording the result
**Then** store error details in `sync_status` with `success: false`
**And** log error with `SYNC_FAILED` code and actionable message

**Database Migration:** Create brand data tables:

`brand_vp_data` (primary brand list from VP sheet):
- `id` SERIAL PRIMARY KEY
- `brand_name` VARCHAR(255) UNIQUE NOT NULL
- `raw_data` JSONB NOT NULL
- `created_at` TIMESTAMPTZ DEFAULT NOW()
- `updated_at` TIMESTAMPTZ DEFAULT NOW()
- Indexes: `idx_brand_vp_data_brand_name`, `idx_brand_vp_data_updated_at`

`brand_meeting_data` (supplementary from 1st Meeting sheet):
- `id` SERIAL PRIMARY KEY
- `brand_name` VARCHAR(255) UNIQUE NOT NULL
- `raw_data` JSONB NOT NULL
- `created_at` TIMESTAMPTZ DEFAULT NOW()
- `updated_at` TIMESTAMPTZ DEFAULT NOW()
- Indexes: `idx_brand_meeting_data_brand_name`, `idx_brand_meeting_data_updated_at`

`sync_status`:
- `id` SERIAL PRIMARY KEY
- `started_at` TIMESTAMPTZ NOT NULL
- `completed_at` TIMESTAMPTZ
- `success` BOOLEAN
- `brands_synced` INTEGER DEFAULT 0
- `error_message` TEXT
- `sync_details` JSONB (per-sheet breakdown)
- Index: `idx_sync_status_started_at` DESC

---

### Story 2.2: Manual Sync Trigger API

As a **BD team member**,
I want **to trigger a manual sync of brand data**,
So that **I can get the latest brands without waiting for the daily auto-sync**.

**Acceptance Criteria:**

**Given** I am authenticated
**When** I call `POST /api/v1/sync`
**Then** the sync process starts
**And** return `{"status": "started", "sync_id": <id>}` immediately (async)

**Given** a sync is already in progress
**When** I call `POST /api/v1/sync`
**Then** return 409 Conflict with `{"code": "SYNC_IN_PROGRESS", "detail": "A sync is already running"}`

**Given** I call `GET /api/v1/sync/status`
**When** authenticated
**Then** return the latest sync status:
```json
{
  "last_sync": "2026-02-04T10:30:00Z",
  "status": "success" | "failed" | "in_progress",
  "brands_synced": 150,
  "error_message": null
}
```

---

### Story 2.3: Brand List UI with Sync Status

As a **BD team member**,
I want **to see the list of synced brands and current sync status**,
So that **I can select a brand to evaluate and know if data is fresh**.

**Acceptance Criteria:**

**Pre-requisite Task:** Initialize shadcn/ui in the frontend project (Tailwind v4 compatible).
Install foundation components: Button, Input, Card, Badge, Table, Toast, Dialog, Progress.

**Given** I am logged in and on the Brands page
**When** the page loads
**Then** I see a header showing "Last synced: [timestamp]" or "Sync in progress..."
**And** sync status shows per-sheet breakdown (VP synced, Meeting synced)
**And** I see a "Sync Now" button
**And** I see a paginated list of brands from VP data (20 per page)
**And** each brand card shows: brand name and key fields from raw_data
**And** if Meeting data exists for a brand, supplementary info is displayed

**Given** I click "Sync Now"
**When** the sync starts
**Then** the button shows a loading state
**And** the status updates to "Syncing..."
**And** when complete, the timestamp updates and brand list refreshes

**Given** the sync fails
**When** viewing the status
**Then** I see "Last sync failed: [error message]" in red
**And** I can click "Sync Now" to retry

**Given** I want to find a specific brand
**When** I type in the search box
**Then** the brand list filters by name (client-side for current page, or API search)

---

### Story 2.4: Real-Time Sync Status via SSE

As a **BD team member**,
I want **to see sync status update in real-time without refreshing**,
So that **I know immediately when new data is available**.

**Acceptance Criteria:**

**Given** I am logged in and connected to the app
**When** I establish connection to `GET /api/v1/events` (SSE endpoint)
**Then** receive a stream of server-sent events

**Given** a sync starts (by me or another user or scheduler)
**When** the sync status changes
**Then** the server broadcasts `event: sync_status` with data:
```json
{"status": "in_progress", "started_at": "..."}
```

**Given** a sync completes
**When** the status changes
**Then** broadcast `event: sync_status` with data:
```json
{"status": "success", "completed_at": "...", "brands_synced": 150}
```

**Given** the frontend receives a `sync_status` event
**When** rendering
**Then** update the sync status display without page refresh

---

### Story 2.5: Daily Automatic Sync (Cloud Scheduler)

As a **system**,
I want **to automatically sync brand data daily**,
So that **the BD team always has fresh data without manual intervention**.

**Acceptance Criteria:**

**Given** Cloud Scheduler is configured
**When** the scheduled time arrives (e.g., 6:00 AM WIB daily)
**Then** trigger `POST /api/v1/sync` with a service account token

**Given** the scheduled sync runs
**When** it completes (success or failure)
**Then** the result is recorded in `sync_status` table
**And** SSE broadcasts the status to connected clients

**Infrastructure:** Add to Terraform:
- `aha_sicu_daily_sync` Cloud Scheduler job
- Service account with invoker permissions

---

## Epic 3: Brand Evaluation Workflow

BD team can complete a full brand evaluation — upload data, run calculators, get final score, and save it.

### Story 3.1: Start Evaluation for a Brand

As a **BD team member**,
I want **to start an evaluation session for a selected brand**,
So that **I can begin the evaluation workflow**.

**Acceptance Criteria:**

**Given** I am on the Brands page (showing VP brand list)
**When** I click "Evaluate" on a brand card
**Then** I am navigated to `/evaluation/{brand_id}`
**And** I see the brand name and basic info at the top
**And** I see the evaluation form with sections: Data Upload, Manual Input, Calculator Results, Final Score

**Given** I have a previous in-progress evaluation for this brand
**When** I start a new evaluation
**Then** I see the previous data pre-filled (manual inputs, uploaded file reference)
**And** I can modify or continue from where I left off

---

### Story 3.2: Excel File Upload and Parsing

As a **BD team member**,
I want **to upload an Excel file for a brand**,
So that **the system can process it through the calculators**.

**Acceptance Criteria:**

**Given** I am on the evaluation page for a brand
**When** I click "Upload Excel" and select a .xlsx or .xls file (≤2MB)
**Then** the file uploads to the backend
**And** I see a progress indicator during upload
**And** the backend validates the file format
**And** Polars parses the file and extracts relevant data
**And** I see "File uploaded successfully" with filename displayed

**Given** I upload an invalid file (wrong format, >2MB, corrupted)
**When** validation fails
**Then** return error with code `UPLOAD_INVALID_FORMAT` or `UPLOAD_FILE_TOO_LARGE`
**And** I see a user-friendly error message
**And** the previous file (if any) remains unchanged

**Given** I upload a new file for a brand that already has one
**When** the upload succeeds
**Then** the new file replaces the old one (upsert behavior)
**And** calculator results are cleared (need to re-run)

**Database Migration:** Create `brand_uploads` table:
- `id` SERIAL PRIMARY KEY
- `brand_id` INTEGER REFERENCES brand_vp_data(id)
- `filename` VARCHAR(255)
- `file_size` INTEGER
- `parsed_data` JSONB (extracted data from Polars)
- `uploaded_by` INTEGER REFERENCES users(id)
- `uploaded_at` TIMESTAMPTZ DEFAULT NOW()
- UNIQUE(brand_id) -- only one active upload per brand

---

### Story 3.3: Manual Data Input Form

As a **BD team member**,
I want **to enter manual data values for a brand evaluation**,
So that **I can provide information that isn't in the Excel file**.

**Acceptance Criteria:**

**Given** I am on the evaluation page
**When** I view the Manual Input section
**Then** I see form fields for marketplace-specific metrics and qualitative notes
**And** fields have appropriate input types (number, text, dropdown)

**Given** I fill in manual input fields
**When** I change a value
**Then** the form auto-saves after a short debounce (or explicit "Save" button)
**And** I see "Saved" indicator

**Given** I return to an evaluation later
**When** the page loads
**Then** my previously entered manual data is pre-filled

**Given** I want to edit existing manual data
**When** I modify a field and save
**Then** the value updates in the database
**And** if calculators were already run, they are marked as "stale" (need recalculation)

**Database Migration:** Create `evaluation_inputs` table:
- `id` SERIAL PRIMARY KEY
- `brand_id` INTEGER REFERENCES brand_vp_data(id)
- `user_id` INTEGER REFERENCES users(id)
- `manual_data` JSONB (flexible key-value for manual inputs)
- `created_at` TIMESTAMPTZ DEFAULT NOW()
- `updated_at` TIMESTAMPTZ DEFAULT NOW()
- UNIQUE(brand_id, user_id) -- one input set per user per brand

---

### Story 3.4: Ads Keyword Calculator

As a **system**,
I want **to execute the Ads Keyword Calculator on uploaded data**,
So that **the BD team gets the ads keyword analysis as part of the evaluation**.

**Acceptance Criteria:**

**Given** a brand has uploaded Excel data with the required columns for Ads Keyword calculation
**When** the calculator is executed
**Then** apply the exact formula logic from the original Google Sheet
**And** return structured results:
```json
{
  "calculator": "ads_keyword",
  "score": 75.5,
  "details": { "keyword_count": 120, "relevant_keywords": 90, ... },
  "calculated_at": "2026-02-04T10:30:00Z"
}
```

**Given** the uploaded data is missing required columns
**When** attempting calculation
**Then** return error with code `CALC_MISSING_DATA` and specify which columns are missing

**Given** the calculator runs successfully
**When** storing results
**Then** save to `calculator_results` table linked to brand and evaluation session

**Implementation:** Pure function in `calculators/ads_keyword.py` - no database I/O inside calculator

**Database Migration:** Create `calculator_results` table:
- `id` SERIAL PRIMARY KEY
- `brand_id` INTEGER REFERENCES brand_vp_data(id)
- `calculator_type` VARCHAR(50) (ads_keyword, discount, top_sku)
- `score` DECIMAL(10,2)
- `details` JSONB
- `calculated_at` TIMESTAMPTZ DEFAULT NOW()
- UNIQUE(brand_id, calculator_type) -- upsert on recalculation

---

### Story 3.5: Discount Check Calculator

As a **system**,
I want **to execute the Discount Check Calculator on uploaded data**,
So that **the BD team gets the discount analysis as part of the evaluation**.

**Acceptance Criteria:**

**Given** a brand has uploaded Excel data with the required columns for Discount Check
**When** the calculator is executed
**Then** apply the exact formula logic from the original Google Sheet
**And** return structured results:
```json
{
  "calculator": "discount",
  "score": 82.0,
  "details": { "avg_discount": 15.5, "discount_frequency": 0.3, ... },
  "calculated_at": "2026-02-04T10:30:00Z"
}
```

**Given** the uploaded data is missing required columns
**When** attempting calculation
**Then** return error with code `CALC_MISSING_DATA`

**Implementation:** Pure function in `calculators/discount.py`

---

### Story 3.6: Top SKU Calculator

As a **system**,
I want **to execute the Top SKU Calculator on uploaded data**,
So that **the BD team gets the SKU analysis as part of the evaluation**.

**Acceptance Criteria:**

**Given** a brand has uploaded Excel data with the required columns for Top SKU
**When** the calculator is executed
**Then** apply the exact formula logic from the original Google Sheet
**And** return structured results:
```json
{
  "calculator": "top_sku",
  "score": 68.0,
  "details": { "top_sku_count": 5, "top_sku_revenue_share": 0.45, ... },
  "calculated_at": "2026-02-04T10:30:00Z"
}
```

**Given** the uploaded data is missing required columns
**When** attempting calculation
**Then** return error with code `CALC_MISSING_DATA`

**Implementation:** Pure function in `calculators/top_sku.py`

---

### Story 3.7: Calculator Orchestration and Auto-Execute

As a **system**,
I want **to run all calculators automatically after file upload**,
So that **the BD team sees results immediately without manual triggering**.

**Acceptance Criteria:**

**Given** a brand file upload completes successfully
**When** the upload is processed
**Then** automatically trigger all three calculators (ads_keyword, discount, top_sku)
**And** run them in parallel for performance
**And** store all results in `calculator_results` table

**Given** any calculator fails
**When** orchestrating
**Then** continue with other calculators (don't fail all)
**And** record which calculators succeeded/failed
**And** return partial results with error details for failed ones

**Given** manual data changes after calculators ran
**When** the user saves manual input
**Then** mark calculator results as "stale" but don't auto-recalculate
**And** show "Recalculate" button to user

**Given** user clicks "Recalculate"
**When** triggered
**Then** re-run all calculators with current data
**And** update results

**Implementation:** Orchestration in `calculators/engine.py`

---

### Story 3.8: Calculator Results Display

As a **BD team member**,
I want **to view the results of each calculator**,
So that **I understand the brand's performance across different metrics**.

**Acceptance Criteria:**

**Given** I am on the evaluation page and calculators have run
**When** viewing the Calculator Results section
**Then** I see a card for each calculator showing:
- Calculator name
- Score (prominently displayed)
- Key details (expandable)
- Calculated timestamp

**Given** a calculator failed
**When** viewing results
**Then** I see an error state for that calculator with the error message
**And** a "Retry" button

**Given** results are stale (data changed since calculation)
**When** viewing results
**Then** I see a "Stale - Recalculate" indicator
**And** clicking it re-runs the calculators

---

### Story 3.9: Final Scoring with Template Selection

As a **BD team member**,
I want **to generate a final score using Fashion or Non-Fashion template**,
So that **I get the overall brand qualification score**.

**Acceptance Criteria:**

**Given** I am on the evaluation page with calculator results available
**When** I view the Final Score section
**Then** I see a template selector (Fashion / Non-Fashion)
**And** the brand's category pre-selects the appropriate template

**Given** I select a scoring template
**When** calculator results and manual inputs are available
**Then** the system combines them using the template's formula
**And** generates a final score (0-100)
**And** displays score breakdown showing contribution of each factor

**Given** the final score is generated
**When** viewing the result
**Then** I see:
- Final score prominently (e.g., "78/100")
- Score interpretation (e.g., "Good Candidate", "Needs Review", "Not Recommended")
- Breakdown table showing each input's contribution
- Template used (Fashion/Non-Fashion)

**Implementation:** Pure function in `calculators/scoring.py` with template logic

---

### Story 3.10: Save Evaluation

As a **BD team member**,
I want **to save a completed evaluation permanently**,
So that **it becomes part of the evaluation history for this brand**.

**Acceptance Criteria:**

**Given** I have a final score generated
**When** I click "Save Evaluation"
**Then** create a new record in `evaluations` table with:
- All calculator results (snapshot)
- Manual input data (snapshot)
- Final score and breakdown
- Template used
- User who evaluated
- Timestamp
**And** show success message "Evaluation saved"
**And** the evaluation appears in history

**Given** I already saved an evaluation for this brand today
**When** I save again
**Then** create a NEW evaluation record (not upsert)
**And** previous evaluations are preserved (history)

**Given** the save fails (database error)
**When** attempting to save
**Then** show error message
**And** data is not lost (still on screen)
**And** I can retry

**Database Migration:** Create `evaluations` table:
- `id` SERIAL PRIMARY KEY
- `brand_id` INTEGER REFERENCES brand_vp_data(id)
- `user_id` INTEGER REFERENCES users(id)
- `template` VARCHAR(20) (fashion, non_fashion)
- `final_score` DECIMAL(5,2)
- `score_breakdown` JSONB
- `calculator_results` JSONB (snapshot)
- `manual_inputs` JSONB (snapshot)
- `created_at` TIMESTAMPTZ DEFAULT NOW()

---

## Epic 4: Evaluation History & Search

Team leader can search, filter, and review past evaluations with full details.

### Story 4.1: Evaluation History List

As a **BD team leader**,
I want **to view a list of all past evaluations**,
So that **I can review the team's work and find specific evaluations**.

**Acceptance Criteria:**

**Given** I am logged in and navigate to `/history`
**When** the page loads
**Then** I see a paginated list of evaluations (20 per page)
**And** each row shows: Brand name (from VP data), Final score, Template, Evaluator, Date
**And** I can click a row to view full details

**Given** there are more than 20 evaluations
**When** I click "Next" or a page number
**Then** the list updates with the next page of results

**Given** I want to sort the list
**When** I click a column header (e.g., Date, Score)
**Then** the list sorts by that column (toggle asc/desc)

---

### Story 4.2: Search by Brand Name

As a **BD team leader**,
I want **to search evaluations by brand name**,
So that **I can quickly find a specific brand's evaluation history**.

**Acceptance Criteria:**

**Given** I am on the History page
**When** I type in the search box (e.g., "Nike")
**Then** the list filters to evaluations where brand name (from brand_vp_data) contains the search term (case-insensitive)
**And** partial matches work (e.g., "Nik" matches "Nike")

**Given** no results match my search
**When** viewing the list
**Then** I see "No evaluations found for '[search term]'"

**API:** `GET /api/v1/evaluations?search=Nike`

---

### Story 4.3: Filter by Date Range

As a **BD team leader**,
I want **to filter evaluations by date range**,
So that **I can find evaluations from a specific time period**.

**Acceptance Criteria:**

**Given** I am on the History page
**When** I select a date range using date pickers (From / To)
**Then** the list filters to evaluations within that date range

**Given** I select only a "From" date
**When** filtering
**Then** show evaluations from that date onwards

**Given** I select only a "To" date
**When** filtering
**Then** show evaluations up to and including that date

**API:** `GET /api/v1/evaluations?date_from=2026-01-01&date_to=2026-01-31`

---

### Story 4.4: Filter by Category

As a **BD team leader**,
I want **to filter evaluations by category (Fashion/Non-Fashion)**,
So that **I can review evaluations for a specific product type**.

**Acceptance Criteria:**

**Given** I am on the History page
**When** I select "Fashion" from the category filter dropdown
**Then** the list shows only evaluations with template = "fashion"

**Given** I select "Non-Fashion"
**When** filtering
**Then** the list shows only evaluations with template = "non_fashion"

**Given** I select "All"
**When** filtering
**Then** the list shows all evaluations regardless of template

**API:** `GET /api/v1/evaluations?category=fashion`

---

### Story 4.5: Evaluation Detail View

As a **BD team leader**,
I want **to view full details of a past evaluation**,
So that **I have complete context for decision-making**.

**Acceptance Criteria:**

**Given** I click on an evaluation in the history list
**When** the detail view opens (modal or page)
**Then** I see:
- Brand name and basic info (from VP data, enriched with Meeting data if available)
- Final score with interpretation
- Score breakdown table
- All calculator results with details
- Manual input values
- Template used
- Evaluator name and email
- Evaluation timestamp

**Given** I am viewing evaluation details
**When** I want to return to the list
**Then** I can close the modal or click "Back to History"

---

### Story 4.6: Real-Time New Evaluation Notifications

As a **BD team member**,
I want **to see when new evaluations are saved by teammates**,
So that **I stay informed without refreshing**.

**Acceptance Criteria:**

**Given** I am connected to SSE endpoint
**When** another user saves a new evaluation
**Then** the server broadcasts `event: new_evaluation` with data:
```json
{
  "evaluation_id": 123,
  "brand_name": "Nike",
  "score": 78,
  "evaluator": "rina@company.com",
  "created_at": "2026-02-04T10:30:00Z"
}
```

**Given** I receive a `new_evaluation` event
**When** I am on the History page
**Then** show a toast notification "New evaluation: Nike (78) by Rina"
**And** optionally refresh the list or show "New evaluations available" banner

---

## Epic 5: Rule Configuration

System owner can view and modify scoring thresholds without code deployment.

### Story 5.1: View Current Scoring Rules

As a **system owner**,
I want **to view the current scoring thresholds and rules**,
So that **I understand how scores are calculated**.

**Acceptance Criteria:**

**Given** I am logged in with role `leader` or `admin`
**When** I navigate to `/rules`
**Then** I see the current scoring configuration:
- Fashion template thresholds and weights
- Non-Fashion template thresholds and weights
- Score interpretation ranges (e.g., 0-40 = Not Recommended, 41-70 = Needs Review, 71-100 = Good Candidate)

**Given** I am logged in with role `member`
**When** I try to access `/rules`
**Then** I see "Access Denied" or am redirected to dashboard

**Database Migration:** Create `scoring_rules` table:
- `id` SERIAL PRIMARY KEY
- `template` VARCHAR(20) (fashion, non_fashion)
- `rules` JSONB (thresholds, weights, interpretations)
- `version` INTEGER DEFAULT 1
- `updated_by` INTEGER REFERENCES users(id)
- `updated_at` TIMESTAMPTZ DEFAULT NOW()

Seed with default rules on first migration.

---

### Story 5.2: Edit Scoring Rules with Password Confirmation

As a **system owner**,
I want **to modify scoring thresholds with password re-confirmation**,
So that **rules can be updated safely without code deployment**.

**Acceptance Criteria:**

**Given** I am on the Rules page with leader/admin role
**When** I click "Edit Rules"
**Then** I see an editable form with current thresholds and weights

**Given** I modify a threshold value
**When** I click "Save Changes"
**Then** a modal appears asking for my password to confirm

**Given** I enter my correct password
**When** I confirm
**Then** the new rules are saved to database
**And** rule `version` increments
**And** `updated_by` and `updated_at` are recorded
**And** I see "Rules updated successfully"

**Given** I enter an incorrect password
**When** I confirm
**Then** I see "Incorrect password"
**And** rules are NOT saved
**And** I can retry or cancel

**Given** rules are updated
**When** a new evaluation calculates scores
**Then** the new rules are applied
**And** the evaluation record stores which rule version was used

---

### Story 5.3: Apply Configured Rules in Scoring

As a **system**,
I want **to apply the configured rules during score calculation**,
So that **scoring reflects the latest business thresholds**.

**Acceptance Criteria:**

**Given** a final score calculation is triggered
**When** the scoring calculator runs
**Then** fetch current rules from `scoring_rules` table for the selected template
**And** apply thresholds and weights from the rules
**And** include `rule_version` in the evaluation record

**Given** rules were updated after an evaluation was saved
**When** viewing a historical evaluation
**Then** show the rule version used at time of evaluation
**And** optionally show "Rules have been updated since this evaluation"

**Implementation:** Scoring calculator reads rules from DB (via service layer, not inside pure function)
