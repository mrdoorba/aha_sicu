## Requirements

### Requirement: One evaluation input per brand
The system SHALL store exactly one `evaluation_inputs` row per brand. The `UNIQUE (brand_id, user_id)` constraint SHALL be replaced with `UNIQUE (brand_id)`. The `user_id` column SHALL be replaced with `last_edited_by` (FK to `users.id`, `ON DELETE SET NULL`).

#### Scenario: First user saves evaluation inputs for a brand
- **WHEN** a user saves evaluation inputs for a brand that has no existing inputs
- **THEN** the system creates a new `evaluation_inputs` row with `brand_id` and `last_edited_by` set to the current user's ID

#### Scenario: Second user saves evaluation inputs for the same brand
- **WHEN** a different user saves evaluation inputs for a brand that already has inputs
- **THEN** the system updates the existing row (last-write-wins), setting `last_edited_by` to the current user's ID and `updated_at` to now

#### Scenario: User who last edited is deleted
- **WHEN** a user account is hard-deleted and they were the `last_edited_by` on evaluation inputs
- **THEN** the `last_edited_by` field becomes NULL but the evaluation data (`manual_data`, `category_type`) remains intact

### Requirement: All users see the same evaluation inputs
The system SHALL return evaluation inputs by `brand_id` only, without filtering by user. All authenticated users see the same data for a given brand.

#### Scenario: Fetching evaluation inputs for a brand
- **WHEN** any authenticated user requests evaluation inputs for a brand
- **THEN** the system returns the single shared `evaluation_inputs` row for that brand (if it exists), regardless of who created or last edited it

#### Scenario: Brand with no evaluation inputs
- **WHEN** any user requests evaluation inputs for a brand with no saved data
- **THEN** the system returns null/empty values (same as current behavior)

### Requirement: Audit tracking via last_edited_by
The system SHALL record the ID of the user who last saved evaluation inputs in the `last_edited_by` column.

#### Scenario: User saves evaluation inputs
- **WHEN** a user saves or updates evaluation inputs for a brand
- **THEN** `last_edited_by` is set to that user's ID and `updated_at` is set to the current timestamp

### Requirement: Data migration consolidates duplicate rows
The Alembic migration SHALL consolidate existing `evaluation_inputs` rows where multiple users have inputs for the same brand. The row with the most recent `updated_at` wins. The migration SHALL also reassign any `user_id` NULL rows.

#### Scenario: Two users have inputs for the same brand
- **WHEN** the migration runs and brand X has inputs from user A (updated Feb 20) and user B (updated Feb 23)
- **THEN** user B's row is kept (most recent), user A's row is deleted, and the kept row's `user_id` is renamed to `last_edited_by`

#### Scenario: Orphaned row (user_id NULL) is the only row for a brand
- **WHEN** the migration runs and brand Y has one input row with `user_id = NULL`
- **THEN** the row is kept with `last_edited_by = NULL`
