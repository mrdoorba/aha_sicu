# Story 3.2: Data File Upload and Parsing

Status: ready-for-dev

## Story

As a **BD team member**,
I want **to upload data files (CSV, Excel, and ZIP) for a brand's evaluation**,
so that **the system can parse and validate them for calculator processing**.

## Acceptance Criteria

1. **File upload slots displayed on evaluation page**
   **Given** I am on the evaluation page for a brand
   **When** I view the File Upload section (Step 4)
   **Then** I see 4 distinct upload slots:
     1. **CPC Ad Report** — accepts `.csv` (for Calculator 1 Sheet 1)
     2. **Keyword Placement Report** — accepts `.csv` (for Calculator 1 Sheet 2)
     3. **Order Export** — accepts `.xlsx`, `.zip` (for Calculators 2 & 3)
     4. **Mass Update / Sales Info** — accepts `.xlsx`, `.zip` (for Calculator 2)
   **And** each slot shows its accepted format, calculator routing label, and current status (empty / uploading / uploaded / error)

2. **Upload a file via GCS signed URL**
   **Given** I select a file for any upload slot
   **When** I initiate the upload
   **Then** the frontend requests a signed URL from `POST /api/v1/upload/signed-url`
   **And** the frontend uploads the file directly to GCS using the signed URL (bypasses Cloud Run size limits)
   **And** I see a progress indicator during upload
   **And** the frontend triggers processing via `POST /api/v1/upload/process`
   **And** the backend downloads the file from GCS, parses it, validates columns, stores parsed data, and deletes the file from GCS
   **And** on success I see "File uploaded successfully" with filename displayed
   **And** the slot status changes to "uploaded"

3. **Per-calculator column validation**
   **Given** a file is uploaded and processing is triggered
   **When** the backend parses the file with Polars
   **Then** validate required columns based on file type:
     - **CPC Ad Report**: requires columns including Nama Produk, Nama Iklan, Tipe Iklan, Penempatan, Tipe Biaya, Biaya
     - **Keyword Report**: requires columns including Kata Kunci Pencarian, Klik, Kunjungan, Pesanan, Pendapatan, Biaya Iklan, ROAS
     - **Order Export**: requires columns including No. Pesanan, Nama Produk, Harga Awal, Harga Setelah Diskon, Jumlah, Voucher Ditanggung Penjual, Paket Diskon, Nomor Referensi SKU, Nama Variasi, Jumlah Produk di Pesan, Cashback Koin, Diskon dari Shopee
     - **Mass Update**: requires columns including Kode Variasi, Nama Produk, Nama Variasi, SKU, Stok (note: headers start at row 3)

4. **ZIP archive handling**
   **Given** I upload a `.zip` file to the Order Export or Mass Update slot
   **When** the backend processes the ZIP
   **Then** extract all Excel files (`.xlsx`, `.xls`), filtering out `__MACOSX` and temp files
   **And** sort by part number (extract "part X of Y" pattern from filenames)
   **And** parse each Excel part with Polars and concatenate vertically into a single DataFrame
   **And** validate the merged DataFrame has required columns
   **And** if ZIP contains no Excel files, return error with `UPLOAD_ZIP_NO_EXCEL`
   **And** if Excel parts have different column structures, return error with `UPLOAD_ZIP_STRUCTURE_MISMATCH`

5. **Upload validation errors**
   **Given** I upload an invalid file
   **When** validation fails
   **Then** return error with appropriate code:
     - `UPLOAD_INVALID_FORMAT` — wrong file extension for the slot
     - `UPLOAD_PARSE_FAILED` — file is corrupted or cannot be parsed
     - `UPLOAD_MISSING_COLUMNS` — required columns for the target calculator are missing (detail lists which columns)
     - `UPLOAD_ZIP_NO_EXCEL` — ZIP contains no Excel files
     - `UPLOAD_ZIP_STRUCTURE_MISMATCH` — Excel parts inside ZIP have different columns
     - `UPLOAD_SIGNED_URL_EXPIRED` — signed URL validity (15 min) exceeded
     - `UPLOAD_PROCESSING_FAILED` — general processing error
   **And** I see a user-friendly error message specifying what's wrong
   **And** the previous file for that slot (if any) remains unchanged

6. **Re-upload (upsert per file type)**
   **Given** I upload a new file to a slot that already has one
   **When** the upload succeeds
   **Then** the new file replaces the old one for that file type (upsert per brand_id + file_type)
   **And** calculator results that depend on this file type are cleared (set to NULL — actual re-run is Story 3.7)
   **And** the slot shows the new filename and upload timestamp

7. **View uploaded files state**
   **Given** I navigate to an evaluation page for a brand
   **When** the page loads
   **Then** I see the current upload state for each slot:
     - Slots with uploaded files show: filename, upload timestamp, row count
     - Slots without files show: "No file uploaded" with upload button
   **And** the data persists across page refreshes

8. **API: Request signed upload URL**
   **Given** I send `POST /api/v1/upload/signed-url`
   **When** authenticated with body:
   ```json
   {
     "filename": "export.zip",
     "content_type": "application/zip",
     "file_type": "order_export",
     "brand_id": 123
   }
   ```
   **Then** validate file_type and brand_id exist
   **And** generate a GCS signed URL (15 min expiry) for the `aha_sicu_uploads` bucket
   **And** return:
   ```json
   {
     "upload_url": "https://storage.googleapis.com/...",
     "upload_id": "uuid-string",
     "expires_at": "2026-02-11T10:45:00Z"
   }
   ```

9. **API: Trigger file processing**
   **Given** I send `POST /api/v1/upload/process`
   **When** authenticated with body:
   ```json
   {
     "upload_id": "uuid-string",
     "brand_id": 123,
     "file_type": "order_export"
   }
   ```
   **Then** download the file from GCS
   **And** detect file type (CSV, Excel, or ZIP)
   **And** if ZIP: extract, sort parts, merge into single DataFrame
   **And** if CSV/Excel: parse directly with Polars
   **And** validate per-calculator column schema
   **And** store parsed data in `brand_uploads` table (upsert by brand_id + file_type)
   **And** delete the file from GCS
   **And** return:
   ```json
   {
     "id": 1,
     "brand_id": 123,
     "file_type": "order_export",
     "filename": "export.zip",
     "file_size": 5242880,
     "row_count": 2500,
     "uploaded_at": "2026-02-11T10:30:00Z"
   }
   ```

10. **API: Get upload status for a brand**
    **Given** I request `GET /api/v1/upload/brands/{brand_id}`
    **When** authenticated
    **Then** return all uploaded files for the brand:
    ```json
    {
      "brand_id": 123,
      "uploads": [
        {
          "id": 1,
          "file_type": "order_export",
          "filename": "export.zip",
          "file_size": 5242880,
          "row_count": 2500,
          "uploaded_at": "2026-02-11T10:30:00Z"
        }
      ]
    }
    ```
    **And** slots without uploads are simply not in the array

## Tasks / Subtasks

- [ ] Task 1: Add backend dependencies (AC: #2, #3, #4)
  - [ ] 1.1 Add `polars` to `backend/pyproject.toml` dependencies
  - [ ] 1.2 Add `fastexcel` to `backend/pyproject.toml` dependencies (calamine-backed Excel engine for Polars)
  - [ ] 1.3 Add `python-multipart` to `backend/pyproject.toml` dependencies (FastAPI file handling)
  - [ ] 1.4 Add `google-cloud-storage` to `backend/pyproject.toml` dependencies (GCS signed URLs + file ops)
  - [ ] 1.5 Run `uv sync` to install

- [ ] Task 2: Create database migration for `brand_uploads` table (AC: #6, #7, #9, #10)
  - [ ] 2.1 Create migration `007_create_brand_uploads_table.py` in `backend/app/db/migrations/versions/`
  - [ ] 2.2 Table schema:
    - `id` SERIAL PRIMARY KEY
    - `brand_id` INTEGER NOT NULL REFERENCES brand_vp_data(id)
    - `file_type` VARCHAR(50) NOT NULL — one of: `cpc_ad_report`, `keyword_report`, `order_export`, `mass_update`
    - `calculator_target` VARCHAR(100) NOT NULL — which calculator(s) this feeds
    - `filename` VARCHAR(255) NOT NULL
    - `file_size` INTEGER NOT NULL
    - `row_count` INTEGER
    - `parsed_data` JSONB NOT NULL (extracted data from Polars)
    - `uploaded_by` INTEGER NOT NULL REFERENCES users(id)
    - `uploaded_at` TIMESTAMPTZ DEFAULT NOW()
    - UNIQUE(brand_id, file_type) — one file per type per brand
  - [ ] 2.3 Add indexes: `idx_brand_uploads_brand_id`, `idx_brand_uploads_file_type`

- [ ] Task 3: Create upload query functions (AC: #9, #10)
  - [ ] 3.1 Create `backend/app/db/queries/uploads.py` with:
    - `get_uploads_by_brand(conn, brand_id)` — returns all uploads for a brand
    - `get_upload_by_type(conn, brand_id, file_type)` — returns single upload or None
    - `upsert_upload(conn, brand_id, file_type, calculator_target, filename, file_size, row_count, parsed_data, uploaded_by)` — INSERT ON CONFLICT(brand_id, file_type) DO UPDATE
    - `delete_upload(conn, brand_id, file_type)` — for cleanup if needed

- [ ] Task 4: Create GCS client module (AC: #2, #8, #9)
  - [ ] 4.1 Create `backend/app/modules/upload/gcs_client.py`:
    - `generate_signed_upload_url(bucket, object_name, content_type, expiry_minutes=15)` → signed URL string
    - `download_file(bucket, object_name)` → bytes
    - `delete_file(bucket, object_name)` → None
    - Use `google-cloud-storage` library
    - Object naming convention: `uploads/{upload_id}/{filename}`
  - [ ] 4.2 Add GCS config to `config.py`:
    - `gcs_upload_bucket: str = "aha_sicu_uploads"`
    - `gcs_credentials_path: str | None = None` (reuse service account or application default credentials)
  - [ ] 4.3 For local dev without GCS: implement a `LocalStorageClient` fallback that saves to a temp directory. Service layer picks client based on config.

- [ ] Task 5: Create file parser module (AC: #3, #4, #5)
  - [ ] 5.1 Create `backend/app/modules/upload/__init__.py`
  - [ ] 5.2 Create `backend/app/modules/upload/parser.py`:
    - `parse_csv(file_bytes)` → `pl.DataFrame`
    - `parse_excel(file_bytes, header_row=0)` → `pl.DataFrame` — Mass Update uses `header_row=2`
    - `validate_columns(df, file_type)` → raises `AppException` with `UPLOAD_MISSING_COLUMNS` if required columns missing
    - `dataframe_to_json(df)` → serializable dict for JSONB storage
    - Column requirements defined as constants per file_type
  - [ ] 5.3 Create `backend/app/modules/upload/zip_handler.py`:
    - `process_zip(zip_bytes, file_type)` → `pl.DataFrame`
    - Extract Excel files, filter out `__MACOSX` and temp files
    - Sort by part number (extract "part X of Y" pattern)
    - Parse each part with Polars, concatenate vertically
    - Validate all parts have the same columns — raise `UPLOAD_ZIP_STRUCTURE_MISMATCH` if not
    - Raise `UPLOAD_ZIP_NO_EXCEL` if no Excel files found in ZIP

- [ ] Task 6: Create upload service (AC: #2, #3, #4, #5, #6, #8, #9, #10)
  - [ ] 6.1 Create `backend/app/modules/upload/service.py`:
    - `request_signed_url(brand_id, file_type, filename, content_type)` — validates brand + file_type, generates signed URL via GCS client, stores upload_id mapping, returns URL + upload_id
    - `process_upload(upload_id, brand_id, file_type, user_id)` — downloads from GCS → detects file type → parses (CSV/Excel/ZIP) → validates columns → stores parsed data → deletes from GCS → returns response
    - `get_brand_uploads(brand_id)` — returns all uploads for a brand
    - Validate `file_type` is one of allowed values (`_VALID_FILE_TYPES` frozenset)
    - Validate file extension matches expected format for file_type
  - [ ] 6.2 Create `backend/app/modules/upload/schemas.py`:
    - `SignedUrlRequest`: filename, content_type, file_type, brand_id
    - `SignedUrlResponse`: upload_url, upload_id, expires_at
    - `ProcessRequest`: upload_id, brand_id, file_type
    - `UploadResponse`: id, brand_id, file_type, filename, file_size, row_count, uploaded_at
    - `BrandUploadsResponse`: brand_id, uploads (list of UploadResponse)

- [ ] Task 7: Create upload router (AC: #8, #9, #10)
  - [ ] 7.1 Create `backend/app/modules/upload/router.py`:
    - `POST /api/v1/upload/signed-url` — generates signed upload URL
    - `POST /api/v1/upload/process` — triggers file processing after GCS upload
    - `GET /api/v1/upload/brands/{brand_id}` — returns all uploads for brand
  - [ ] 7.2 Register upload router in `main.py`
  - [ ] 7.3 Use `Depends(get_current_user)` on all endpoints

- [ ] Task 8: Add `UploadException` to exceptions (AC: #5)
  - [ ] 8.1 Add `UploadException` class to `core/exceptions.py` (like SyncException pattern)

- [ ] Task 9: Add frontend API types and hooks (AC: #1, #2, #7, #8, #9, #10)
  - [ ] 9.1 Add upload endpoint path types to `apiClient.ts`:
    - `POST /api/v1/upload/signed-url`
    - `POST /api/v1/upload/process`
    - `GET /api/v1/upload/brands/{brand_id}`
  - [ ] 9.2 Create `hooks/useUpload.ts`:
    - `useBrandUploads(brandId)` — TanStack Query for GET upload status
    - `useRequestSignedUrl()` — mutation for POST signed-url
    - `useProcessUpload()` — mutation for POST process
    - `useUploadFile(brandId)` — orchestration hook that:
      1. Requests signed URL
      2. Uploads file directly to GCS via `fetch(PUT signedUrl, { body: file })`
      3. Triggers processing
      4. Invalidates `brandUploads` query on success
      5. Tracks progress via XHR `upload.onprogress`

- [ ] Task 10: Build file upload components (AC: #1, #2, #4, #5, #6, #7)
  - [ ] 10.1 Create `components/evaluation/FileUploadSlot.tsx`:
    - Single file slot component with: label, accepted format(s), calculator routing info
    - States: empty (upload button), uploading (progress bar), uploaded (filename + timestamp + row count + re-upload), error (message + retry)
    - File input accepts only the allowed formats for the slot (`.csv` or `.xlsx,.zip`)
    - Shows row count after successful processing
  - [ ] 10.2 Create `components/evaluation/FileUploadSection.tsx`:
    - Renders 4 `FileUploadSlot` components in a grid
    - Uses `useBrandUploads` to fetch current upload state
    - Passes `useUploadFile` orchestration to each slot
  - [ ] 10.3 Update `EvaluationSections.tsx` Section 4 to use `FileUploadSection` instead of static placeholder cards

- [ ] Task 11: Write backend tests (AC: #2, #3, #4, #5, #6, #8, #9, #10)
  - [ ] 11.1 Unit test `parser.py`: CSV parsing, Excel parsing, column validation success/failure, Mass Update header row 3 handling
  - [ ] 11.2 Unit test `zip_handler.py`: extract + merge multi-part Excel, filter __MACOSX, sort by part number, mismatch columns error, no Excel error
  - [ ] 11.3 Integration test `POST /api/v1/upload/signed-url`:
    - Valid request → 200 with signed URL
    - Invalid file_type → 400
    - Non-existent brand → 404
  - [ ] 11.4 Integration test `POST /api/v1/upload/process`:
    - Valid CSV → 200 with response (mock GCS download)
    - Valid Excel → 200 with response
    - Valid ZIP → 200 with merged data
    - Missing columns → 400 with UPLOAD_MISSING_COLUMNS
    - Bad ZIP → 400 with UPLOAD_ZIP_NO_EXCEL
    - Re-upload same file_type → 200, replaces old data
  - [ ] 11.5 Integration test `GET /api/v1/upload/brands/{brand_id}`:
    - Empty uploads → 200 with empty array
    - After upload → 200 with uploads

- [ ] Task 12: Write frontend tests (AC: #1, #2, #5, #7)
  - [ ] 12.1 Test FileUploadSlot renders empty state with upload button
  - [ ] 12.2 Test FileUploadSlot renders uploaded state with filename, timestamp, row count
  - [ ] 12.3 Test FileUploadSlot renders error state with message
  - [ ] 12.4 Test FileUploadSlot renders uploading state with progress
  - [ ] 12.5 Test FileUploadSection renders 4 upload slots with correct labels
  - [ ] 12.6 Test file input accept attribute matches slot formats (csv for CSV slots, xlsx+zip for Excel slots)

## Dev Notes

### This Is a Full-Stack Story

Backend: new module, migration, GCS integration, Polars parsing, ZIP handling. Frontend: new components replacing placeholders, GCS direct upload flow.

### GCS Signed URL Upload Flow

Per architecture, GCS signed URLs are **required** — Seller Center exports can reach 100MB+ as ZIP archives containing multiple Excel parts, exceeding Cloud Run's 32MB request body limit. The upload flow:

```
Frontend                    GCS                         Backend
   │                         │                            │
   ├─ POST /signed-url ──────┼────────────────────────────►│ generate URL
   │◄─ { upload_url } ───────┼────────────────────────────┤
   │                         │                            │
   ├─ PUT upload_url ────────►│ store file                 │
   │◄─ 200 OK ───────────────┤                            │
   │                         │                            │
   ├─ POST /process ─────────┼────────────────────────────►│ download → parse
   │                         │◄── download ───────────────┤ → validate → store
   │                         │◄── delete ─────────────────┤ → cleanup
   │◄─ { result } ───────────┼────────────────────────────┤
```

**GCS bucket**: `aha_sicu_uploads` in `asia-southeast1`, auto-delete after 24h, private access.

**Local dev fallback**: When GCS is not configured (`gcs_upload_bucket` is empty), use a `LocalStorageClient` that writes to a local temp directory. This avoids requiring GCS setup for local development. The service layer selects the storage client based on config.

### ZIP Archive Handling

Seller Center exports large datasets as ZIP archives containing multiple Excel parts:
```
seller_export.zip
├── data_part_1_of_3.xlsx
├── data_part_2_of_3.xlsx
└── data_part_3_of_3.xlsx
```

Processing pipeline:
1. Extract all `.xlsx`/`.xls` files, filter out `__MACOSX` and temp files
2. Sort by part number (regex: `part_?(\d+)_of_(\d+)`)
3. Parse each part with Polars
4. Validate all parts have identical columns → `UPLOAD_ZIP_STRUCTURE_MISMATCH` if not
5. Vertically concatenate into a single DataFrame
6. Validate merged result has required columns per file_type

ZIP is accepted for **Order Export** and **Mass Update** slots (the Excel-based ones). CSV slots do not accept ZIP.

### Polars for Parsing

Polars is chosen over pandas per architecture (faster, no GIL). Key considerations:
- CSV: `pl.read_csv(BytesIO(file_bytes))`
- Excel: `pl.read_excel(BytesIO(file_bytes), engine="calamine")` — uses `fastexcel` (calamine-backed)
- Mass Update Excel: headers start at row 3 — use `pl.read_excel(source, engine="calamine", read_options={"header_row": 2})`
- ZIP: extract parts → parse each → `pl.concat(dfs)`

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

| file_type | Accepted Extensions | Parser |
|-----------|---------------------|--------|
| `cpc_ad_report` | `.csv` | `pl.read_csv()` |
| `keyword_report` | `.csv` | `pl.read_csv()` |
| `order_export` | `.xlsx`, `.zip` | `pl.read_excel()` or `process_zip()` |
| `mass_update` | `.xlsx`, `.zip` | `pl.read_excel(header_row=2)` or `process_zip()` |

### Calculator Target Mapping

| file_type | calculator_target | Notes |
|-----------|-------------------|-------|
| `cpc_ad_report` | `ads_keyword` | Calculator 1, Sheet 1 |
| `keyword_report` | `ads_keyword` | Calculator 1, Sheet 2 |
| `order_export` | `top_sku,discount` | Shared by Calculator 2 & 3 |
| `mass_update` | `top_sku` | Calculator 2 only |

### Upload ID Tracking

The `upload_id` is a UUID generated when the signed URL is requested. It serves as the object name prefix in GCS (`uploads/{upload_id}/{filename}`) and correlates the signed URL request with the processing trigger. Store in an in-memory dict or lightweight DB record — it only needs to survive the 15-min upload window.

Recommendation: use an in-memory dict (`_pending_uploads: dict[str, PendingUpload]`) in the service module. On Cloud Run with a single instance this is sufficient. If this becomes unreliable at scale, migrate to a Redis or DB-backed store.

### What This Story Does NOT Do

1. **NO** calculator execution on upload — that is Story 3.7
2. **NO** clearing `calculator_results` on re-upload — `calculator_results` table doesn't exist yet (Story 3.4)
3. **NO** SSE broadcast after upload — deferred to Story 3.7 orchestration

### Existing Code to Modify

**EvaluationSections.tsx** — replace static file upload placeholder cards (Section 4, lines 110-136) with the new `FileUploadSection` component.

**main.py** — register upload router.

**config.py** — add GCS bucket config.

### Architecture Compliance

**Backend Pattern (MUST follow):**
- Module structure: `modules/upload/{__init__, router, schemas, service, parser, zip_handler, gcs_client}.py`
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
- Use TanStack Query for data fetching (GET upload status)
- GCS direct upload uses raw `fetch(PUT)` — not through apiClient
- Process trigger uses apiClient POST

### Column Validation Details

**CPC Ad Report CSV** — required columns (case-sensitive):
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
- ILIKE queries need `ESCAPE '\'` (not applicable here)
- Response schemas must match ACs field-by-field
- Frontend hooks must use apiClient.ts (except GCS direct upload)
- File List must include ALL changed files

### Code Review Lessons — Pre-Apply

- Exception chaining: always `raise ... from e`
- Validate file_type against a frozenset, not just string comparison
- Response schemas must match ACs field-by-field
- File upload/processing needs proper error handling for parse failures
- Use `from io import BytesIO` for in-memory file handling
- Network/external service errors (GCS) must have broad `except Exception` with logging fallback

### Testing Requirements

**Backend Tests (pytest):**

```
backend/tests/unit/test_parser.py                    — Polars parsing + column validation
backend/tests/unit/test_zip_handler.py               — ZIP extract + merge
backend/tests/integration/api/test_upload.py          — upload API endpoint tests
```

- Test CSV parsing with valid/invalid data
- Test Excel parsing with valid/invalid data
- Test Mass Update Excel with row 3 headers
- Test column validation for all 4 file types
- Test ZIP extraction: multi-part merge, __MACOSX filter, sort by part, mismatch error, no-Excel error
- Test POST signed-url: valid request, invalid file_type, non-existent brand
- Test POST process: valid CSV, valid Excel, valid ZIP, missing columns, bad ZIP (mock GCS)
- Test GET uploads: empty state, after upload
- Test upsert behavior (re-upload same file_type)
- Run: `cd backend && uv run python -m pytest -v`

**Frontend Tests (Vitest + @testing-library/react):**

```
frontend/src/components/evaluation/FileUploadSlot.test.tsx
frontend/src/components/evaluation/FileUploadSection.test.tsx
```

- Test FileUploadSlot renders empty/uploading/uploaded/error states
- Test FileUploadSection renders 4 slots with labels
- Test file input accept attribute matches slot formats
- Run: `cd frontend && npx vitest run --reporter=verbose`

### Library & Framework Requirements

| Library | Version | Usage in This Story | Status |
|---------|---------|---------------------|--------|
| polars | latest | CSV and Excel parsing | **NEW — add to pyproject.toml** |
| fastexcel | latest | Polars Excel engine (calamine) | **NEW — add to pyproject.toml** |
| python-multipart | latest | FastAPI file handling | **NEW — add to pyproject.toml** |
| google-cloud-storage | latest | GCS signed URLs, download, delete | **NEW — add to pyproject.toml** |
| asyncpg | existing | Database queries | Installed |
| pydantic | existing | Request/response schemas | Installed |
| @tanstack/react-query | existing | Data fetching + mutations | Installed |
| shadcn/ui (Card, Button, Badge, Progress) | existing | Upload slot UI | Installed |
| lucide-react | existing | Icons (Upload, FileText, X, Check, Loader2) | Installed |

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
backend/app/modules/upload/zip_handler.py
backend/app/modules/upload/gcs_client.py
backend/tests/unit/test_parser.py
backend/tests/unit/test_zip_handler.py
backend/tests/integration/api/test_upload.py
frontend/src/components/evaluation/FileUploadSlot.tsx
frontend/src/components/evaluation/FileUploadSlot.test.tsx
frontend/src/components/evaluation/FileUploadSection.tsx
frontend/src/components/evaluation/FileUploadSection.test.tsx
frontend/src/hooks/useUpload.ts
```

**Existing files to modify:**

```
backend/pyproject.toml                                ← MODIFY: add polars, fastexcel, python-multipart, google-cloud-storage
backend/app/main.py                                   ← MODIFY: register upload router
backend/app/config.py                                 ← MODIFY: add GCS bucket config
backend/app/core/exceptions.py                        ← MODIFY: add UploadException
frontend/src/services/apiClient.ts                    ← MODIFY: add upload endpoint path types
frontend/src/components/evaluation/EvaluationSections.tsx ← MODIFY: replace file upload placeholders with FileUploadSection
```

### References

- [Source: _bmad-output/planning-artifacts/epics.md — Story 3.2 ACs]
- [Source: _bmad-output/planning-artifacts/architecture.md — GCS upload flow, ZIP handler, module structure, file types]
- [Source: _bmad-output/planning-artifacts/sprint-change-proposal-2026-02-09.md — File type updates]
- [Source: _bmad-output/lessons-learned.md — Code review patterns]
- [Source: logic/calculator-1-kata-kunci-iklan-shopee.md — CPC Ad Report + Keyword Report column requirements]
- [Source: logic/calculator-2-penjualan.md — Order Export + Mass Update column requirements]
- [Source: logic/calculator-3-discount-checkup.md — Order Export column requirements]
