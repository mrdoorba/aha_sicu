# API Reference

Complete reference for all REST API endpoints in the Store ICU (AHA SICU) backend. Endpoints are grouped by module.

**Base URL:** `/api/v1` (except `/health`)

**Authentication:** All endpoints except `/health` require a Bearer token in the `Authorization` header. The backend accepts Firebase ID tokens (human users) and Google OIDC tokens (service accounts such as Cloud Scheduler). On first Firebase login, the user is auto-provisioned in the database.

**Roles:** `member`, `leader`, `admin` (plus synthetic `scheduler` for OIDC service accounts). Role checks return `403` with code `RULE_ACCESS_DENIED` on failure.

---

## Table of Contents

1. [Health](#health)
2. [Auth](#auth)
3. [Accounts](#accounts)
4. [Brands](#brands)
5. [Evaluations](#evaluations)
6. [Calculators](#calculators)
7. [Upload](#upload)
8. [Rules](#rules)
9. [Sync](#sync)
10. [Email](#email)

---

## Health

| Method | Path | Auth | Roles |
|--------|------|------|-------|
| GET | `/health` | None | Any |

### GET /health

Health check endpoint used by Cloud Run.

**Response `200`**

```json
{
  "status": "healthy"
}
```

---

## Auth

| Method | Path | Auth | Roles |
|--------|------|------|-------|
| GET | `/api/v1/me` | Required | Any |

### GET /api/v1/me

Return the currently authenticated user's profile.

**Response `200` -- `UserResponse`**

| Field | Type | Description |
|-------|------|-------------|
| `id` | `int` | Internal user ID |
| `email` | `string` | User email |
| `role` | `string` | One of `member`, `leader`, `admin` |
| `last_login` | `datetime \| null` | Timestamp of last login |

---

## Accounts

All endpoints in this module require the `admin` role. An admin cannot target their own account for role changes, password resets, or deletion (returns `409` with code `ACCOUNT_SELF_ACTION`).

| Method | Path | Auth | Roles | Description |
|--------|------|------|-------|-------------|
| GET | `/api/v1/accounts` | Required | admin | List all accounts |
| POST | `/api/v1/accounts` | Required | admin | Create account |
| PATCH | `/api/v1/accounts/{user_id}/role` | Required | admin | Update role |
| POST | `/api/v1/accounts/{user_id}/reset-password` | Required | admin | Reset password |
| DELETE | `/api/v1/accounts/{user_id}` | Required | admin | Delete account |

### GET /api/v1/accounts

List all user accounts.

**Response `200` -- `UserListResponse[]`**

| Field | Type | Description |
|-------|------|-------------|
| `id` | `int` | User ID |
| `email` | `string` | Email address |
| `role` | `string` | `member`, `leader`, or `admin` |
| `created_at` | `datetime` | Account creation timestamp |
| `last_login` | `datetime \| null` | Last login timestamp |

### POST /api/v1/accounts

Create a new user account (provisions both Firebase Auth and database record).

**Request body -- `CreateAccountRequest`**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `email` | `string` | Yes | -- | Email address |
| `password` | `string` | Yes | -- | Password (min 6 characters) |
| `role` | `string` | No | `"member"` | One of `member`, `leader`, `admin` |

**Response `201` -- `UserListResponse`**

Same shape as the list response item above.

### PATCH /api/v1/accounts/{user_id}/role

Update a user's role.

**Path parameters**

| Param | Type | Description |
|-------|------|-------------|
| `user_id` | `int` | Target user ID |

**Request body -- `UpdateRoleRequest`**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `role` | `string` | Yes | One of `member`, `leader`, `admin` |

**Response `200` -- `UserListResponse`**

**Side effects:** Cannot target own account (`409`).

### POST /api/v1/accounts/{user_id}/reset-password

Reset a user's password.

**Path parameters**

| Param | Type | Description |
|-------|------|-------------|
| `user_id` | `int` | Target user ID |

**Request body -- `ResetPasswordRequest`**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `password` | `string` | Yes | New password (min 6 characters) |

**Response `204` -- No Content**

**Side effects:** Cannot target own account (`409`).

### DELETE /api/v1/accounts/{user_id}

Delete a user account.

**Path parameters**

| Param | Type | Description |
|-------|------|-------------|
| `user_id` | `int` | Target user ID |

**Response `204` -- No Content**

**Side effects:** Cannot target own account (`409`). Deletes both the database record and the Firebase Auth user.

---

## Brands

All endpoints require authentication. Any authenticated role can access.

| Method | Path | Auth | Roles | Description |
|--------|------|------|-------|-------------|
| GET | `/api/v1/brands` | Required | Any | Paginated brand list |
| GET | `/api/v1/brands/{brand_id}` | Required | Any | Single brand detail |

### GET /api/v1/brands

Get a paginated list of brands with optional search. Returns brands from VP data enriched with Meeting data when available.

**Query parameters**

| Param | Type | Default | Constraints | Description |
|-------|------|---------|-------------|-------------|
| `page` | `int` | `1` | >= 1 | Page number |
| `limit` | `int` | `20` | 1--100 | Items per page |
| `search` | `string \| null` | `null` | max 200 chars | Case-insensitive brand name search |

**Response `200` -- `BrandListResponse`**

| Field | Type | Description |
|-------|------|-------------|
| `items` | `BrandListItem[]` | List of brands |
| `total` | `int` | Total matching brands |
| `page` | `int` | Current page |
| `limit` | `int` | Items per page |
| `pages` | `int` | Total pages |

**`BrandListItem` fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | `int` | Brand ID |
| `brand_name` | `string` | Brand name |
| `raw_data` | `object` | Full VP spreadsheet row as JSON |
| `updated_at` | `datetime` | Last sync timestamp |
| `meeting_raw_data` | `object \| null` | Meeting spreadsheet row as JSON (if available) |

### GET /api/v1/brands/{brand_id}

Get a single brand by ID with meeting data enrichment.

**Path parameters**

| Param | Type | Description |
|-------|------|-------------|
| `brand_id` | `int` | Brand ID |

**Response `200` -- `BrandDetailResponse`**

| Field | Type | Description |
|-------|------|-------------|
| `id` | `int` | Brand ID |
| `brand_name` | `string` | Brand name |
| `raw_data` | `object` | Full VP spreadsheet row as JSON |
| `updated_at` | `datetime` | Last sync timestamp |
| `meeting_raw_data` | `object \| null` | Meeting spreadsheet row as JSON |

**Errors:** `404` if brand not found.

---

## Evaluations

All endpoints require authentication unless otherwise noted. The delete endpoint requires `leader` or `admin` role.

| Method | Path | Auth | Roles | Description |
|--------|------|------|-------|-------------|
| GET | `/api/v1/evaluations` | Required | Any | Paginated evaluation list |
| GET | `/api/v1/evaluations/grouped` | Required | Any | Evaluations grouped by brand |
| GET | `/api/v1/evaluations/grouped/{brand_id}` | Required | Any | Evaluations for a specific brand |
| DELETE | `/api/v1/evaluations/{evaluation_id}` | Required | leader, admin | Delete evaluation |
| GET | `/api/v1/evaluations/{evaluation_id}` | Required | Any | Full evaluation detail |
| GET | `/api/v1/evaluations/brands/{brand_id}` | Required | Any | Get evaluation inputs state |
| PUT | `/api/v1/evaluations/brands/{brand_id}` | Required | Any | Save evaluation inputs |
| POST | `/api/v1/evaluations/brands/{brand_id}/score` | Required | Any | Generate final score |
| POST | `/api/v1/evaluations/brands/{brand_id}/save` | Required | Any | Save completed evaluation |

### GET /api/v1/evaluations

List all evaluations with pagination, sorting, and filtering.

**Query parameters**

| Param | Type | Default | Constraints | Description |
|-------|------|---------|-------------|-------------|
| `page` | `int` | `1` | >= 1 | Page number |
| `limit` | `int` | `20` | 1--100 | Items per page |
| `sort_by` | `string` | `"created_at"` | `created_at` or `final_score` | Sort field |
| `sort_order` | `string` | `"desc"` | `asc` or `desc` | Sort direction |
| `search` | `string \| null` | `null` | max 200 chars | Filter by brand name |
| `date_from` | `date \| null` | `null` | -- | Start date filter (inclusive) |
| `date_to` | `date \| null` | `null` | -- | End date filter (inclusive) |

**Response `200` -- `EvaluationListResponse`**

| Field | Type | Description |
|-------|------|-------------|
| `items` | `EvaluationListItem[]` | Evaluation records |
| `total` | `int` | Total matching evaluations |
| `page` | `int` | Current page |
| `limit` | `int` | Items per page |
| `pages` | `int` | Total pages |

**`EvaluationListItem` fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | `int` | Evaluation ID |
| `brand_name` | `string` | Brand name |
| `final_score` | `float` | Final computed score |
| `verdict` | `string` | Evaluation verdict |
| `template` | `string` | Template used (`fashion` or `non_fashion`) |
| `evaluator_email` | `string` | Email of the user who created the evaluation |
| `created_at` | `datetime` | Creation timestamp |
| `period` | `string` | Evaluation period label |

### GET /api/v1/evaluations/grouped

List evaluations grouped by brand (one row per brand) with pagination.

**Query parameters**

| Param | Type | Default | Constraints | Description |
|-------|------|---------|-------------|-------------|
| `page` | `int` | `1` | >= 1 | Page number |
| `limit` | `int` | `20` | 1--100 | Items per page |
| `search` | `string \| null` | `null` | max 200 chars | Filter by brand name |
| `date_from` | `date \| null` | `null` | -- | Start date filter |
| `date_to` | `date \| null` | `null` | -- | End date filter |

**Response `200` -- `GroupedEvaluationListResponse`**

| Field | Type | Description |
|-------|------|-------------|
| `items` | `GroupedEvaluationItem[]` | Brand-level summaries |
| `total` | `int` | Total brands with evaluations |
| `page` | `int` | Current page |
| `limit` | `int` | Items per page |
| `pages` | `int` | Total pages |

**`GroupedEvaluationItem` fields:**

| Field | Type | Description |
|-------|------|-------------|
| `brand_id` | `int` | Brand ID |
| `brand_name` | `string` | Brand name |
| `evaluation_count` | `int` | Number of evaluations for this brand |
| `top_score` | `float` | Highest score among evaluations |
| `top_verdict` | `string` | Verdict corresponding to the top score |
| `latest_date` | `datetime` | Most recent evaluation date |

### GET /api/v1/evaluations/grouped/{brand_id}

List individual evaluations for a specific brand, sorted by date descending.

**Path parameters**

| Param | Type | Description |
|-------|------|-------------|
| `brand_id` | `int` | Brand ID |

**Query parameters**

| Param | Type | Default | Constraints | Description |
|-------|------|---------|-------------|-------------|
| `limit` | `int \| null` | `null` | 1--1000 | Max items to return (for accordion expand) |
| `date_from` | `date \| null` | `null` | -- | Start date filter |
| `date_to` | `date \| null` | `null` | -- | End date filter |

**Response `200` -- `BrandEvaluationListResponse`**

| Field | Type | Description |
|-------|------|-------------|
| `items` | `BrandEvaluationItem[]` | Evaluations for this brand |
| `total` | `int` | Total evaluations for this brand |

**`BrandEvaluationItem` fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | `int` | Evaluation ID |
| `final_score` | `float` | Final score |
| `verdict` | `string` | Verdict |
| `template` | `string` | Template used |
| `evaluator_email` | `string` | Evaluator email |
| `created_at` | `datetime` | Creation timestamp |
| `period` | `string` | Period label |

### DELETE /api/v1/evaluations/{evaluation_id}

Permanently delete an evaluation. Only accessible by leaders and admins.

**Path parameters**

| Param | Type | Description |
|-------|------|-------------|
| `evaluation_id` | `int` | Evaluation ID |

**Response `204` -- No Content**

**Errors:** `404` if not found. `403` if role is `member`.

### GET /api/v1/evaluations/{evaluation_id}

Get full details of a single evaluation by ID.

**Path parameters**

| Param | Type | Description |
|-------|------|-------------|
| `evaluation_id` | `int` | Evaluation ID |

**Response `200` -- `EvaluationDetailResponse`**

| Field | Type | Description |
|-------|------|-------------|
| `id` | `int` | Evaluation ID |
| `brand_id` | `int` | Brand ID |
| `brand_name` | `string` | Brand name |
| `final_score` | `float` | Final computed score |
| `verdict` | `string` | Verdict string |
| `template` | `string` | `fashion` or `non_fashion` |
| `score_breakdown` | `object[]` | Per-category scoring details |
| `calculator_results` | `object` | Results from all calculators |
| `manual_inputs` | `object` | User-provided manual data |
| `email_output` | `string \| null` | Generated email text |
| `evaluator_email` | `string` | Evaluator email |
| `created_at` | `datetime` | Creation timestamp |
| `rule_version` | `int` | Version of scoring rules used |
| `period` | `string` | Period label |
| `brand_raw_data` | `BrandRawData` | Extracted brand fields for email composition |

**`BrandRawData` fields:**

| Field | Type | Description |
|-------|------|-------------|
| `email` | `string \| null` | Brand contact email |
| `pic_name` | `string \| null` | Person in charge name |
| `store_link` | `string \| null` | Store URL |
| `kategori` | `string \| null` | Category |

**Errors:** `404` if not found.

### GET /api/v1/evaluations/brands/{brand_id}

Get the current shared evaluation inputs state for a brand. Returns null values if no inputs exist yet.

**Path parameters**

| Param | Type | Description |
|-------|------|-------------|
| `brand_id` | `int` | Brand ID |

**Response `200` -- `EvaluationStateResponse`**

| Field | Type | Description |
|-------|------|-------------|
| `brand_id` | `int` | Brand ID |
| `category_type` | `string \| null` | `fashion` or `non_fashion` |
| `manual_data` | `object \| null` | User-entered manual data |
| `updated_at` | `datetime \| null` | Last update timestamp |

### PUT /api/v1/evaluations/brands/{brand_id}

Upsert evaluation inputs for a brand. Records the current user as `last_edited_by`.

**Path parameters**

| Param | Type | Description |
|-------|------|-------------|
| `brand_id` | `int` | Brand ID |

**Request body -- `EvaluationInputsUpdate`**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `category_type` | `string \| null` | No | `fashion` or `non_fashion` |
| `manual_data` | `object \| null` | No | Manual input data |

**Response `200` -- `EvaluationStateResponse`**

Same shape as the GET response above.

**Errors:** `404` if brand does not exist.

### POST /api/v1/evaluations/brands/{brand_id}/score

Generate the final score for a brand evaluation using current manual inputs and calculator results.

**Path parameters**

| Param | Type | Description |
|-------|------|-------------|
| `brand_id` | `int` | Brand ID |

**Request body -- `ScoringRequest`**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `template` | `string` | Yes | -- | `fashion` or `non_fashion` |
| `verdict` | `string` | No | `""` | Verdict value |
| `store_name` | `string` | No | `""` | Store name (max 200 chars) |
| `period` | `string` | No | `""` | Period label (max 50 chars) |
| `brand_name` | `string` | No | `""` | Brand name (max 200 chars) |
| `email` | `string \| null` | No | `null` | Brand email (max 254 chars) |

**Response `200` -- `ScoringResponse`**

| Field | Type | Description |
|-------|------|-------------|
| `total_score` | `float` | Computed total score |
| `category_scores` | `CategoryScoreItem[]` | Per-category breakdown |
| `verdict` | `string` | Final verdict |
| `conclusion` | `string` | Conclusion text |
| `marketing_estimation` | `string` | Marketing estimation text |
| `marketing_percentage` | `string` | Marketing percentage |
| `marketing_budget` | `string` | Marketing budget value |
| `closing_message` | `string` | Closing message text |
| `email_subject` | `string` | Generated email subject line |
| `email_body` | `string` | Generated email body text |
| `template` | `string` | Template used |
| `rule_version` | `int` | Scoring rule version used |

**`CategoryScoreItem` fields:**

| Field | Type | Description |
|-------|------|-------------|
| `category` | `string` | Category name |
| `score` | `float` | Earned score |
| `max_score` | `float` | Maximum possible score |
| `rows` | `RowScoreItem[]` | Individual metric scores |
| `available` | `bool` | Whether data was available for this category |

**`RowScoreItem` fields:**

| Field | Type | Description |
|-------|------|-------------|
| `row` | `int` | Row index |
| `metric` | `string` | Metric name |
| `value` | `any` | Actual value |
| `benchmark` | `string` | Benchmark description |
| `verdict` | `string` | Per-metric verdict |
| `message` | `string` | Verdict message |
| `score` | `float` | Score for this metric |

**Errors:** `400` if required data is missing.

### POST /api/v1/evaluations/brands/{brand_id}/save

Save a completed evaluation as a permanent, immutable record. Multiple saves for the same brand create separate records (evaluation history).

**Path parameters**

| Param | Type | Description |
|-------|------|-------------|
| `brand_id` | `int` | Brand ID |

**Request body -- `SaveEvaluationRequest`**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `template` | `string` | Yes | -- | `fashion` or `non_fashion` |
| `final_score` | `float` | Yes | -- | Final score |
| `verdict` | `string` | Yes | -- | Verdict value |
| `score_breakdown` | `object[]` | Yes | -- | Per-category scoring details |
| `calculator_results` | `object` | Yes | -- | Calculator output data |
| `manual_inputs` | `object` | Yes | -- | User-entered manual data |
| `rule_version` | `int` | No | `1` | Scoring rule version |
| `email_output` | `string \| null` | No | `null` | Generated email text |
| `period` | `string` | No | `""` | Period label |

**Response `200` -- `SaveEvaluationResponse`**

| Field | Type | Description |
|-------|------|-------------|
| `id` | `int` | Newly created evaluation ID |
| `brand_id` | `int` | Brand ID |
| `final_score` | `float` | Final score |
| `verdict` | `string` | Verdict |
| `template` | `string` | Template used |
| `created_at` | `datetime` | Creation timestamp |
| `period` | `string` | Period label |

**Errors:** `404` if brand does not exist. `422` if required fields are missing.

**Side effects:** Creates an INSERT-only record. The `evaluator_email` is automatically set from the authenticated user.

---

## Calculators

Calculator endpoints live under the evaluations router at `/api/v1/evaluations/brands/{brand_id}/calculators/...`. All require authentication; any role can access.

| Method | Path | Auth | Roles | Description |
|--------|------|------|-------|-------------|
| GET | `.../calculators/results` | Required | Any | Get stored calculator results |
| POST | `.../calculators/ads_keyword` | Required | Any | Run Ads Keyword calculator |
| POST | `.../calculators/discount` | Required | Any | Run Discount Check calculator |
| POST | `.../calculators/top_sku` | Required | Any | Run Top SKU calculator |
| POST | `.../calculators/run-all` | Required | Any | Run all ready calculators |
| GET | `.../calculators/status` | Required | Any | Get calculator readiness status |

All paths above are prefixed with `/api/v1/evaluations/brands/{brand_id}`.

### GET /api/v1/evaluations/brands/{brand_id}/calculators/results

Return all stored calculator results for a brand. Returns an empty list if the brand has no results (does not 404).

**Response `200` -- `CalculatorResultsListResponse`**

| Field | Type | Description |
|-------|------|-------------|
| `brand_id` | `int` | Brand ID |
| `results` | `CalculatorResultItem[]` | Stored results |

**`CalculatorResultItem` fields:**

| Field | Type | Description |
|-------|------|-------------|
| `calculator_type` | `string` | Calculator identifier (e.g., `ads_keyword`, `discount`, `top_sku`) |
| `output_text` | `string` | Human-readable output |
| `details` | `object` | Detailed calculation data |
| `calculated_at` | `datetime` | When the calculation was run |

### POST /api/v1/evaluations/brands/{brand_id}/calculators/ads_keyword

Execute the Ads Keyword Calculator. Loads required CSV data and manual inputs, runs the calculator, and stores the result.

**Request body:** None

**Response `200` -- `CalculatorResultResponse`**

| Field | Type | Description |
|-------|------|-------------|
| `calculator_type` | `string` | `"ads_keyword"` |
| `output_text` | `string` | Human-readable output |
| `details` | `object` | Detailed calculation data |
| `calculated_at` | `datetime` | Calculation timestamp |

**Errors:** `400` if required data (CSV uploads or manual inputs) is missing.

### POST /api/v1/evaluations/brands/{brand_id}/calculators/discount

Execute the Discount Check Calculator. Loads order export data and runs the calculator.

**Request body:** None

**Response `200` -- `CalculatorResultResponse`** (same shape as above)

**Errors:** `400` if required data is missing.

### POST /api/v1/evaluations/brands/{brand_id}/calculators/top_sku

Execute the Top SKU Calculator. Loads order export and mass update data.

**Request body:** None

**Response `200` -- `CalculatorResultResponse`** (same shape as above)

**Errors:** `400` if required data is missing.

### POST /api/v1/evaluations/brands/{brand_id}/calculators/run-all

Run all calculators whose required files are available. Skips calculators with missing prerequisites instead of failing.

**Request body:** None

**Response `200` -- `RunAllResponse`**

| Field | Type | Description |
|-------|------|-------------|
| `results` | `RunCalculatorItem[]` | Per-calculator outcomes |

**`RunCalculatorItem` fields:**

| Field | Type | Description |
|-------|------|-------------|
| `calculator_type` | `string` | Calculator identifier |
| `status` | `string` | `"success"`, `"skipped"`, or `"error"` |
| `result` | `object \| null` | Calculator output (if success) |
| `reason` | `string \| null` | Reason for skip/error |

### GET /api/v1/evaluations/brands/{brand_id}/calculators/status

Return the readiness status of each calculator for a brand, showing which files/inputs are available vs. missing.

**Response `200` -- `CalculatorStatusResponse`**

| Field | Type | Description |
|-------|------|-------------|
| `brand_id` | `int` | Brand ID |
| `calculators` | `object` | Map of calculator type to `SingleCalculatorStatus` |

**`SingleCalculatorStatus` fields:**

| Field | Type | Description |
|-------|------|-------------|
| `status` | `string` | `"ready"` or `"pending"` |
| `has_result` | `bool` | Whether a stored result exists |
| `required_files` | `string[]` | File types needed |
| `required_manual` | `string[]` | Manual input fields needed |
| `available_files` | `string[]` | File types already uploaded |
| `missing_files` | `string[]` | File types still needed |
| `missing_manual` | `string[]` | Manual fields still needed |
| `calculated_at` | `datetime \| null` | When last calculated (if any) |

---

## Upload

All endpoints require authentication. Any role can access.

| Method | Path | Auth | Roles | Description |
|--------|------|------|-------|-------------|
| POST | `/api/v1/upload/signed-url` | Required | Any | Get GCS signed upload URL |
| POST | `/api/v1/upload/process` | Required | Any | Process uploaded file |
| GET | `/api/v1/upload/brands/{brand_id}` | Required | Any | List uploads for a brand |
| PUT | `/api/v1/upload/local/{upload_id}/{filename:path}` | Required | Any | Local dev file upload |

### POST /api/v1/upload/signed-url

Generate a GCS signed URL for direct file upload from the browser.

**Request body -- `SignedUrlRequest`**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `filename` | `string` | Yes | Original filename |
| `content_type` | `string` | Yes | MIME type (e.g., `text/csv`) |
| `file_type` | `string` | Yes | Logical file type identifier |
| `brand_id` | `int` | Yes | Target brand ID |

**Response `200` -- `SignedUrlResponse`**

| Field | Type | Description |
|-------|------|-------------|
| `upload_url` | `string` | Signed URL for PUT upload |
| `upload_id` | `string` | Generated upload ID for subsequent processing |
| `expires_at` | `datetime` | URL expiration timestamp |

### POST /api/v1/upload/process

Process an uploaded file: download from GCS (or local storage), parse, validate, store parsed data, and auto-execute any calculators that become ready.

**Request body -- `ProcessRequest`**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `upload_id` | `string` | Yes | Upload ID from signed-url response |
| `brand_id` | `int` | Yes | Brand ID |
| `file_type` | `string` | Yes | Logical file type identifier |

**Response `200` -- `ProcessUploadResponse`**

| Field | Type | Description |
|-------|------|-------------|
| `upload` | `UploadResponse` | Metadata about the stored upload |
| `auto_calculated` | `AutoCalculatedItem[]` | Calculators that were auto-executed |

**`UploadResponse` fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | `int` | Upload record ID |
| `brand_id` | `int` | Brand ID |
| `file_type` | `string` | File type |
| `filename` | `string` | Original filename |
| `file_size` | `int` | File size in bytes |
| `row_count` | `int` | Number of parsed rows |
| `uploaded_at` | `datetime` | Upload timestamp |

**`AutoCalculatedItem` fields:**

| Field | Type | Description |
|-------|------|-------------|
| `calculator_type` | `string` | Calculator identifier |
| `status` | `string` | `"success"`, `"skipped"`, or `"error"` |
| `result` | `object \| null` | Calculator output (if success) |
| `reason` | `string \| null` | Reason for skip/error |

**Side effects:** Stores parsed CSV data in the database. Triggers automatic calculator execution for any calculators whose prerequisites are now met.

### GET /api/v1/upload/brands/{brand_id}

Return all uploaded files for a brand.

**Path parameters**

| Param | Type | Description |
|-------|------|-------------|
| `brand_id` | `int` | Brand ID |

**Response `200` -- `BrandUploadsResponse`**

| Field | Type | Description |
|-------|------|-------------|
| `brand_id` | `int` | Brand ID |
| `uploads` | `UploadResponse[]` | List of uploads |

### PUT /api/v1/upload/local/{upload_id}/{filename:path}

Local development endpoint for receiving file bytes that would go to GCS in production. Only available when `gcs_upload_bucket` is not configured.

**Path parameters**

| Param | Type | Description |
|-------|------|-------------|
| `upload_id` | `string` | Upload ID |
| `filename` | `string` | Filename (path parameter) |

**Request body:** Raw file bytes

**Response `200`**

```json
{
  "status": "ok"
}
```

**Errors:** `404` if `gcs_upload_bucket` is configured (production mode). `400` if filename is invalid.

**Side effects:** Writes file to local filesystem at the path matching the GCS object name structure.

---

## Rules

All endpoints require `leader` or `admin` role.

| Method | Path | Auth | Roles | Description |
|--------|------|------|-------|-------------|
| GET | `/api/v1/rules` | Required | leader, admin | List all scoring rules |
| PUT | `/api/v1/rules/{template}` | Required | leader, admin | Update rules for a template |

### GET /api/v1/rules

Get all scoring rules for all templates.

**Response `200` -- `ScoringRuleResponse[]`**

| Field | Type | Description |
|-------|------|-------------|
| `id` | `int` | Rule record ID |
| `template` | `string` | Template name (`fashion`, `non_fashion`, or `default`) |
| `rules` | `object` | Nested rule definitions (each key maps to a dict of metric rules) |
| `version` | `int` | Auto-incremented version number |
| `updated_by` | `int \| null` | User ID of last editor |
| `updated_at` | `datetime` | Last update timestamp |

### PUT /api/v1/rules/{template}

Update scoring rules for a specific template. Increments the version number automatically.

**Path parameters**

| Param | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `template` | `string` | `fashion`, `non_fashion`, or `default` | Target template |

**Request body -- `ScoringRuleUpdateRequest`**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `rules` | `object` | Yes | Non-empty dict where each value must also be a dict |

**Response `200` -- `ScoringRuleResponse`**

Same shape as the list response item above.

**Side effects:** Increments the rule version. Records `updated_by` from the authenticated user. Frontend handles password re-confirmation via Firebase reauthentication before calling this endpoint.

---

## Sync

All endpoints require authentication. Any role can access.

| Method | Path | Auth | Roles | Description |
|--------|------|------|-------|-------------|
| POST | `/api/v1/sync` | Required | Any | Trigger brand data sync |
| GET | `/api/v1/sync/status` | Required | Any | Get latest sync status |

### POST /api/v1/sync

Trigger a manual sync of brand data from Google Sheets. Executes synchronously and returns results when complete. Uses a PostgreSQL advisory lock to prevent concurrent syncs.

**Request body:** None

**Response `200` -- `SyncStatusResponse`**

| Field | Type | Description |
|-------|------|-------------|
| `id` | `int` | Sync operation ID |
| `last_sync` | `datetime` | Effective sync timestamp (completed_at or started_at) |
| `status` | `string` | `"success"`, `"failed"`, or `"in_progress"` |
| `started_at` | `datetime` | When the sync started |
| `completed_at` | `datetime \| null` | When the sync finished |
| `brands_synced` | `int` | Number of brands synced |
| `error_message` | `string \| null` | Error details if failed |
| `sync_details` | `object \| null` | Detailed per-sheet results |

**Errors:** `409` with code `SYNC_IN_PROGRESS` if a sync is already running.

**Side effects:** Fetches data from Google Sheets (VP and Meeting sheets), upserts brand records in the database. Creates a `sync_status` record tracking the operation.

### GET /api/v1/sync/status

Get the latest sync operation's status.

**Response `200` -- `SyncStatusResponse | null`**

Same shape as the POST response. Returns `null` if no sync has ever been run.

---

## Email

All endpoints require authentication. Any role can access.

| Method | Path | Auth | Roles | Description |
|--------|------|------|-------|-------------|
| POST | `/api/v1/email/send` | Required | Any | Send evaluation report email |
| GET | `/api/v1/email/preview/{evaluation_id}` | Required | Any | Preview email as HTML |

### POST /api/v1/email/send

Send an evaluation report email. Fetches evaluation data, renders the HTML template with the provided chart image, and sends the email via SMTP.

**Request body -- `SendEmailRequest`**

| Field | Type | Required | Default | Constraints | Description |
|-------|------|----------|---------|-------------|-------------|
| `evaluation_id` | `int` | Yes | -- | -- | Evaluation to send |
| `recipients` | `EmailStr[]` | Yes | -- | 1--10 items | To addresses |
| `cc` | `EmailStr[]` | No | `[]` | max 10 items | CC addresses |
| `bcc` | `EmailStr[]` | No | `[]` | max 10 items | BCC addresses |
| `chart_image` | `string` | Yes | -- | -- | Base64-encoded PNG chart image |
| `subject` | `string \| null` | No | `null` | max 200 chars | Custom subject (auto-generated if null) |
| `note` | `string \| null` | No | `null` | max 500 chars | Optional note included in email body |

**Validation:** Total recipients across To + CC + BCC cannot exceed 10.

**Response `200` -- `SendEmailResponse`**

| Field | Type | Description |
|-------|------|-------------|
| `success` | `bool` | Whether the email was sent |
| `message_id` | `string` | SMTP message ID |
| `recipients` | `string[]` | List of recipient addresses |

**Side effects:** Sends an email via configured SMTP server. Fetches evaluation detail to populate the template.

### GET /api/v1/email/preview/{evaluation_id}

Preview the evaluation email as rendered HTML in the browser. Uses placeholder chart image and data URI-encoded header/footer assets.

**Path parameters**

| Param | Type | Description |
|-------|------|-------------|
| `evaluation_id` | `int` | Evaluation ID |

**Query parameters**

| Param | Type | Default | Constraints | Description |
|-------|------|---------|-------------|-------------|
| `note` | `string \| null` | `null` | max 500 chars | Optional note to include in preview |

**Response `200` -- `text/html`**

Returns the full HTML email content directly as an HTML response (not JSON).

**Errors:** `404` if evaluation not found.
