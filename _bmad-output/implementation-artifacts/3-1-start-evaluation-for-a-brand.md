# Story 3.1: Start Evaluation for a Brand

Status: review

## Story

As a **BD team member**,
I want **to start an evaluation session for a selected brand**,
so that **I can begin the evaluation workflow with brand info displayed and section navigation ready**.

## Acceptance Criteria

1. **Navigate to evaluation page from brand list**
   **Given** I am on the Brands page (showing VP brand list)
   **When** I click "Evaluate" on a brand row
   **Then** I am navigated to `/evaluation/{brand_id}`

2. **Brand info displayed at top**
   **Given** I am on the evaluation page for a brand
   **When** the page loads
   **Then** I see the brand name prominently at the top
   **And** I see brand info populated from VP data (key fields from `raw_data`)
   **And** if Meeting data exists for this brand, supplementary info is also displayed
   **And** if no Meeting data exists, VP data only is shown (no errors)

3. **Evaluation form structure with section navigation**
   **Given** I am on the evaluation page
   **When** viewing the page layout
   **Then** I see a left sidebar with section navigation matching the scoring system workflow:
     - Step 1: Brand Info & Operational
     - Step 2: Business, Content & Visitors
     - Step 3: Promo Tools & Products/Status
     - Step 4: File Upload
     - Step 5: Ads, Campaign, Competition, Stock, Discount & Review
   **And** I see each section as a scrollable area in the main content
   **And** clicking a section nav item scrolls to that section
   **And** the active section highlights in the nav as I scroll

4. **Section placeholders for future stories**
   **Given** I am on the evaluation page
   **When** viewing each section
   **Then** I see the following section scaffolds:
     - **File Upload section**: 4 labeled file slots (CPC Ad Report, Keyword Report, Order Export, Mass Update) — each showing "No file uploaded" placeholder
     - **Manual Input sections**: Section headers with category names and field count hints (e.g., "Operational — 5 fields") — empty form containers
     - **Calculator Results section**: 3 calculator cards (Ads Keyword, Top SKU, Discount Check) showing "Pending: upload required files" state
     - **Final Score section**: "Not yet calculated" placeholder with category score breakdown skeleton

5. **Category type selector (Fashion / Non-Fashion)**
   **Given** I am on the evaluation page
   **When** I view the Brand Info section
   **Then** I see a Fashion / Non-Fashion selector (radio buttons or toggle)
   **And** selecting a category saves immediately (auto-save)
   **And** the selection persists when I return later

6. **Resume from previous in-progress evaluation**
   **Given** I have a previous in-progress evaluation for this brand (saved `evaluation_inputs` record)
   **When** I navigate to `/evaluation/{brand_id}`
   **Then** the category type selector shows my previous selection
   **And** any previously saved manual data is available (used by Story 3.3 when fields are implemented)

7. **Brand without Meeting data**
   **Given** I select a brand that has no Meeting data
   **When** the evaluation page loads
   **Then** brand info shows VP data only (name, key fields)
   **And** Meeting-enriched fields area shows "No meeting data available"
   **And** the page is fully functional — no errors

8. **API: Get single brand detail**
   **Given** I request `GET /api/v1/brands/{brand_id}`
   **When** authenticated
   **Then** return brand VP data with LEFT JOIN Meeting data:
   ```json
   {
     "id": 1,
     "brand_name": "Nike",
     "raw_data": { ... },
     "updated_at": "2026-02-04T10:30:00Z",
     "meeting_raw_data": { ... } | null
   }
   ```
   **And** if brand_id not found, return 404 with `{"code": "BRAND_NOT_FOUND", "detail": "Brand not found"}`

9. **API: Get evaluation state**
   **Given** I request `GET /api/v1/evaluations/brands/{brand_id}`
   **When** authenticated
   **Then** return the current user's evaluation inputs for this brand (if any):
   ```json
   {
     "brand_id": 1,
     "category_type": "fashion" | "non_fashion" | null,
     "manual_data": { ... } | null,
     "updated_at": "2026-02-04T10:30:00Z" | null
   }
   ```
   **And** if no evaluation inputs exist for this user+brand, return the same shape with `null` values

10. **API: Save evaluation inputs**
    **Given** I send `PUT /api/v1/evaluations/brands/{brand_id}`
    **When** authenticated with body:
    ```json
    {
      "category_type": "fashion",
      "manual_data": { ... }
    }
    ```
    **Then** upsert `evaluation_inputs` record for this user+brand
    **And** return the saved record with `updated_at` timestamp
    **And** if brand_id not found, return 404

## Tasks / Subtasks

- [x] Task 1: Create database migration for `evaluation_inputs` table (AC: #6, #9, #10)
  - [x] 1.1 Create migration `006_create_evaluation_inputs_table.py` in `backend/app/db/migrations/versions/`
  - [x] 1.2 Table schema:
    - `id` SERIAL PRIMARY KEY
    - `brand_id` INTEGER NOT NULL REFERENCES brand_vp_data(id)
    - `user_id` INTEGER NOT NULL REFERENCES users(id)
    - `category_type` VARCHAR(20) — `fashion`, `non_fashion`, or NULL
    - `manual_data` JSONB DEFAULT '{}'
    - `created_at` TIMESTAMPTZ DEFAULT NOW()
    - `updated_at` TIMESTAMPTZ DEFAULT NOW()
    - UNIQUE(brand_id, user_id) — one input set per user per brand
  - [x] 1.3 Add indexes: `idx_evaluation_inputs_brand_id`, `idx_evaluation_inputs_user_id`

- [x] Task 2: Add backend query functions (AC: #8, #9, #10)
  - [x] 2.1 Add `get_brand_by_id(conn, brand_id)` to `db/queries/brands.py` — returns VP data LEFT JOIN Meeting data for a single brand by ID
  - [x] 2.2 Create `db/queries/evaluations.py` with:
    - `get_evaluation_inputs(conn, brand_id, user_id)` — returns evaluation_inputs row or None
    - `upsert_evaluation_inputs(conn, brand_id, user_id, category_type, manual_data)` — INSERT ON CONFLICT DO UPDATE
  - [x] 2.3 Ensure `ESCAPE '\'` on any ILIKE queries (if applicable) per lessons learned

- [x] Task 3: Add backend brand detail endpoint (AC: #8)
  - [x] 3.1 Add `GET /api/v1/brands/{brand_id}` to `modules/brands/router.py`
  - [x] 3.2 Add `BrandDetailResponse` schema to `modules/brands/schemas.py` (same shape as BrandListItem)
  - [x] 3.3 Add `get_brand_detail(brand_id)` to `modules/brands/service.py`
  - [x] 3.4 Return 404 with `BRAND_NOT_FOUND` code if brand doesn't exist

- [x] Task 4: Create evaluations module backend (AC: #9, #10)
  - [x] 4.1 Create `modules/evaluations/__init__.py`
  - [x] 4.2 Create `modules/evaluations/schemas.py`:
    - `EvaluationStateResponse`: brand_id, category_type (str|None), manual_data (dict|None), updated_at (datetime|None)
    - `EvaluationInputsUpdate`: category_type (str|None), manual_data (dict|None)
  - [x] 4.3 Create `modules/evaluations/service.py`:
    - `get_evaluation_state(brand_id, user_id)` — fetches evaluation_inputs, returns response
    - `save_evaluation_inputs(brand_id, user_id, data)` — upserts evaluation_inputs, validates brand exists
  - [x] 4.4 Create `modules/evaluations/router.py`:
    - `GET /api/v1/evaluations/brands/{brand_id}` — calls `get_evaluation_state`
    - `PUT /api/v1/evaluations/brands/{brand_id}` — calls `save_evaluation_inputs`
  - [x] 4.5 Register evaluations router in `main.py`

- [x] Task 5: Add frontend route and page scaffold (AC: #1, #3)
  - [x] 5.1 Create `pages/EvaluationPage.tsx` — main evaluation page with Header, section nav, and content area
  - [x] 5.2 Add route `/evaluation/:brandId` to `App.tsx` wrapped in `ProtectedRoute`
  - [x] 5.3 Page layout: Header at top, left sidebar (section nav ~200px), main content area, right side score panel placeholder

- [x] Task 6: Add "Evaluate" button to brand table (AC: #1)
  - [x] 6.1 Add "Evaluate" button column to `BrandTable.tsx` — uses `useNavigate` to go to `/evaluation/{brand.id}`
  - [x] 6.2 Button style: Primary variant, compact size
  - [x] 6.3 Add `TableHead` for the "Action" column

- [x] Task 7: Add frontend API types and hooks (AC: #2, #6, #8, #9, #10)
  - [x] 7.1 Add `/api/v1/brands/{brand_id}` path type to `apiClient.ts`
  - [x] 7.2 Add `/api/v1/evaluations/brands/{brand_id}` GET and PUT path types to `apiClient.ts`
  - [x] 7.3 Create `hooks/useBrandDetail.ts` — `useBrandDetail(brandId)` using TanStack Query
  - [x] 7.4 Create `hooks/useEvaluation.ts`:
    - `useEvaluationState(brandId)` — fetches GET evaluation state
    - `useSaveEvaluationInputs(brandId)` — mutation for PUT evaluation inputs

- [x] Task 8: Build brand info header component (AC: #2, #7)
  - [x] 8.1 Create `components/evaluation/EvaluationHeader.tsx`:
    - Displays brand name prominently (large heading)
    - Shows key VP data fields from `raw_data` (brand name, marketplace fields, etc.)
    - Shows Meeting data enrichment if available, or "No meeting data available" label
    - Back button to navigate to `/brands`
  - [x] 8.2 Handle loading state (skeleton) and error state

- [x] Task 9: Build section navigation sidebar (AC: #3)
  - [x] 9.1 Create `components/evaluation/SectionNav.tsx`:
    - 5 step sections matching the UX workflow:
      1. Brand Info & Operational
      2. Business, Content & Visitors
      3. Promo Tools & Products/Status
      4. File Upload
      5. Ads, Campaign, Competition & Review
    - Each item is a button that scrolls to the corresponding section
    - Active section is highlighted based on scroll position (Intersection Observer)
  - [x] 9.2 Sticky positioning so nav stays visible while scrolling

- [x] Task 10: Build section placeholder content (AC: #4, #5)
  - [x] 10.1 Create `components/evaluation/EvaluationSections.tsx` — renders all 5 sections with `id` attributes for scroll targeting
  - [x] 10.2 Section 1 (Brand Info & Operational):
    - Brand info read-only display (from EvaluationHeader)
    - Fashion/Non-Fashion radio selector (auto-saves via `useSaveEvaluationInputs`)
    - "Operational — 5 fields" placeholder
  - [x] 10.3 Section 2 (Business, Content & Visitors):
    - "Business — 8 fields" placeholder
    - "Content — 2 fields" placeholder
    - "Visitors — 4 fields" placeholder
  - [x] 10.4 Section 3 (Promo Tools & Products/Status):
    - "Promo Tools — 11 fields" placeholder
    - "Products/Status — 2 fields" placeholder
  - [x] 10.5 Section 4 (File Upload):
    - 4 upload slot cards: CPC Ad Report (.csv), Keyword Placement Report (.csv), Order Export (.xlsx), Mass Update (.xlsx)
    - Each shows: file type label, accepted format, calculator routing info, "No file uploaded" status
  - [x] 10.6 Section 5 (Ads, Campaign, Competition & Review):
    - "Ads — 5 fields" placeholder
    - "Campaign — 3 fields" placeholder
    - "Competition — 3 products" placeholder
    - Calculator Results: 3 cards (Ads Keyword, Top SKU, Discount Check) with "Pending: upload required files" state
    - Final Score: "Not yet calculated" with category breakdown skeleton
    - "Save Evaluation" button (disabled — enabled in Story 3.10)

- [x] Task 11: Write backend tests (AC: #8, #9, #10)
  - [x] 11.1 Test `GET /api/v1/brands/{brand_id}` — returns brand with meeting data, returns 404 for unknown ID
  - [x] 11.2 Test `GET /api/v1/evaluations/brands/{brand_id}` — returns null state for new evaluation, returns saved state for existing
  - [x] 11.3 Test `PUT /api/v1/evaluations/brands/{brand_id}` — creates new inputs, updates existing inputs, validates brand exists (404)
  - [x] 11.4 Test evaluation_inputs unique constraint (brand_id, user_id)

- [x] Task 12: Write frontend tests (AC: #1, #2, #3, #4, #5, #6)
  - [x] 12.1 Test BrandTable renders "Evaluate" button for each brand row
  - [x] 12.2 Test EvaluationPage renders brand info header with brand name
  - [x] 12.3 Test EvaluationPage renders section navigation with 5 steps
  - [x] 12.4 Test section placeholders render file upload slots and category placeholders
  - [x] 12.5 Test Fashion/Non-Fashion selector renders and calls save mutation on change
  - [x] 12.6 Test back button navigates to `/brands`

## Dev Notes

### This Is a Full-Stack Story

Both backend and frontend changes. New database migration, new module, new API endpoints, new page, new components.

### Architecture Compliance

**Backend Pattern (MUST follow):**
- Module structure: `modules/evaluations/{__init__, router, schemas, service}.py`
- Queries in: `db/queries/evaluations.py`
- Migration in: `db/migrations/versions/006_create_evaluation_inputs_table.py`
- Router prefix: `/api/v1/evaluations`
- Use `Depends(get_current_user)` on all endpoints
- Use asyncpg parameterized SQL (`$1, $2`) — never string interpolation
- Use `raise AppException(...)` for structured errors — never bare HTTPException
- Response schemas must match ACs field-by-field

**Frontend Pattern (MUST follow):**
- Pages in `src/pages/`
- Components in `src/components/evaluation/` (new feature directory)
- Hooks in `src/hooks/`
- API types in `src/services/apiClient.ts`
- Use TanStack Query for data fetching — never raw `fetch()`
- Use `openapi-fetch` client from `apiClient.ts`
- Use shadcn/ui components for UI elements
- Use Tailwind CSS for styling

### Current Component State — What Exists Today

**App.tsx:**
- Routes: `/login`, `/dashboard`, `/brands`, `/` → redirect to dashboard
- Protected routes use `<ProtectedRoute>` wrapper
- Skip-to-content link exists at top

**BrandTable.tsx (`components/brands/BrandTable.tsx`):**
- Displays brand list as a table with columns: Brand Name, Key Info, Meeting Data
- Uses shadcn `Table` components
- No "Evaluate" button or action column currently
- Brands are passed as `BrandListItem[]` prop from BrandsPage

**BrandsPage.tsx (`pages/BrandsPage.tsx`):**
- Full page with Header, SyncStatus, search, BrandTable, and pagination
- Uses `useBrands(page, limit, debouncedSearch)` hook
- Brands come from `GET /api/v1/brands`

**Backend brands module:**
- `GET /api/v1/brands` — paginated list (with LEFT JOIN meeting data)
- `get_brands_with_meeting()` — query with optional ILIKE search
- No `GET /api/v1/brands/{brand_id}` endpoint yet

**Backend evaluations module:**
- Does not exist — created in this story

**apiClient.ts:**
- Has path types for: `/api/v1/me`, `/api/v1/brands`, `/api/v1/sync/status`, `/api/v1/events`, `/api/v1/sync`
- Uses middleware to inject Firebase auth token
- Pattern: define path types → create client → use in hooks

### UX Layout Reference

**Evaluation page layout (from UX design spec):**
```
┌──────────────────────────────────────────────────────────────┐
│  [Header: nav + user info]                                    │
├──────────┬────────┬─────────────────────────┬───────────────┤
│ Sidebar  │ Step   │                         │  Score Panel  │
│ (nav)    │ Nav    │  [Section content]      │  (placeholder)│
│          │(200px) │                         │  Final: --    │
│          │        │  Back to Brands         │  Ops: --      │
│          │        │                         │               │
└──────────┴────────┴─────────────────────────┴───────────────┘
```

- Left sidebar: 5-step section navigation (sticky)
- Main content: scrollable sections with Brand Info at top, forms in middle, results at bottom
- Right panel: score summary (placeholder — populated in Story 3.9)

**Step breakdown (from UX spec):**

| Step | Content | Shopee Link |
|------|---------|-------------|
| 1. Brand Info + Operational | Basic brand details (from VP/Meeting sync), operational metrics | Yes |
| 2. Business + Content + Visitors | Monthly sales, conversion, content quality, visitors | Yes |
| 3. Promo Tools + Products/Status | 11 promo tool revenues, product count, store status | Yes |
| 4. File Upload | 4 file slots per calculator | — |
| 5. Ads + Campaign + Competition + Review | Ad metrics, campaign, competition, calculator results, final score | Yes |

### File Upload Slot Details (Placeholders for Story 3.2)

| Slot | Label | Format | Calculator Target |
|------|-------|--------|-------------------|
| 1 | CPC Ad Report | `.csv` | Calculator 1 (Ads Keyword — Sheet 1) |
| 2 | Keyword Placement Report | `.csv` | Calculator 1 (Ads Keyword — Sheet 2) |
| 3 | Order Export | `.xlsx` | Calculator 2 (Top SKU) & Calculator 3 (Discount Check) |
| 4 | Mass Update / Sales Info | `.xlsx` | Calculator 2 (Top SKU) |

### Scoring Categories for Section Nav

| # | Category | Scoring Rows | Max Points | Step |
|---|----------|-------------|------------|------|
| 1 | Operational | H7-H9 | 10 | Step 1 |
| 2 | Business | H13, H19 | 20 | Step 2 |
| 3 | Content | H24 | 0 (info) | Step 2 |
| 4 | Visitors | H28-H29 | 5 | Step 2 |
| 5 | Promo Tools | H42-H43 | -15 penalty | Step 3 |
| 6 | Products/Status | H45-H46 | 15 | Step 3 |
| 7 | Ads | H50-H51 | -5 to +5 | Step 5 |
| 8 | Campaign | H57 | -10 penalty | Step 5 |
| 9 | Competition | (info) | 0 (info) | Step 5 |
| 10 | Stock | H70 | -5 to 10 | Step 5 |
| 11 | Discount | H73 | 0 or 5 | Step 5 |

### Key Implementation Guidance

**Brand detail query pattern:**
```sql
SELECT
    v.id, v.brand_name, v.raw_data, v.updated_at,
    m.raw_data AS meeting_raw_data
FROM brand_vp_data v
LEFT JOIN brand_meeting_data m ON v.brand_name = m.brand_name
WHERE v.id = $1
```

**Evaluation inputs upsert pattern:**
```sql
INSERT INTO evaluation_inputs (brand_id, user_id, category_type, manual_data, updated_at)
VALUES ($1, $2, $3, $4, NOW())
ON CONFLICT (brand_id, user_id) DO UPDATE SET
    category_type = COALESCE(EXCLUDED.category_type, evaluation_inputs.category_type),
    manual_data = COALESCE(EXCLUDED.manual_data, evaluation_inputs.manual_data),
    updated_at = NOW()
RETURNING id, brand_id, user_id, category_type, manual_data, created_at, updated_at
```

**Scroll-to-section pattern:**
```tsx
const scrollToSection = (sectionId: string) => {
  document.getElementById(sectionId)?.scrollIntoView({ behavior: 'smooth' });
};
```

**Intersection Observer for active section:**
```tsx
// Track which section is visible to highlight in nav
const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) setActiveSection(entry.target.id);
    });
  },
  { rootMargin: '-20% 0px -80% 0px' }
);
```

**Fashion/Non-Fashion auto-save pattern:**
```tsx
const saveMutation = useSaveEvaluationInputs(brandId);

const handleCategoryChange = (value: string) => {
  setCategoryType(value);
  saveMutation.mutate({ category_type: value, manual_data: currentManualData });
};
```

### Anti-Patterns to Avoid

1. **DO NOT** implement actual form fields for manual input — those are Story 3.3
2. **DO NOT** implement actual file upload functionality — that is Story 3.2
3. **DO NOT** implement calculator execution — that is Stories 3.4-3.7
4. **DO NOT** implement final scoring — that is Story 3.9
5. **DO NOT** implement save evaluation — that is Story 3.10
6. **DO NOT** use raw `fetch()` in frontend — use `apiClient.ts` with openapi-fetch
7. **DO NOT** use string interpolation in SQL queries — use `$1, $2` parameterized queries
8. **DO NOT** add `aria-label` to elements that already have visible text
9. **DO NOT** create a wizard-style multi-page form — use single page with scrollable sections (per UX spec anti-patterns)
10. **DO NOT** forget `ESCAPE '\'` on ILIKE queries per lessons learned

### Previous Story Intelligence

**From Story 2.3 (Brand List UI — first frontend story):**
- Established frontend component patterns: components in `components/{feature}/`, hooks in `hooks/`, pages in `pages/`
- shadcn/ui components installed: Button, Input, Card, Badge, Table, Toast, Dialog, Progress
- BrandTable receives brands as props, BrandsPage orchestrates fetch + pagination
- 69 frontend tests passing after Story 2.6

**From Story 2.6 (Accessibility Retrofit):**
- All icon-only buttons need `aria-label`, decorative icons need `aria-hidden="true"`
- Use `aria-busy` on loading containers
- Tab navigation and keyboard accessibility are expected

**From Epic 2 Retrospective:**
- Story File List must include ALL files changed on the feature branch
- Response schemas must match ACs field-by-field — verify before marking done
- Frontend hooks must use `apiClient.ts`, never raw `fetch()`
- Error handling in TanStack Query queryFn: throw errors, don't swallow them

### Code Review Lessons — Pre-Apply

- ILIKE queries MUST include `ESCAPE '\'` when using `_escape_like()` helper
- Search parameters need `max_length` validation on Query params
- Exception chaining: always `raise ... from e` — never lose original traceback
- Table name validation: use `_VALID_TABLES` frozenset + `_validate_table()` helper for dynamic table names
- Response schemas must match ACs field-by-field
- Story File List must include ALL files changed on the feature branch
- Type definitions must stay in sync between `apiClient.ts` paths and hooks

### Testing Requirements

**Backend Tests (pytest):**

```
backend/tests/unit/test_evaluation_queries.py    — query function tests
backend/tests/integration/api/test_evaluations.py — API endpoint tests
backend/tests/integration/api/test_brands_detail.py — brand detail endpoint test
```

- Test `GET /api/v1/brands/{brand_id}` — returns brand with meeting data, 404 for missing
- Test `GET /api/v1/evaluations/brands/{brand_id}` — returns null state for new, saved state for existing
- Test `PUT /api/v1/evaluations/brands/{brand_id}` — creates, updates, validates brand_id
- Run: `cd backend && uv run python -m pytest -v`

**Frontend Tests (Vitest + @testing-library/react):**

```
frontend/src/pages/EvaluationPage.test.tsx       — page render tests
frontend/src/components/evaluation/EvaluationHeader.test.tsx — brand info display
frontend/src/components/evaluation/SectionNav.test.tsx — navigation rendering
frontend/src/components/brands/BrandTable.test.tsx — evaluate button tests (extend existing)
```

- Test BrandTable "Evaluate" button renders and navigates
- Test EvaluationPage renders all 5 section nav items
- Test EvaluationHeader shows brand name and VP data
- Test Fashion/Non-Fashion selector renders
- Test file upload slot placeholders render with labels
- Run: `cd frontend && npx vitest run --reporter=verbose`

### Library & Framework Requirements

| Library | Version | Usage in This Story | Status |
|---------|---------|---------------------|--------|
| react-router-dom | existing | `useParams`, `useNavigate` for evaluation route | Installed |
| @tanstack/react-query | existing | `useQuery`, `useMutation` for evaluation data | Installed |
| openapi-fetch | existing | API client path types for new endpoints | Installed |
| shadcn/ui (Card, Button, Badge) | existing | Section cards, evaluate button, status badges | Installed |
| lucide-react | existing | Icons (ArrowLeft, FileText, Upload, etc.) | Installed |
| asyncpg | existing | Database queries | Installed |
| pydantic | existing | Request/response schemas | Installed |

**New shadcn/ui components that may be needed:**
- Check if `RadioGroup` is installed — needed for Fashion/Non-Fashion selector. If not, install via `npx shadcn@latest add radio-group`

**No new backend dependencies required.**

### Project Structure Notes

**New files to create:**

```
backend/app/db/migrations/versions/006_create_evaluation_inputs_table.py
backend/app/db/queries/evaluations.py
backend/app/modules/evaluations/__init__.py
backend/app/modules/evaluations/router.py
backend/app/modules/evaluations/schemas.py
backend/app/modules/evaluations/service.py
backend/tests/unit/test_evaluation_queries.py
backend/tests/integration/api/test_evaluations.py
backend/tests/integration/api/test_brands_detail.py
frontend/src/pages/EvaluationPage.tsx
frontend/src/pages/EvaluationPage.test.tsx
frontend/src/components/evaluation/EvaluationHeader.tsx
frontend/src/components/evaluation/EvaluationHeader.test.tsx
frontend/src/components/evaluation/SectionNav.tsx
frontend/src/components/evaluation/SectionNav.test.tsx
frontend/src/components/evaluation/EvaluationSections.tsx
frontend/src/hooks/useBrandDetail.ts
frontend/src/hooks/useEvaluation.ts
```

**Existing files to modify:**

```
backend/app/main.py                              ← MODIFY: register evaluations router
backend/app/modules/brands/router.py             ← MODIFY: add GET /brands/{brand_id}
backend/app/modules/brands/schemas.py            ← MODIFY: add BrandDetailResponse (if different from list item)
backend/app/modules/brands/service.py            ← MODIFY: add get_brand_detail()
backend/app/db/queries/brands.py                 ← MODIFY: add get_brand_by_id()
frontend/src/App.tsx                             ← MODIFY: add evaluation route
frontend/src/services/apiClient.ts               ← MODIFY: add new endpoint path types
frontend/src/components/brands/BrandTable.tsx     ← MODIFY: add Evaluate button column
frontend/src/components/brands/BrandTable.test.tsx ← MODIFY: test Evaluate button
```

### References

- [Source: _bmad-output/planning-artifacts/epics.md — Story 3.1 ACs]
- [Source: _bmad-output/planning-artifacts/architecture.md — Backend module structure, DB schema, API conventions]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md — Evaluation page layout, step breakdown, anti-patterns]
- [Source: _bmad-output/planning-artifacts/sprint-change-proposal-2026-02-09.md — Story 3.1 updates from calculator spec alignment]
- [Source: _bmad-output/lessons-learned.md — Code review patterns, testing conventions]
- [Source: logic/scoring-system-template-sicu.md — Scoring categories, row mappings, category structure]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6 (claude-opus-4-6)

### Debug Log References

- IntersectionObserver not available in jsdom — fixed by adding mock in test/setup.ts
- "Meeting Data" text and "Step N." text matched multiple elements in full-page tests — fixed by using `getAllByText`, `getByRole` with scoping, and `querySelectorAll` within nav landmark

### Completion Notes List

- All 12 tasks completed across backend + frontend
- Backend: 93 tests passing (10 new tests added)
- Frontend: 85 tests passing (18 new tests added, 1 pre-existing App.test.tsx failure due to Firebase API key — not related to this story)
- Fashion/Non-Fashion selector auto-saves via `useSaveEvaluationInputs` mutation
- File upload slots are placeholder cards (actual upload in Story 3.2)
- Calculator result cards show "Pending: upload required files" state
- Final Score shows "Not yet calculated" skeleton
- "Save Evaluation" button rendered but disabled (enabled in Story 3.10)
- Score Summary panel placeholder visible on lg screens
- shadcn RadioGroup + Label installed for category selector

### Change Log

1. `b7dea38` — Backend foundation: migration 006, queries, brand detail endpoint, evaluations module
2. `6182d19` — Frontend: evaluation page, components, hooks, route, Evaluate button
3. `8d5e9f6` — Backend + frontend tests

### File List

**New files:**
- `backend/app/db/migrations/versions/006_create_evaluation_inputs_table.py`
- `backend/app/db/queries/evaluations.py`
- `backend/app/modules/evaluations/__init__.py`
- `backend/app/modules/evaluations/router.py`
- `backend/app/modules/evaluations/schemas.py`
- `backend/app/modules/evaluations/service.py`
- `backend/tests/unit/test_evaluation_queries.py`
- `backend/tests/integration/api/test_brands_detail.py`
- `backend/tests/integration/api/test_evaluations.py`
- `frontend/src/pages/EvaluationPage.tsx`
- `frontend/src/pages/EvaluationPage.test.tsx`
- `frontend/src/components/evaluation/EvaluationHeader.tsx`
- `frontend/src/components/evaluation/EvaluationHeader.test.tsx`
- `frontend/src/components/evaluation/SectionNav.tsx`
- `frontend/src/components/evaluation/SectionNav.test.tsx`
- `frontend/src/components/evaluation/EvaluationSections.tsx`
- `frontend/src/components/ui/radio-group.tsx`
- `frontend/src/components/ui/label.tsx`
- `frontend/src/hooks/useBrandDetail.ts`
- `frontend/src/hooks/useEvaluation.ts`

**Modified files:**
- `backend/app/main.py` — registered evaluations router
- `backend/app/modules/brands/router.py` — added GET /{brand_id}
- `backend/app/modules/brands/schemas.py` — added BrandDetailResponse
- `backend/app/modules/brands/service.py` — added get_brand_detail()
- `backend/app/db/queries/brands.py` — added get_brand_by_id()
- `frontend/src/App.tsx` — added /evaluation/:brandId route
- `frontend/src/services/apiClient.ts` — added brand detail + evaluation path types
- `frontend/src/components/brands/BrandTable.tsx` — added Evaluate button + Action column
- `frontend/src/components/brands/BrandTable.test.tsx` — wrapped in BrowserRouter, added Evaluate test
- `frontend/src/test/setup.ts` — added IntersectionObserver mock
