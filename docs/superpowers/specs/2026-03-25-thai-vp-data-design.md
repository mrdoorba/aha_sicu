# Thai VP Data Integration — Design Spec

**Date:** 2026-03-25
**Status:** Approved

## Overview

Add Thailand (TH) VP data from a separate Google Sheet alongside the existing Indonesia (ID) VP data. Includes column drift detection to catch accidental header changes in either sheet.

## 1. Database Schema

**New migration (034):** Add `marketplace VARCHAR(2)` to `brand_vp_data` and `brand_meeting_data`. Follows the same pattern as migration 026 which added `marketplace` to `scoring_rules`, `evaluation_inputs`, and `evaluations`.

- `CHECK (marketplace IN ('ID', 'TH'))` — reuse constraint pattern from migration 026
- Default `'ID'` for the column
- Backfill all existing rows with `marketplace = 'ID'`
- Change unique constraint from `(brand_name)` to `(brand_name, marketplace)`
- Add index on `marketplace` for filtering

**Query updates required:**
- `batch_upsert_brand_data`: Change `ON CONFLICT (brand_name)` to `ON CONFLICT (brand_name, marketplace)`, add `marketplace` to INSERT column list
- `upsert_brand_data`: Same ON CONFLICT update
- `get_brands_with_meeting`: Add `AND v.marketplace = m.marketplace` to the LEFT JOIN condition to prevent cross-marketplace matching
- `get_brand_by_id`: Same JOIN condition update
- `get_brands_count_with_search`: Add `WHERE marketplace` filter so pagination counts match filtered results

**Related tables:** `brand_uploads` and `calculator_results` reference `brand_vp_data.id` via FK. Since each marketplace gets its own `brand_vp_data` row (different `id`), uploads and calculator results are naturally scoped per marketplace via the FK. No changes needed.

## 2. Configuration — Per-Marketplace Sheet Config

Each marketplace defines its own sheet configuration:

**Indonesia (ID):**
- `GSHEETS_VP_SPREADSHEET_ID` — existing env var
- Range: `VP!A:Y`
- Brand column: `Nama Brand`
- Expected headers: all columns A-Y (defined in code)

**Thailand (TH):**
- `GSHEETS_VP_SPREADSHEET_ID_TH` — new env var
- Range: `VP!A:W`
- Brand column: `Brand`
- Expected headers: all columns A-W (defined in code)

New Settings fields (Pydantic, maps to env vars):
- `gsheets_vp_spreadsheet_id_th` → `GSHEETS_VP_SPREADSHEET_ID_TH`
- `gsheets_vp_range_th` → `GSHEETS_VP_RANGE_TH` (default: `VP!A:W`)
- `gsheets_vp_brand_column_th` → `GSHEETS_VP_BRAND_COLUMN_TH` (default: `Brand`)

Expected headers are defined in code (not env vars) — drift detection is specifically meant to catch unexpected changes. Legitimate header changes require a code update and redeploy.

## 3. Column Drift Detection

A pre-sync validation step before any data is fetched/upserted:

1. Fetch only the header row using a limited range (e.g., `VP!1:1`) via a new `fetch_headers()` method on `GoogleSheetsClient` — avoids fetching all data twice
2. Compare against the marketplace's `expected_headers` list
3. If any mismatch (missing, renamed, reordered, or extra columns) — skip that marketplace's sync entirely
4. Return a structured error:

```json
{
  "marketplace": "TH",
  "sheet": "VP",
  "status": "column_drift",
  "expected": ["Brand", "Email", "..."],
  "actual": ["Brands", "Email", "..."],
  "missing": ["Brand"],
  "unexpected": ["Brands"]
}
```

Validates **all** columns (not just the 6 used ones) to catch any drift early.

## 4. Sync Flow Changes

When `POST /api/v1/sync` is triggered:

1. Validate headers for all marketplaces (ID + TH) in parallel
2. If any marketplace has drift — skip that marketplace, continue others
3. Sync valid marketplaces — thread `marketplace` param through the entire call chain: `run_sync` → `_sync_vp_sheet` → `_sync_sheet_to_table` → `batch_upsert_brand_data`
4. Return per-marketplace results:

```json
{
  "status": "partial_failure",
  "results": {
    "vp_id": {"status": "success", "count": 12},
    "vp_th": {"status": "column_drift", "error": "...details..."},
    "meeting_id": {"status": "success", "count": 10}
  }
}
```

Each marketplace syncs independently — a drift in one does not block the other.

**Backward compatibility:** The sync_details keys change from `vp_sheet`/`meeting_sheet` to `vp_id`/`vp_th`/`meeting_id`. Old stored sync records in the DB retain old keys. The SyncStatus frontend component must handle both old and new key formats gracefully during the transition.

## 5. Backend API Changes

**Brands endpoint:**

`GET /api/v1/brands?marketplace=ID,TH&search=something`

- `marketplace` param accepts comma-separated values (supports multi-select)
- Defaults to all marketplaces if omitted
- Search scopes to the active marketplace filter
- Response includes `marketplace` field on each brand

**Schema updates required:**
- `BrandListItem`: Add `marketplace: str` field
- `BrandDetailResponse`: Add `marketplace: str` field
- Frontend `BrandListItem` type in `useBrands.ts`: Add `marketplace` field

**Brand detail:** No structural change — brand ID is unique. Response gains a `marketplace` field.

## 6. Frontend Changes

### BrandsPage — Marketplace Filter Chips

- Two toggle buttons: `[Indonesia]` `[Thailand]`
- Both active by default (show all brands)
- Toggle one off to narrow down
- Search bar filters within active marketplace selection
- Filter state passed as query param to the brands API

### SyncStatus — Per-Marketplace Breakdown

- Current: `VP: 12 brands | M1: 10 brands`
- New: `VP ID: 12 | VP TH: 8 | M1 ID: 10`
- Handle both old (`vp_sheet`) and new (`vp_id`/`vp_th`) sync_details keys for backward compatibility

### Column Drift Popup — Dialog Modal

- Triggered when sync result contains a `column_drift` status
- Title: "Column Mismatch Detected"
- Body: which marketplace, which columns are wrong (missing/unexpected)
- Single "OK" dismiss button
- Non-blocking — successful marketplace syncs still reflected in status

### BrandTable — Marketplace-Aware Display

- Small marketplace badge (flag emoji) on each row for clarity when both filters are active
- `PRIORITY_KEYS` and `summarizeRawData()` must be marketplace-aware: use Indonesian column names (`Nama PIC/ Jabatan*`, `Kategori`, `No WA*`) for ID brands, Thai column names (`PIC`, `Product Category`, `Contact Number`) for TH brands

## 7. Column Name Mapping for Evaluations

Per-marketplace field mapping for `BrandRawData` extraction:

| Purpose | Indonesia Column | Thailand Column |
|---------|-----------------|-----------------|
| email | `Email` | `Email` |
| pic_name | `Nama PIC/ Jabatan*` | `PIC` |
| store_link | `Link Shopee Mall / LazMall` | `Shopee Link` |
| kategori | `Kategori` | `Product Category` |

The mapping lives in the evaluation service as a constant dict keyed by marketplace. The `get_evaluation_detail` function already reads `marketplace` from the evaluation row — use it to select the correct column names when extracting `BrandRawData` fields from `raw_data`.

No downstream changes needed — emails and UI display consume `BrandRawData` fields by their normalized names.

## Thai VP Sheet Column Mapping

| Column | Thai Header |
|--------|------------|
| Brand name (key) | `Brand` |
| Email | `Email` |
| PIC name | `PIC` |
| Store link | `Shopee Link` |
| Category | `Product Category` |
| Contact number | `Contact Number` |

Full expected headers list (all A-W columns) to be provided during implementation.

## 8. Infrastructure (Terraform)

The new Thai env vars follow the same pattern as existing Indonesia spreadsheet config — plain-text Cloud Run environment variables (not secrets).

**Files to update:**

| File | Change |
|------|--------|
| `infrastructure/terraform/variables.tf` | Add 3 root variables: `gsheets_vp_spreadsheet_id_th`, `gsheets_vp_range_th`, `gsheets_vp_brand_column_th` |
| `infrastructure/terraform/modules/environment/variables.tf` | Add same 3 as module variables |
| `infrastructure/terraform/modules/environment/main.tf` | Add 3 `env {}` blocks to Cloud Run service definition |
| `infrastructure/terraform/main.tf` | Pass the 3 vars to both dev and prod module blocks |
| `environments/dev.tfvars` | Set Thai spreadsheet ID for dev |
| `environments/prod.tfvars` | Set Thai spreadsheet ID for prod |

**No new Cloud Scheduler job needed** — the existing daily sync (`POST /api/v1/sync`) handles all configured spreadsheets at runtime.

**Service account access:** The existing `sheets-sa` service account must be granted read access to the Thai Google Sheet (done in Google Sheets sharing UI, not Terraform).

## Out of Scope

- Thai meeting sheet (does not exist yet)
- Global marketplace context/state (stays local per page)
- Additional marketplaces beyond ID and TH
