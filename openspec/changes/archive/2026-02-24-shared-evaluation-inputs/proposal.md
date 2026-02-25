## Why

Evaluation inputs are currently isolated per-user — each user only sees their own data for a brand. In practice, the team works collaboratively: one person fills in fields, and everyone should see the result. Worse, when a user account is deleted (`ON DELETE SET NULL`), their evaluation inputs become orphaned (`user_id = NULL`) and invisible to all users, effectively losing work.

## What Changes

- **BREAKING**: Change `evaluation_inputs` from per-user-per-brand to per-brand (shared). All users see and edit the same evaluation data for a given brand.
- Keep hard-delete for user accounts. With the shared model, `user_id` is no longer the ownership key — it becomes an audit-only field (`last_edited_by`). When a user is deleted, `last_edited_by` is set to NULL but the evaluation data itself remains intact.
- Track who last edited evaluation inputs (`last_edited_by`, FK to `users` with `ON DELETE SET NULL`). Last-write-wins for conflict resolution — no locking, no merge.
- Remove the `UNIQUE (brand_id, user_id)` constraint; replace with `UNIQUE (brand_id)` since there is now one evaluation input row per brand.
- Existing orphaned evaluation inputs (`user_id IS NULL`) and duplicates (same brand, different users) are consolidated during migration — one row per brand, most recent data wins.

## Capabilities

### New Capabilities

- `shared-evaluation-inputs`: Shared evaluation input model — one row per brand, visible to all users, with last-edited-by audit tracking.

### Modified Capabilities

- `evaluation-scoring`: Scoring queries currently join on `user_id`; must adapt to the shared model where inputs are per-brand, not per-user.

## Impact

- **Backend**: `evaluation_inputs` table schema change (drop `user_id`, add `last_edited_by`), new Alembic migration, query rewrites in `evaluations.py`.
- **API**: `GET/PUT /api/v1/evaluations/brands/{id}` no longer scoped to `user_id`. Account deletion unchanged.
- **Frontend**: No major changes expected — evaluation forms already render whatever the API returns.
- **Database**: Migration to consolidate duplicate `evaluation_inputs` rows (same brand, different users) into single rows.
