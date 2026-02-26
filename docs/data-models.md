# Data Models

**Generated:** 2026-02-16 | **Scan Level:** Exhaustive | **Part:** Backend

## Database

- **Provider:** Cloud SQL (managed PostgreSQL)
- **Driver:** asyncpg (async) + psycopg2 (migrations)
- **Migrations:** Alembic (17 migrations)
- **Connection Pool:** 1-5 connections (configurable via env)

## Schema Overview

```
users ─────────────────┐
                       │
brand_vp_data ────┐    │
                  ├────┼── evaluation_inputs (shared per-brand)
brand_meeting_data┘    │
                       ├── brand_uploads
                       │
                       ├── calculator_results
                       │
                       ├── evaluations (immutable snapshots)
                       │
                       └── scoring_rules

sync_status (standalone)
```

---

## Table Definitions

### users

User accounts linked to Firebase Auth.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | SERIAL | PRIMARY KEY | Auto-increment ID |
| `firebase_uid` | VARCHAR | UNIQUE, NOT NULL | Firebase Auth UID |
| `email` | VARCHAR | NOT NULL | User email |
| `role` | VARCHAR | DEFAULT 'member' | `admin`, `leader`, or `member` |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Account creation time |
| `last_login` | TIMESTAMP | | Last login timestamp |

**Notes:** Auto-created on first login via `/api/v1/me` endpoint.

---

### brand_vp_data

Brand data synced from the VP Google Sheet.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | SERIAL | PRIMARY KEY | Auto-increment ID |
| `brand_name` | VARCHAR | UNIQUE, NOT NULL | Brand identifier |
| `raw_data` | JSONB | | All VP sheet columns as key-value pairs |
| `created_at` | TIMESTAMP | DEFAULT NOW() | First sync time |
| `updated_at` | TIMESTAMP | DEFAULT NOW() | Last sync update |

---

### brand_meeting_data

Brand data synced from the 1st Meeting Google Sheet.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | SERIAL | PRIMARY KEY | Auto-increment ID |
| `brand_name` | VARCHAR | UNIQUE, NOT NULL | Brand identifier (matches VP data) |
| `raw_data` | JSONB | | All meeting sheet columns |
| `created_at` | TIMESTAMP | DEFAULT NOW() | First sync time |
| `updated_at` | TIMESTAMP | DEFAULT NOW() | Last sync update |

**Relationship:** LEFT JOIN to `brand_vp_data` via `brand_name`.

---

### sync_status

Records of Google Sheets sync operations.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | SERIAL | PRIMARY KEY | Sync operation ID |
| `started_at` | TIMESTAMP | NOT NULL | Sync start time |
| `completed_at` | TIMESTAMP | | Sync completion time |
| `success` | BOOLEAN | | Overall success flag |
| `brands_synced` | INTEGER | | Total brands synced |
| `error_message` | TEXT | | Error details if failed |
| `sync_details` | JSONB | | Per-sheet breakdown |

**sync_details structure:**
```json
{
  "vp_result": { "sheet_type": "vp", "rows_synced": 150, "rows_skipped": 0, "errors": [], "success": true },
  "meeting_result": { "sheet_type": "meeting", "rows_synced": 120, "rows_skipped": 0, "errors": [], "success": true }
}
```

---

### evaluation_inputs

Shared per-brand evaluation state (work-in-progress). One active draft per brand.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | SERIAL | PRIMARY KEY | Auto-increment ID |
| `brand_id` | INTEGER | FK → brand_vp_data.id | Target brand |
| `last_edited_by` | INTEGER | FK → users.id, ON DELETE SET NULL | Last editor |
| `category_type` | VARCHAR | | `fashion`, `non_fashion`, or null |
| `manual_data` | JSONB | | All manually entered form data |
| `updated_at` | TIMESTAMP | DEFAULT NOW() | Last auto-save time |

**Unique constraint:** `(brand_id)` — one in-progress evaluation per brand (shared across users).

**manual_data structure:**
```json
{
  "operational": { "unfulfilledOrderRate": 2.5, "lateShipmentRate": 1.0, "preparationTime": 1.5, "chatResponseRate": 95, "overallRating": 4.8 },
  "business": { "salesMonth0": 50000000, "salesMonth1": 48000000, "...": "...", "conversionRate": 3.5 },
  "visitors": { "totalVisitors": 10000, "totalFollowers": 5000, "returningVisitors": 2000 },
  "promoTools": { "promoToko": 1000000, "paketDiskon": 500000, "...11 fields...": "..." },
  "products": { "productCount": 200, "storeStatus": "mall" },
  "ads": { "adSales": 20000000, "adCost": 2000000 },
  "campaign": { "nominatedSessions": 5, "availableSessions": 8 },
  "competition": { "product1": { "keyword": "...", "marketPrice": 50000 }, "product2": {}, "product3": {} }
}
```

---

### brand_uploads

Uploaded Shopee report files per brand.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | SERIAL | PRIMARY KEY | Auto-increment ID |
| `brand_id` | INTEGER | FK → brand_vp_data.id | Target brand |
| `file_type` | VARCHAR | NOT NULL | `cpc_ad_report`, `keyword_report`, `order_export`, `mass_update` |
| `calculator_target` | VARCHAR | | Target calculator for this file type |
| `filename` | VARCHAR | NOT NULL | Original filename |
| `file_size` | INTEGER | | File size in bytes |
| `row_count` | INTEGER | | Number of data rows parsed |
| `parsed_data` | JSONB | | Parsed file content as list of dicts |
| `uploaded_by` | INTEGER | FK → users.id | Uploader |
| `uploaded_at` | TIMESTAMP | DEFAULT NOW() | Upload timestamp |

**Unique constraint:** `(brand_id, file_type)` — latest upload replaces previous.

---

### calculator_results

Stored outputs from automated calculators.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | SERIAL | PRIMARY KEY | Auto-increment ID |
| `brand_id` | INTEGER | FK → brand_vp_data.id | Target brand |
| `calculator_type` | VARCHAR | NOT NULL | `ads_keyword`, `discount`, `top_sku` |
| `details` | JSONB | | Structured calculator output |
| `output_text` | TEXT | | Human-readable formatted output |
| `calculated_at` | TIMESTAMP | DEFAULT NOW() | Calculation timestamp |

**Unique constraint:** `(brand_id, calculator_type)` — latest result replaces previous.

---

### evaluations

Immutable evaluation snapshots (INSERT-only, never updated).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | SERIAL | PRIMARY KEY | Evaluation ID |
| `brand_id` | INTEGER | FK → brand_vp_data.id | Evaluated brand |
| `user_id` | INTEGER | FK → users.id | Evaluator |
| `template` | VARCHAR | NOT NULL | Scoring template used (`default`) |
| `final_score` | NUMERIC | NOT NULL | Total score (0-100 range) |
| `verdict` | VARCHAR | NOT NULL | `✔️`, `❌`, `❌ Non Mall`, `❌ No Brand`, `❌ Opex`, `⭕️` |
| `score_breakdown` | JSONB | | Full category scores array |
| `calculator_results` | JSONB | | Calculator outputs at time of save |
| `manual_inputs` | JSONB | | Manual data at time of save |
| `rule_version` | INTEGER | | Scoring rules version used |
| `email_output` | TEXT | | Generated email body |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Save timestamp |

**Design:** Each save creates a NEW row (immutable snapshots). Multiple evaluations per brand are allowed.

---

### scoring_rules

Configurable scoring rules with versioning.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | SERIAL | PRIMARY KEY | Rule set ID |
| `template` | VARCHAR | UNIQUE, NOT NULL | Template name (`default`) |
| `rules` | JSONB | NOT NULL | Complete scoring rules |
| `version` | INTEGER | DEFAULT 1 | Auto-incremented on update |
| `updated_by` | INTEGER | FK → users.id | Last editor |
| `updated_at` | TIMESTAMP | DEFAULT NOW() | Last update time |

**rules JSONB structure** (abbreviated):
```json
{
  "categories": {
    "operational": { "rows": [...], "max_score": 0 },
    "business": { "rows": [...], "max_score": 0 },
    "visitors": { "rows": [...], "max_score": 15 },
    "promo_tools": { "rows": [...], "max_score": 15 },
    "products_status": { "rows": [...], "max_score": 10 },
    "ads": { "rows": [...], "max_score": 20 },
    "campaign": { "rows": [...], "max_score": 10 },
    "stock": { "rows": [...], "max_score": 15 },
    "discount": { "rows": [...], "max_score": 15 }
  },
  "interpretation": { "ranges": [...], "closing_messages": [...], "competition_messages": [...] },
  "marketing": { "floor": 0.12, "floor_fashion": 0.15, "base_subtraction": 0.05, "upper_limit_base": 0.55 }
}
```

---

## Migration History

| # | Migration | Summary |
|---|-----------|---------|
| 001 | create_users_table | Users with firebase_uid, email, role |
| 002 | create_brands_table | Generic brands table (later replaced) |
| 003 | create_sync_status_table | Sync operation tracking |
| 004 | replace_brands_with_vp_and_meeting | Split into brand_vp_data + brand_meeting_data |
| 005 | add_sync_details | JSONB sync_details column |
| 006 | create_evaluation_inputs_table | Per-user evaluation state |
| 007 | create_brand_uploads_table | File upload tracking |
| 008 | create_calculator_results_table | Calculator output storage |
| 009 | create_evaluations_table | Immutable evaluation snapshots |
| 010 | create_scoring_rules_table | Scoring rules with fashion/non_fashion templates |
| 011 | add_marketing_rules | Marketing calculation parameters |
| 012 | add_message_templates | Email/WhatsApp message templates in rules |
| 013 | unify_scoring_rules_template | Merge into single "default" template |
| 014 | nullable_user_fks_for_account_deletion | Make user FKs nullable with ON DELETE SET NULL |
| 015 | shared_evaluation_inputs | Convert evaluation_inputs from per-user to shared per-brand |
| 016 | update_closing_messages | Update closing message templates |
| 017 | remove_unused_verdict_closing_messages | Remove unused verdict closing messages |

## Entity Relationships

- `evaluation_inputs` → `brand_vp_data` (brand_id), `users` (last_edited_by, ON DELETE SET NULL)
- `brand_uploads` → `brand_vp_data` (brand_id), `users` (uploaded_by, ON DELETE SET NULL)
- `calculator_results` → `brand_vp_data` (brand_id)
- `evaluations` → `brand_vp_data` (brand_id), `users` (user_id, ON DELETE SET NULL)
- `scoring_rules` → `users` (updated_by, ON DELETE SET NULL)
- `brand_vp_data` ↔ `brand_meeting_data` (via brand_name LEFT JOIN)
