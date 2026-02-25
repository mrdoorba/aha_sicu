## MODIFIED Requirements

### Requirement: JSONB data integrity on save
The system SHALL pass Python dicts directly to asyncpg for JSONB columns, relying on the registered JSONB codec for encoding. The system SHALL NOT call `json.dumps()` before passing values to asyncpg JSONB parameters.

#### Scenario: Saving manual data stores a JSONB object
- **WHEN** evaluation inputs are saved with manual_data containing all sections (operational, business, visitors, etc.)
- **THEN** the database stores a JSONB object (not a JSON string literal) that can be read back as a Python dict without additional parsing

#### Scenario: Saving manual data preserves all sections
- **WHEN** manual_data with populated business, visitors, products, and ads sections is saved
- **THEN** all sections are retrievable as nested dicts when read back via the shared `get_evaluation_inputs` query (filtered by `brand_id` only, no `user_id`)

### Requirement: Defensive parsing of existing double-encoded data
The system SHALL handle both properly-encoded JSONB objects (dicts) and legacy double-encoded JSONB strings when reading `manual_data` from the database. This ensures existing data continues to work without a data migration.

#### Scenario: Scoring with properly-encoded data
- **WHEN** `generate_score` reads manual_data that is a proper dict from the database
- **THEN** all category scores are calculated using the actual input values

#### Scenario: Scoring with legacy double-encoded data
- **WHEN** `generate_score` reads manual_data that is a JSON string (from prior double-encoding)
- **THEN** the string is parsed to a dict before scoring, and all category scores are calculated using the actual input values

### Requirement: Consistent JSONB handling across all evaluation queries
The system SHALL use the same encoding pattern (no pre-encoding) for all JSONB parameters in evaluation-related database queries, including `insert_evaluation` for `score_breakdown`, `calculator_results`, and `manual_inputs`.

#### Scenario: Saving evaluation record with JSONB fields
- **WHEN** an evaluation is saved with score_breakdown, calculator_results, and manual_inputs
- **THEN** all three JSONB fields are stored as proper JSONB objects (not double-encoded strings)

### Requirement: Scoring uses shared evaluation inputs
The scoring flow SHALL load evaluation inputs by `brand_id` only (not by `user_id`), since inputs are now shared across all users.

#### Scenario: Any user triggers scoring for a brand
- **WHEN** any authenticated user triggers `generate_score` for a brand
- **THEN** the system loads the single shared `evaluation_inputs` row for that brand and uses its `manual_data` for score calculation

#### Scenario: Scoring records the requesting user
- **WHEN** a user generates a score for a brand
- **THEN** the resulting `evaluations` row records that user's ID as the scorer, even though the inputs are shared
