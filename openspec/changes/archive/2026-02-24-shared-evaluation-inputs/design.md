## Context

Evaluation inputs are currently scoped per-user-per-brand. The `evaluation_inputs` table has a `UNIQUE (brand_id, user_id)` constraint and all read/write queries filter by both `brand_id` and `user_id`. This means:

- Each user sees only their own inputs — no collaboration
- When a user is hard-deleted, `ON DELETE SET NULL` orphans their rows (`user_id = NULL`), making data invisible to everyone
- The `get_any_evaluation_inputs` function already exists as a workaround for calculator readiness checks, hinting that the per-user model is already leaking

Key touchpoints in the codebase:
- **Queries**: `get_evaluation_inputs` (read), `upsert_evaluation_inputs` (write), `get_any_evaluation_inputs` (readiness)
- **Service**: `get_evaluation_state`, `save_evaluation_inputs`, `generate_score`
- **Calculator service**: `_run_ads_keyword`, `_run_discount`, `_run_top_sku` — all pass `user_id` to load inputs
- **Router**: `GET/PUT /api/v1/evaluations/brands/{brand_id}` — passes `current_user["id"]`
- **DB schema**: `evaluation_inputs` table with `user_id` FK and `UNIQUE (brand_id, user_id)` constraint

## Goals / Non-Goals

**Goals:**
- All users see and edit the same evaluation inputs for a brand (shared model)
- User deletion does not cause evaluation data loss
- Track who last edited for audit purposes
- Zero-downtime migration from per-user to per-brand model

**Non-Goals:**
- Real-time push updates (polling/SSE) — users refresh to see changes
- Conflict resolution UI — last-write-wins is sufficient
- Soft-delete for users — hard-delete is kept, shared model makes it safe
- Changes to the `evaluations` table — final scored evaluations remain per-user (immutable history records)

## Decisions

### 1. Rename `user_id` → `last_edited_by` on `evaluation_inputs`

**Decision**: Rename the column rather than drop + add. The column keeps its FK to `users.id` with `ON DELETE SET NULL`.

**Rationale**: A rename is simpler than drop + recreate. The column already allows NULL (migration 014). The semantic change from "owner" to "audit trail" is captured by the name change.

**Alternative considered**: Drop `user_id` entirely, add a new `last_edited_by` column. Rejected — unnecessary data movement, same end result.

### 2. Replace `UNIQUE (brand_id, user_id)` with `UNIQUE (brand_id)`

**Decision**: One row per brand. The upsert conflict target changes from `(brand_id, user_id)` to `(brand_id)`.

**Rationale**: This is the core model change. With shared inputs, there's exactly one canonical row per brand.

### 3. Consolidate duplicates in migration

**Decision**: The Alembic migration will consolidate duplicate rows (same brand, multiple users) by keeping the row with the most recent `updated_at`. Other rows are deleted.

**Migration steps** (single Alembic migration):
1. For each `brand_id` with multiple rows: keep the one with `MAX(updated_at)`, delete the rest
2. Rename column `user_id` → `last_edited_by`
3. Drop `UNIQUE (brand_id, user_id)` constraint (`uq_evaluation_inputs_brand_user`)
4. Drop index `idx_evaluation_inputs_user_id`
5. Add `UNIQUE (brand_id)` constraint

**Rollback**: Reverse the constraint/rename. Deleted duplicates are not recoverable, but the most recent data is preserved which is the same data users were seeing.

### 4. Remove `user_id` parameter from query and service functions

**Decision**: Strip `user_id` from the following function signatures:
- `get_evaluation_inputs(conn, brand_id)` — remove `user_id` param, query `WHERE brand_id = $1` only
- `upsert_evaluation_inputs(conn, brand_id, last_edited_by, ...)` — rename param, conflict on `(brand_id)`
- `get_evaluation_state(brand_id)` — remove `user_id`
- `save_evaluation_inputs(brand_id, last_edited_by, ...)` — rename param
- `generate_score(brand_id, user_id, ...)` — keep `user_id` for the evaluations record, but load inputs by `brand_id` only

**`get_any_evaluation_inputs` can be removed** — it becomes identical to `get_evaluation_inputs`.

### 5. Router changes — minimal

**Decision**: Endpoints keep `current_user` dependency (for authentication) but stop passing `user_id` for reads, and pass it as `last_edited_by` for writes.

- `GET /api/v1/evaluations/brands/{brand_id}` → calls `get_evaluation_state(brand_id)` (no user_id)
- `PUT /api/v1/evaluations/brands/{brand_id}` → calls `save_evaluation_inputs(brand_id, last_edited_by=current_user["id"], ...)`
- Calculator endpoints → load inputs by `brand_id` only
- `POST .../score` → keep `user_id` for the evaluation record (who scored), load inputs by `brand_id`

### 6. Frontend — no changes needed

**Decision**: The frontend already renders whatever the API returns. Since the API response shape (`EvaluationStateResponse`) doesn't change — only the scoping changes server-side — no frontend modifications are required.

## Risks / Trade-offs

**[Last-write-wins data loss]** → Acceptable for this team size. If two users edit the same brand simultaneously, the last save wins. Mitigation: `updated_at` timestamp and `last_edited_by` provide visibility into who changed what and when.

**[Migration deletes duplicate rows]** → Only the most recent row per brand is kept. Mitigation: this matches what users expect (they want to see the latest data). Older inputs from other users for the same brand are lost, but in practice the team treats inputs as shared work.

**[Orphaned `last_edited_by` after user deletion]** → Shows NULL instead of the editor's name. Mitigation: queries already handle this with `COALESCE(u.email, 'Pengguna Dihapus')` pattern. Apply the same pattern if `last_edited_by` is ever displayed.
