# Phase 1: Data Model Foundation - Research

**Researched:** 2026-03-16
**Domain:** PostgreSQL schema migration (Alembic), asyncpg query layer, FastAPI routing
**Confidence:** HIGH — all findings sourced from live codebase inspection

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Marketplace identifier**
- Country code format: `ID` (Indonesia) and `TH` (Thailand)
- Currency codes (`IDR`, `THB`) derived from marketplace code when needed for display
- Mapping lives in a code constant (`app/core/marketplace.py`), not a DB table
- `MARKETPLACE_CURRENCY = {'ID': 'IDR', 'TH': 'THB'}` and `MARKETPLACE_LABELS` dict

**Marketplace column type**
- `VARCHAR(2) NOT NULL` with `CHECK (marketplace IN ('ID', 'TH'))`
- Not a PostgreSQL ENUM — easier to extend later with ALTER

**scoring_rules schema change**
- Add `marketplace VARCHAR(2) NOT NULL DEFAULT 'ID'` column
- Change UNIQUE constraint from `(template)` to `(template, marketplace)`
- Existing "default" row backfilled as `marketplace = 'ID'`
- New THB row inserted: `default/TH` (2 total rows: default/ID, default/TH)

**evaluation_inputs schema change**
- Add `marketplace VARCHAR(2) NOT NULL DEFAULT 'ID'` column
- UNIQUE constraint stays on `(brand_id)` — one row per brand, marketplace is just another editable field
- All existing rows backfilled to `marketplace = 'ID'`
- A brand can switch marketplace between evaluations by updating the field

**evaluations schema change**
- Add `marketplace VARCHAR(2) NOT NULL DEFAULT 'ID'` column
- All existing evaluations backfilled to `marketplace = 'ID'`
- NOT NULL — no NULL handling needed anywhere
- Marketplace copied from evaluation_inputs at scoring time

**THB threshold derivation**
- Fixed conversion rate `0.0019` (1 IDR = 0.0019 THB) hard-coded in migration
- Only currency-denominated thresholds converted (e.g., `six_month_avg_threshold: 100,000,000` → THB equivalent)
- Percentage thresholds, counts, and ratios stay the same across marketplaces
- Exact conversion — no rounding to clean numbers
- Claude's discretion: scan full rules JSONB to identify all currency-denominated values

**Migration strategy**
- Two-step Alembic pattern: add column with DEFAULT → backfill → set NOT NULL
- Single migration file covering all three tables (scoring_rules, evaluation_inputs, evaluations)
- THB rules seeded in the same migration

**API fallback behavior**
- All existing endpoints default to `marketplace = 'ID'` when param is omitted
- Backward compatible — existing frontend works without changes until Phase 4
- GET /rules without ?marketplace= returns IDR rules
- Scoring engine reads marketplace from evaluation_inputs automatically

**Scoring flow**
- `generate_score` reads `evaluation_inputs.marketplace` for the brand
- Fetches rules with `WHERE template=$1 AND marketplace=$2`
- Stores marketplace on the evaluation record at insert time
- Caller doesn't need to pass marketplace explicitly

### Claude's Discretion

- Exact set of currency-denominated rule values needing THB conversion (scan rules JSONB)
- Migration file numbering and naming
- Whether to split into multiple migrations or keep as one
- Index strategy for the new marketplace columns

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| DATA-01 | Evaluation stores marketplace selection (ID or TH) chosen by user at evaluation time | evaluations + evaluation_inputs tables both receive marketplace column; upsert/insert queries updated |
| DATA-02 | Scoring rules table supports marketplace dimension (IDR rules and THB rules coexist) | scoring_rules UNIQUE constraint changed from (template) to (template, marketplace); two rows result |
| DATA-03 | THB scoring rule thresholds seeded from IDR conversion (admin-editable after) | Migration seeds default/TH row by copying default/ID and converting currency-denominated fields at 0.0019 |
</phase_requirements>

---

## Summary

This phase is a pure backend schema + migration phase. No frontend changes, no scoring engine behavior changes. Three PostgreSQL tables receive a new `marketplace VARCHAR(2) NOT NULL` column, existing rows are backfilled to `'ID'`, and a THB rules row is seeded. A new `app/core/marketplace.py` constant file is created. Three layers of query code are updated (rules queries, evaluations queries, upsert logic) to pass and filter by marketplace.

The codebase already has 25 Alembic migrations following a well-established pattern. Migration 013 unified `fashion`/`non_fashion` scoring rules into a single `default` template — so the current live state has **one row** in `scoring_rules` with `template = 'default'`. This phase adds a `marketplace` column and converts that one row into two (`default/ID` and `default/TH`).

Key discovery: `generate_score` in `service.py` currently fetches rules using `get_rules_by_template(conn, "default")` — this must be updated to also filter by marketplace read from `evaluation_inputs`. The `evaluation_inputs` table already uses a shared-per-brand model (UNIQUE on `brand_id` only, after migration 015).

**Primary recommendation:** Write a single migration `026_add_marketplace_to_schema.py`, implement `app/core/marketplace.py`, update the three query functions, update the service orchestration. Straightforward, low-risk, fully contained in the backend.

---

## Standard Stack

### Core (already in use — no new installs needed)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Alembic | (project default) | Schema migrations | Already used for all 25 migrations |
| asyncpg | (project default) | Async PostgreSQL driver | All queries use this |
| SQLAlchemy (core only) | (project default) | Alembic helper, `op.add_column`, `sa.Column` | Pattern in migrations 022, others |
| FastAPI | (project default) | API routing | All routers use this |

### No New Dependencies

This phase requires zero new Python package installations. All tooling is present.

---

## Architecture Patterns

### Recommended Project Structure Changes

```
backend/
├── app/
│   ├── core/
│   │   └── marketplace.py          # NEW — constant mapping dict
│   ├── db/
│   │   ├── migrations/versions/
│   │   │   └── 026_add_marketplace_to_schema.py   # NEW — single migration
│   │   └── queries/
│   │       ├── rules.py            # MODIFY — add marketplace param
│   │       └── evaluations.py      # MODIFY — update insert + upsert
│   └── modules/
│       ├── rules/
│       │   ├── router.py           # MODIFY — add optional ?marketplace= param
│       │   ├── service.py          # MODIFY — pass marketplace to query
│       │   └── schemas.py          # MODIFY — add marketplace to response
│       └── evaluations/
│           └── service.py          # MODIFY — read marketplace from inputs, pass to rules query
```

### Pattern 1: Two-Step Alembic Column Addition (NOT NULL)

The project's documented pattern for adding NOT NULL columns to tables with existing data.

```python
# Source: Confirmed from existing migrations (e.g., 022, 015) and STATE.md decisions

def upgrade() -> None:
    # Step 1: Add nullable with DEFAULT (existing rows get 'ID' automatically)
    op.execute("""
        ALTER TABLE scoring_rules
            ADD COLUMN marketplace VARCHAR(2) NOT NULL DEFAULT 'ID'
            CHECK (marketplace IN ('ID', 'TH'));
    """)
    # Step 2: (optional explicit backfill if DEFAULT wasn't used)
    # Step 3: Seed new THB row
    conn = op.get_bind()
    # ... read existing row, convert, insert TH row
    # Step 4: Change UNIQUE constraint
    op.execute("""
        ALTER TABLE scoring_rules
            DROP CONSTRAINT scoring_rules_template_key;
        ALTER TABLE scoring_rules
            ADD CONSTRAINT uq_scoring_rules_template_marketplace
            UNIQUE (template, marketplace);
    """)
```

**Important:** Because `NOT NULL DEFAULT 'ID'` is used, PostgreSQL fills existing rows immediately on the ALTER TABLE. No separate backfill UPDATE is needed for this case. The CHECK constraint fires at row-insert time for new rows.

### Pattern 2: Migration Uses `conn = op.get_bind()` + `sa.text()`

Every migration that manipulates data (not just DDL) uses this pattern:

```python
# Source: migrations/010, 013, 015 — all use this exact pattern
import sqlalchemy as sa
from alembic import op

conn = op.get_bind()
row = conn.execute(
    sa.text("SELECT rules, version FROM scoring_rules WHERE template = :t AND marketplace = :m"),
    {"t": "default", "m": "ID"},
).fetchone()
```

### Pattern 3: Query Functions — asyncpg positional params ($1, $2)

```python
# Source: backend/app/db/queries/rules.py (existing pattern)
async def get_rules_by_template_and_marketplace(
    conn: Connection,
    template: str,
    marketplace: str,
) -> RuleRow | None:
    return await fetch_one(
        conn,
        """
        SELECT id, template, marketplace, rules, version, updated_by, updated_at
        FROM scoring_rules
        WHERE template = $1 AND marketplace = $2
        """,
        template,
        marketplace,
    )
```

### Pattern 4: `app/core/marketplace.py` Constant Module

```python
# Source: CONTEXT.md decision — new file, follows app/core/utils.py, app/core/exceptions.py pattern

MARKETPLACE_CURRENCY: dict[str, str] = {
    "ID": "IDR",
    "TH": "THB",
}

MARKETPLACE_LABELS: dict[str, str] = {
    "ID": "Indonesia",
    "TH": "Thailand",
}

VALID_MARKETPLACES: tuple[str, ...] = tuple(MARKETPLACE_CURRENCY.keys())
```

### Pattern 5: FastAPI Optional Query Parameter with Default

```python
# Source: CONTEXT.md decision + existing router pattern in rules/router.py
from typing import Annotated
from fastapi import Query

@router.get("", response_model=list[ScoringRuleResponse])
async def list_rules(
    marketplace: Annotated[str, Query()] = "ID",
    current_user: dict = Depends(require_role("leader", "admin")),
) -> list[ScoringRuleResponse]:
    return await get_all_rules(marketplace=marketplace)
```

### Anti-Patterns to Avoid

- **Using a DB table for marketplace lookup:** Decided against — use `app/core/marketplace.py` constants only
- **PostgreSQL ENUM for marketplace:** Decided against — use VARCHAR(2) + CHECK constraint for easier future extension
- **Multiple migration files:** Decided against — all three tables in one migration for atomicity
- **Rounding THB values:** Decided against — exact conversion, admins adjust later
- **Passing marketplace as explicit caller param to `generate_score`:** Decided against — service reads it from `evaluation_inputs.marketplace` automatically

---

## Current State — Critical Observations

### scoring_rules actual state (post-migration 013)

After migration 013, the table has **one row**: `template = 'default'`. Migrations 010 seeded `fashion` and `non_fashion`, but 013 unified them and deleted both, inserting `default`.

The UNIQUE constraint was created as `template VARCHAR(20) UNIQUE NOT NULL` in migration 010 — PostgreSQL auto-names this `scoring_rules_template_key`. Migration 013 did not rename the constraint. This is the constraint the new migration must `DROP CONSTRAINT scoring_rules_template_key`.

### Currency-denominated values in the current "default" rules JSONB

Based on inspection of migration 010 (seeded values) and 013 (unified), the JSONB structure is:

```
operational:
  unfulfilled_order_rate.threshold = 1.0        → PERCENTAGE — no conversion
  late_shipment_rate.threshold = 1.0             → PERCENTAGE — no conversion
  preparation_time.threshold = 1.0               → TIME (days) — no conversion
  chat_response_rate.threshold = 95.0            → PERCENTAGE — no conversion
  overall_rating.threshold = 4.7                 → RATIO — no conversion

business:
  monthly_sales_trend.threshold_pct = 90.0       → PERCENTAGE — no conversion
  six_month_avg_threshold.threshold = 100000000  → IDR CURRENCY *** CONVERT ***
  conversion_rate.threshold = 3.0                → PERCENTAGE — no conversion

content:
  quality_ratio.threshold = 95.0                 → PERCENTAGE — no conversion

visitors:
  returning_visitors_pct.threshold = 23.0        → PERCENTAGE — no conversion
  followers.threshold = 50000                    → COUNT — no conversion

promo_tools:
  usage_pct_threshold.threshold = 80.0           → PERCENTAGE — no conversion
  effectiveness_pct_threshold.threshold = 90.0   → PERCENTAGE — no conversion

products_status:
  product_count.threshold = 35                   → COUNT — no conversion
  store_status_points.mall/star_plus/... = 10/5/0 → SCORE POINTS — no conversion

ads:
  roi_threshold.threshold = 9.0                  → RATIO — no conversion
  gmv_ratio_threshold.threshold = 84.0           → PERCENTAGE — no conversion
  cost_ratio_range.min/max = 5.0/10.0            → PERCENTAGE — no conversion

campaign:
  participation_pct_threshold.threshold = 90.0   → PERCENTAGE — no conversion

stock:
  high_threshold.threshold = 24                  → COUNT (weeks) — no conversion
  mid_threshold.threshold = 12                   → COUNT (weeks) — no conversion
  low_penalty.threshold = 12                     → COUNT (weeks) — no conversion

discount:
  fake_discount_flag.points_no_flag/flag = 5/0   → SCORE POINTS — no conversion

interpretation:
  ranges[].min/max = 71/41/40                    → SCORE POINTS — no conversion

marketing (added in migration 011, see STATE.md):
  floor.value, floor_fashion.value               → PERCENTAGE RATIOS — no conversion
  fashion_adjustment.value                       → PERCENTAGE — no conversion
```

**Conclusion:** Only `business.six_month_avg_threshold.threshold` is currency-denominated. THB value = `100000000 * 0.0019 = 190000.0`.

Note: Later migrations (011, 012, 016–021) may have added additional fields to the JSONB. The planner should verify by reading migrations 011–021 before finalizing the THB conversion dict. The implementer should scan the live `default` row's rules JSONB at migration time using `conn.execute(sa.text("SELECT rules FROM scoring_rules WHERE template='default'")).fetchone()` to confirm no additional currency fields were added.

### evaluation_inputs UNIQUE constraint (post-migration 015)

Constraint name: `uq_evaluation_inputs_brand` on `(brand_id)`. The `upsert_evaluation_inputs` function uses `ON CONFLICT (brand_id)`. Adding `marketplace` column does NOT change this — marketplace is updated via the normal COALESCE upsert path.

### evaluations table — no UNIQUE constraint

`evaluations` is INSERT-only (immutable snapshots). No constraint changes needed for evaluations — only column addition.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Marketplace validation | Custom validator class | CHECK constraint in DB + Pydantic `Literal["ID", "TH"]` | DB enforces at write time; Pydantic at API time |
| Currency conversion at runtime | Dynamic exchange rate fetch | Hard-coded 0.0019 in migration only | Thresholds are static config, not live converted |
| Marketplace → currency mapping | DB lookup table | `app/core/marketplace.py` dict constant | Immutable, testable, zero DB round-trips |
| JSONB deep-merge for rules | Custom recursive merge | Full replace (existing `update_rules` pattern) | Existing pattern already tested |

---

## Common Pitfalls

### Pitfall 1: Constraint Name Collision

**What goes wrong:** `DROP CONSTRAINT scoring_rules_template_key` fails if the name differs from the auto-assigned PostgreSQL name.
**Why it happens:** PostgreSQL auto-names inline UNIQUE constraints as `{table}_{column}_key`. The migration 010 used `UNIQUE NOT NULL` inline on `template`, so the constraint is `scoring_rules_template_key`.
**How to avoid:** Use `DROP CONSTRAINT IF EXISTS scoring_rules_template_key` in the migration. Verify with `\d scoring_rules` in psql before writing the migration if there is any doubt.
**Warning signs:** Migration fails on `DROP CONSTRAINT` step with "constraint does not exist."

### Pitfall 2: Forgetting the CHECK Constraint on All Three Tables

**What goes wrong:** marketplace column accepts arbitrary 2-char strings (e.g., 'XX') if CHECK is omitted from one table.
**Why it happens:** Each `ALTER TABLE` must independently add the CHECK constraint.
**How to avoid:** Include `CHECK (marketplace IN ('ID', 'TH'))` on all three ADD COLUMN statements.

### Pitfall 3: `get_rules_by_template` Still Called Without Marketplace

**What goes wrong:** Phase 2 scoring breaks or silently returns None after this migration — the old function queries `WHERE template = $1` and will return both rows if marketplace column doesn't filter.
**Why it happens:** `generate_score` in `service.py` calls `rules_queries.get_rules_by_template(conn, "default")`. After this migration, that query returns two rows but `fetch_one` returns only the first match (non-deterministic order).
**How to avoid:** Phase 1 MUST update `rules.py` to add `get_rules_by_template_and_marketplace` AND update `generate_score` in `service.py` to read `eval_inputs["marketplace"]` and pass it to the new query. The old `get_rules_by_template` can remain for backward compat with the rules API default-ID path.
**Warning signs:** Scoring returns wrong rules or `None` for rules after migration.

### Pitfall 4: `upsert_evaluation_inputs` RETURNING Clause Missing `marketplace`

**What goes wrong:** Service code reads `row["marketplace"]` but it's not in the RETURNING clause — KeyError at runtime.
**Why it happens:** `upsert_evaluation_inputs` has an explicit `RETURNING id, brand_id, last_edited_by, category_type, manual_data, created_at, updated_at` — `marketplace` is not listed.
**How to avoid:** Update RETURNING clause and `EvaluationInputsRow` TypedDict to include `marketplace`.

### Pitfall 5: `insert_evaluation` Positional Parameter Shift

**What goes wrong:** asyncpg raises "too many/few parameters" or binds wrong value to wrong column.
**Why it happens:** `insert_evaluation` uses positional `$1`–`$11` params. Adding `marketplace` as `$12` requires careful update of both the SQL and the `fetch_one` call arguments.
**How to avoid:** Add `marketplace` as the last parameter (`$12`) and append it last in the `fetch_one` call. Update `InsertedEvaluationRow` TypedDict if marketplace needs to be in the return.

### Pitfall 6: Rules API `get_all_rules` Returns Both Rows Without Filtering

**What goes wrong:** Existing `GET /api/v1/rules` returns both ID and TH rows, breaking tests that assert `len(data) == 1`.
**Why it happens:** `get_all_rules` runs `SELECT ... FROM scoring_rules ORDER BY template` — after migration there are 2 rows.
**How to avoid:** Update `get_all_rules` to accept `marketplace: str = "ID"` parameter. Update `rules/router.py` to accept optional `?marketplace=` query param (default "ID"). Backward compatible — existing frontend gets IDR rules without changes.

---

## Code Examples

### Migration: Add marketplace column (two-step for NOT NULL)

```python
# Source: live codebase — migrations/010, 013, 015, 022 patterns combined

revision = "026"
down_revision = "025"

def upgrade() -> None:
    import json
    import sqlalchemy as sa
    from alembic import op

    conn = op.get_bind()

    # --- scoring_rules ---
    # Step 1: Add column with DEFAULT (fills existing rows to 'ID' automatically)
    op.execute("""
        ALTER TABLE scoring_rules
            ADD COLUMN marketplace VARCHAR(2) NOT NULL DEFAULT 'ID'
                CHECK (marketplace IN ('ID', 'TH'));
    """)

    # Step 2: Drop old UNIQUE(template), add UNIQUE(template, marketplace)
    op.execute("""
        ALTER TABLE scoring_rules
            DROP CONSTRAINT IF EXISTS scoring_rules_template_key,
            ADD CONSTRAINT uq_scoring_rules_template_marketplace
                UNIQUE (template, marketplace);
    """)

    # Step 3: Seed THB row — read current 'default/ID' row, convert, insert
    row = conn.execute(
        sa.text("SELECT rules, version FROM scoring_rules WHERE template = 'default' AND marketplace = 'ID'")
    ).fetchone()
    if row:
        rules = json.loads(row[0]) if isinstance(row[0], str) else dict(row[0])
        THB_RATE = 0.0019
        # Convert only currency-denominated threshold(s)
        rules["business"]["six_month_avg_threshold"]["threshold"] = (
            rules["business"]["six_month_avg_threshold"]["threshold"] * THB_RATE
        )
        conn.execute(
            sa.text(
                "INSERT INTO scoring_rules (template, marketplace, rules, version, updated_at) "
                "VALUES ('default', 'TH', CAST(:rules AS jsonb), :version, NOW())"
            ),
            {"rules": json.dumps(rules), "version": row[1]},
        )

    # --- evaluation_inputs ---
    op.execute("""
        ALTER TABLE evaluation_inputs
            ADD COLUMN marketplace VARCHAR(2) NOT NULL DEFAULT 'ID'
                CHECK (marketplace IN ('ID', 'TH'));
    """)

    # --- evaluations ---
    op.execute("""
        ALTER TABLE evaluations
            ADD COLUMN marketplace VARCHAR(2) NOT NULL DEFAULT 'ID'
                CHECK (marketplace IN ('ID', 'TH'));
    """)
```

### Updated `RuleRow` TypedDict

```python
# Source: backend/app/db/queries/rules.py — add marketplace field

class RuleRow(TypedDict):
    id: int
    template: str
    marketplace: str          # NEW
    rules: dict[str, Any]
    version: int
    updated_by: int | None
    updated_at: datetime
```

### Updated `get_rules_by_template_and_marketplace`

```python
# Source: extends existing get_rules_by_template pattern

async def get_rules_by_template_and_marketplace(
    conn: Connection,
    template: str,
    marketplace: str,
) -> RuleRow | None:
    """Get scoring rules for a specific template and marketplace."""
    return await fetch_one(
        conn,
        """
        SELECT id, template, marketplace, rules, version, updated_by, updated_at
        FROM scoring_rules
        WHERE template = $1 AND marketplace = $2
        """,
        template,
        marketplace,
    )
```

### Updated `get_all_rules` with marketplace filter

```python
# Source: extends existing get_all_rules pattern

async def get_all_rules(conn: Connection, marketplace: str = "ID") -> list[RuleRow]:
    """Get all scoring rules for a marketplace, ordered by template."""
    return await fetch_all(
        conn,
        """
        SELECT id, template, marketplace, rules, version, updated_by, updated_at
        FROM scoring_rules
        WHERE marketplace = $1
        ORDER BY template
        """,
        marketplace,
    )
```

### Updated `upsert_evaluation_inputs` signature and RETURNING

```python
# Source: extends existing upsert pattern in evaluations.py

async def upsert_evaluation_inputs(
    conn: Connection,
    brand_id: int,
    last_edited_by: int,
    category_type: str | None,
    manual_data: dict[str, Any] | None,
    marketplace: str | None = None,    # NEW — None means preserve existing
) -> EvaluationInputsRow:
    return await fetch_one(
        conn,
        """
        INSERT INTO evaluation_inputs
            (brand_id, last_edited_by, category_type, manual_data, marketplace, updated_at)
        VALUES ($1, $2, $3, $4, COALESCE($5, 'ID'), NOW())
        ON CONFLICT (brand_id) DO UPDATE SET
            last_edited_by = EXCLUDED.last_edited_by,
            category_type = COALESCE(EXCLUDED.category_type, evaluation_inputs.category_type),
            manual_data = COALESCE(EXCLUDED.manual_data, evaluation_inputs.manual_data),
            marketplace = COALESCE(EXCLUDED.marketplace, evaluation_inputs.marketplace),
            updated_at = NOW()
        RETURNING id, brand_id, last_edited_by, category_type, manual_data,
                  marketplace, created_at, updated_at
        """,
        brand_id,
        last_edited_by,
        category_type,
        manual_data,
        marketplace,
    )
```

### Updated `insert_evaluation` with marketplace

```python
# Source: extends existing insert_evaluation in evaluations.py — add $12 param

async def insert_evaluation(
    conn: Connection,
    brand_id: int,
    user_id: int,
    template: str,
    final_score: float,
    verdict: str,
    score_breakdown: list[dict[str, Any]],
    calculator_results: dict[str, Any],
    manual_inputs: dict[str, Any],
    rule_version: int = 1,
    email_output: str | None = None,
    period: str = "",
    marketplace: str = "ID",          # NEW
) -> InsertedEvaluationRow:
    return await fetch_one(
        conn,
        """
        INSERT INTO evaluations (
            brand_id, user_id, template, final_score, verdict,
            score_breakdown, calculator_results, manual_inputs,
            rule_version, email_output, period, marketplace
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
        RETURNING id, brand_id, final_score, verdict, template, created_at, period
        """,
        brand_id, user_id, template, final_score, verdict,
        score_breakdown, calculator_results, manual_inputs,
        rule_version, email_output, period, marketplace,
    )
```

### Updated `generate_score` service orchestration

```python
# Source: backend/app/modules/evaluations/service.py — add marketplace read + pass through

async def generate_score(conn, brand_id, user_id, template, verdict, store_name, period, brand_name, email=None):
    # ... existing brand validation ...
    eval_inputs = await eval_queries.get_evaluation_inputs(conn, brand_id)
    manual_data = ensure_dict((eval_inputs or {}).get("manual_data"))
    marketplace = (eval_inputs or {}).get("marketplace", "ID")    # NEW

    # ... existing calc_rows fetch ...

    # Load rules for the brand's marketplace
    rule_row = await rules_queries.get_rules_by_template_and_marketplace(conn, "default", marketplace)  # CHANGED

    # ... rest unchanged ...
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| fashion + non_fashion templates | Single "default" template | Migration 013 | Phase 1 seeds default/ID + default/TH (not fashion/TH, non_fashion/TH) |
| UNIQUE(brand_id, user_id) on evaluation_inputs | UNIQUE(brand_id) — one row per brand | Migration 015 | marketplace column safe to add without constraint conflict |
| `get_rules_by_template(conn, template)` | `get_rules_by_template_and_marketplace(conn, template, marketplace)` | This phase | Old function still usable with default marketplace='ID' for backward compat |

**Key insight from migration 013:** The "default" template unification means Phase 1 only needs to insert ONE new THB rules row (for "default/TH"), not multiple template variants. This simplifies the seeding logic.

---

## Open Questions

1. **Additional currency-denominated fields added by migrations 011–021**
   - What we know: Migrations 011 (marketing rules) and 012 (message templates) added new JSONB fields. Marketing fields are percentage ratios (floor 0.12, 0.15), not currency amounts.
   - What's unclear: Whether any message template fields in migrations 016–021 contain currency values embedded in strings.
   - Recommendation: The migration should programmatically read the live `default` row and only convert `business.six_month_avg_threshold.threshold`. If any other field is currency-denominated, the implementer will catch it by inspecting the live JSONB at migration-write time. This is low risk — the only IDR amount identified in the original seed data is `six_month_avg_threshold`.

2. **Index on marketplace columns**
   - What we know: Claude's discretion per CONTEXT.md. The existing pattern: `idx_scoring_rules_template` exists; `idx_evaluations_brand_id` and `idx_evaluations_created_at` exist.
   - Recommendation: Add a composite index `idx_scoring_rules_template_marketplace ON scoring_rules (template, marketplace)` — replaces the old single-column index. For `evaluation_inputs` and `evaluations`, marketplace filtering will not be a primary query pattern in Phase 1 (Phase 4 adds filtering), so defer those indexes.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest with pytest-asyncio |
| Config file | `backend/pyproject.toml` — `asyncio_mode = "auto"`, `testpaths = ["tests"]` |
| Quick run command | `cd backend && uv run pytest tests/integration/api/test_rules.py tests/unit/ -x -q` |
| Full suite command | `cd backend && uv run pytest -x -q` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| DATA-01 | evaluation_inputs stores marketplace; upsert preserves it | unit | `uv run pytest tests/unit/evaluations/test_queries.py -x` | ❌ Wave 0 |
| DATA-01 | evaluations row has marketplace on insert | unit | `uv run pytest tests/unit/evaluations/test_queries.py -x` | ❌ Wave 0 |
| DATA-02 | scoring_rules has two rows (default/ID, default/TH) post-migration | integration | `uv run pytest tests/integration/api/test_rules.py -x` | ✅ (needs update) |
| DATA-02 | GET /rules?marketplace=ID returns IDR row only | integration | `uv run pytest tests/integration/api/test_rules.py -x` | ✅ (needs update) |
| DATA-02 | GET /rules?marketplace=TH returns THB row only | integration | `uv run pytest tests/integration/api/test_rules.py -x` | ✅ (needs update) |
| DATA-03 | THB six_month_avg_threshold = IDR value × 0.0019 | unit | `uv run pytest tests/unit/marketplace/test_marketplace.py -x` | ❌ Wave 0 |
| DATA-03 | Non-currency thresholds identical between ID and TH rows | unit | `uv run pytest tests/unit/marketplace/test_marketplace.py -x` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `cd backend && uv run pytest tests/unit/ -x -q`
- **Per wave merge:** `cd backend && uv run pytest -x -q`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `tests/unit/evaluations/test_queries.py` — unit tests for `insert_evaluation` with marketplace param and `upsert_evaluation_inputs` with marketplace COALESCE
- [ ] `tests/unit/marketplace/test_marketplace.py` — tests for `app/core/marketplace.py` constants and THB conversion correctness
- [ ] `tests/unit/marketplace/__init__.py` — package init
- [ ] Existing `tests/integration/api/test_rules.py` needs updates — currently asserts `len(data) == 1` which will fail if `get_all_rules` returns both rows. Test must be updated to pass `?marketplace=ID` and assert 1 row.

---

## Sources

### Primary (HIGH confidence)

- Live codebase inspection — `backend/app/db/migrations/versions/010_create_scoring_rules_table.py` — original scoring_rules schema, JSONB seed data
- Live codebase inspection — `backend/app/db/migrations/versions/013_unify_scoring_rules_template.py` — current state: one "default" template
- Live codebase inspection — `backend/app/db/migrations/versions/015_shared_evaluation_inputs.py` — current UNIQUE constraint on evaluation_inputs
- Live codebase inspection — `backend/app/db/migrations/versions/022_add_period_to_evaluations.py` — column-add migration pattern using `op.add_column`
- Live codebase inspection — `backend/app/db/queries/rules.py` — current query signatures
- Live codebase inspection — `backend/app/db/queries/evaluations.py` — `insert_evaluation` positional params, `upsert_evaluation_inputs` RETURNING clause
- Live codebase inspection — `backend/app/modules/evaluations/service.py` — `generate_score` orchestration, where marketplace read must be inserted
- Live codebase inspection — `backend/app/modules/rules/router.py`, `service.py`, `schemas.py` — rules API structure
- Live codebase inspection — `backend/tests/conftest.py`, `tests/integration/api/test_rules.py` — test infrastructure
- `.planning/phases/01-data-model-foundation/01-CONTEXT.md` — all user decisions

### Secondary (MEDIUM confidence)

- `.planning/codebase/ARCHITECTURE.md` — module pattern, data flow descriptions
- `.planning/codebase/CONVENTIONS.md` — naming, async patterns, error handling

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new dependencies, all tooling confirmed live
- Architecture: HIGH — all patterns verified from existing migration files
- Currency-denominated field identification: MEDIUM — based on migration 010 seed data; later migrations (011–021) should be spot-checked by implementer for any additional currency fields added to the JSONB
- Pitfalls: HIGH — each pitfall is traceable to a specific existing code pattern

**Research date:** 2026-03-16
**Valid until:** 2026-04-16 (stable backend stack)