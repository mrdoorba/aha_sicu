# Story 2.3: Brand List UI with Sync Status

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **BD team member**,
I want **to see the list of synced brands and current sync status**,
so that **I can select a brand to evaluate and know if data is fresh**.

## Acceptance Criteria

1. **Given** I am logged in and on the Brands page
   **When** the page loads
   **Then** I see a header showing "Last synced: [timestamp]" or "Sync in progress..."
   **And** sync status shows per-sheet breakdown (VP synced, Meeting synced)
   **And** I see a "Sync Now" button
   **And** I see a paginated list of brands from VP data (20 per page)
   **And** each brand card shows: brand name and key fields from raw_data
   **And** if Meeting data exists for a brand, supplementary info is displayed

2. **Given** I click "Sync Now"
   **When** the sync starts
   **Then** the button shows a loading state
   **And** the status updates to "Syncing..."
   **And** when complete, the timestamp updates and brand list refreshes

3. **Given** the sync fails
   **When** viewing the status
   **Then** I see "Last sync failed: [error message]" in red
   **And** I can click "Sync Now" to retry

4. **Given** I want to find a specific brand
   **When** I type in the search box
   **Then** the brand list filters by name (client-side for current page, or API search)

## Tasks / Subtasks

- [x] Task 0: Initialize shadcn/ui prerequisite components (AC: all)
  - [x] Verify shadcn/ui Button, Input, Card, Badge, Table, Toast, Dialog, Progress are installed
  - [x] Install any missing components: `npx shadcn@latest add <component>`
  - [x] Verify Toaster provider is wired in App.tsx or layout

- [x] Task 1: Create GET /api/v1/brands endpoint with pagination (AC: #1)
  - [x] Add `backend/app/modules/brands/` module with `__init__.py`, `router.py`, `schemas.py`, `service.py`
  - [x] Create `BrandListResponse` schema (paginated: items, total, page, limit, pages)
  - [x] Create `BrandListItem` schema (id, brand_name, key raw_data fields, meeting_data if available)
  - [x] Implement `get_brands_paginated()` in service.py — queries `brand_vp_data` with LEFT JOIN to `brand_meeting_data` on brand_name
  - [x] Add `GET /api/v1/brands` route with `?page=1&limit=20` query params, requires auth
  - [x] Register brands router in `main.py`
  - [x] Write integration tests for pagination, auth, empty state

- [x] Task 2: Add brand search endpoint (AC: #4)
  - [x] Add `?search=<term>` query param to `GET /api/v1/brands`
  - [x] Implement case-insensitive partial match on `brand_name` using `ILIKE '%term%'`
  - [x] Ensure search works with pagination (total reflects filtered count)
  - [x] Write integration tests for search with results, no results, partial match

- [x] Task 3: Create SyncStatus component (AC: #1, #2, #3)
  - [x] Create `frontend/src/components/sync/SyncStatus.tsx`
  - [x] Create `frontend/src/hooks/useSync.ts` hook using TanStack Query
    - `useSyncStatus()` — polls `GET /api/v1/sync/status` every 10 seconds
    - `useTriggerSync()` — mutation calling `POST /api/v1/sync`
  - [x] Display sync status with color-coded Badge:
    - Green badge: "Synced [timestamp]" with per-sheet breakdown
    - Yellow/amber badge: "Syncing..." with loading spinner
    - Red badge: "Sync failed: [error]"
  - [x] "Sync Now" button: triggers manual sync, shows loading state, disabled while syncing
  - [x] On sync completion: auto-refresh sync status display
  - [x] Toast notification on sync success/failure

- [x] Task 4: Create BrandsPage with brand list table (AC: #1)
  - [x] Create `frontend/src/pages/BrandsPage.tsx`
  - [x] Create `frontend/src/hooks/useBrands.ts` hook using TanStack Query
    - `useBrands(page, limit, search)` — fetches `GET /api/v1/brands`
  - [x] Create `frontend/src/components/brands/BrandTable.tsx`
    - Uses shadcn/ui Table component
    - Columns: Brand Name, key VP data fields, Meeting data indicator
    - Each row shows brand name prominently, supplementary info from raw_data
    - If Meeting data exists for a brand, show supplementary badge/info
  - [x] Integrate SyncStatus component at top of page
  - [x] Page layout: SyncStatus header → Search box → Brand table → Pagination

- [x] Task 5: Add search and pagination controls (AC: #1, #4)
  - [x] Add search Input above table with debounced search (300ms)
  - [x] Create pagination controls below table (Previous / Page X of Y / Next)
  - [x] Wire search query param to `useBrands` hook
  - [x] Empty state: "No brands found" when search has no results
  - [x] Empty state: "No brands synced yet. Click 'Sync Now' to get started." when table is empty

- [x] Task 6: Add routing and navigation (AC: #1)
  - [x] Add `/brands` route to App.tsx (protected route)
  - [x] Add navigation link to Brands page in Header or Sidebar
  - [x] Ensure BrandsPage is accessible from dashboard

- [x] Task 7: Write frontend tests (AC: all)
  - [x] Test SyncStatus component renders all states (synced, syncing, failed)
  - [x] Test BrandTable renders brand data correctly
  - [x] Test search input triggers filtered query
  - [x] Test pagination controls navigate between pages
  - [x] Test "Sync Now" button triggers sync and shows loading state

## Dev Notes

### Architecture Compliance

**API Conventions (MUST follow):**
- REST with raw responses (no wrapper) — [Source: architecture.md#API & Communication]
- Paginated response format: `{ "items": [...], "total": 100, "page": 1, "limit": 20, "pages": 5 }`
- Error format: `{"code": "...", "detail": "...", "timestamp": "..."}`
- All endpoints under `/api/v1/` require Bearer token authentication
- Offset-based pagination: `?page=1&limit=20`
- Query param filtering: `?search=Nike`

**Module Pattern (MUST follow):**
- Backend: All brand code lives in `backend/app/modules/brands/` — router.py, schemas.py, service.py
- Router uses `APIRouter(prefix="/api/v1/brands", tags=["brands"])`
- Authentication via `Depends(get_current_user)` on every endpoint
- Business logic in `service.py`, not in router
- Database queries use existing `db/queries/brands.py` functions (extend as needed)

**Frontend Pattern (MUST follow):**
- Components in `src/components/{feature}/` — e.g., `src/components/brands/`, `src/components/sync/`
- Hooks in `src/hooks/` — e.g., `useBrands.ts`, `useSync.ts`
- Pages in `src/pages/` — e.g., `BrandsPage.tsx`
- Use TanStack Query for all server state (brands list, sync status)
- Use `openapi-fetch` via `apiClient.ts` for API calls with auth middleware
- Use shadcn/ui components: Table, Badge, Button, Input, Card, Progress, Toast
- Component naming: PascalCase files and exports

**Frontend State Management:**
- TanStack Query for server state (brands, sync status) — auto-refetch, caching, polling
- React Context for auth state only (already exists in `AuthContext.tsx`)
- No additional state management libraries

**Naming Conventions (MUST FOLLOW):**

| Element | Pattern | Example |
|---------|---------|---------|
| Python functions | `snake_case` | `get_brands_paginated()` |
| Python classes | `PascalCase` | `BrandListResponse`, `BrandListItem` |
| API endpoints | plural nouns | `GET /api/v1/brands` |
| JSON response fields | `snake_case` | `brand_name`, `raw_data`, `total_count` |
| TypeScript components | `PascalCase` | `BrandTable`, `SyncStatus` |
| TypeScript hooks | `useCamelCase` | `useBrands()`, `useSyncStatus()` |
| TypeScript variables | `camelCase` | `brandName`, `isLoading`, `isSyncing` |
| CSS classes | Tailwind utilities | `className="flex items-center gap-2"` |

### Technical Implementation Details

**Backend: GET /api/v1/brands Endpoint**

The existing `db/queries/brands.py` already has:
- `get_brand_data(conn, table, limit, offset)` — paginated brand retrieval
- `get_brand_count(conn, table)` — total count for pagination
- `get_brand_by_name(conn, table, brand_name)` — single brand lookup

For Story 2.3, extend or compose these to:
1. Query `brand_vp_data` with pagination (primary brand source)
2. LEFT JOIN `brand_meeting_data` by `brand_name` to enrich with Meeting data
3. Support `?search=<term>` via `ILIKE` on `brand_vp_data.brand_name`
4. Return paginated response with joined data

**Important:** The `raw_data` JSONB column contains the complete Google Sheets row. The frontend will need to extract and display relevant fields from this JSONB. The exact fields depend on the VP sheet structure — the API should return the raw_data as-is and let the frontend extract what it needs.

**SQL Query Pattern:**
```sql
SELECT
    v.id, v.brand_name, v.raw_data, v.updated_at,
    m.raw_data AS meeting_raw_data
FROM brand_vp_data v
LEFT JOIN brand_meeting_data m ON v.brand_name = m.brand_name
WHERE ($1::text IS NULL OR v.brand_name ILIKE '%' || $1 || '%')
ORDER BY v.brand_name ASC
LIMIT $2 OFFSET $3
```

**Frontend: API Client Extension**

The existing `apiClient.ts` uses `openapi-fetch`. For this story, extend the paths interface or add manual fetch functions using the existing auth middleware pattern:

```typescript
// In hooks/useBrands.ts
import { useQuery } from '@tanstack/react-query';

export function useBrands(page = 1, limit = 20, search = '') {
  return useQuery({
    queryKey: ['brands', page, limit, search],
    queryFn: async () => {
      const params = new URLSearchParams({ page: String(page), limit: String(limit) });
      if (search) params.set('search', search);
      const token = await getCurrentUserToken();
      const res = await fetch(`${API_BASE_URL}/api/v1/brands?${params}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error('Failed to fetch brands');
      return res.json();
    },
  });
}
```

**Frontend: Sync Status Polling**

```typescript
// In hooks/useSync.ts
export function useSyncStatus() {
  return useQuery({
    queryKey: ['syncStatus'],
    queryFn: async () => {
      const token = await getCurrentUserToken();
      const res = await fetch(`${API_BASE_URL}/api/v1/sync/status`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error('Failed to fetch sync status');
      return res.json();
    },
    refetchInterval: 10_000, // Poll every 10 seconds
  });
}

export function useTriggerSync() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      const token = await getCurrentUserToken();
      const res = await fetch(`${API_BASE_URL}/api/v1/sync`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.status === 409) throw new Error('Sync already in progress');
      if (!res.ok) throw new Error('Failed to trigger sync');
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['syncStatus'] });
    },
  });
}
```

**Sync Status Display Logic:**

| Backend `status` Value | Badge Variant | Display Text | Color |
|----------------------|---------------|--------------|-------|
| `"success"` | `default` (green) | "Last synced: [relative time]" | Green (#22C55E) |
| `"in_progress"` | `secondary` (amber) | "Syncing..." + spinner | Amber (#F59E0B) |
| `"failed"` | `destructive` (red) | "Last sync failed: [error]" | Red (#EF4444) |
| `null` (no sync yet) | `outline` (gray) | "Never synced" | Gray |

**Per-Sheet Breakdown (from sync_details JSONB):**
```
VP Sheet: 120 brands synced ✓
Meeting Sheet: 30 brands synced ✓
```
Or on failure:
```
VP Sheet: 120 brands synced ✓
Meeting Sheet: Failed — Rate limit exceeded ✗
```

### UX Design Requirements

**Page Layout (from UX Design Specification):**
```
┌──────────────────────────────────────────────────────────────┐
│  Header (existing)                                           │
├──────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Sync Status Card                                       │  │
│  │ Last synced: 5 minutes ago     [Sync Now]              │  │
│  │ VP: 120 brands ✓  |  Meeting: 30 brands ✓             │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────┐                        │
│  │ 🔍 Search brands...              │                        │
│  └──────────────────────────────────┘                        │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Brand Name        │ Key Info        │ Meeting Data     │  │
│  ├───────────────────┼─────────────────┼──────────────────┤  │
│  │ Brand ABC         │ Category: ...   │ ✓ Available      │  │
│  │ Brand DEF         │ Category: ...   │ — Not available  │  │
│  │ ...               │ ...             │ ...              │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ◀ Previous  Page 1 of 5  Next ▶                             │
└──────────────────────────────────────────────────────────────┘
```

**Design Tokens (from UX spec):**
- Primary: #4361EE (AHA Blue) — buttons, active navigation
- Success: #22C55E — synced status
- Warning: #F59E0B — syncing state
- Error: #EF4444 — sync failures
- Background: #FAFAFA — page background
- Card: #FFFFFF — card backgrounds
- Text primary: #18181B
- Text muted: #71717A
- Border: #E4E4E7

**Typography:**
- Page title: 24px, weight 600
- Table headers: 13px, weight 400, uppercase
- Table cells: 14px, weight 400
- Timestamps: 12px, monospace, muted color
- Numbers/scores: monospace font

**Interaction Patterns:**
- "Sync Now" button: Secondary variant, shows spinner during sync, disabled while syncing
- Search: Debounced (300ms), placeholder "Search brands..."
- Table rows: Hover state (subtle background change), clickable in future stories
- Pagination: Simple Previous/Next with page indicator
- Toast notifications: Bottom-right, auto-dismiss after 3 seconds for success

**Empty States:**
- No brands: Card with message "No brands synced yet. Click 'Sync Now' to get started."
- No search results: "No brands found matching '[search term]'"
- Loading: Skeleton loading state for table rows

### Existing Code Context (from Story 2.2)

**What already exists — DO NOT recreate:**

| Component | File | Status |
|-----------|------|--------|
| `POST /api/v1/sync` endpoint | `modules/sync/router.py` | Exists — triggers manual sync |
| `GET /api/v1/sync/status` endpoint | `modules/sync/router.py` | Exists — returns sync status |
| `SyncStatusResponse` schema | `modules/sync/schemas.py` | Exists — includes status, last_sync, sync_details |
| `SyncTriggerResponse` schema | `modules/sync/schemas.py` | Exists — returns sync_id |
| `get_brand_data()` query | `db/queries/brands.py` | Exists — paginated brand retrieval |
| `get_brand_count()` query | `db/queries/brands.py` | Exists — total count |
| `get_brand_by_name()` query | `db/queries/brands.py` | Exists — single brand lookup |
| `upsert_brand_data()` query | `db/queries/brands.py` | Exists — used by sync service |
| shadcn/ui Button | `components/ui/button.tsx` | Exists — multiple variants |
| shadcn/ui Table | `components/ui/table.tsx` | Exists — full table components |
| shadcn/ui Badge | `components/ui/badge.tsx` | Exists — status badges |
| shadcn/ui Card | `components/ui/card.tsx` | Exists — card layout |
| shadcn/ui Input | `components/ui/input.tsx` | Exists — text input |
| shadcn/ui Progress | `components/ui/progress.tsx` | Exists — progress bar |
| shadcn/ui Dialog | `components/ui/dialog.tsx` | Exists — modals |
| shadcn/ui Sonner | `components/ui/sonner.tsx` | Exists — toast notifications |
| apiClient | `services/apiClient.ts` | Exists — openapi-fetch with auth middleware |
| AuthContext | `context/AuthContext.tsx` | Exists — Firebase auth state |
| Header | `components/layout/Header.tsx` | Exists — user info, logout |
| ProtectedRoute | `components/auth/ProtectedRoute.tsx` | Exists — auth guard |

**What needs to be created:**

| Component | File | Action |
|-----------|------|--------|
| `brands/` module | `backend/app/modules/brands/` | **Create** — router, schemas, service |
| `GET /api/v1/brands` endpoint | `modules/brands/router.py` | **Create** — paginated brand list with search |
| `BrandListResponse` schema | `modules/brands/schemas.py` | **Create** — paginated response |
| `BrandListItem` schema | `modules/brands/schemas.py` | **Create** — individual brand item |
| `get_brands_paginated()` service | `modules/brands/service.py` | **Create** — query with JOIN |
| Brands router registration | `backend/app/main.py` | **Modify** — register brands_router |
| `SyncStatus` component | `frontend/src/components/sync/SyncStatus.tsx` | **Create** |
| `BrandTable` component | `frontend/src/components/brands/BrandTable.tsx` | **Create** |
| `BrandsPage` page | `frontend/src/pages/BrandsPage.tsx` | **Create** |
| `useBrands` hook | `frontend/src/hooks/useBrands.ts` | **Create** |
| `useSync` hook | `frontend/src/hooks/useSync.ts` | **Create** |
| `/brands` route | `frontend/src/App.tsx` | **Modify** — add route |
| Navigation links | `frontend/src/components/layout/Header.tsx` | **Modify** — add Brands nav |

### Library & Framework Requirements

| Library | Version | Usage in This Story | Status |
|---------|---------|---------------------|--------|
| FastAPI | existing | `APIRouter`, `Depends`, `Query` params | Installed |
| asyncpg | existing | Database queries via connection pool | Installed |
| Pydantic | existing | `BrandListResponse`, `BrandListItem` schemas | Installed |
| TanStack Query | ^5.90.20 | `useQuery`, `useMutation`, `useQueryClient` | Installed |
| react-router-dom | ^7.13.0 | Route for `/brands` page | Installed |
| lucide-react | ^0.563.0 | Icons for sync status, search, pagination | Installed |
| sonner | ^2.0.7 | Toast notifications for sync events | Installed |
| openapi-fetch | ^0.15.0 | API client with auth middleware | Installed |

**No new dependencies required** — this story uses only what is already installed.

### File Structure Requirements

**Files to create (backend):**
```
backend/app/modules/brands/__init__.py
backend/app/modules/brands/router.py        ← GET /brands endpoint
backend/app/modules/brands/schemas.py       ← BrandListResponse, BrandListItem
backend/app/modules/brands/service.py       ← get_brands_paginated()
backend/tests/integration/api/test_brands.py ← Integration tests
```

**Files to modify (backend):**
```
backend/app/main.py                          ← Register brands_router
backend/app/db/queries/brands.py             ← Add search + JOIN query functions
```

**Files to create (frontend):**
```
frontend/src/components/sync/SyncStatus.tsx  ← Sync status display + trigger
frontend/src/components/brands/BrandTable.tsx ← Brand list table
frontend/src/pages/BrandsPage.tsx            ← Brands page composition
frontend/src/hooks/useBrands.ts              ← Brand list data hook
frontend/src/hooks/useSync.ts                ← Sync status + trigger hooks
```

**Files to modify (frontend):**
```
frontend/src/App.tsx                         ← Add /brands route
frontend/src/components/layout/Header.tsx    ← Add navigation link
frontend/src/services/apiClient.ts           ← Extend API paths (optional)
```

### Testing Requirements

**Backend Tests (pytest):**
- Test `GET /api/v1/brands` returns paginated response with 200
- Test `GET /api/v1/brands` requires authentication (401 without token)
- Test `GET /api/v1/brands?page=1&limit=20` pagination works correctly
- Test `GET /api/v1/brands?search=Nike` filters by brand name
- Test `GET /api/v1/brands?search=nonexistent` returns empty list with total=0
- Test response includes Meeting data when available for a brand
- Test response handles brands with no Meeting data (null/absent)

**Frontend Tests (Vitest + Testing Library):**
- Test SyncStatus renders "Last synced: [time]" for success state
- Test SyncStatus renders "Syncing..." for in_progress state
- Test SyncStatus renders error message for failed state
- Test SyncStatus "Sync Now" button triggers sync mutation
- Test BrandTable renders brand rows from data
- Test BrandsPage search input debounces and filters
- Test BrandsPage pagination controls work
- Test empty states render correctly

**Test Patterns:**
- Backend: Use `AsyncClient` (httpx), mock auth via `get_current_user` override, test database fixtures
- Frontend: Use `@testing-library/react`, mock TanStack Query responses, use `vi.fn()` for API mocks

### Anti-Patterns to Avoid

1. **DO NOT** create a separate API endpoint for search — use query params on `GET /brands`
2. **DO NOT** fetch all brands at once — always use server-side pagination
3. **DO NOT** use React Context for brand list state — use TanStack Query
4. **DO NOT** poll sync status more frequently than every 10 seconds
5. **DO NOT** add SSE/WebSocket for real-time sync — that belongs to Story 2.4
6. **DO NOT** add brand selection/evaluation start — that belongs to Story 3.1
7. **DO NOT** add client-side sorting — keep it simple, server-side only
8. **DO NOT** parse raw_data JSONB in the backend — return as-is, let frontend extract fields
9. **DO NOT** create Dashboard page widgets — this story is the Brands page only
10. **DO NOT** add dark mode — light mode only per UX spec

### Previous Story Intelligence

**From Story 2.2 (Manual Sync Trigger API):**
- `POST /api/v1/sync` returns 202 with `sync_id` — use for triggering sync from UI
- `POST /api/v1/sync` returns 409 when sync in progress — handle gracefully in UI (show toast, keep button disabled)
- `GET /api/v1/sync/status` returns `SyncStatusResponse` with `status` field: `"success"`, `"failed"`, or `"in_progress"`
- `SyncStatusResponse` has `last_sync`, `brands_synced`, `error_message`, `sync_details` (per-sheet breakdown)
- Advisory lock (`pg_advisory_xact_lock(1)`) prevents concurrent sync race conditions — backend handles this, frontend just shows 409 gracefully
- 44 existing tests passing — ensure no regressions

**From Story 2.1 (Google Sheets Sync Backend):**
- `brand_vp_data` table stores VP sheet brands with `raw_data` JSONB
- `brand_meeting_data` table stores Meeting sheet brands with `raw_data` JSONB
- Both tables use `brand_name` as unique key — this is the JOIN field
- `db/queries/brands.py` has validated table names: only `brand_vp_data` and `brand_meeting_data` allowed
- Brand queries use parameterized SQL with `$1, $2` placeholders

**From Story 1.3 (Frontend Login Flow):**
- Auth context provides `user`, `loading`, `login`, `logout`
- ProtectedRoute wraps authenticated pages with loading/redirect logic
- Header shows user email and logout button
- App.tsx uses react-router-dom v7 with Routes/Route components

**From shadcn/ui Setup (commit e8b8b9b):**
- shadcn/ui initialized with New York style, zinc base color
- Components installed to `src/components/ui/`
- `cn()` utility in `src/lib/utils.ts` for Tailwind class merging
- Tailwind CSS v4 with CSS variables configured

### Git Intelligence Summary

Recent commits show:
- Story 2.2 complete with code review fixes (7996fd1, c8d57f9)
- shadcn/ui fully set up with project color palette (e8b8b9b, 063fc29)
- Existing components migrated to shadcn semantic classes (063fc29)
- Sprint change proposal architecture updates merged (b254162)
- All code follows established patterns and naming conventions
- Test suite: 44 backend tests passing, frontend tests passing

### Project Structure Notes

- This story is the **first full-stack feature story** — both backend and frontend changes
- This is the **first frontend feature page** — establishes patterns for future pages
- Backend follows existing module structure: `modules/brands/{router,schemas,service}.py`
- Frontend follows architecture: components in `components/`, hooks in `hooks/`, pages in `pages/`
- All shadcn/ui foundation components are already installed — no new UI library setup needed
- No infrastructure/Terraform changes needed
- No database migrations needed — using existing `brand_vp_data` and `brand_meeting_data` tables

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 2.3: Brand List UI with Sync Status]
- [Source: _bmad-output/planning-artifacts/architecture.md#API & Communication]
- [Source: _bmad-output/planning-artifacts/architecture.md#Frontend Architecture]
- [Source: _bmad-output/planning-artifacts/architecture.md#Implementation Patterns & Consistency Rules]
- [Source: _bmad-output/planning-artifacts/architecture.md#Module Boundaries]
- [Source: _bmad-output/planning-artifacts/architecture.md#Data Architecture — Brand Data (Dual-Sheet Model)]
- [Source: _bmad-output/planning-artifacts/prd.md#Brand Data Management — FR3, FR4, FR5]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Design System Foundation]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Visual Design Foundation]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Component Strategy]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#UX Consistency Patterns]
- [Source: _bmad-output/implementation-artifacts/2-2-manual-sync-trigger-api.md#Dev Notes]
- [Source: _bmad-output/implementation-artifacts/2-2-manual-sync-trigger-api.md#Dev Agent Record]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

- Mock pattern fix: `AsyncMock()` as db replacement breaks `__aenter__` protocol; must use `patch(...) as mock_db` (MagicMock) pattern for `db.connection()` context manager mocking
- SyncStatus test: "Syncing..." text appears in both badge and button — use `getAllByText` for ambiguous matches

### Completion Notes List

- Task 0: All 8 shadcn/ui components verified installed. Wired `QueryClientProvider` and `Toaster` into App.tsx
- Task 1: Created `backend/app/modules/brands/` module (router, schemas, service) following sync module pattern. `GET /api/v1/brands` endpoint with pagination, auth, LEFT JOIN for meeting data
- Task 2: Added `?search=<term>` query param with ILIKE case-insensitive search. Search works with pagination (filtered count)
- Task 3: Created `SyncStatus` component with color-coded badges (green/amber/red), per-sheet breakdown, Sync Now button with loading state, toast notifications
- Task 4: Created `BrandsPage` with SyncStatus header, search input, BrandTable with skeleton loading, pagination controls
- Task 5: Debounced search (300ms), pagination Previous/Next with page indicator, empty states for no brands and no search results
- Task 6: Added `/brands` protected route in App.tsx, navigation links (Dashboard, Brands) with active state in Header
- Task 7: 20 new frontend tests (7 SyncStatus, 6 BrandTable, 7 BrandsPage) covering all states and interactions

### File List

**Created (Backend):**
- backend/app/modules/brands/__init__.py
- backend/app/modules/brands/router.py
- backend/app/modules/brands/schemas.py
- backend/app/modules/brands/service.py
- backend/tests/integration/api/test_brands.py

**Modified (Backend):**
- backend/app/db/queries/brands.py — added get_brands_with_meeting(), get_brands_count_with_search(), _escape_like(), ESCAPE clause
- backend/app/main.py — registered brands_router
- backend/app/modules/sync/router.py — added advisory lock transaction (code review 1 fix)
- backend/app/modules/sync/schemas.py — added SyncStatusResponse model_validator, last_sync, status enum (code review 1 fix)
- backend/app/modules/sync/service.py — renamed sync_details keys to vp_sheet/meeting_sheet (code review 1 fix)
- backend/tests/integration/api/test_sync.py — updated assertions for status enum (code review 1 fix)
- backend/tests/integration/api/test_sync_trigger.py — added transaction mock support (code review 1 fix)
- backend/tests/unit/sync/test_service.py — updated status/last_sync assertions (code review 1 fix)

**Created (Frontend):**
- frontend/src/hooks/useSync.ts
- frontend/src/hooks/useBrands.ts
- frontend/src/components/sync/SyncStatus.tsx
- frontend/src/components/sync/SyncStatus.test.tsx
- frontend/src/components/brands/BrandTable.tsx
- frontend/src/components/brands/BrandTable.test.tsx
- frontend/src/pages/BrandsPage.tsx
- frontend/src/pages/BrandsPage.test.tsx

**Modified (Frontend):**
- frontend/src/App.tsx — added QueryClientProvider, Toaster, BrandsPage route
- frontend/src/components/layout/Header.tsx — added navigation links with active state
- frontend/src/services/apiClient.ts — added brands and sync path types for openapi-fetch

### Senior Developer Review (AI)

**Reviewer:** Mr. Door on 2026-02-06
**Outcome:** Approved with fixes applied

**Issues Found:** 3 High, 4 Medium, 3 Low — **All 10 fixed**

| # | Severity | Issue | Fix Applied |
|---|----------|-------|-------------|
| H1 | HIGH | Hooks bypass openapi-fetch client (architecture violation) | Refactored useBrands.ts, useSync.ts to use apiClient.ts |
| H2 | HIGH | Hooks send `Bearer null` when unauthenticated | Fixed by H1 — apiClient middleware skips header when no token |
| H3 | HIGH | ILIKE search vulnerable to pattern injection (`%`, `_`) | Added `_escape_like()` helper in brands.py |
| M1 | MEDIUM | baseUrl duplicated in 3 files | Fixed by H1 — single source in apiClient.ts |
| M2 | MEDIUM | BrandsPage silently swallows API errors | Added isError state with error UI display |
| M3 | MEDIUM | Backend tests don't verify query params reach database | Added mock call_args assertions for offset/limit/search |
| M4 | MEDIUM | Brand list doesn't refresh after sync completes | Added useEffect in SyncStatus to detect status transition and invalidate brands query |
| L1 | LOW | summarizeRawData shows arbitrary JSONB keys | Filtered meta keys, sorted alphabetically |
| L2 | LOW | Skeleton shows 5 rows vs 20-per-page limit | Increased to 10 skeleton rows |
| L3 | LOW | formatRelativeTime crashes on invalid/future dates | Added isNaN and negative diff guards |

#### Second Review (AI)

**Reviewer:** Mr. Door on 2026-02-06
**Outcome:** Approved with fixes applied

**Issues Found:** 4 High, 3 Medium, 3 Low — **All 10 fixed**

| # | Severity | Issue | Fix Applied |
|---|----------|-------|-------------|
| H1 | HIGH | ILIKE escape ineffective — missing `ESCAPE '\'` clause in SQL | Added `ESCAPE '\'` to both ILIKE clauses in brands.py |
| H2 | HIGH | Backend tests don't exercise _escape_like or verify escaped search | Added _escape_like unit test + special char search integration test |
| H3 | HIGH | useSyncStatus swallows errors silently (returns null) | Changed to throw on error, added isError handling + error UI in SyncStatus |
| H4 | HIGH | Search parameter has no max_length validation | Added `max_length=200` to search Query param + validation test |
| M1 | MEDIUM | Story File List missing 7 git-changed files | Updated File List with all sync module + apiClient changes |
| M2 | MEDIUM | BrandTable duplicate table header/structure code | Merged into single Table with conditional body content |
| M3 | MEDIUM | SyncStatus effect ref design intent unclear | Added comment clarifying intentional undefined initialization |
| L1 | LOW | META_KEYS case-insensitive filter undocumented | Added comment explaining toLowerCase() handles JSONB key casing |
| L2 | LOW | formatRelativeTime timezone assumption undocumented | Added JSDoc comment noting UTC timestamp assumption |
| L3 | LOW | Frontend types duplicated across apiClient.ts and hooks | Added cross-reference comments to keep types in sync |

### Change Log

- 2026-02-06: Story 2.3 implemented — Brand List UI with Sync Status. Full-stack feature: backend brands API with pagination/search, frontend BrandsPage with SyncStatus, BrandTable, search, pagination. 52 backend tests + 47 frontend tests all passing.
- 2026-02-06: Code review #1 fixes applied — 10 issues resolved (3 HIGH, 4 MEDIUM, 3 LOW). Refactored hooks to use openapi-fetch apiClient, added LIKE escape, error handling, sync completion refresh, improved tests.
- 2026-02-06: Code review #2 fixes applied — 10 issues resolved (4 HIGH, 3 MEDIUM, 3 LOW). Fixed ILIKE ESCAPE clause, search max_length, sync error handling, BrandTable refactor, documentation. 55 backend + 48 frontend tests passing.
