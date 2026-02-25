# API Contracts

**Generated:** 2026-02-16 | **Scan Level:** Exhaustive | **Part:** Backend (FastAPI)

## Base URL

- **Dev:** Cloud Run service URL (asia-southeast1)
- **Local:** `http://localhost:8000`
- **API Prefix:** `/api/v1`

## Authentication

All endpoints (except `/health`) require a Firebase Auth Bearer token in the `Authorization` header. The SSE endpoint (`/api/v1/events`) accepts the token via `?token=` query parameter (EventSource API limitation).

Role-based access:
- **member** — Standard evaluation access
- **leader** — Can view all evaluations + manage scoring rules
- **admin** — Full access including rules management

---

## Health Check

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| `GET` | `/health` | None | Service health check |

**Response:** `{ "status": "healthy" }`

---

## Auth Module

### GET /api/v1/me

Get current authenticated user profile. Auto-creates user record on first login.

**Response:** `UserResponse`
```json
{
  "id": 1,
  "email": "user@example.com",
  "role": "member",
  "last_login": "2026-02-16T10:00:00Z"
}
```

---

## Brands Module

### GET /api/v1/brands

List brands with pagination and search.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `page` | int | 1 | Page number |
| `limit` | int | 20 | Items per page |
| `search` | string | "" | Search by brand name (ILIKE) |

**Response:** `BrandListResponse`
```json
{
  "items": [
    {
      "id": 1,
      "brand_name": "Brand X",
      "raw_data": { "...VP sheet columns..." },
      "updated_at": "2026-02-16T10:00:00Z",
      "meeting_raw_data": { "...meeting sheet columns..." }
    }
  ],
  "total": 150,
  "page": 1,
  "limit": 20,
  "pages": 8
}
```

### GET /api/v1/brands/{brand_id}

Get single brand detail with VP and meeting data.

**Response:** `BrandDetailResponse`
```json
{
  "id": 1,
  "brand_name": "Brand X",
  "raw_data": { "...VP columns..." },
  "updated_at": "2026-02-16T10:00:00Z",
  "meeting_raw_data": { "...meeting columns..." }
}
```

---

## Evaluations Module

### GET /api/v1/evaluations

List saved evaluations with filtering.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `page` | int | 1 | Page number |
| `limit` | int | 20 | Items per page |
| `sort_by` | string | "created_at" | Sort field: `created_at` or `final_score` |
| `sort_order` | string | "desc" | Sort direction: `asc` or `desc` |
| `search` | string | "" | Search by brand name |
| `date_from` | date | null | Filter start date |
| `date_to` | date | null | Filter end date |

**Response:** `EvaluationListResponse`
```json
{
  "items": [
    {
      "id": 1,
      "brand_name": "Brand X",
      "final_score": 72,
      "verdict": "✔️",
      "template": "default",
      "evaluator_email": "user@example.com",
      "created_at": "2026-02-16T10:00:00Z"
    }
  ],
  "total": 50,
  "page": 1,
  "limit": 20,
  "pages": 3
}
```

### GET /api/v1/evaluations/{evaluation_id}

Get full evaluation detail with all scores and data.

**Response:** `EvaluationDetailResponse`
```json
{
  "id": 1,
  "brand_id": 42,
  "brand_name": "Brand X",
  "final_score": 72,
  "verdict": "✔️",
  "template": "default",
  "score_breakdown": { "...category scores..." },
  "calculator_results": { "...calculator outputs..." },
  "manual_inputs": { "...manual data..." },
  "email_output": "...",
  "rule_version": 5,
  "created_at": "2026-02-16T10:00:00Z",
  "evaluator_email": "user@example.com"
}
```

### GET /api/v1/evaluations/brands/{brand_id}

Get current user's evaluation state (in-progress inputs) for a brand.

**Response:** `EvaluationStateResponse`
```json
{
  "brand_id": 42,
  "category_type": "non_fashion",
  "manual_data": { "operational": { "...fields..." }, "business": { "..." } },
  "updated_at": "2026-02-16T10:00:00Z"
}
```

### PUT /api/v1/evaluations/brands/{brand_id}

Save/update evaluation inputs (auto-save target).

**Request:** `EvaluationInputsUpdate`
```json
{
  "category_type": "non_fashion",
  "manual_data": { "operational": { "unfulfilledOrderRate": 2.5 } }
}
```

**Response:** Updated `EvaluationStateResponse`

### POST /api/v1/evaluations/brands/{brand_id}/score

Generate final score from all inputs and calculator results.

**Request:** `ScoringRequest`
```json
{
  "template": "default",
  "verdict": "✔️",
  "store_name": "Store X",
  "period": "January 2026",
  "brand_name": "Brand X",
  "email": "user@example.com"
}
```

**Response:** `ScoringResponse`
```json
{
  "total_score": 72,
  "category_scores": [
    {
      "category": "Kesehatan Operasional Toko",
      "score": 0,
      "max_score": 0,
      "rows": [ { "row": 1, "metric": "...", "value": "...", "benchmark": "...", "verdict": "✔️", "message": "...", "score": 0 } ],
      "available": true
    }
  ],
  "verdict": "✔️",
  "conclusion": "...",
  "marketing_estimation": "...",
  "marketing_percentage": "15%",
  "marketing_budget": "Rp 10,000,000",
  "closing_message": "...",
  "email_subject": "...",
  "email_body": "...",
  "whatsapp_link": "https://wa.me/...",
  "template": "default",
  "rule_version": 5
}
```

### POST /api/v1/evaluations/brands/{brand_id}/save

Save evaluation as immutable snapshot.

**Request:** `SaveEvaluationRequest` (same as ScoringRequest)

**Response:** `SaveEvaluationResponse`
```json
{
  "evaluation_id": 123,
  "template": "default",
  "final_score": 72,
  "verdict": "✔️",
  "created_at": "2026-02-16T10:00:00Z"
}
```

---

## Calculator Endpoints

### GET /api/v1/evaluations/brands/{brand_id}/calculators/status

Check which calculators are ready to run.

**Response:** `CalculatorStatusResponse`
```json
{
  "brand_id": 42,
  "calculators": {
    "ads_keyword": {
      "status": "ready",
      "has_result": false,
      "required_files": ["cpc_ad_report", "keyword_report"],
      "available_files": ["cpc_ad_report", "keyword_report"],
      "missing_files": [],
      "required_manual": ["total_products"],
      "missing_manual": [],
      "calculated_at": null
    },
    "discount": { "status": "pending", "missing_files": ["order_export"] },
    "top_sku": { "status": "pending", "missing_files": ["order_export", "mass_update"] }
  }
}
```

### GET /api/v1/evaluations/brands/{brand_id}/calculators/results

Get stored calculator results for a brand.

**Response:** `CalculatorResultsListResponse` (list of calculator results)

### POST /api/v1/evaluations/brands/{brand_id}/calculators/{type}

Run a single calculator. Type: `ads_keyword`, `discount`, `top_sku`

**Response:** `CalculatorResultResponse`
```json
{
  "calculator_type": "ads_keyword",
  "output_text": "AK2: Product participation 85%...",
  "details": { "...structured data..." },
  "calculated_at": "2026-02-16T10:00:00Z"
}
```

### POST /api/v1/evaluations/brands/{brand_id}/calculators/run-all

Run all ready calculators at once.

**Response:** `RunAllResponse`
```json
{
  "results": [
    { "calculator_type": "ads_keyword", "status": "success", "result": { "..." } },
    { "calculator_type": "discount", "status": "skipped", "reason": "missing files" }
  ]
}
```

---

## Upload Module

### POST /api/v1/upload/signed-url

Request a signed URL for file upload to GCS.

**Request:** `SignedUrlRequest`
```json
{
  "filename": "cpc_report.csv",
  "content_type": "text/csv",
  "file_type": "cpc_ad_report",
  "brand_id": 42
}
```

**File Types:** `cpc_ad_report`, `keyword_report`, `order_export`, `mass_update`

**Response:** `SignedUrlResponse`
```json
{
  "upload_url": "https://storage.googleapis.com/...",
  "upload_id": "uuid-here",
  "expires_at": "2026-02-16T10:15:00Z"
}
```

### POST /api/v1/upload/process

Process an uploaded file (parse, store, auto-run calculators).

**Request:** `ProcessRequest`
```json
{
  "upload_id": "uuid-here",
  "brand_id": 42,
  "file_type": "cpc_ad_report"
}
```

**Response:** `ProcessUploadResponse`
```json
{
  "upload": { "id": 1, "brand_id": 42, "file_type": "cpc_ad_report", "filename": "report.csv", "file_size": 12345, "row_count": 500, "uploaded_at": "..." },
  "auto_calculated": [
    { "calculator_type": "ads_keyword", "status": "success", "result": { "..." } }
  ]
}
```

### GET /api/v1/upload/brands/{brand_id}

List all uploads for a brand.

**Response:** `BrandUploadsResponse`
```json
{
  "brand_id": 42,
  "uploads": [ { "id": 1, "file_type": "cpc_ad_report", "filename": "report.csv", "row_count": 500, "uploaded_at": "..." } ]
}
```

---

## Rules Module

### GET /api/v1/rules

List all scoring rule templates. **Requires:** leader or admin role.

**Response:** `list[ScoringRuleResponse]`
```json
[
  {
    "id": 1,
    "template": "default",
    "rules": { "...category rules with thresholds..." },
    "version": 5,
    "updated_by": 1,
    "updated_at": "2026-02-16T10:00:00Z"
  }
]
```

### PUT /api/v1/rules/{template}

Update scoring rules for a template. **Requires:** leader or admin role.

**Request:** `ScoringRuleUpdateRequest`
```json
{ "rules": { "...updated rules JSON..." } }
```

**Response:** Updated `ScoringRuleResponse`

---

## Sync Module

### POST /api/v1/sync

Trigger Google Sheets data sync. Executes synchronously and returns 200 with results when complete. Returns 409 if a sync is already in progress.

**Response:** `SyncStatusResponse`
```json
{
  "id": 15,
  "last_sync": "2026-02-16T10:00:00Z",
  "status": "success",
  "started_at": "2026-02-16T09:59:50Z",
  "completed_at": "2026-02-16T10:00:00Z",
  "brands_synced": 150,
  "error_message": null,
  "sync_details": {
    "vp_sheet": { "rows_synced": 150, "rows_skipped": 0, "status": "success" },
    "meeting_sheet": { "rows_synced": 120, "rows_skipped": 0, "status": "success" }
  }
}
```

### GET /api/v1/sync/status

Get latest sync operation status.

**Response:** `SyncStatusResponse`
```json
{
  "id": 15,
  "last_sync": "2026-02-16T10:00:00Z",
  "status": "success",
  "started_at": "2026-02-16T09:59:50Z",
  "completed_at": "2026-02-16T10:00:00Z",
  "brands_synced": 150,
  "error_message": null,
  "sync_details": {
    "vp_result": { "rows_synced": 150, "success": true },
    "meeting_result": { "rows_synced": 120, "success": true }
  }
}
```

---

## Events Module (SSE)

### GET /api/v1/events?token={firebase_token}

Server-Sent Events endpoint for real-time updates.

**Event Types:**
- `sync_status` — Sync operation started/completed
- `new_evaluation` — Another user saved an evaluation

**Format:**
```
event: sync_status
data: {"status": "completed", "brands_synced": 150}

event: new_evaluation
data: {"brand_name": "Brand X", "evaluator": "user@example.com"}
```

---

## Error Responses

All endpoints return standard HTTP error codes:

| Code | Meaning |
|------|---------|
| 401 | Invalid or missing Firebase token |
| 403 | Insufficient role permissions |
| 404 | Resource not found |
| 409 | Conflict (e.g., sync already in progress) |
| 422 | Validation error |
| 500 | Internal server error |

Error body format:
```json
{ "detail": "Error description" }
```
