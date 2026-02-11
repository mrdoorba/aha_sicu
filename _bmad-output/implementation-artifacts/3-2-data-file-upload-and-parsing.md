# Story 3.2: Data File Upload and Parsing

Status: ready-for-dev

## Story

As a **BD team member**,
I want **to upload data files (CSV and Excel) for a brand's evaluation**,
so that **the system can parse and validate them for calculator processing**.

## Acceptance Criteria

1. **File upload slots displayed on evaluation page**
   **Given** I am on the evaluation page for a brand
   **When** I view the File Upload section (Step 4)
   **Then** I see 4 distinct upload slots:
     1. **CPC Ad Report** — accepts `.csv` (for Calculator 1 Sheet 1)
     2. **Keyword Placement Report** — accepts `.csv` (for Calculator 1 Sheet 2)
     3. **Order Export** — accepts `.xlsx` (for Calculators 2 & 3)
     4. **Mass Update / Sales Info** — accepts `.xlsx` (for Calculator 2)
   **And** each slot shows its accepted format, calculator routing label, and current status (empty / uploaded / error)

2. **Upload a file to a slot**
   **Given** I select a file for any upload slot (correct format, ≤2MB)
   **When** the file uploads to the backend
   **Then** I see a progress indicator during upload
   **And** the backend validates the file format (CSV or Excel as appropriate)
   **And** Polars parses the file and validates per-calculator column schema (see AC #3)
   **And** on success I see "File uploaded successfully" with filename displayed
   **And** the slot status changes from "empty" to "uploaded"

3. **Per-calculator column validation**
   **Given** a file is uploaded
   **When** the backend parses the file with Polars
   **Then** validate required columns based on file type:
     - **CPC Ad Report**: requires columns including Nama Produk, Nama Iklan, Tipe Iklan, Penempatan, Tipe Biaya, Biaya
     - **Keyword Report**: requires columns including Kata Kunci Pencarian, Klik, Kunjungan, Pesanan, Pendapatan, Biaya Iklan, ROAS
     - **Order Export**: requires columns including No. Pesanan, Nama Produk, Harga Awal, Harga Setelah Diskon, Jumlah, Voucher Ditanggung Penjual, Paket Diskon, Nomor Referensi SKU, Nama Variasi, Jumlah Produk di Pesan, Cashback Koin, Diskon dari Shopee
     - **Mass Update**: requires columns including Kode Variasi, Nama Produk, Nama Variasi, SKU, Stok (note: headers start at row 3)

4. **Upload validation errors**
   **Given** I upload an invalid file (wrong format, >2MB, corrupted, missing required columns)
   **When** validation fails
   **Then** return error with appropriate code:
     - `UPLOAD_INVALID_FORMAT` — wrong file extension for the slot
     - `UPLOAD_FILE_TOO_LARGE` — exceeds 2MB limit
     - `UPLOAD_PARSE_FAILED` — file is corrupted or cannot be parsed
     - `UPLOAD_MISSING_COLUMNS` — required columns for the target calculator are missing (detail lists which columns)
   **And** I see a user-friendly error message specifying what's wrong
   **And** the previous file for that slot (if any) remains unchanged

5. **Re-upload (upsert per file type)**
   **Given** I upload a new file to a slot that already has one
   **When** the upload succeeds
   **Then** the new file replaces the old one for that file type (upsert per brand_id + file_type)
   **And** calculator results that depend on this file type are cleared (set to NULL — actual re-run is Story 3.7)
   **And** the slot shows the new filename and upload timestamp

6. **View uploaded files state**
   **Given** I navigate to an evaluation page for a brand
   **When** the page loads
   **Then** I see the current upload state for each slot:
     - Slots with uploaded files show: filename, upload timestamp, file size
     - Slots without files show: "No file uploaded" with upload button
   **And** the data persists across page refreshes

7. **API: Upload file**
   **Given** I send `POST /api/v1/upload/brands/{brand_id}` with multipart form data
   **When** authenticated with body containing:
     - `file`: the file binary
     - `file_type`: one of `cpc_ad_report`, `keyword_report`, `order_export`, `mass_update`
   **Then** validate format, size, and columns
   **And** parse with Polars and store parsed data as JSONB
   **And** return:
   ```json
   {
     "id": 1,
     "brand_id": 123,
     "file_type": "cpc_ad_report",
     "filename": "report.csv",
     "file_size": 102400,
     "row_count": 500,
     "uploaded_at": "2026-02-11T10:30:00Z"
   }
   ```
   **And** if brand_id not found, return 404 with `BRAND_NOT_FOUND`

8. **API: Get upload status for a brand**
   **Given** I request `GET /api/v1/upload/brands/{brand_id}`
   **When** authenticated
   **Then** return all uploaded files for the brand:
   ```json
   {
     "brand_id": 123,
     "uploads": [
       {
         "id": 1,
         "file_type": "cpc_ad_report",
         "filename": "report.csv",
         "file_size": 102400,
         "row_count": 500,
         "uploaded_at": "2026-02-11T10:30:00Z"
       }
     ]
   }
   ```
   **And** slots without uploads are simply not in the array

## Tasks / Subtasks

- [ ] Task 1: Add backend dependencies (AC: #2, #3)
  - [ ] 1.1 Add `polars` to `backend/pyproject.toml` dependencies
  - [ ] 1.2 Add `python-multipart` to `backend/pyproject.toml` dependencies (required for FastAPI file uploads)
  - [ ] 1.3 Run `uv sync` to install

- [ ] Task 2: Create database migration for `brand_uploads` table (AC: #5, #6, #7)
  - [ ] 2.1 Create migration `007_create_brand_uploads_table.py` in `backend/app/db/migrations/versions/`
  - [ ] 2.2 Table schema:
    - `id` SERIAL PRIMARY KEY
    - `brand_id` INTEGER NOT NULL REFERENCES brand_vp_data(id)
    - `file_type` VARCHAR(50) NOT NULL — one of: `cpc_ad_report`, `keyword_report`, `order_export`, `mass_update`
    - `calculator_target` VARCHAR(100) — which calculator(s) this feeds
    - `filename` VARCHAR(255) NOT NULL
    - `file_size` INTEGER NOT NULL
    - `row_count` INTEGER
    - `parsed_data` JSONB NOT NULL (extracted data from Polars)
    - `uploaded_by` INTEGER NOT NULL REFERENCES users(id)
    - `uploaded_at` TIMESTAMPTZ DEFAULT NOW()
    - UNIQUE(brand_id, file_type) — one file per type per brand
  - [ ] 2.3 Add indexes: `idx_brand_uploads_brand_id`, `idx_brand_uploads_file_type`
  - [ ] 2.4 Add calculator_target default values mapping:
    - `cpc_ad_report` → `ads_keyword`
    - `keyword_report` → `ads_keyword`
    - `order_export` → `top_sku,discount`
    - `mass_update` → `top_sku`

- [ ] Task 3: Create upload query functions (AC: #7, #8)
  - [ ] 3.1 Create `backend/app/db/queries/uploads.py` with:
    - `get_uploads_by_brand(conn, brand_id)` — returns all uploads for a brand
    - `get_upload_by_type(conn, brand_id, file_type)` — returns single upload or None
    - `upsert_upload(conn, brand_id, file_type, calculator_target, filename, file_size, row_count, parsed_data, uploaded_by)` — INSERT ON CONFLICT(brand_id, file_type) DO UPDATE
    - `delete_upload(conn, brand_id, file_type)` — for cleanup if needed

- [ ] Task 4: Create file parser module (AC: #2, #3, #4)
  - [ ] 4.1 Create `backend/app/modules/upload/__init__.py`
  - [ ] 4.2 Create `backend/app/modules/upload/parser.py`:
    - `parse_csv(file_bytes, filename)` → `pl.DataFrame` — parse CSV with Polars
    - `parse_excel(file_bytes, filename, header_row=0)` → `pl.DataFrame` — parse Excel with Polars. Mass Update uses `header_row=2` (headers at row 3)
    - `validate_columns(df, file_type)` → raises `AppException` with `UPLOAD_MISSING_COLUMNS` if required columns missing
    - `dataframe_to_json(df)` → serializable dict/list for JSONB storage
    - Column requirements defined as constants per file_type:
      - `CPC_AD_REPORT_COLUMNS`: Nama Produk, Nama Iklan, Tipe Iklan, Penempatan, Tipe Biaya, Biaya
      - `KEYWORD_REPORT_COLUMNS`: Kata Kunci Pencarian, Klik, Kunjungan, Pesanan, Pendapatan, Biaya Iklan, ROAS
      - `ORDER_EXPORT_COLUMNS`: No. Pesanan, Nama Produk, Harga Awal, Harga Setelah Diskon, Jumlah, Voucher Ditanggung Penjual, Paket Diskon, Nomor Referensi SKU, Nama Variasi, Jumlah Produk di Pesan, Cashback Koin, Diskon dari Shopee
      - `MASS_UPDATE_COLUMNS`: Kode Variasi, Nama Produk, Nama Variasi, SKU, Stok

- [ ] Task 5: Create upload service (AC: #2, #3, #4, #5, #7, #8)
  - [ ] 5.1 Create `backend/app/modules/upload/service.py`:
    - `process_upload(brand_id, file_type, file, user_id)` — orchestrates: validate format → validate size → parse → validate columns → store parsed data → return response
    - `get_brand_uploads(brand_id)` — returns all uploads for a brand
    - Validate `file_type` is one of allowed values (frozenset)
    - Validate file extension matches expected format for file_type (.csv for ad reports, .xlsx for export/mass_update)
    - Validate file size ≤ 2MB (2_097_152 bytes)
  - [ ] 5.2 Create `backend/app/modules/upload/schemas.py`:
    - `UploadResponse`: id, brand_id, file_type, filename, file_size, row_count, uploaded_at
    - `BrandUploadsResponse`: brand_id, uploads (list of UploadResponse)
    - `FileTypeEnum`: literal values for valid file types

- [ ] Task 6: Create upload router (AC: #7, #8)
  - [ ] 6.1 Create `backend/app/modules/upload/router.py`:
    - `POST /api/v1/upload/brands/{brand_id}` — accepts multipart (file + file_type form field)
    - `GET /api/v1/upload/brands/{brand_id}` — returns all uploads for brand
  - [ ] 6.2 Register upload router in `main.py`
  - [ ] 6.3 Use `Depends(get_current_user)` on all endpoints

- [ ] Task 7: Add `UploadException` to exceptions (AC: #4)
  - [ ] 7.1 Add `UploadException` class to `core/exceptions.py` (like SyncException pattern)

- [ ] Task 8: Add frontend API types and hooks (AC: #1, #2, #6, #7, #8)
  - [ ] 8.1 Add `/api/v1/upload/brands/{brand_id}` GET and POST path types to `apiClient.ts`
  - [ ] 8.2 Create `hooks/useUpload.ts`:
    - `useBrandUploads(brandId)` — fetches GET upload status using TanStack Query
    - `useUploadFile(brandId)` — mutation for POST file upload (multipart FormData)
  - [ ] 8.3 Note: multipart uploads can't use openapi-fetch easily — use raw `fetch` with auth token injection for the POST upload only. GET can use apiClient.

- [ ] Task 9: Build file upload components (AC: #1, #2, #4, #5, #6)
  - [ ] 9.1 Create `components/evaluation/FileUploadSlot.tsx`:
    - Single file slot component with: label, accepted format, calculator routing info
    - States: empty (upload button), uploading (progress), uploaded (filename + timestamp + re-upload), error (message + retry)
    - File input accepts only the allowed format for the slot (.csv or .xlsx)
    - Shows file size after upload
  - [ ] 9.2 Create `components/evaluation/FileUploadSection.tsx`:
    - Renders 4 `FileUploadSlot` components in a grid
    - Uses `useBrandUploads` to fetch current upload state
    - Passes `useUploadFile` mutation to each slot
  - [ ] 9.3 Update `EvaluationSections.tsx` Section 4 to use `FileUploadSection` instead of static placeholder cards

- [ ] Task 10: Write backend tests (AC: #2, #3, #4, #5, #7, #8)
  - [ ] 10.1 Unit test `parser.py`: test CSV parsing, Excel parsing, column validation success/failure, Mass Update header row handling
  - [ ] 10.2 Integration test `POST /api/v1/upload/brands/{brand_id}`:
    - Upload valid CSV → 200 with response
    - Upload valid Excel → 200 with response
    - Upload wrong format → 400 with UPLOAD_INVALID_FORMAT
    - Upload too large → 400 with UPLOAD_FILE_TOO_LARGE
    - Upload missing columns → 400 with UPLOAD_MISSING_COLUMNS
    - Upload to non-existent brand → 404 with BRAND_NOT_FOUND
    - Re-upload same file_type → 200, replaces old data
  - [ ] 10.3 Integration test `GET /api/v1/upload/brands/{brand_id}`:
    - Returns empty uploads array for brand with no uploads
    - Returns uploads after successful upload

- [ ] Task 11: Write frontend tests (AC: #1, #2, #4, #6)
  - [ ] 11.1 Test FileUploadSlot renders empty state with upload button
  - [ ] 11.2 Test FileUploadSlot renders uploaded state with filename and timestamp
  - [ ] 11.3 Test FileUploadSlot renders error state with message
  - [ ] 11.4 Test FileUploadSection renders 4 upload slots with correct labels
  - [ ] 11.5 Test file input accepts only the correct format per slot

## Dev Notes

### This Is a Full-Stack Story

Backend: new module, migration, Polars parsing. Frontend: new components replacing placeholders. No GCS in this story (direct upload for MVP).

### Architecture Decision: Direct Upload vs GCS Signed URL

The architecture document specifies a GCS signed-URL upload flow for production (Cloud Run 32MB limit). However, for this story:

- **File size limit is 2MB** — well within Cloud Run's 32MB request limit
- **5 internal users** — no concurrency concerns
- **MVP scope** — GCS adds complexity (signed URLs, bucket setup, IAM)
- **Decision**: Use **direct multipart upload** to the backend for now. GCS can be added later if files exceed Cloud Run limits. The `parser.py` module is the same regardless of upload mechanism.

If GCS is needed later, the refactor is localized: change the upload router to generate signed URLs and add a process trigger endpoint. The parser module remains unchanged.

### Polars for Parsing

Polars is chosen over pandas per architecture (faster, no GIL). Key considerations:
- CSV: `pl.read_csv(BytesIO(file_bytes))`
- Excel: `pl.read_excel(BytesIO(file_bytes))` — requires `xlsx2csv` or `openpyxl` engine
- Mass Update Excel: headers start at row 3 — use `pl.read_excel(source, engine="calamine", read_options={"header_row": 2})`
- Polars Excel support may need additional dependency: add `fastexcel` (calamine-backed, recommended for Polars)

### JSONB Storage Format

Parsed data is stored as JSONB in `brand_uploads.parsed_data`. Format:
```json
{
  "columns": ["col1", "col2", ...],
  "data": [
    {"col1": "val1", "col2": "val2"},
    {"col1": "val3", "col2": "val4"}
  ],
  "row_count": 500
}
```

This preserves the parsed data for calculator consumption without re-parsing.

### File Type to Extension Mapping

| file_type | Extension | Parser |
|-----------|-----------|--------|
| `cpc_ad_report` | `.csv` | `pl.read_csv()` |
| `keyword_report` | `.csv` | `pl.read_csv()` |
| `order_export` | `.xlsx` | `pl.read_excel()` |
| `mass_update` | `.xlsx` | `pl.read_excel(header_row=2)` |

### Calculator Target Mapping

| file_type | calculator_target | Notes |
|-----------|-------------------|-------|
| `cpc_ad_report` | `ads_keyword` | Calculator 1, Sheet 1 |
| `keyword_report` | `ads_keyword` | Calculator 1, Sheet 2 |
| `order_export` | `top_sku,discount` | Shared by Calculator 2 & 3 |
| `mass_update` | `top_sku` | Calculator 2 only |

### What This Story Does NOT Do

1. **NO** GCS signed URL flow — direct upload for MVP
2. **NO** ZIP archive handling — single file uploads only (ZIP deferred)
3. **NO** calculator execution on upload — that is Story 3.7
4. **NO** clearing calculator_results on re-upload — calculator_results table doesn't exist yet (Story 3.4)
5. **NO** progress indicator via SSE — use simple HTTP response

### Existing Code to Modify

**EvaluationSections.tsx** — replace static file upload placeholder cards (Section 4, lines 110-136) with the new `FileUploadSection` component.

**main.py** — register upload router.

### Architecture Compliance

**Backend Pattern (MUST follow):**
- Module structure: `modules/upload/{__init__, router, schemas, service, parser}.py`
- Queries in: `db/queries/uploads.py`
- Migration in: `db/migrations/versions/007_create_brand_uploads_table.py`
- Router prefix: `/api/v1/upload`
- Use `Depends(get_current_user)` on all endpoints
- Use asyncpg parameterized SQL (`$1, $2`) — never string interpolation
- Use `raise AppException(...)` for structured errors — never bare HTTPException
- Exception chaining: always `raise ... from e`

**Frontend Pattern (MUST follow):**
- Components in `src/components/evaluation/` (existing feature directory)
- Hooks in `src/hooks/`
- API types in `src/services/apiClient.ts`
- Use TanStack Query for data fetching
- For multipart POST, use fetch with auth token (openapi-fetch doesn't handle multipart well)

### Column Validation Details

**CPC Ad Report CSV** — columns may have varying names. Required columns (check these exist, case-sensitive):
```
Nama Produk, Nama Iklan, Tipe Iklan, Penempatan, Tipe Biaya, Biaya
```

**Keyword Placement Report CSV** — required columns:
```
Kata Kunci Pencarian, Klik, Kunjungan, Pesanan, Pendapatan, Biaya Iklan, ROAS
```

**Order Export Excel** — required columns:
```
No. Pesanan, Nama Produk, Harga Awal, Harga Setelah Diskon, Jumlah,
Voucher Ditanggung Penjual, Paket Diskon, Nomor Referensi SKU,
Nama Variasi, Jumlah Produk di Pesan, Cashback Koin, Diskon dari Shopee
```

**Mass Update Excel** — headers at row 3 (0-indexed row 2). Required columns:
```
Kode Variasi, Nama Produk, Nama Variasi, SKU, Stok
```

### Previous Story Intelligence

**From Story 3.1:**
- Evaluation page exists at `/evaluation/:brandId`
- `EvaluationSections.tsx` has placeholder file upload cards (FILE_UPLOAD_SLOTS array)
- `useBrandDetail` and `useEvaluation` hooks exist
- shadcn components installed: Button, Input, Card, Badge, Table, Toast, Dialog, Progress
- Backend modules follow: `modules/{feature}/{router, schemas, service}.py`
- apiClient.ts uses openapi-fetch with auth middleware

**From lessons-learned.md:**
- Exception chaining: always `raise ... from e`
- ILIKE queries need `ESCAPE '\'` (not applicable here but keep in mind)
- Response schemas must match ACs field-by-field
- Frontend hooks must use apiClient.ts (except multipart POST)
- File List must include ALL changed files

### Code Review Lessons — Pre-Apply

- Exception chaining: always `raise ... from e`
- Validate file_type against a frozenset, not just string comparison
- Response schemas must match ACs field-by-field
- File upload endpoints need proper error handling for parse failures
- Use `from io import BytesIO` for in-memory file handling

### Testing Requirements

**Backend Tests (pytest):**

```
backend/tests/unit/test_parser.py                    — Polars parsing + column validation
backend/tests/integration/api/test_upload.py          — upload API endpoint tests
```

- Test CSV parsing with valid/invalid data
- Test Excel parsing with valid/invalid data
- Test Mass Update Excel with row 3 headers
- Test column validation for all 4 file types
- Test POST upload: valid file, wrong format, too large, missing columns, brand not found
- Test GET uploads: empty state, after upload
- Test upsert behavior (re-upload same file_type)
- Run: `cd backend && uv run python -m pytest -v`

**Frontend Tests (Vitest + @testing-library/react):**

```
frontend/src/components/evaluation/FileUploadSlot.test.tsx
frontend/src/components/evaluation/FileUploadSection.test.tsx
```

- Test FileUploadSlot renders empty/uploaded/error states
- Test FileUploadSection renders 4 slots with labels
- Test file input accept attribute matches slot format
- Run: `cd frontend && npx vitest run --reporter=verbose`

### Library & Framework Requirements

| Library | Version | Usage in This Story | Status |
|---------|---------|---------------------|--------|
| polars | latest | CSV and Excel parsing | **NEW — add to pyproject.toml** |
| fastexcel | latest | Polars Excel engine (calamine) | **NEW — add to pyproject.toml** |
| python-multipart | latest | FastAPI file upload support | **NEW — add to pyproject.toml** |
| fastapi UploadFile | existing | Multipart file handling | Installed |
| asyncpg | existing | Database queries | Installed |
| pydantic | existing | Request/response schemas | Installed |
| @tanstack/react-query | existing | Data fetching + mutations | Installed |
| shadcn/ui (Card, Button, Badge, Progress) | existing | Upload slot UI | Installed |
| lucide-react | existing | Icons (Upload, FileText, X, Check) | Installed |

### Project Structure Notes

**New files to create:**

```
backend/app/db/migrations/versions/007_create_brand_uploads_table.py
backend/app/db/queries/uploads.py
backend/app/modules/upload/__init__.py
backend/app/modules/upload/router.py
backend/app/modules/upload/schemas.py
backend/app/modules/upload/service.py
backend/app/modules/upload/parser.py
backend/tests/unit/test_parser.py
backend/tests/integration/api/test_upload.py
frontend/src/components/evaluation/FileUploadSlot.tsx
frontend/src/components/evaluation/FileUploadSlot.test.tsx
frontend/src/components/evaluation/FileUploadSection.tsx
frontend/src/components/evaluation/FileUploadSection.test.tsx
frontend/src/hooks/useUpload.ts
```

**Existing files to modify:**

```
backend/pyproject.toml                                ← MODIFY: add polars, fastexcel, python-multipart
backend/app/main.py                                   ← MODIFY: register upload router
backend/app/core/exceptions.py                        ← MODIFY: add UploadException
frontend/src/services/apiClient.ts                    ← MODIFY: add upload endpoint path types
frontend/src/components/evaluation/EvaluationSections.tsx ← MODIFY: replace file upload placeholders with FileUploadSection
```

### References

- [Source: _bmad-output/planning-artifacts/epics.md — Story 3.2 ACs]
- [Source: _bmad-output/planning-artifacts/architecture.md — Upload flow, module structure, file types]
- [Source: _bmad-output/planning-artifacts/sprint-change-proposal-2026-02-09.md — File type updates]
- [Source: _bmad-output/lessons-learned.md — Code review patterns]
- [Source: logic/calculator-1-kata-kunci-iklan-shopee.md — CPC Ad Report + Keyword Report column requirements]
- [Source: logic/calculator-2-penjualan.md — Order Export + Mass Update column requirements]
- [Source: logic/calculator-3-discount-checkup.md — Order Export column requirements]
