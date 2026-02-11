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
- FR6: BD team member can upload data files (CSV and Excel) for a specific brand's calculator processing — multiple files per evaluation, each routed to its target calculator
- FR7: System can parse uploaded data files (CSV and Excel) using Polars
- FR8: BD team member can enter manual data values for a specific brand, organized by scoring system categories (~40+ fields across operational, business, content, visitors, promo, ads, campaign, competition, stock, and discount sections)
- FR9: System can validate uploaded file format and per-calculator column schema before processing
- FR10: BD team member can re-upload data files for a brand (upsert — replaces previous upload per file type)
- FR11: BD team member can edit previously entered manual data for a brand

**Calculators (FR12-FR18)**
- FR12: System can execute Ads Keyword Calculator using CPC Ad Report CSV and Keyword Placement Report CSV, producing text-based ad analysis with overview, type breakdown, recommendations, top/bottom performers, and flags
- FR13: System can execute Discount Check Calculator using Order Export data, producing discount percentage analysis, range, voucher/bundle percentages, and fake discount detection flag
- FR14: System can execute Top SKU Calculator using Order Export and Mass Update data, producing top 20% selling SKU tables (with revenue and stock) and average stock metric
- FR15: System can execute applicable calculators when their required input files become available for a brand
- FR16: BD team member can view individual calculator results for a brand — text summaries with flags (Ads Keyword), ranked product tables (Top SKU), and discount analysis text (Discount Check)
- FR17: System can combine calculator results with manual input data for a brand using the 75-row scoring system template (Fashion/Non-Fashion variants) to produce final score, category breakdowns, and output messages
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
- NFR13: File parsing handles .csv, .xlsx, and .xls formats

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

### Story 2.6: Retrofit Accessibility Basics

As a **BD team member using assistive technology**,
I want **core UI elements to have proper ARIA annotations and keyboard patterns**,
So that **I can navigate and operate Store ICU with a screen reader or keyboard alone**.

> **Context:** Accessibility audit found ~50% compliance. Good foundation exists (Radix UI primitives, semantic HTML, proper form labels on LoginPage). This story addresses high-impact, low-effort gaps across existing Epic 2 components.

**Acceptance Criteria:**

**AC1 — Icon-only buttons have accessible names**

**Given** the app renders icon-only buttons (e.g., sync, logout, search clear, pagination arrows)
**When** a screen reader focuses any icon-only button
**Then** it announces a meaningful label (via `aria-label`)
**And** the following components are updated:
  - `Header.tsx` — logout button, any icon-only actions
  - `BrandTable.tsx` — pagination arrows, sort toggles
  - `SyncStatus.tsx` — sync trigger button (if icon-only variant)
  - `BrandsPage.tsx` — search clear button, any icon-only filter controls

**AC2 — Live regions announce sync state changes**

**Given** the sync status changes (idle → syncing → success/failure)
**When** `SyncStatus.tsx` renders the updated state
**Then** the status text is wrapped in an `aria-live="polite"` region
**And** sync completion or failure is announced to screen readers without requiring focus change

**AC3 — Skip-to-content link exists**

**Given** I land on any page using keyboard navigation
**When** I press Tab as the first action
**Then** a "Skip to main content" link becomes visible
**And** activating it moves focus to the `<main>` landmark (or primary content area)
**And** the link is implemented in `App.tsx` or the top-level layout component

**AC4 — Search input has an accessible label**

**Given** the brand search input on `BrandsPage.tsx`
**When** a screen reader focuses the input
**Then** it announces a descriptive label (e.g., "Search brands")
**And** the label is either a visually-hidden `<label>` element or an `aria-label` attribute

**AC5 — Logout confirmation uses accessible Dialog**

**Given** I click the logout button in `Header.tsx`
**When** the confirmation prompt appears
**Then** it uses the shadcn `Dialog` component (Radix-based, already installed)
**And** focus is trapped inside the dialog while open
**And** pressing Escape closes the dialog
**And** the dialog has an accessible title (`aria-labelledby` or Dialog.Title)

**AC6 — Loading skeleton has aria-busy**

**Given** the brand table in `BrandTable.tsx` is loading data
**When** a skeleton/loading state is displayed
**Then** the table or its container has `aria-busy="true"`
**And** when loading completes, `aria-busy` is removed or set to `"false"`

**Out of scope (deferred):**
- Hardcoded color classes → design tokens (cosmetic, low impact)
- Keyboard shortcuts (Ctrl+K search, etc.)
- Automated a11y testing setup (jest-axe / vitest-axe)
- `aria-current` on nav links (single-page app with one active view)

**NFR mapping:** Cross-cutting accessibility concern — no specific FR; supports NFR usability expectations.

**Files to modify:**
- `frontend/src/App.tsx` — skip-to-content link
- `frontend/src/components/Header.tsx` — aria-labels on icon buttons, Dialog for logout
- `frontend/src/components/brands/BrandTable.tsx` — aria-labels on pagination/sort, aria-busy on loading
- `frontend/src/components/brands/SyncStatus.tsx` — aria-live region
- `frontend/src/pages/BrandsPage.tsx` — search input label, aria-labels on icon controls

---

## Epic 3: Brand Evaluation Workflow

BD team can complete a full brand evaluation — upload data files, run calculators, enter manual inputs, generate final score using the 75-row scoring system, and save the evaluation.

> **Authoritative calculator specifications:** `logic/calculator-1-kata-kunci-iklan-shopee.md`, `logic/calculator-2-penjualan.md`, `logic/calculator-3-discount-checkup.md`, `logic/scoring-system-template-sicu.md`

### Story 3.1: Start Evaluation for a Brand

As a **BD team member**,
I want **to start an evaluation session for a selected brand**,
So that **I can begin the evaluation workflow**.

**Acceptance Criteria:**

**Given** I am on the Brands page (showing VP brand list)
**When** I click "Evaluate" on a brand card
**Then** I am navigated to `/evaluation/{brand_id}`
**And** I see the brand name and basic info at the top (populated from VP data + Meeting data)
**And** I see the evaluation form organized by scoring system categories:
  - File Upload section (4 file slots for calculator inputs)
  - Manual Input sections grouped by scoring categories (Operational, Business, Content, Visitors, Promo Tools, Products/Status, Ads, Campaign, Competition, Stock, Discount)
  - Calculator Results section
  - Final Score section
**And** I see multi-section navigation matching the scoring categories

**Given** I have a previous in-progress evaluation for this brand
**When** I start a new evaluation
**Then** I see the previous data pre-filled (manual inputs, uploaded file references per file type)
**And** I can modify or continue from where I left off

**Given** I select a brand that has no Meeting data
**When** the evaluation page loads
**Then** brand info shows VP data only (name, marketplace, category)
**And** Meeting-enriched fields are empty but editable

---

### Story 3.2: Data File Upload and Parsing

As a **BD team member**,
I want **to upload data files (CSV and Excel) for a brand**,
So that **the system can process them through the appropriate calculators**.

**Acceptance Criteria:**

**Given** I am on the evaluation page for a brand
**When** I view the File Upload section
**Then** I see 4 distinct upload slots:
  1. **CPC Ad Report** — accepts `.csv` (for Calculator 1 Sheet 1)
  2. **Keyword Placement Report** — accepts `.csv` (for Calculator 1 Sheet 2)
  3. **Order Export** — accepts `.xlsx` (for Calculators 2 & 3)
  4. **Mass Update / Sales Info** — accepts `.xlsx` (for Calculator 2)
**And** each slot shows its calculator routing label and accepted format
**And** each slot shows per-slot status (empty, uploaded, error)

**Given** I select a file for any upload slot (≤2MB, correct format)
**When** the file uploads to the backend
**Then** I see a progress indicator during upload
**And** the backend validates file format (CSV or Excel as appropriate)
**And** Polars parses the file and validates per-calculator column schema:
  - CPC Ad Report: requires columns for Nama Produk, Nama Iklan, Tipe Iklan, Penempatan, Tipe Biaya, Biaya
  - Keyword Report: requires columns for Kata Kunci Pencarian, Klik, Kunjungan, Pesanan, Pendapatan, Biaya Iklan, ROAS
  - Order Export: requires columns for No. Pesanan, Nama Produk, Harga Awal, Harga Setelah Diskon, Jumlah, etc.
  - Mass Update: requires columns for Kode Variasi, Nama Produk, Nama Variasi, SKU, Stok (starting from row 3 headers)
**And** I see "File uploaded successfully" with filename displayed

**Given** I upload an invalid file (wrong format, >2MB, corrupted, missing required columns)
**When** validation fails
**Then** return error with code `UPLOAD_INVALID_FORMAT`, `UPLOAD_FILE_TOO_LARGE`, or `UPLOAD_MISSING_COLUMNS`
**And** I see a user-friendly error message specifying what's wrong
**And** the previous file for that slot (if any) remains unchanged

**Given** I upload a new file to a slot that already has one
**When** the upload succeeds
**Then** the new file replaces the old one for that file type (upsert per file_type)
**And** calculator results that depend on this file type are cleared (need to re-run)

**Database Migration:** Create `brand_uploads` table:
- `id` SERIAL PRIMARY KEY
- `brand_id` INTEGER REFERENCES brand_vp_data(id)
- `file_type` VARCHAR(50) NOT NULL — one of: `cpc_ad_report`, `keyword_report`, `order_export`, `mass_update`
- `calculator_target` VARCHAR(50) — which calculator(s) this feeds: `ads_keyword`, `top_sku`, `discount`, or `top_sku,discount`
- `filename` VARCHAR(255)
- `file_size` INTEGER
- `parsed_data` JSONB (extracted data from Polars)
- `uploaded_by` INTEGER REFERENCES users(id)
- `uploaded_at` TIMESTAMPTZ DEFAULT NOW()
- UNIQUE(brand_id, file_type) — one file per type per brand

---

### Story 3.3: Manual Data Input Form

As a **BD team member**,
I want **to enter manual data values for a brand evaluation organized by scoring categories**,
So that **I can provide the ~40+ fields required by the scoring system**.

**Acceptance Criteria:**

**Given** I am on the evaluation page
**When** I view the Manual Input sections
**Then** I see form fields organized by scoring system categories:

| Category | Rows | Fields |
|----------|------|--------|
| Operational | 7-11 | Pesanan Tidak Terselesaikan (%), Keterlambatan (%), Masa Pengemasan (days), Chat Dibalas (%), Penilaian (rating) |
| Business | 13-20 | Monthly sales figures for 6 months (IDR), Conversion rate (%) |
| Content | 22-24 | "Perlu ditingkatkan" count, "Kualitas baik" count |
| Visitors | 26-29 | Total visitors, Lama toko (months), Pengikut (followers) |
| Promo Tools | 31-41 | 11 promo tool fields: Voucher Toko, Voucher Produk, Flash Sale, Diskon Toko, Paket Diskon, Shopee Live, Iklan, SPaylater, Free Ongkir, Star+, Gratis Ongkir Xtra — each with IDR revenue values |
| Products/Status | 45-46 | Jumlah Produk (count), Status Toko (dropdown: Mall/Star+/Star/Regular) |
| Ads | 48-49 | Penjualan iklan (IDR), Biaya iklan (IDR) |
| Campaign | 55-56 | Sesi dinominasikan (count), Sesi tersedia (count) |
| Competition | 60-63 | Top 3 competitor products with: product name, price, keywords, market price |
| Fashion/Non-Fashion | — | Category selector affecting scoring thresholds |

**And** each field has appropriate input type (number for IDR/percentages, text for names, dropdown for Status Toko)
**And** IDR fields show Indonesian number formatting
**And** percentage fields show benchmark values as helper text

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
**And** if final scoring was already generated, it is marked as "stale" (need recalculation)

**Given** I select Fashion vs Non-Fashion category
**When** the selection changes
**Then** benchmark helper text updates to show category-specific thresholds (e.g., ROI >8 for Fashion vs >9 for Non-Fashion, conversion >2% vs >3%)

**Database Migration:** Create `evaluation_inputs` table:
- `id` SERIAL PRIMARY KEY
- `brand_id` INTEGER REFERENCES brand_vp_data(id)
- `user_id` INTEGER REFERENCES users(id)
- `category_type` VARCHAR(20) — `fashion` or `non_fashion`
- `manual_data` JSONB (structured by scoring category keys)
- `created_at` TIMESTAMPTZ DEFAULT NOW()
- `updated_at` TIMESTAMPTZ DEFAULT NOW()
- UNIQUE(brand_id, user_id) — one input set per user per brand

---

### Story 3.4: Ads Keyword Calculator

As a **system**,
I want **to execute the Ads Keyword Calculator on uploaded CSV data**,
So that **the BD team gets the ads keyword analysis as part of the evaluation**.

> **Authoritative spec:** `logic/calculator-1-kata-kunci-iklan-shopee.md`

**Acceptance Criteria:**

**Given** a brand has uploaded CPC Ad Report CSV and Keyword Placement Report CSV
**When** the calculator is executed with the manual input `total_products` (AK1)

**Then — Sheet 1 (CPC Ad Report) processing:**
- Parse CSV with column mapping (A=Nama Produk, B=Nama Iklan, C=Tipe Iklan, D=Penempatan, E=Tipe Biaya, F=blank offset, G=Biaya)
- Apply `CleanName` helper: extract text before first ` - ` dash from Nama Produk
- Calculate **AK2** (Ad Overview): count unique products with ads, format as `"X dari Y produk ({pct}%) sudah beriklan"`
- Calculate **AK3** (Ad Type Breakdown): group by Tipe Iklan × Penempatan × Tipe Biaya, calculate spend and product count per combination, format as multi-line text
- Calculate **AK4** (7 Recommendation Flags):
  1. Flag if any ad type has 0 products
  2. Flag if Pencarian Otomatis < 50% of total ad spend
  3. Flag if Pencarian Manual products < Pencarian Otomatis products
  4. Flag if Rekomendasi placement used
  5. Flag for product count without ads (AK1 - unique_ad_products)
  6. Flag if no ROAS bidding found
  7. Flag if no Otomatis bidding found

**Then — Sheet 2 (Keyword Report) processing:**
- Parse CSV with columns: Kata Kunci, Klik, Kunjungan, Pesanan, Pendapatan, Biaya Iklan, ROAS
- Calculate thresholds: AM6 (avg clicks, cap 100), AM7 (avg visits, cap 100), AM8 (avg orders, cap 50), AM9 (avg revenue), AM10 (avg ad spend)
- Run **TOP ads query**: primary filter (clicks>AM6 AND visits>AM7 AND orders>AM8 AND revenue>AM9 AND spend<AM10), fallback with halved thresholds if <3 results
- Run **BOTTOM ads query**: primary filter (clicks<AM6 AND visits<AM7 AND orders<AM8 AND revenue<AM9 AND spend>AM10), fallback with halved thresholds if <3 results
- Calculate **AL3** flag: ROAS median assessment
- Calculate **AL6-AL9** flags: keyword-level recommendation flags

**Then — combine output text:**
- Return combined text: AK2 + AK3 + AK4 + TOP ads listing (AL2) + AL3 + BOTTOM ads listing (AL5) + AL6 + AL7 + AL8 + AL9

**Given** the uploaded CSVs are missing required columns
**When** attempting calculation
**Then** return error with code `CALC_MISSING_DATA` and specify which columns are missing

**Given** the calculator runs successfully
**When** storing results
**Then** save to `calculator_results` table with `output_text` (combined text) and `details` JSONB (structured intermediate values: AK1, AK2, AK3, AK4, thresholds, flags)

**Test fixtures:** MND sample data (AK1=80, expected AK2 output), KYPSO sample data (AK1=54) from spec

**Implementation:** Pure function in `calculators/ads_keyword.py` — no database I/O inside calculator

**Database Migration:** Create `calculator_results` table:
- `id` SERIAL PRIMARY KEY
- `brand_id` INTEGER REFERENCES brand_vp_data(id)
- `calculator_type` VARCHAR(50) — `ads_keyword`, `discount`, `top_sku`
- `details` JSONB (structured intermediate values)
- `output_text` TEXT (formatted text output)
- `calculated_at` TIMESTAMPTZ DEFAULT NOW()
- UNIQUE(brand_id, calculator_type) — upsert on recalculation

---

### Story 3.5: Discount Check Calculator

As a **system**,
I want **to execute the Discount Check Calculator on uploaded Order Export data**,
So that **the BD team gets the discount analysis as part of the evaluation**.

> **Authoritative spec:** `logic/calculator-3-discount-checkup.md`

**Acceptance Criteria:**

**Given** a brand has uploaded Order Export Excel (same file used by Calculator 2)
**When** the calculator is executed

**Then — processing pipeline:**
1. **Urutan calculation**: Count item position within same order (same No. Pesanan = increment, different = reset to 1)
2. **Price cleaning**: Remove `.` thousands separator from Harga Awal and Harga Setelah Diskon, convert to numbers
3. **Voucher/Paket allocation**: Voucher Ditanggung Penjual and Paket Diskon only applied when Urutan = 1 (first line item per order) to avoid double-counting order-level discounts
4. **Total Discount (N)**: `(Harga Awal - Harga Setelah Diskon) + Voucher(Urutan=1) + Paket(Urutan=1)`
5. **Discount % (O)**: `N / Harga Awal`
6. **Total Paid (P)**: `Harga Setelah Diskon - Voucher(Urutan=1) - Paket(Urutan=1)`
7. **Product Summary**: Group by Nama Produk (exact match) — total quantity and average discount % per product
8. **TOP SKU Filter**: Products where `Qty > AVERAGE(all Qty)` AND `AvgDisc < 1.0` (100%), ordered by Qty desc, limit = `ROUND(unique_products × 20%)`

**Then — produce 5 output values:**
1. `% Diskon TOP SKU`: `SUMIF(P>0, N) / SUM(P)` — formatted as percentage (e.g., "2.7%")
2. `Range`: `ROUNDUP(MIN(top_sku_avg_disc), 3) ~ ROUNDUP(MAX(top_sku_avg_disc), 3)` — e.g., "0.0% ~ 6.7%"
3. `Voucher %`: `SUM(voucher) / SUM(harga_setelah_diskon)` — e.g., "Voucher 0.3%"
4. `Paket Diskon %`: `SUM(paket) / SUM(harga_setelah_diskon)` — e.g., "Paket Diskon 0.0%"
5. `Fake Discount Flag`: If `SUM(N) / SUM(P) > 20%` → flag text, otherwise empty

**Given** the uploaded Excel is missing required columns (No. Pesanan, Nama Produk, Harga Awal, Harga Setelah Diskon, Jumlah, Voucher Ditanggung Penjual, Paket Diskon)
**When** attempting calculation
**Then** return error with code `CALC_MISSING_DATA` and specify which columns are missing

**Given** the calculator runs successfully
**When** storing results
**Then** save to `calculator_results` table with `output_text` (5 formatted values) and `details` JSONB (intermediate values: product summary, top SKU list, voucher totals, paket totals)

**Test fixtures from spec:**
- SUKA Nov 2025: "% Diskon TOP SKU: 2.7%, Range: 0.0% ~ 6.7%, Voucher 0.3%, Paket Diskon 0.0%" (no flag)
- KYPSO Oct 2025: "% Diskon TOP SKU: 217.3%, Range: 56.1% ~ 73.1%" (flag triggered)
- MND Nov 2025: "% Diskon TOP SKU: 102.9%, Range: 42.2% ~ 50.4%" (flag triggered)

**Implementation:** Pure function in `calculators/discount.py`

---

### Story 3.6: Top SKU Calculator

As a **system**,
I want **to execute the Top SKU Calculator on uploaded Order Export and Mass Update data**,
So that **the BD team gets the SKU analysis as part of the evaluation**.

> **Authoritative spec:** `logic/calculator-2-penjualan.md`

**Acceptance Criteria:**

**Given** a brand has uploaded Order Export Excel AND Mass Update Excel
**When** the calculator is executed

**Then — processing pipeline:**
1. **Per-line extraction** from Order Export:
   - SKU = Nomor Referensi SKU
   - Product+Variant label = `Nama Produk & " - " & Nama Variasi`
   - Quantity = Jumlah
   - Revenue = `(Harga Setelah Diskon × Jumlah) - (Voucher Ditanggung Penjual / Jumlah Produk di Pesan) - (Cashback Koin / Jumlah Produk di Pesan) + (Diskon dari Shopee / Jumlah Produk di Pesan)`
   - All price strings: remove `.` thousands separator before converting to numbers
2. **Aggregate by product+variant** (exact match on label): total quantity, total revenue (omzet)
3. **Rank top products**: Sort by Total Omzet descending, limit = `MAX(ROUND(unique_products × 20%), 20)`
4. **Enrich with Kode Variasi**: Prepare mass_update name column (`Nama Produk & " - " & Nama Variasi`), XLOOKUP product label → Kode Variasi. "Kode Variasi tidak ditemukan" if no match.
5. **Average selling price**: `MAXIFS(revenue_per_line, product_label, this_product)` — highest single-line revenue per product
6. **Stock lookup**: Use Kode Variasi from step 4 to lookup Stok from mass_update. If "tidak ditemukan" → stock = 0.
7. **Average stock**: `ROUND(AVERAGE(all top SKU stocks))`

**Then — produce 2 outputs:**

**Output 1 — Top Selling SKU with Revenue table:**
| Column | Description |
|--------|-------------|
| Kode Variasi | From mass_update lookup (or "Kode Variasi tidak ditemukan") |
| Product Name | Product + Variant label |
| Total Omzet | Sum of revenue per product (IDR) |
| Rata2 Harga Jual | Max single-line revenue per product (IDR) |

**Output 2 — Top Selling SKU with Stock table:**
| Column | Description |
|--------|-------------|
| Kode Variasi | Same as Output 1 |
| Nama Produk | Product name (without variant) |
| Varian | Variant name only |
| Stok | Stock from mass_update (0 if tidak ditemukan) |

**And** return average stock as a single integer metric

**Given** Order Export is missing required columns (Nama Produk, Nomor Referensi SKU, Nama Variasi, Harga Setelah Diskon, Jumlah, Jumlah Produk di Pesan, Voucher Ditanggung Penjual, Cashback Koin, Diskon dari Shopee)
**When** attempting calculation
**Then** return error with code `CALC_MISSING_DATA` and specify which columns are missing

**Given** Mass Update is missing required columns (Kode Variasi, Nama Produk, Nama Variasi, SKU, Stok)
**When** attempting calculation
**Then** return error with code `CALC_MISSING_DATA` and specify which columns are missing

**Given** the calculator runs successfully
**When** storing results
**Then** save to `calculator_results` table with `details` JSONB (output_1 table, output_2 table, average_stock integer, per-product aggregates)

**Test fixtures from spec:**
- KYPSO Oct 2025: 20 products, top = "KYPSO Sovereign - Cokelat Muda" at 4,355,000 omzet, avg stock 123
- MND Nov 2025: 20 products, top = "Seoul Shoulder Bag - Black" at 19,593,731 omzet, avg stock 125

**Implementation:** Pure function in `calculators/top_sku.py`

---

### Story 3.7: Calculator Orchestration and File Routing

As a **system**,
I want **to run applicable calculators when their required input files become available**,
So that **the BD team sees results as soon as possible without waiting for all files**.

**Acceptance Criteria:**

**Given** a brand file upload completes successfully
**When** the upload is processed
**Then** check which calculators now have ALL their required files:
  - **Calculator 1 (Ads Keyword)**: needs `cpc_ad_report` + `keyword_report` + manual `total_products` (AK1)
  - **Calculator 2 (Top SKU)**: needs `order_export` + `mass_update`
  - **Calculator 3 (Discount Check)**: needs `order_export`
**And** run only the calculators whose requirements are fully satisfied
**And** store results in `calculator_results` table

**Given** an `order_export` file is uploaded
**When** checking calculator readiness
**Then** run Calculator 3 (Discount Check) immediately (only needs order_export)
**And** if `mass_update` is also already uploaded → also run Calculator 2 (Top SKU)
**And** if `mass_update` is NOT yet uploaded → show Calculator 2 as "Pending: needs Mass Update file"

**Given** a `mass_update` file is uploaded and `order_export` already exists
**When** checking calculator readiness
**Then** run Calculator 2 (Top SKU)

**Given** any calculator fails during execution
**When** orchestrating
**Then** continue with other calculators (don't fail all)
**And** record which calculators succeeded/failed
**And** return partial results with error details for failed ones

**Given** a file is re-uploaded (replacing a previous one)
**When** the upload succeeds
**Then** clear calculator results that depend on that file type
**And** re-run applicable calculators with the new data

**Given** user manually triggers "Recalculate"
**When** triggered
**Then** re-run all calculators that have their required files
**And** update results

**Implementation:** Orchestration in `calculators/engine.py` with file-type dependency mapping

---

### Story 3.8: Calculator Results Display

As a **BD team member**,
I want **to view the results of each calculator in their native format**,
So that **I understand the brand's performance across different metrics**.

**Acceptance Criteria:**

**Given** I am on the evaluation page and Calculator 1 (Ads Keyword) has run
**When** viewing its results
**Then** I see multi-line text output preserving formatting:
  - AK2: Ad overview line (e.g., "34 dari 80 produk (42.5%) sudah beriklan")
  - AK3: Ad type breakdown (multi-line, grouped by type/placement/bidding)
  - AK4: 7 recommendation flags (each on its own line)
  - TOP ads listing with keyword details
  - AL3: ROAS median flag
  - BOTTOM ads listing with keyword details
  - AL6-AL9: Keyword recommendation flags

**Given** Calculator 2 (Top SKU) has run
**When** viewing its results
**Then** I see two tables:
  - Revenue ranking table: Kode Variasi, Product Name, Total Omzet (IDR formatted), Rata2 Harga Jual (IDR formatted)
  - Stock ranking table: Kode Variasi, Nama Produk, Varian, Stok
**And** I see the average stock metric in the header (e.g., "Average Stok: 123")
**And** tables are sortable by column

**Given** Calculator 3 (Discount Check) has run
**When** viewing its results
**Then** I see 5 text values:
  - % Diskon TOP SKU (e.g., "2.7%")
  - Range (e.g., "0.0% ~ 6.7%")
  - Voucher percentage (e.g., "Voucher 0.3%")
  - Paket Diskon percentage (e.g., "Paket Diskon 0.0%")
  - Fake discount flag (warning indicator if present)

**Given** a calculator hasn't run yet (missing required files)
**When** viewing results
**Then** I see a pending state showing which files are still needed (e.g., "Waiting for: Mass Update file")

**Given** a calculator failed
**When** viewing results
**Then** I see an error state with the error message
**And** a "Retry" button

---

### Story 3.9: Final Scoring with Scoring System Template

As a **system**,
I want **to generate a final score using the 75-row scoring system template**,
So that **the BD team gets the overall brand qualification assessment**.

> **Authoritative spec:** `logic/scoring-system-template-sicu.md`

**Acceptance Criteria:**

**Given** calculator results and manual inputs are available
**When** the scoring system is executed with Fashion or Non-Fashion template

**Then — compute per-category scores:**

| Category | Rows | Max Points | Scoring Logic |
|----------|------|------------|---------------|
| Operational | H7-H9 | 10 | Based on Pesanan Tidak Terselesaikan, Keterlambatan, Pengemasan/Chat/Penilaian thresholds |
| Business | H13, H19 | 20 | Monthly sales trend (10pts), Conversion rate vs threshold (10pts) |
| Visitors | H28-H29 | 5 | Total visitors and store age scoring |
| Promo Tools | H42-H43 | -15 penalty | Count of unused promo tools → opportunity flags |
| Products/Status | H45-H46 | 15 | Mall=10pts, Star+=5pts. Product count thresholds |
| Ads | H50-H51 | -5 to +5 | ROI scoring (penalty if <1, bonus if >threshold). Fashion: >8, Non-Fashion: >9 |
| Campaign | H57 | -10 penalty | Ratio of nominated/available campaign sessions |
| Stock | H70 | -5 to +10 | From Calculator 2 average stock metric. Thresholds for scoring |
| Discount | H73 | 0 or 5 | From Calculator 3 fake discount flag (flag → 0pts, no flag → 5pts) |

**And** apply Fashion-specific thresholds where applicable:
  - ROI threshold: >8 (Fashion) vs >9 (Non-Fashion)
  - Marketing G72: +5% for Fashion
  - Conversion threshold: >2% (Fashion) vs >3% (Non-Fashion)

**Then — compute derived formulas:**
- G68: Marketing cost estimation from discount data (Calculator 3 discount % × total revenue)
- G72: Recommended marketing percentage
- G73: Marketing budget recommendation (monthly sales × G72)

**Then — compute final score:**
- Sum all category scores (range: negative to 100)
- Determine verdict (F75): one of "✔️", "❌", "❌ Non Mall", "❌ No Brand", "❌ Opex", "⭕️", or empty

**Then — generate output messages:**
- G-column text values per metric (recommendation text for each scoring row)
- G66: Conclusion summary
- G75: Closing message
- G1: Email output — mailto link with structured body assembled from all G-column values
- E1: WhatsApp output — api.whatsapp.com link

**Given** the final score is generated
**When** viewing the result
**Then** I see:
  - Final score with verdict icon (e.g., "78 ✔️" or "-5 ❌")
  - Per-category score breakdown table matching the 11 scoring categories
  - Template used (Fashion/Non-Fashion)
  - Generated email body (copyable)
  - WhatsApp link (clickable)

**Given** required calculator results are missing
**When** attempting to generate final score
**Then** show which calculators need to run first
**And** block scoring until dependencies are met

**Implementation:** Pure function in `calculators/scoring.py` with template logic. Consider splitting: 3.9a (scoring calculation + per-category logic) + 3.9b (output generation: email, WA, verdict messages)

---

### Story 3.10: Save Evaluation

As a **BD team member**,
I want **to save a completed evaluation permanently**,
So that **it becomes part of the evaluation history for this brand**.

**Acceptance Criteria:**

**Given** I have a final score generated
**When** I click "Save Evaluation"
**Then** create a new record in `evaluations` table with:
  - All manual inputs organized by scoring category (JSONB snapshot)
  - All calculator outputs: text output for Calc 1, tables + avg stock for Calc 2, 5 values + flag for Calc 3
  - Final score (numeric, can be negative)
  - Per-category score breakdown (11 categories)
  - Verdict (F75 value — e.g., "✔️", "❌", "⭕️")
  - Scoring template used (Fashion/Non-Fashion)
  - Rule version (for future rule configuration tracking)
  - Generated email output text
  - Evaluator (user_id) and timestamp
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
- `template` VARCHAR(20) — `fashion` or `non_fashion`
- `final_score` DECIMAL(5,2) — can be negative
- `verdict` VARCHAR(20) — F75 value
- `score_breakdown` JSONB — per-category scores matching scoring system rows
- `calculator_results` JSONB — snapshot of all calculator outputs (text + tables + flags)
- `manual_inputs` JSONB — snapshot of all manual input values by category
- `rule_version` INTEGER DEFAULT 1
- `email_output` TEXT — generated email body text
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

---

## Epic 6: Production Deployment & Launch

> **Goal:** Deploy the application to production and validate with real users.
> **Depends on:** Epic 5 completion
> **Estimated stories:** 3–4

### Story 6.1: Infrastructure Provisioning

As a **DevOps engineer**,
I want **to provision production infrastructure using Terraform**,
So that **the application has a secure, scalable production environment**.

**Scope:**
- Terraform apply for Cloud Run, Cloud SQL (or Neon prod), GCS buckets, IAM roles
- Secrets management (Firebase credentials, database URL, GCS keys)
- Network and security configuration
- Environment-specific configuration (prod vs dev)

---

### Story 6.2: CI/CD Pipeline Activation

As a **DevOps engineer**,
I want **to activate the CI/CD pipeline for automated deployments**,
So that **code merged to main is automatically tested and deployed**.

**Scope:**
- GitHub Actions workflow for build, test, deploy
- Workload Identity Federation for keyless GCP authentication
- Staging environment deployment (optional, if budget allows)
- Rollback strategy and deployment gates

---

### Story 6.3: Production Smoke Testing

As a **QA engineer**,
I want **to run end-to-end smoke tests against the production environment**,
So that **we verify the full workflow works in production before user onboarding**.

**Scope:**
- Full evaluation workflow: login → brand selection → file upload → calculators → scoring → save
- Verify GCS signed URL uploads work in production
- Verify database connectivity and data persistence
- Verify SSE sync status in production environment

---

### Story 6.4: BD Team Onboarding & Real-Data Validation

As a **BD team member**,
I want **to evaluate 1-2 real brands using the production app**,
So that **we validate calculator accuracy with actual client data before wider rollout**.

**Scope:**
- BD team account provisioning and access setup
- Guided walkthrough of evaluation workflow
- Real brand evaluation with actual Shopee export data
- Calculator result validation against manual calculations
- Bug/fix fast-track process for any discrepancies found
