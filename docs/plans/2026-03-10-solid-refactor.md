# SOLID Principles Refactoring — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers-extended-cc:executing-plans to implement this plan task-by-task.

**Goal:** Refactor backend and frontend to better adhere to SOLID principles without changing any behavior.

**Architecture:** Extract-don't-rewrite approach. Move existing code into new modules/files, use barrel re-exports to preserve all import paths. Tests must pass after every step.

**Tech Stack:** Python/FastAPI (backend), React/TypeScript (frontend)

---

## Phase 1: Backend — Single Responsibility Fixes

### Task 1: Extract scoring models to `calculators/scoring/models.py`

**Files:**
- Create: `backend/app/calculators/scoring/__init__.py`
- Create: `backend/app/calculators/scoring/models.py`
- Modify: `backend/app/calculators/scoring.py` (will become the package)

**Step 1: Create the scoring package directory**

```bash
mkdir -p backend/app/calculators/scoring
```

**Step 2: Create `models.py` with dataclasses extracted from `scoring.py` lines 10-61**

```python
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class RowScore:
    """Individual row in a scoring category."""

    row: int
    label: str
    value: str
    weight: float
    score: float
    max_score: float
    note: str = ""


@dataclass
class CategoryScore:
    """Aggregated score for a single category."""

    category: str
    rows: list[RowScore] = field(default_factory=list)
    subtotal: float = 0.0
    max_subtotal: float = 0.0


@dataclass
class ScoringResult:
    """Final output of the scoring calculator."""

    total_score: float
    category_scores: list[CategoryScore]
    verdict: str
    conclusion: str
    marketing_estimation: str
    marketing_percentage: str
    marketing_budget: str
    closing_message: str
    email_subject: str
    email_body: str
    template: str
    rule_version: int = 1
```

**Step 3: Update `scoring.py` to import from `models.py` instead of defining inline**

Remove the `RowScore`, `CategoryScore`, `ScoringResult` dataclass definitions (lines 22-61) from `scoring.py` and replace with:

```python
from app.calculators.scoring.models import CategoryScore, RowScore, ScoringResult
```

**Step 4: Create `__init__.py` that re-exports everything from the old `scoring.py`**

Wait — we can't have both `scoring.py` and `scoring/` in the same directory. We need to:
1. Rename `scoring.py` → `scoring/_calculator.py`
2. Create `scoring/__init__.py` that re-exports from `_calculator.py`

Actually, let's do this properly:

```bash
# Move the original file into the package
mv backend/app/calculators/scoring.py backend/app/calculators/_scoring_old.py
mkdir -p backend/app/calculators/scoring
mv backend/app/calculators/_scoring_old.py backend/app/calculators/scoring/_calculator.py
```

Create `backend/app/calculators/scoring/__init__.py`:
```python
"""Scoring calculator package.

Re-exports all public names from the original scoring module so that
existing imports like `from app.calculators.scoring import calculate_score`
continue to work.
"""

from app.calculators.scoring._calculator import (  # noqa: F401
    DEFAULT_RULES,
    CategoryScore,
    RowScore,
    ScoringResult,
    calculate_score,
)
```

Then update `_calculator.py` to import models from `models.py` instead of defining them inline.

**Step 5: Run tests**

```bash
cd backend && uv run pytest -x -q
```

Expected: All tests pass — imports are preserved via `__init__.py`.

**Step 6: Commit**

```bash
git add backend/app/calculators/scoring/
git commit -m "Extract scoring module into package with models.py"
```

---

### Task 2: Extract scoring helpers to `calculators/scoring/helpers.py`

**Files:**
- Create: `backend/app/calculators/scoring/helpers.py`
- Modify: `backend/app/calculators/scoring/_calculator.py`

**Step 1: Create `helpers.py` with helper functions from `_calculator.py` lines 68-211**

Move these functions to `helpers.py`:
- `INDO_MONTHS` (line 68)
- `_generate_month_labels` (line 71)
- `_safe_num` (line 92)
- `_safe_str` (line 109)
- `_get_nested` (line 116)
- `_fmt_pct_1dp` (line 128)
- `_fmt_pct_0dp` (line 133)
- `_fmt_num_1dp` (line 138)
- `_fmt_num_2dp` (line 143)
- `_fmt_idr` (line 148)
- `_rounddown` (line 156)
- `_extract_pct` (line 162)
- `_get_rule_category` (line 183)
- `_get_rule_value` (line 190)
- `_SafeDict` (line 195)
- `_format_message_template` (line 202)

Add required imports at top of `helpers.py`:
```python
from __future__ import annotations

import math
import re
from typing import Any
```

**Step 2: Update `_calculator.py` to import from `helpers.py`**

Replace removed definitions with:
```python
from app.calculators.scoring.helpers import (
    INDO_MONTHS,
    _SafeDict,
    _extract_pct,
    _fmt_idr,
    _fmt_num_1dp,
    _fmt_num_2dp,
    _fmt_pct_0dp,
    _fmt_pct_1dp,
    _format_message_template,
    _generate_month_labels,
    _get_nested,
    _get_rule_category,
    _get_rule_value,
    _rounddown,
    _safe_num,
    _safe_str,
)
```

**Step 3: Run tests**

```bash
cd backend && uv run pytest -x -q
```

**Step 4: Commit**

```bash
git add backend/app/calculators/scoring/helpers.py backend/app/calculators/scoring/_calculator.py
git commit -m "Extract scoring helpers to dedicated module"
```

---

### Task 3: Extract scoring rules to `calculators/scoring/rules.py`

**Files:**
- Create: `backend/app/calculators/scoring/rules.py`
- Modify: `backend/app/calculators/scoring/_calculator.py`
- Modify: `backend/app/calculators/scoring/__init__.py`

**Step 1: Create `rules.py` with constants from `_calculator.py` lines 225-454**

Move these to `rules.py`:
- `DEFAULT_RULES` (lines 225-431)
- `PROMO_TOOLS` (lines 439-451)
- `PROMO_START_ROW` (line 454)

```python
"""Default scoring rules and promo tool configuration."""

from typing import Any

DEFAULT_RULES: dict[str, Any] = {
    # ... exact content from lines 225-431
}

PROMO_TOOLS: list[tuple[str, str, float]] = [
    # ... exact content from lines 439-451
]

PROMO_START_ROW: int = 31
```

**Step 2: Update `_calculator.py` to import from `rules.py`**

```python
from app.calculators.scoring.rules import DEFAULT_RULES, PROMO_START_ROW, PROMO_TOOLS
```

**Step 3: Update `__init__.py` to re-export `DEFAULT_RULES`**

`DEFAULT_RULES` is imported by test files, so ensure `__init__.py` still re-exports it. It already does via the `_calculator` import, but verify after the move.

**Step 4: Run tests**

```bash
cd backend && uv run pytest -x -q
```

**Step 5: Commit**

```bash
git add backend/app/calculators/scoring/rules.py backend/app/calculators/scoring/_calculator.py
git commit -m "Extract scoring rules and constants to dedicated module"
```

---

### Task 4: Extract scoring messages to `calculators/scoring/messages.py`

**Files:**
- Create: `backend/app/calculators/scoring/messages.py`
- Modify: `backend/app/calculators/scoring/_calculator.py`

**Step 1: Create `messages.py` with message generators from `_calculator.py` lines 1073-1395**

Move these functions:
- `_generate_operational_messages` (line 1073)
- `_generate_business_messages` (line 1114)
- `_generate_visitors_messages` (line 1157)
- `_generate_promo_messages` (line 1184)
- `_generate_products_messages` (line 1242)
- `_generate_ads_messages` (line 1269)
- `_generate_campaign_messages` (line 1336)
- `_generate_competition_messages` (line 1358)

Add imports they need from `helpers.py`:
```python
from app.calculators.scoring.helpers import (
    _format_message_template,
    _get_rule_category,
    _safe_num,
    # ... whatever else these functions use
)
from app.calculators.scoring.models import CategoryScore, RowScore
```

**Step 2: Update `_calculator.py` to import from `messages.py`**

**Step 3: Run tests**

```bash
cd backend && uv run pytest -x -q
```

**Step 4: Commit**

```bash
git add backend/app/calculators/scoring/messages.py backend/app/calculators/scoring/_calculator.py
git commit -m "Extract scoring message generators to dedicated module"
```

---

### Task 5: Extract category scorers to `calculators/scoring/categories.py`

**Files:**
- Create: `backend/app/calculators/scoring/categories.py`
- Modify: `backend/app/calculators/scoring/_calculator.py`

**Step 1: Create `categories.py` with category scoring functions from `_calculator.py` lines 461-1071**

Move these functions:
- `_score_operational` (line 461)
- `_score_business` (line 542)
- `_score_visitors` (line 611)
- `_promo_verdict` (line 662)
- `_score_promo_tools` (line 683)
- `_score_products` (line 746)
- `_score_ads` (line 792)
- `_score_campaign` (line 872)
- `_score_competition` (line 910)
- `_score_stock` (line 948)
- `_score_discount_row` (line 1028)

Add imports from `helpers.py`, `models.py`, and `rules.py` as needed.

**Step 2: Update `_calculator.py` to import from `categories.py`**

**Step 3: Run tests**

```bash
cd backend && uv run pytest -x -q
```

Note: Some tests import private scoring functions like `_score_business` directly. Update `__init__.py` to re-export any that tests import:

```python
# In __init__.py, add test-used private names
from app.calculators.scoring.categories import (  # noqa: F401
    _score_business,
    _score_products,
    _score_visitors,
)
```

**Step 4: Commit**

```bash
git add backend/app/calculators/scoring/categories.py backend/app/calculators/scoring/_calculator.py backend/app/calculators/scoring/__init__.py
git commit -m "Extract category scoring functions to dedicated module"
```

---

### Task 6: Extract email/computation helpers to `calculators/scoring/computations.py`

**Files:**
- Create: `backend/app/calculators/scoring/computations.py`
- Modify: `backend/app/calculators/scoring/_calculator.py`

**Step 1: Create `computations.py` with remaining helper functions from `_calculator.py` lines 1396-1602**

Move these functions:
- `_parse_d73_percentages` (line 1396)
- `_compute_g68` (line 1409)
- `_parse_g68_left` (line 1430)
- `_compute_g72` (line 1446)
- `_compute_g73` (line 1496)
- `_compute_g66` (line 1521)
- `_compute_g75` (line 1580)
- `_assemble_email_body` (line 1603)

**Step 2: Update `_calculator.py` to import from `computations.py`**

**Step 3: Run tests**

```bash
cd backend && uv run pytest -x -q
```

**Step 4: Commit**

```bash
git add backend/app/calculators/scoring/computations.py backend/app/calculators/scoring/_calculator.py
git commit -m "Extract scoring computation and email helpers to dedicated module"
```

---

### Task 7: Verify scoring package is clean — `_calculator.py` should be ~100 lines

**Step 1: Verify `_calculator.py` now only contains**

- Imports from the submodules
- The main `calculate_score` function (lines 1721-1829)
- No loose functions or constants

**Step 2: Run full test suite**

```bash
cd backend && uv run pytest -x -q
```

**Step 3: Commit if any cleanup was needed**

---

### Task 8: Extract `upload/service.py` god function into composed steps

**Files:**
- Modify: `backend/app/modules/upload/service.py`

**Step 1: Extract `_validate_upload` from `process_upload` (lines 149-169)**

Create a private function at module level:

```python
async def _validate_upload(
    conn: Connection, upload_id: str, brand_id: int, file_type: str
) -> asyncpg.Record:
    """Validate upload exists and brand matches."""
    # Move validation logic from process_upload lines 149-169
    upload_row = await upload_queries.get_upload(conn=conn, upload_id=upload_id)
    if not upload_row:
        raise UploadException(code="UPLOAD_NOT_FOUND", detail="...")
    if upload_row["brand_id"] != brand_id:
        raise UploadException(code="BRAND_MISMATCH", detail="...")
    if upload_row["status"] != "pending":
        raise UploadException(code="ALREADY_PROCESSED", detail="...")
    return upload_row
```

**Step 2: Extract `_download_and_parse` from `process_upload` (lines 180-218)**

```python
async def _download_and_parse(
    upload_row: dict, file_type: str
) -> list[dict]:
    """Download file from GCS and parse it."""
    # Move download + parse logic from process_upload lines 180-218
    ...
```

**Step 3: Extract `_store_and_trigger` from `process_upload` (lines 230-262)**

```python
async def _store_and_trigger(
    conn: Connection, brand_id: int, file_type: str,
    parsed_data: list[dict], user_id: str
) -> None:
    """Store parsed data and trigger applicable calculators."""
    # Move store + calculator trigger logic from process_upload lines 230-262
    ...
```

**Step 4: Simplify `process_upload` to orchestrate the three functions**

```python
async def process_upload(upload_id, brand_id, file_type, user_id):
    async with db.connection() as conn:
        upload_row = await _validate_upload(conn, upload_id, brand_id, file_type)
        parsed_data = await _download_and_parse(upload_row, file_type)
        await _store_and_trigger(conn, brand_id, file_type, parsed_data, user_id)
        return ProcessUploadResponse(...)
```

**Step 5: Run tests**

```bash
cd backend && uv run pytest -x -q
```

**Step 6: Commit**

```bash
git add backend/app/modules/upload/service.py
git commit -m "Extract upload/service.py god function into composed steps"
```

---

### Task 9: Move calculator business logic from `evaluations/router.py` to service

**Files:**
- Modify: `backend/app/modules/evaluations/router.py`
- Modify: `backend/app/modules/evaluations/service.py`

**Step 1: Add service functions for calculator operations**

Add to `evaluations/service.py`:

```python
async def get_calculator_results(brand_id: int) -> dict:
    """Fetch all calculator results for a brand."""
    async with db.connection() as conn:
        results = await calc_result_queries.get_results_by_brand(
            conn=conn, brand_id=brand_id
        )
        return {r["calculator_type"]: r["result_data"] for r in results}


async def get_calculator_status(brand_id: int) -> dict:
    """Check readiness status of all calculators for a brand."""
    async with db.connection() as conn:
        return await check_calculator_readiness(brand_id=brand_id, conn=conn)


async def run_all_calculators_service(brand_id: int) -> list[dict]:
    """Run all ready calculators for a brand."""
    async with db.connection() as conn:
        return await run_ready_calculators(brand_id=brand_id, conn=conn)
```

**Step 2: Update router endpoints to call service functions**

Replace direct DB calls in `get_calculator_results` (lines 189-211), `run_all_calculators` (lines 266-288), and `get_calculator_status` (lines 295-307) with calls to the new service functions.

**Step 3: Remove now-unused imports from router** (engine imports, db import, query imports)

**Step 4: Run tests**

```bash
cd backend && uv run pytest -x -q
```

**Step 5: Commit**

```bash
git add backend/app/modules/evaluations/router.py backend/app/modules/evaluations/service.py
git commit -m "Move calculator business logic from evaluations router to service"
```

---

### Task 10: Extract `sync/service.py` sheet logic into private functions

**Files:**
- Modify: `backend/app/modules/sync/service.py`

**Step 1: Extract `_sync_vp_sheet` from `run_sync` (lines 109-133)**

```python
async def _sync_vp_sheet(
    conn: Connection, sheets_client: GoogleSheetsClient, settings: Settings
) -> SheetSyncResult:
    """Fetch and sync VP sheet data."""
    # Move VP sheet sync logic from run_sync lines 109-133
    ...
```

**Step 2: Extract `_sync_meeting_sheet` from `run_sync` (lines 136-159)**

```python
async def _sync_meeting_sheet(
    conn: Connection, sheets_client: GoogleSheetsClient, settings: Settings
) -> SheetSyncResult:
    """Fetch and sync Meeting sheet data."""
    # Move Meeting sheet sync logic from run_sync lines 136-159
    ...
```

**Step 3: Simplify `run_sync` to orchestrate**

```python
async def run_sync(sync_id: int | None = None) -> SyncResult:
    async with db.connection() as conn:
        # ... create sync status record ...
        vp_result = await _sync_vp_sheet(conn, sheets_client, settings)
        meeting_result = await _sync_meeting_sheet(conn, sheets_client, settings)
        # ... compute totals, update status ...
```

**Step 4: Run tests**

```bash
cd backend && uv run pytest -x -q
```

**Step 5: Commit**

```bash
git add backend/app/modules/sync/service.py
git commit -m "Extract sync sheet logic into private helper functions"
```

---

## Phase 2: Backend — Open/Closed Improvements

### Task 11: Consolidate calculator engine config into registry

**Files:**
- Modify: `backend/app/calculators/engine.py`

**Step 1: Create `CalculatorConfig` dataclass and consolidate dicts**

Replace the four separate dicts (lines 24-48) with a single registry:

```python
from dataclasses import dataclass, field
from typing import Callable

@dataclass
class CalculatorConfig:
    required_files: list[str]
    required_manual: list[str] = field(default_factory=list)
    runner: Callable = None  # type: ignore[assignment]

CALCULATOR_REGISTRY: dict[str, CalculatorConfig] = {
    "ads_keyword": CalculatorConfig(
        required_files=["cpc_ad_report", "keyword_report"],
        required_manual=["total_products"],
        runner=run_ads_keyword_calculator,
    ),
    "discount": CalculatorConfig(
        required_files=["order_export"],
        runner=run_discount_calculator,
    ),
    "top_sku": CalculatorConfig(
        required_files=["order_export", "mass_update"],
        runner=run_top_sku_calculator,
    ),
}

# Derived lookup — computed once, not manually maintained
FILE_TO_CALCULATORS: dict[str, list[str]] = {}
for calc_name, config in CALCULATOR_REGISTRY.items():
    for file_type in config.required_files:
        FILE_TO_CALCULATORS.setdefault(file_type, []).append(calc_name)
```

**Step 2: Update all references in engine.py**

Replace:
- `CALCULATOR_REQUIRED_FILES[calc]` → `CALCULATOR_REGISTRY[calc].required_files`
- `CALCULATOR_REQUIRED_MANUAL.get(calc, [])` → `CALCULATOR_REGISTRY[calc].required_manual`
- `_CALCULATOR_RUNNERS[calc]` → `CALCULATOR_REGISTRY[calc].runner`
- `FILE_TO_CALCULATORS` stays the same (derived automatically)

**Step 3: Run tests**

```bash
cd backend && uv run pytest -x -q
```

**Step 4: Commit**

```bash
git add backend/app/calculators/engine.py
git commit -m "Consolidate calculator engine config into single registry"
```

---

### Task 12: Strategy pattern for file parsing in `upload/service.py`

**Files:**
- Modify: `backend/app/modules/upload/service.py`

**Step 1: Replace `if/elif` parsing branches with parser registry**

Replace the hard-coded parsing branches in `_download_and_parse` with:

```python
from typing import Callable

_PARSERS: dict[str, Callable] = {
    "zip": parse_zip,
    "csv": parse_csv,
    "xlsx": parse_excel,
}

# In _download_and_parse:
parser = _PARSERS.get(extension)
if not parser:
    raise UploadException(code="UNSUPPORTED_FORMAT", detail=f"...")
parsed_data = await parser(file_bytes)
```

**Step 2: Run tests**

```bash
cd backend && uv run pytest -x -q
```

**Step 3: Commit**

```bash
git add backend/app/modules/upload/service.py
git commit -m "Use parser registry instead of if/elif branches for file parsing"
```

---

## Phase 3: Backend — Dependency Inversion

### Task 13: Create `get_db_connection` FastAPI dependency

**Files:**
- Modify: `backend/app/core/dependencies.py`

**Step 1: Add `get_db_connection` generator dependency**

```python
from app.db.connection import db

async def get_db_connection():
    """Yield a database connection from the pool."""
    async with db.connection() as conn:
        yield conn
```

**Step 2: Run tests**

```bash
cd backend && uv run pytest -x -q
```

**Step 3: Commit**

```bash
git add backend/app/core/dependencies.py
git commit -m "Add get_db_connection FastAPI dependency for DI"
```

---

### Task 14: Migrate `evaluations/service.py` to accept `conn` parameter

**Files:**
- Modify: `backend/app/modules/evaluations/service.py`
- Modify: `backend/app/modules/evaluations/router.py`

**Step 1: Update service functions to accept `conn` as a parameter**

Change each service function from:
```python
async def list_evaluations(...):
    async with db.connection() as conn:
        ...
```

To:
```python
async def list_evaluations(*, conn: Connection, ...):
    ...
```

**Step 2: Update router to inject `conn` via `Depends(get_db_connection)`**

```python
from app.core.dependencies import get_db_connection

@router.get("/")
async def list_evaluations_endpoint(
    conn: Connection = Depends(get_db_connection),
    ...
):
    return await service.list_evaluations(conn=conn, ...)
```

**Step 3: Remove `from app.db.connection import db` from service.py**

**Step 4: Run tests**

```bash
cd backend && uv run pytest -x -q
```

**Step 5: Commit**

```bash
git add backend/app/modules/evaluations/service.py backend/app/modules/evaluations/router.py
git commit -m "Inject db connection into evaluations service via FastAPI DI"
```

---

## Phase 4: Frontend — Single Responsibility Fixes

### Task 15: Split `formConfig.ts` into focused modules

**Files:**
- Create: `frontend/src/components/evaluation/forms/types.ts`
- Create: `frontend/src/components/evaluation/forms/defaults.ts`
- Create: `frontend/src/components/evaluation/forms/fields.ts`
- Create: `frontend/src/components/evaluation/forms/formUtils.ts`
- Modify: `frontend/src/components/evaluation/forms/formConfig.ts` (becomes barrel re-export)

**Step 1: Create `types.ts`**

Move from `formConfig.ts`:
- `OperationalData` (lines 3-9)
- `BusinessData` (lines 11-20)
- `VisitorsData` (lines 22-26)
- `PromoToolsData` (lines 28-40)
- `ProductsData` (lines 42-45)
- `AdsData` (lines 47-50)
- `CampaignData` (lines 52-55)
- `CompetitionProduct` (lines 57-63)
- `CompetitionData` (lines 65-69)
- `ManualData` (lines 71-80)
- `InputType` (line 84)
- `FieldDefinition` (lines 86-94)
- `SelectOption` (lines 96-99)
- `CategoryDefinition` (lines 101-105)
- `SectionProgress` (lines 252-255)

**Step 2: Create `defaults.ts`**

Move `EMPTY_MANUAL_DATA` (lines 314-367). Import `ManualData` from `./types`.

**Step 3: Create `fields.ts`**

Move all field definition arrays and constants:
- `STORE_STATUS_OPTIONS` (lines 109-114)
- `SECTION_LINKS` (lines 118-125)
- `INDO_MONTHS`, `GENERIC_LABELS` (lines 129-130)
- `OPERATIONAL_FIELDS` through `COMPETITION_FIELDS` (lines 152-221)
- `MANUAL_DATA_FIELDS` (lines 225-234)

Import types from `./types`.

**Step 4: Create `formUtils.ts`**

Move utility functions:
- `generateMonthLabels` (lines 132-148)
- `formatIDR` (lines 238-241)
- `parseIDR` (lines 243-248)
- `countFilledInFlat` (lines 257-263)
- `computeSectionProgress` (lines 265-310)

Import types from `./types` and fields from `./fields`.

**Step 5: Make `formConfig.ts` a barrel re-export**

```typescript
// Barrel re-export for backward compatibility
export * from './types';
export * from './defaults';
export * from './fields';
export * from './formUtils';
```

**Step 6: Run tests and type-check**

```bash
cd frontend && npm run test:run && npm run build
```

**Step 7: Commit**

```bash
git add frontend/src/components/evaluation/forms/
git commit -m "Split formConfig.ts into types, defaults, fields, and utils modules"
```

---

### Task 16: Extract merge logic from `useAutoSaveForm.ts`

**Files:**
- Create: `frontend/src/hooks/manualDataUtils.ts`
- Modify: `frontend/src/hooks/useAutoSaveForm.ts`

**Step 1: Create `manualDataUtils.ts`**

Move `buildManualData` (lines 15-31) and `mergeWithOverrides` (lines 34-49) to the new file:

```typescript
import { EMPTY_MANUAL_DATA } from '@/components/evaluation/forms/formConfig';
import type { ManualData } from '@/components/evaluation/forms/formConfig';

export function buildManualData(
  initialData: Record<string, unknown> | null,
): ManualData {
  // ... exact code from lines 15-31
}

export function mergeWithOverrides(
  base: ManualData,
  overrides: Partial<ManualData>,
): ManualData {
  // ... exact code from lines 34-49
}
```

**Step 2: Update `useAutoSaveForm.ts` to import from `manualDataUtils.ts`**

```typescript
import { buildManualData, mergeWithOverrides } from './manualDataUtils';
```

Remove the inline definitions. Keep re-exporting them if they were exported:
```typescript
export { buildManualData, mergeWithOverrides } from './manualDataUtils';
```

**Step 3: Run tests**

```bash
cd frontend && npm run test:run && npm run build
```

**Step 4: Commit**

```bash
git add frontend/src/hooks/manualDataUtils.ts frontend/src/hooks/useAutoSaveForm.ts
git commit -m "Extract manual data merge logic from useAutoSaveForm to utility module"
```

---

### Task 17: Group `EvaluationSections.tsx` props into focused interfaces

**Files:**
- Modify: `frontend/src/components/evaluation/EvaluationSections.tsx`

**Step 1: Split the 19-prop interface into grouped sub-interfaces**

```typescript
interface FormProps {
  manualData: ManualData;
  onFieldChange: (category: string, key: string, value: number | string | null) => void;
  onFieldBlur: () => void;
  rules?: ScoringRules;
  storeLink: string | null;
}

interface ScoringProps {
  storeName: string;
  brandName: string;
  onGenerateScore: (request: ScoringRequest) => void;
  scoringResult: ScoringResult | null;
  isGenerating: boolean;
  isStale: boolean;
  scoringError: Error | null;
}

interface SaveProps {
  onSaveEvaluation: () => void;
  isSaving: boolean;
  isSaved: boolean;
  saveError: Error | null;
}

interface StatusProps {
  saveStatus: SaveStatus;
  lastSaved: Date | null;
  onRetrySave: () => void;
}

interface EvaluationSectionsProps extends FormProps, ScoringProps, SaveProps, StatusProps {
  brandId: number;
  categoryType: string | null;
  onCategoryChange: (value: string) => void;
  onActiveSection: (sectionId: string) => void;
}
```

**Step 2: No runtime changes — just type-level organization**

The component function signature stays the same. The extends composition means all props are still available.

**Step 3: Run tests and type-check**

```bash
cd frontend && npm run test:run && npm run build
```

**Step 4: Commit**

```bash
git add frontend/src/components/evaluation/EvaluationSections.tsx
git commit -m "Group EvaluationSections props into focused sub-interfaces"
```

---

### Task 18: Extract `useEvaluationOrchestrator` hook from `EvaluationPage.tsx`

**Files:**
- Create: `frontend/src/hooks/useEvaluationOrchestrator.ts`
- Modify: `frontend/src/pages/EvaluationPage.tsx`

**Step 1: Create the orchestrator hook**

Move all hook calls and state management from EvaluationPage (lines 20-128) into:

```typescript
export function useEvaluationOrchestrator(brandId: number) {
  // All the hook calls from EvaluationPage lines 28-75
  const { brand, brandLoading, brandError } = useBrandDetail(brandId);
  const { evaluationState } = useEvaluationState(brandId);
  const saveMutation = useSaveEvaluationInputs(brandId);
  const [activeSection, setActiveSection] = useState('section-1');
  const { manualData, handleFieldChange, triggerSave, retrySave, saveStatus, lastSaved } =
    useAutoSaveForm({ ... });
  // ... scoring, calculator results, rules, save evaluation ...
  // ... handleSaveEvaluation, handleCategoryChange ...

  return {
    brand, brandLoading, brandError,
    activeSection, setActiveSection,
    manualData, handleFieldChange, triggerSave, retrySave, saveStatus, lastSaved,
    sectionProgress, storeLink,
    generateScore, scoringResult, lastPeriod, isStale, isGenerating, scoringError,
    calculatorResultsData,
    activeRules,
    handleSaveEvaluation, isSaving, isSaved, saveError,
    handleCategoryChange,
    categoryType: evaluationState?.category_type ?? null,
  };
}
```

**Step 2: Simplify EvaluationPage to use the hook**

```typescript
export default function EvaluationPage() {
  const { brandId } = useParams();
  const navigate = useNavigate();
  const { t } = useTranslation();

  const numericBrandId = Number(brandId);
  const isValidBrandId = !isNaN(numericBrandId) && numericBrandId > 0;

  const state = useEvaluationOrchestrator(isValidBrandId ? numericBrandId : 0);

  // ... just the JSX, no business logic
}
```

**Step 3: Run tests**

```bash
cd frontend && npm run test:run && npm run build
```

**Step 4: Commit**

```bash
git add frontend/src/hooks/useEvaluationOrchestrator.ts frontend/src/pages/EvaluationPage.tsx
git commit -m "Extract useEvaluationOrchestrator hook from EvaluationPage"
```

---

## Phase 5: Frontend — Dependency Inversion

### Task 19: Abstract Firebase auth behind an interface

**Files:**
- Create: `frontend/src/services/authService.ts`
- Create: `frontend/src/services/firebaseAuthService.ts`
- Modify: `frontend/src/context/AuthContext.tsx`
- Modify: `frontend/src/services/apiClient.ts`

**Step 1: Create `authService.ts` interface**

```typescript
import type { User } from 'firebase/auth';

export interface AuthService {
  getToken(): Promise<string | null>;
  subscribe(callback: (user: User | null) => void): () => void;
  login(email: string, password: string): Promise<void>;
  logout(): Promise<void>;
}
```

**Step 2: Create `firebaseAuthService.ts` concrete implementation**

```typescript
import type { AuthService } from './authService';
import {
  getCurrentUserToken,
  loginWithEmail,
  logout,
  subscribeToAuthChanges,
} from '../firebase/auth';

export const firebaseAuthService: AuthService = {
  getToken: getCurrentUserToken,
  subscribe: subscribeToAuthChanges,
  login: loginWithEmail,
  logout,
};
```

**Step 3: Update `AuthContext.tsx` to accept `AuthService`**

```typescript
import type { AuthService } from '../services/authService';
import { firebaseAuthService } from '../services/firebaseAuthService';

interface AuthProviderProps {
  children: ReactNode;
  authService?: AuthService;  // injectable, defaults to Firebase
}

export function AuthProvider({
  children,
  authService = firebaseAuthService,
}: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    return authService.subscribe((user) => {
      setUser(user);
      setLoading(false);
    });
  }, [authService]);

  const login = (email: string, password: string) => authService.login(email, password);
  const logoutFn = () => authService.logout();

  // ... rest stays the same
}
```

**Step 4: Update `apiClient.ts` to use auth service**

```typescript
import { firebaseAuthService } from './firebaseAuthService';

const authMiddleware: Middleware = {
  async onRequest({ request }) {
    const token = await firebaseAuthService.getToken();
    if (token) {
      request.headers.set('Authorization', `Bearer ${token}`);
    }
    return request;
  },
};
```

Remove the direct `import { getCurrentUserToken } from '../firebase/auth'`.

**Step 5: Run tests**

```bash
cd frontend && npm run test:run && npm run build
```

**Step 6: Commit**

```bash
git add frontend/src/services/authService.ts frontend/src/services/firebaseAuthService.ts frontend/src/context/AuthContext.tsx frontend/src/services/apiClient.ts
git commit -m "Abstract Firebase auth behind AuthService interface for DI"
```

---

## Final Verification

### Task 20: Full test suite and build verification

**Step 1: Run all backend tests**

```bash
cd backend && uv run pytest -v
```

Expected: All tests pass.

**Step 2: Run all frontend tests**

```bash
cd frontend && npm run test:run
```

Expected: All tests pass.

**Step 3: Run frontend build**

```bash
cd frontend && npm run build
```

Expected: Build succeeds with no TypeScript errors.

**Step 4: Verify no behavior changes**

Sanity-check that:
- All import paths still work (barrel re-exports)
- No new public API surfaces introduced
- No runtime behavior differences
