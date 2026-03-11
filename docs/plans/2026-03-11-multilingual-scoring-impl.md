# Multilingual Scoring Engine — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers-extended-cc:executing-plans to implement this plan task-by-task.

**Goal:** Replace hardcoded Indonesian text in scoring engine output with structured translatable data (`key + vars + fallback`) so the frontend can render text in ID/EN/TH based on user language toggle.

**Architecture:** Backend scoring engine produces `TranslatableText` objects alongside existing Indonesian text. Frontend helper checks for `_i18n` field — if present, renders via `t(key, vars)`; if absent, falls back to raw Indonesian text. No DB migration needed (all JSONB).

**Tech Stack:** Python (FastAPI, dataclasses), TypeScript (React, i18next), JSONB (PostgreSQL)

**Design Doc:** `docs/plans/2026-03-11-multilingual-scoring-design.md`

---

## Task 0: Add `TranslatableText` dataclass to models

**Files:**
- Modify: `backend/app/calculators/scoring/models.py`
- Test: `backend/tests/unit/calculators/test_translatable_text.py`

**Step 1: Write the failing test**

```python
# backend/tests/unit/calculators/test_translatable_text.py
"""Tests for TranslatableText and i18n-aware model serialization."""

from dataclasses import asdict

from app.calculators.scoring.models import TranslatableText


def test_translatable_text_serializes_to_dict():
    t = TranslatableText(key="scoring.preparationTime.pass", vars={"value": "0.56"})
    result = asdict(t)
    assert result == {"key": "scoring.preparationTime.pass", "vars": {"value": "0.56"}}


def test_translatable_text_empty_vars():
    t = TranslatableText(key="verdict.good", vars={})
    result = asdict(t)
    assert result == {"key": "verdict.good", "vars": {}}
```

**Step 2: Run test to verify it fails**

Run: `cd backend && uv run pytest tests/unit/calculators/test_translatable_text.py -v`
Expected: FAIL with ImportError (TranslatableText doesn't exist yet)

**Step 3: Write minimal implementation**

Add to `backend/app/calculators/scoring/models.py` after the imports, before `RowScore`:

```python
@dataclass
class TranslatableText:
    """Structured data for frontend i18n rendering."""

    key: str                         # i18n translation key
    vars: dict[str, str]             # interpolation variables
```

**Step 4: Run test to verify it passes**

Run: `cd backend && uv run pytest tests/unit/calculators/test_translatable_text.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/app/calculators/scoring/models.py backend/tests/unit/calculators/test_translatable_text.py
git commit -m "Add TranslatableText dataclass for i18n support"
```

---

## Task 1: Add `_i18n` fields to `RowScore`, `CategoryScore`, and `ScoringResult`

**Files:**
- Modify: `backend/app/calculators/scoring/models.py`
- Test: `backend/tests/unit/calculators/test_translatable_text.py` (extend)

**Step 1: Write the failing test**

Append to `test_translatable_text.py`:

```python
from app.calculators.scoring.models import RowScore, CategoryScore, ScoringResult


def test_row_score_i18n_fields_default_to_none():
    row = RowScore(
        row=7, metric="Tingkat Pesanan Tidak Terselesaikan",
        value=0.5, benchmark="<1%", verdict="✔️", message="pass", score=4.0,
    )
    assert row.metric_i18n is None
    assert row.message_i18n is None
    assert row.benchmark_i18n is None


def test_row_score_i18n_fields_set():
    row = RowScore(
        row=7, metric="Tingkat Pesanan Tidak Terselesaikan",
        value=0.5, benchmark="<1%", verdict="✔️", message="pass", score=4.0,
        metric_i18n=TranslatableText(key="scoring.unfulfilledOrderRate", vars={}),
        message_i18n=TranslatableText(key="scoring.unfulfilledOrderRate.pass", vars={"value": "0.5%"}),
    )
    assert row.metric_i18n.key == "scoring.unfulfilledOrderRate"
    assert row.message_i18n.vars == {"value": "0.5%"}


def test_row_score_i18n_serializes_in_asdict():
    row = RowScore(
        row=7, metric="test", value=0, benchmark="", verdict="", message="", score=0,
        metric_i18n=TranslatableText(key="k", vars={"a": "b"}),
    )
    d = asdict(row)
    assert d["metric_i18n"] == {"key": "k", "vars": {"a": "b"}}
    assert d["message_i18n"] is None


def test_category_score_i18n_field():
    cat = CategoryScore(category="Kesehatan Operasional Toko", score=10, max_score=10)
    assert cat.category_i18n is None

    cat2 = CategoryScore(
        category="Kesehatan Operasional Toko", score=10, max_score=10,
        category_i18n=TranslatableText(key="category.operational", vars={}),
    )
    assert cat2.category_i18n.key == "category.operational"


def test_scoring_result_i18n_fields():
    result = ScoringResult(
        total_score=50, category_scores=[], verdict="✔️",
        conclusion="test", marketing_estimation="test",
        marketing_percentage="10%", marketing_budget="test",
        closing_message="test", email_subject="test",
        email_body="test", template="fashion",
    )
    assert result.conclusion_i18n is None
    assert result.marketing_budget_i18n is None
    assert result.closing_message_i18n is None
    assert result.email_subject_i18n is None
```

**Step 2: Run test to verify it fails**

Run: `cd backend && uv run pytest tests/unit/calculators/test_translatable_text.py -v`
Expected: FAIL with AttributeError

**Step 3: Write minimal implementation**

Update `models.py`:

```python
@dataclass
class RowScore:
    """Score for a single metric row."""

    row: int
    metric: str
    value: Any           # D column: raw value
    benchmark: str       # E column: threshold
    verdict: str         # F column: "✔️" or "❌" or "-"
    message: str         # G column: text output
    score: float         # H column: points
    metric_i18n: TranslatableText | None = None
    message_i18n: TranslatableText | None = None
    benchmark_i18n: TranslatableText | None = None


@dataclass
class CategoryScore:
    """Aggregated score for a category."""

    category: str
    score: float
    max_score: float
    rows: list[RowScore] = field(default_factory=list)
    available: bool = True
    category_i18n: TranslatableText | None = None


@dataclass
class ScoringResult:
    """Complete result of the scoring system."""

    total_score: float
    category_scores: list[CategoryScore]
    verdict: str                     # F75 value
    conclusion: str                  # G66
    marketing_estimation: str        # G68
    marketing_percentage: str        # G72
    marketing_budget: str            # G73
    closing_message: str             # G75
    email_subject: str
    email_body: str                  # G1 assembled
    template: str                    # "fashion" or "non_fashion"
    rule_version: int = 1
    conclusion_i18n: list[TranslatableText] | None = None
    marketing_budget_i18n: TranslatableText | None = None
    closing_message_i18n: TranslatableText | None = None
    email_subject_i18n: TranslatableText | None = None
```

**Step 4: Run test to verify it passes**

Run: `cd backend && uv run pytest tests/unit/calculators/test_translatable_text.py -v`
Expected: PASS

**Step 5: Run all existing scoring tests to verify no regression**

Run: `cd backend && uv run pytest tests/unit/calculators/test_scoring.py -v`
Expected: All existing tests PASS (new fields have defaults)

**Step 6: Commit**

```bash
git add backend/app/calculators/scoring/models.py backend/tests/unit/calculators/test_translatable_text.py
git commit -m "Add i18n fields to RowScore, CategoryScore, ScoringResult"
```

---

## Task 2: Add i18n to operational scoring category (`categories.py`)

**Files:**
- Modify: `backend/app/calculators/scoring/categories.py:20-98`
- Test: `backend/tests/unit/calculators/test_scoring_i18n.py` (new)

**Step 1: Write the failing test**

```python
# backend/tests/unit/calculators/test_scoring_i18n.py
"""Tests for i18n fields in scoring categories and messages."""

from app.calculators.scoring.categories import _score_operational
from app.calculators.scoring.messages import _generate_operational_messages


def test_operational_rows_have_metric_i18n():
    manual = {"operational": {
        "unfulfilledOrderRate": 0.5, "lateShipmentRate": 0.3,
        "preparationTime": 0.8, "chatResponseRate": 98.0, "overallRating": 4.9,
    }}
    cat = _score_operational(manual)

    expected_keys = {
        7: "scoring.unfulfilledOrderRate",
        8: "scoring.lateShipmentRate",
        9: "scoring.preparationTime",
        10: "scoring.chatResponseRate",
        11: "scoring.overallRating",
    }
    for row in cat.rows:
        if row.row in expected_keys:
            assert row.metric_i18n is not None, f"Row {row.row} missing metric_i18n"
            assert row.metric_i18n.key == expected_keys[row.row]

    assert cat.category_i18n is not None
    assert cat.category_i18n.key == "category.operational"


def test_operational_messages_have_i18n():
    manual = {"operational": {
        "unfulfilledOrderRate": 0.5, "lateShipmentRate": 0.3,
        "preparationTime": 0.8, "chatResponseRate": 98.0, "overallRating": 4.9,
    }}
    cat = _score_operational(manual)
    _generate_operational_messages(cat, manual)

    for row in cat.rows:
        if row.row in (7, 8, 9, 10, 11):
            assert row.message_i18n is not None, f"Row {row.row} missing message_i18n"
            assert "pass" in row.message_i18n.key or "fail" in row.message_i18n.key


def test_operational_fail_messages_have_i18n():
    manual = {"operational": {
        "unfulfilledOrderRate": 5.0, "lateShipmentRate": 5.0,
        "preparationTime": 3.0, "chatResponseRate": 80.0, "overallRating": 3.0,
    }}
    cat = _score_operational(manual)
    _generate_operational_messages(cat, manual)

    for row in cat.rows:
        if row.row in (7, 8, 9, 10, 11):
            assert row.message_i18n is not None
            assert "fail" in row.message_i18n.key
```

**Step 2: Run test to verify it fails**

Run: `cd backend && uv run pytest tests/unit/calculators/test_scoring_i18n.py::test_operational_rows_have_metric_i18n -v`
Expected: FAIL (metric_i18n is None)

**Step 3: Implement — update `_score_operational()` in `categories.py`**

For each `RowScore` constructor in `_score_operational()`, add `metric_i18n` parameter. Example for row 7:

```python
rows.append(RowScore(
    row=7, metric="Tingkat Pesanan Tidak Terselesaikan",
    value=d7, benchmark=f"<{uor_threshold:g}%", verdict=f7, message="", score=h7,
    metric_i18n=TranslatableText(key="scoring.unfulfilledOrderRate", vars={}),
))
```

Map for all operational rows:
- Row 7: `scoring.unfulfilledOrderRate`
- Row 8: `scoring.lateShipmentRate`
- Row 9: `scoring.preparationTime`
- Row 10: `scoring.chatResponseRate`
- Row 11: `scoring.overallRating`

Add `category_i18n` to the returned `CategoryScore`:
```python
return CategoryScore(
    category="Kesehatan Operasional Toko",
    score=total, max_score=10.0, rows=rows,
    category_i18n=TranslatableText(key="category.operational", vars={}),
)
```

**Then update `_generate_operational_messages()` in `messages.py`** to set `message_i18n` alongside `row.message`. After setting `row.message`, add:

```python
if row.verdict == "✔️":
    row.message_i18n = TranslatableText(
        key=f"scoring.{rule_key}.pass",
        vars={"value": val_str, "threshold": threshold_str},
    )
else:
    row.message_i18n = TranslatableText(
        key=f"scoring.{rule_key}.fail",
        vars={"value": val_str, "threshold": threshold_str},
    )
```

Import `TranslatableText` at the top of both files.

**Step 4: Run tests**

Run: `cd backend && uv run pytest tests/unit/calculators/test_scoring_i18n.py -v`
Expected: PASS

**Step 5: Run existing tests**

Run: `cd backend && uv run pytest tests/unit/calculators/test_scoring.py -v`
Expected: All PASS

**Step 6: Commit**

```bash
git add backend/app/calculators/scoring/categories.py backend/app/calculators/scoring/messages.py backend/tests/unit/calculators/test_scoring_i18n.py
git commit -m "Add i18n to operational scoring category and messages"
```

---

## Task 3: Add i18n to remaining scoring categories (`categories.py`)

**Files:**
- Modify: `backend/app/calculators/scoring/categories.py`
- Modify: `backend/app/calculators/scoring/messages.py`
- Test: `backend/tests/unit/calculators/test_scoring_i18n.py` (extend)

Apply the same pattern from Task 2 to all remaining categories. For each `_score_*` function add `metric_i18n` and `category_i18n`. For each `_generate_*_messages` function add `message_i18n`.

**Category keys:**
- `_score_business` → `category.business`
- `_score_visitors` → `category.visitors`
- `_score_promo_tools` → `category.promo`
- `_score_products` → `category.products`
- `_score_ads` → `category.ads`
- `_score_campaign` → `category.campaign`
- `_score_competition` → `category.competition`
- `_score_stock` → `category.stock`
- `_score_discount_row` → `category.discount`

**Metric keys (by row number):**
- 13: `scoring.monthlySales` (dynamic: `vars: {month: "Jan 2026"}`)
- 14-18: `scoring.pastMonthlySales` (dynamic: `vars: {month: label}`)
- 19: `scoring.avgSales6mo`
- 20: `scoring.conversionRate`
- 26: `scoring.totalVisitors`
- 27: `scoring.returningVisitors`
- 28: `scoring.returningVisitorPct`
- 29: `scoring.totalFollowers`
- 31-41: `scoring.promo.<fieldKey>` (e.g. `scoring.promo.promoToko`)
- 42: `scoring.promoUsageRate`
- 43: `scoring.promoEffectiveness`
- 45: `scoring.productCount`
- 46: `scoring.storeStatus`
- 48: `scoring.adSales`
- 49: `scoring.adCost`
- 50: `scoring.adsROI`
- 51: `scoring.adsGMVPct`
- 52: `scoring.adsCostPct`
- 53: `scoring.adsCheckup`
- 55: `scoring.nominatedSessions`
- 56: `scoring.availableSessions`
- 57: `scoring.campaignParticipation`
- 61-63: `scoring.competitionProduct`
- 70: `scoring.avgStockTop20`
- 71: `scoring.stockAvailability`
- 73: `scoring.discountCheckup`

**Message keys pattern:** `scoring.<ruleKey>.pass`, `scoring.<ruleKey>.fail`, `scoring.<ruleKey>.noData`, etc.

**Step 1: Write tests for each category** (one test function per category at minimum)

Example for business:
```python
def test_business_rows_have_metric_i18n():
    manual = {"business": {
        "salesMonth0": 200_000_000, "salesMonth1": 180_000_000,
        "salesMonth2": 190_000_000, "salesMonth3": 170_000_000,
        "salesMonth4": 160_000_000, "salesMonth5": 150_000_000,
        "salesStartMonth": "2026-01",
    }}
    cat = _score_business(manual)
    assert cat.category_i18n.key == "category.business"
    row13 = next(r for r in cat.rows if r.row == 13)
    assert row13.metric_i18n is not None
    assert row13.metric_i18n.key == "scoring.monthlySales"
```

**Step 2: Implement all categories following the pattern from Task 2**

**Step 3: Run all tests**

Run: `cd backend && uv run pytest tests/unit/calculators/ -v`
Expected: All PASS

**Step 4: Commit**

```bash
git add backend/app/calculators/scoring/categories.py backend/app/calculators/scoring/messages.py backend/tests/unit/calculators/test_scoring_i18n.py
git commit -m "Add i18n to all scoring categories and messages"
```

---

## Task 4: Add i18n to computed sections (`computations.py`)

**Files:**
- Modify: `backend/app/calculators/scoring/computations.py`
- Test: `backend/tests/unit/calculators/test_scoring_i18n.py` (extend)

The computed sections (G66, G73, G75) return strings. We need them to return both the string (fallback) AND structured i18n data.

**Approach:** Change return types to return a tuple `(text, i18n_data)` or modify the functions to return a new dataclass. The cleanest approach: add parallel `_compute_g66_i18n()`, `_compute_g73_i18n()`, `_compute_g75_i18n()` functions that return `list[TranslatableText]` or `TranslatableText`, keeping existing functions unchanged for backward compat.

**Step 1: Write tests**

```python
from app.calculators.scoring.computations import (
    _compute_g66_i18n,
    _compute_g73_i18n,
    _compute_g75_i18n,
)
from app.calculators.scoring.models import CategoryScore, RowScore, TranslatableText


def test_g66_i18n_returns_translatable_list():
    """G66 conclusion should produce a list of TranslatableText items."""
    ops = CategoryScore(
        category="Kesehatan Operasional Toko", score=10, max_score=10,
        rows=[RowScore(row=10, metric="Persentase Chat Dibalas",
                       value=98, benchmark=">95%", verdict="✔️", message="", score=0)],
    )
    promo = CategoryScore(
        category="Promo Toko", score=0, max_score=15,
        rows=[RowScore(row=43, metric="", value=0.5, benchmark="", verdict="❌", message="", score=10)],
    )
    campaign = CategoryScore(
        category="Partisipasi Campaign", score=10, max_score=10,
        rows=[RowScore(row=57, metric="", value=0.5, benchmark="", verdict="❌", message="", score=10)],
    )
    manual = {"business": {
        "salesMonth0": 200_000_000, "salesMonth1": 180_000_000,
        "salesMonth2": 190_000_000, "salesMonth3": 170_000_000,
        "salesMonth4": 160_000_000, "salesMonth5": 150_000_000,
    }}
    items = _compute_g66_i18n([ops, promo, campaign], manual, "15.3% ~ 22.7%")
    assert len(items) > 0
    assert all(isinstance(i, TranslatableText) for i in items)
    # First item should be sales range
    assert items[0].key == "conclusion.salesRange"
    assert "min" in items[0].vars
    assert "max" in items[0].vars


def test_g73_i18n_returns_translatable_text():
    result = _compute_g73_i18n("✔️", 0.15, 200_000_000)
    assert result is not None
    assert result.key == "marketing.budgetRecommendation"
    assert "pct" in result.vars


def test_g73_i18n_returns_none_for_rejected():
    result = _compute_g73_i18n("❌", 0.15, 200_000_000)
    assert result is None


def test_g75_i18n_returns_translatable_text():
    result = _compute_g75_i18n("✔️", "Toko Salt")
    assert result is not None
    assert result.key == "closing.potential"
    assert result.vars["store_name"] == "Toko Salt"
```

**Step 2: Implement parallel i18n functions**

Add to `computations.py`:

```python
def _compute_g66_i18n(
    categories: list[CategoryScore],
    manual_data: dict,
    g68_text: str,
) -> list[TranslatableText]:
    """G66 i18n: return structured list of conclusion items."""
    items: list[TranslatableText] = []
    biz = _get_nested(manual_data, "business") or {}
    sales_months = [_safe_num(biz.get(f"salesMonth{i}")) for i in range(6)]
    valid_sales = [s for s in sales_months if s > 0]

    if valid_sales:
        items.append(TranslatableText(
            key="conclusion.salesRange",
            vars={"min": f"{min(valid_sales) / 1_000_000:.0f}", "max": f"{max(valid_sales) / 1_000_000:.0f}"},
        ))

    ops_cat = next((c for c in categories if c.category == "Kesehatan Operasional Toko"), None)
    if ops_cat:
        chat_row = next((r for r in ops_cat.rows if r.row == 10), None)
        if chat_row and chat_row.verdict == "❌":
            items.append(TranslatableText(key="conclusion.operationalChatIssue", vars={}))
        else:
            items.append(TranslatableText(key="conclusion.operationalGood", vars={}))

    items.append(TranslatableText(key="conclusion.productNaming", vars={}))
    items.append(TranslatableText(key="conclusion.photoBackground", vars={}))

    promo_cat = next((c for c in categories if c.category == "Promo Toko"), None)
    if promo_cat:
        eff_row = next((r for r in promo_cat.rows if r.row == 43), None)
        if eff_row and isinstance(eff_row.value, float) and eff_row.value < 0.80:
            items.append(TranslatableText(key="conclusion.promoUnderutilized", vars={}))

    campaign_cat = next((c for c in categories if c.category == "Partisipasi Campaign"), None)
    if campaign_cat:
        camp_row = next((r for r in campaign_cat.rows if r.row == 57), None)
        if camp_row and isinstance(camp_row.value, float) and camp_row.value < 0.80:
            items.append(TranslatableText(key="conclusion.campaignLow", vars={}))

    items.append(TranslatableText(key="conclusion.stockNotArchived", vars={}))
    items.append(TranslatableText(key="conclusion.unsoldProducts", vars={}))

    if g68_text:
        items.append(TranslatableText(key="conclusion.discountRange", vars={"range": g68_text}))

    return items


def _compute_g73_i18n(verdict: str, g72_value: float, d13: float, rules: dict | None = None) -> TranslatableText | None:
    if verdict.startswith("❌"):
        return None
    mkt_rules = _get_rule_category(rules, "marketing")
    display_max = _get_rule_value(mkt_rules, "display_max", "value", 0.25)
    display_min = _get_rule_value(mkt_rules, "display_min", "value", 0.10)
    display_pct = max(min(g72_value, display_max), display_min)
    return TranslatableText(key="marketing.budgetRecommendation", vars={"pct": f"{display_pct * 100:.0f}%"})


def _compute_g75_i18n(verdict: str, store_name: str = "", rules: dict | None = None) -> TranslatableText | None:
    verdict_key_map = {
        "✔️": "closing.potential",
        "❌": "closing.valueAdd",
        "❌ Non Mall": "closing.directAnalysis",
        "❌ No Brand": "closing.noBrand",
        "❌ Opex": "closing.experience",
    }
    key = verdict_key_map.get(verdict)
    if not key:
        return None
    return TranslatableText(key=key, vars={"store_name": store_name})
```

**Step 3: Run tests**

Run: `cd backend && uv run pytest tests/unit/calculators/test_scoring_i18n.py -v`
Expected: PASS

**Step 4: Commit**

```bash
git add backend/app/calculators/scoring/computations.py backend/tests/unit/calculators/test_scoring_i18n.py
git commit -m "Add i18n functions for conclusion, marketing budget, and closing message"
```

---

## Task 5: Wire i18n into `calculate_score()` orchestrator

**Files:**
- Modify: `backend/app/calculators/scoring/_calculator.py`
- Test: `backend/tests/unit/calculators/test_scoring_i18n.py` (extend)

**Step 1: Write the failing test**

```python
from app.calculators.scoring import calculate_score


def test_calculate_score_has_i18n_fields(full_manual_data):
    """The full scoring result should include i18n fields."""
    result = calculate_score(
        manual_data=full_manual_data,
        calculator_results={},
        template="fashion",
        verdict="✔️",
        store_name="Test Store",
        period="Jan 2026",
        brand_name="Test Brand",
    )
    # ScoringResult i18n fields
    assert result.conclusion_i18n is not None
    assert len(result.conclusion_i18n) > 0
    assert result.closing_message_i18n is not None
    assert result.email_subject_i18n is not None

    # CategoryScore i18n
    for cat in result.category_scores:
        assert cat.category_i18n is not None, f"{cat.category} missing category_i18n"

    # RowScore i18n (spot check operational)
    ops = next(c for c in result.category_scores if c.category == "Kesehatan Operasional Toko")
    for row in ops.rows:
        assert row.metric_i18n is not None, f"Row {row.row} missing metric_i18n"
        if row.message:
            assert row.message_i18n is not None, f"Row {row.row} missing message_i18n"
```

Note: Use the `full_manual_data` fixture from the existing `test_scoring.py` file. Copy it or import it.

**Step 2: Implement — update `calculate_score()` in `_calculator.py`**

Import and call the new i18n functions:

```python
from app.calculators.scoring.computations import (
    # ... existing imports ...
    _compute_g66_i18n,
    _compute_g73_i18n,
    _compute_g75_i18n,
)
```

After computing g66, g73, g75, add:

```python
g66_i18n = _compute_g66_i18n(all_categories, manual_data, g68)
g73_i18n = _compute_g73_i18n(verdict, g72, d13, rules)
g75_i18n = _compute_g75_i18n(verdict, store_name, rules)
email_subject_i18n = TranslatableText(
    key="email.subject",
    vars={"store": store_name, "period": period},
)
```

Pass them to ScoringResult:

```python
return ScoringResult(
    # ... existing fields ...
    conclusion_i18n=g66_i18n,
    marketing_budget_i18n=g73_i18n,
    closing_message_i18n=g75_i18n,
    email_subject_i18n=email_subject_i18n,
)
```

**Step 3: Run tests**

Run: `cd backend && uv run pytest tests/unit/calculators/test_scoring_i18n.py tests/unit/calculators/test_scoring.py -v`
Expected: All PASS

**Step 4: Commit**

```bash
git add backend/app/calculators/scoring/_calculator.py backend/tests/unit/calculators/test_scoring_i18n.py
git commit -m "Wire i18n fields into calculate_score orchestrator"
```

---

## Task 6: Add i18n to ads keyword calculator

**Files:**
- Modify: `backend/app/calculators/ads_keyword.py`
- Test: `backend/tests/unit/calculators/test_scoring_i18n.py` (extend)

**Step 1: Write test**

```python
from app.calculators.ads_keyword import calculate_sheet1


def test_ads_sheet1_has_i18n_details():
    """Sheet 1 should return i18n structured data in details."""
    rows = [
        {"Status": "Berjalan", "Jenis Iklan": "Iklan Produk", "Nama Iklan": "Ad 1",
         "Penempatan Iklan": "Semua Penempatan", "Mode Bidding": "Bidding Otomatis"},
    ]
    result = calculate_sheet1(rows, 10)
    # i18n keys should exist alongside text
    assert "ak2_i18n" in result
    assert result["ak2_i18n"]["key"] == "ads.summary"
    assert "active" in result["ak2_i18n"]["vars"]
```

**Step 2: Implement**

Add `_i18n` variants to each section output. The `details` dict from `calculate_ads_keyword` already stores structured data in `ak2`, `ak3`, etc. Add companion `ak2_i18n`, `ak3_i18n`, etc. keys with `TranslatableText`-shaped dicts.

For `calculate_sheet1()`, after building `ak2` string:

```python
ak2_i18n = {
    "key": "ads.summary",
    "vars": {
        "active": str(count_active),
        "paused": str(count_paused),
        "ended": str(count_ended),
        "unique_count": str(unique_count),
        "product_pct": _format_pct(product_pct),
        "total_products": str(total_products),
    },
}
```

Similarly for `ak3_i18n`, `ak4_i18n`, and `al*_i18n` keys.

Include these in the returned dicts and in `AdsKeywordResult.details`.

**Step 3: Run tests**

Run: `cd backend && uv run pytest tests/unit/calculators/test_scoring_i18n.py -v`
Expected: PASS

**Step 4: Commit**

```bash
git add backend/app/calculators/ads_keyword.py backend/tests/unit/calculators/test_scoring_i18n.py
git commit -m "Add i18n structured data to ads keyword calculator"
```

---

## Task 7: Update API schemas for i18n fields

**Files:**
- Modify: `backend/app/modules/evaluations/schemas.py`
- Test: Check existing integration tests still pass

**Step 1: Update schemas**

Add `_i18n` optional fields to response schemas:

```python
class TranslatableTextSchema(BaseModel):
    """i18n structured data for frontend translation."""
    key: str
    vars: dict[str, str] = {}


class RowScoreItem(BaseModel):
    row: int
    metric: str
    value: Any
    benchmark: str
    verdict: str
    message: str
    score: float
    metric_i18n: TranslatableTextSchema | None = None
    message_i18n: TranslatableTextSchema | None = None
    benchmark_i18n: TranslatableTextSchema | None = None


class CategoryScoreItem(BaseModel):
    category: str
    score: float
    max_score: float
    rows: list[RowScoreItem]
    available: bool = True
    category_i18n: TranslatableTextSchema | None = None


class ScoringResponse(BaseModel):
    total_score: float
    category_scores: list[CategoryScoreItem]
    verdict: str
    conclusion: str
    marketing_estimation: str
    marketing_percentage: str
    marketing_budget: str
    closing_message: str
    email_subject: str
    email_body: str
    template: str
    rule_version: int
    conclusion_i18n: list[TranslatableTextSchema] | None = None
    marketing_budget_i18n: TranslatableTextSchema | None = None
    closing_message_i18n: TranslatableTextSchema | None = None
    email_subject_i18n: TranslatableTextSchema | None = None
```

**Step 2: Run integration tests**

Run: `cd backend && uv run pytest tests/integration/ -v`
Expected: All PASS (new fields are optional)

**Step 3: Commit**

```bash
git add backend/app/modules/evaluations/schemas.py
git commit -m "Add i18n fields to evaluation API response schemas"
```

---

## Task 8: Add frontend `renderTranslatable` helper

**Files:**
- Create: `frontend/src/utils/renderTranslatable.ts`
- Test: `frontend/src/utils/renderTranslatable.test.ts`

**Step 1: Write the test**

```typescript
// frontend/src/utils/renderTranslatable.test.ts
import { describe, it, expect, vi } from 'vitest';
import { renderTranslatable } from './renderTranslatable';

describe('renderTranslatable', () => {
  const mockT = vi.fn((key: string, vars?: Record<string, string>) => {
    if (key === 'scoring.preparationTime.pass') {
      return `✔️ Preparation Time = ${vars?.value} days [Good]`;
    }
    return key;
  });

  it('should use i18n when available', () => {
    const result = renderTranslatable(
      'fallback text',
      { key: 'scoring.preparationTime.pass', vars: { value: '0.56' } },
      mockT,
    );
    expect(result).toBe('✔️ Preparation Time = 0.56 days [Good]');
    expect(mockT).toHaveBeenCalledWith('scoring.preparationTime.pass', { value: '0.56' });
  });

  it('should fall back to text when i18n is null', () => {
    const result = renderTranslatable('fallback text', null, mockT);
    expect(result).toBe('fallback text');
  });

  it('should fall back to text when i18n is undefined', () => {
    const result = renderTranslatable('fallback text', undefined, mockT);
    expect(result).toBe('fallback text');
  });
});
```

**Step 2: Implement**

```typescript
// frontend/src/utils/renderTranslatable.ts
import type { TFunction } from 'i18next';

export interface TranslatableText {
  key: string;
  vars: Record<string, string>;
}

/**
 * Render a backend field with i18n support.
 * If i18n data exists, use t() for translation. Otherwise, fall back to raw text.
 */
export function renderTranslatable(
  fallbackText: string,
  i18n: TranslatableText | null | undefined,
  t: TFunction,
): string {
  if (i18n) {
    return t(i18n.key, i18n.vars);
  }
  return fallbackText;
}
```

**Step 3: Run test**

Run: `cd frontend && npx vitest run src/utils/renderTranslatable.test.ts`
Expected: PASS

**Step 4: Commit**

```bash
git add frontend/src/utils/renderTranslatable.ts frontend/src/utils/renderTranslatable.test.ts
git commit -m "Add renderTranslatable frontend helper for i18n fallback"
```

---

## Task 9: Add scoring translation keys to locale files

**Files:**
- Modify: `frontend/src/locales/en.json`
- Modify: `frontend/src/locales/th.json`
- Modify: `frontend/src/locales/id.json`

**No test needed** — translation key accuracy verified by visual QA.

**Step 1: Add all scoring-related keys to each locale file**

This is a large batch of keys. Add them under a `scoring` namespace. Key categories:

1. **Metric names** (`scoring.unfulfilledOrderRate`, etc.)
2. **Pass/fail messages** (`scoring.unfulfilled_order_rate.pass`, etc.)
3. **Category names** (`category.operational`, etc.)
4. **Verdict labels** (`verdict.good`, `verdict.bad`, etc.)
5. **Conclusion items** (`conclusion.salesRange`, etc.)
6. **Marketing** (`marketing.budgetRecommendation`)
7. **Closing messages** (`closing.potential`, etc.)
8. **Ads analysis** (`ads.summary`, etc.)
9. **Email sections** (`email.subject`, etc.)

Example entries for `en.json`:
```json
{
  "scoring.unfulfilled_order_rate.pass": "✔️ Unfulfilled Order Rate = {{value}} [Good]",
  "scoring.unfulfilled_order_rate.fail": "❌ Unfulfilled Order Rate = {{value}} [Needs Improvement, recommended: <{{threshold}}%]",
  "scoring.unfulfilledOrderRate": "Unfulfilled Order Rate",
  "category.operational": "Store Operational Health",
  "verdict.good": "Good",
  "conclusion.salesRange": "Store revenue in the range of {{min}} million - {{max}} million per month over the last 6 months",
  "marketing.budgetRecommendation": "💡Minimum marketing budget needed by AHA to improve store sales performance = {{pct}}",
  "closing.potential": "We see that the potential of Store {{store_name}} is not yet maximized. Please click the following link to schedule a deeper consultation session to find the right solution for your business.\n\ncal-bd2.ahacommerce.net\n\nWe hope that what we have shared can be beneficial.",
  "ads.summary": "• Total Ads: {{active}} Active, {{paused}} Paused and {{ended}} Ended.\n• Involving {{unique_count}} ({{product_pct}}) products out of total products: {{total_products}}."
}
```

Equivalent entries for `th.json` with Thai translations and `id.json` with Indonesian translations (matching current hardcoded text).

**Step 2: Commit**

```bash
git add frontend/src/locales/en.json frontend/src/locales/th.json frontend/src/locales/id.json
git commit -m "Add scoring translation keys for EN, TH, ID locales"
```

---

## Task 10: Update `CategoryMetricCard` to use `renderTranslatable`

**Files:**
- Modify: `frontend/src/components/dashboard/CategoryMetricCard.tsx`

**Step 1: Update component**

The card currently receives `metric`, `benchmark`, `message` as strings. We need to also accept optional `_i18n` fields.

Update the interface:

```typescript
import type { TranslatableText } from '../../utils/renderTranslatable';

interface CategoryMetricCardProps {
  metric: string;
  value: unknown;
  verdict: string;
  score: number;
  benchmark: string;
  message: string;
  metric_i18n?: TranslatableText | null;
  message_i18n?: TranslatableText | null;
  benchmark_i18n?: TranslatableText | null;
}
```

Inside the component, use `renderTranslatable`:

```typescript
const { t } = useTranslation();
const displayMetric = renderTranslatable(metric, metric_i18n, t);
const displayMessage = renderTranslatable(message, message_i18n, t);
const displayBenchmark = renderTranslatable(benchmark, benchmark_i18n, t);
```

Replace `{metric}` → `{displayMetric}`, `{message}` content rendering → use `displayMessage`, etc.

**Important:** The `displayValue` logic checks for `metric.includes('Tingkat')` and `metric.startsWith('%')`. These checks should use the **original** `metric` (Indonesian) for backward compat with old data, OR better: check the `metric_i18n.key` if available.

**Step 2: Update parent components** that pass props to `CategoryMetricCard` to also pass `_i18n` fields from the API response.

**Step 3: Run frontend tests**

Run: `cd frontend && npx vitest run`
Expected: All PASS

**Step 4: Commit**

```bash
git add frontend/src/components/dashboard/CategoryMetricCard.tsx
git commit -m "Update CategoryMetricCard to render translated metric names and messages"
```

---

## Task 11: Update `KesimpulanSection` for translated conclusion/budget/closing

**Files:**
- Modify: `frontend/src/components/dashboard/KesimpulanSection.tsx`

**Step 1: Update interface and rendering**

Add i18n fields to `ScoringSummary`:

```typescript
interface ScoringSummary {
  conclusion?: string;
  conclusion_i18n?: TranslatableText[];
  marketing_estimation?: string;
  marketing_budget?: string;
  marketing_budget_i18n?: TranslatableText;
  closing_message?: string;
  closing_message_i18n?: TranslatableText;
}
```

For conclusion bullet points, prefer `conclusion_i18n` array if available:

```typescript
{summary.conclusion_i18n ? (
  <ul className="space-y-2">
    {summary.conclusion_i18n.map((item, i) => (
      <li key={i} className="flex items-start gap-2 text-sm text-foreground">
        <span className="mt-1.5 size-1.5 rounded-full bg-primary shrink-0" />
        <span>{t(item.key, item.vars)}</span>
      </li>
    ))}
  </ul>
) : summary.conclusion ? (
  // fallback to raw text
  <ul>...</ul>
) : null}
```

Similarly for `marketing_budget` and `closing_message`.

**Step 2: Commit**

```bash
git add frontend/src/components/dashboard/KesimpulanSection.tsx
git commit -m "Update KesimpulanSection to render translated conclusion and closing"
```

---

## Task 12: Update `DataIntelligence` ads section for translated output

**Files:**
- Modify: `frontend/src/components/dashboard/DataIntelligence.tsx`

**Step 1: Update `AdsContent` component**

The ads section currently renders `output_text` as a `<pre>` block. With i18n, we need to render structured sections from the `details` object.

If `details.ak2_i18n` exists, render translated sections. Otherwise, fall back to `output_text` pre-formatted text.

```typescript
function AdsContent({ data, t }: { data: Record<string, unknown>; t: TFunction }) {
  const details = data.details as Record<string, unknown> | undefined;
  const text = (data.output_text as string) || '';

  // If i18n data exists, render translated
  if (details?.ak2_i18n) {
    return <AdsTranslatedContent details={details} t={t} />;
  }

  // Fallback to raw text
  if (!text) return <p className="...">{t('common.noData')}</p>;
  return <pre className="...">{text}</pre>;
}
```

**Step 2: Commit**

```bash
git add frontend/src/components/dashboard/DataIntelligence.tsx
git commit -m "Update DataIntelligence ads section for translated output"
```

---

## Task 13: Update `useEvaluationOrchestrator` to pass i18n data

**Files:**
- Modify: `frontend/src/hooks/useEvaluationOrchestrator.ts:97-102`

**Step 1: Update scoring_summary assembly**

Add i18n fields when assembling `scoring_summary`:

```typescript
calcResults['scoring_summary'] = {
  conclusion: scoringResult.conclusion,
  conclusion_i18n: scoringResult.conclusion_i18n,
  marketing_estimation: scoringResult.marketing_estimation,
  marketing_budget: scoringResult.marketing_budget,
  marketing_budget_i18n: scoringResult.marketing_budget_i18n,
  closing_message: scoringResult.closing_message,
  closing_message_i18n: scoringResult.closing_message_i18n,
};
```

**Step 2: Commit**

```bash
git add frontend/src/hooks/useEvaluationOrchestrator.ts
git commit -m "Pass i18n fields through useEvaluationOrchestrator"
```

---

## Task 14: Update parent components passing data to CategoryMetricCard

**Files:**
- Modify: Components that render `CategoryMetricCard` (find via grep for `CategoryMetricCard`)
- These likely pass row data from `score_breakdown` — ensure they also pass `_i18n` fields

**Step 1: Find all usages**

Search for `<CategoryMetricCard` across the frontend.

**Step 2: Update each usage** to spread `_i18n` fields from the API response row data.

Since the backend now includes `metric_i18n`, `message_i18n`, `benchmark_i18n` in each row's JSONB, and the frontend receives these via the API, the parent components just need to pass them through:

```typescript
<CategoryMetricCard
  {...row}  // This already spreads metric, message, etc.
  // i18n fields are now part of row data from the API
/>
```

**Step 3: Commit**

```bash
git add [affected component files]
git commit -m "Pass i18n fields to CategoryMetricCard from parent components"
```

---

## Task 15: End-to-end verification and cleanup

**Step 1: Run all backend tests**

Run: `cd backend && uv run pytest -v`
Expected: All PASS

**Step 2: Run all frontend tests**

Run: `cd frontend && npx vitest run`
Expected: All PASS

**Step 3: Manual verification**

1. Start dev server
2. Create a new evaluation (this will produce i18n data)
3. Switch language to EN → verify metric names, messages, conclusion, closing all render in English
4. Switch to TH → verify Thai rendering
5. Switch back to ID → verify Indonesian rendering matches previous behavior
6. Open an OLD evaluation (no i18n data) → verify it still renders in Indonesian without errors

**Step 4: Final commit**

```bash
git commit -m "Complete multilingual scoring engine implementation"
```

---

## Summary of Changes

| Component | Files Changed | What Changed |
|-----------|--------------|-------------|
| Backend Models | `models.py` | Added `TranslatableText`, `_i18n` fields to `RowScore`, `CategoryScore`, `ScoringResult` |
| Scoring Categories | `categories.py` | Added `metric_i18n`, `category_i18n` to all `_score_*()` functions |
| Scoring Messages | `messages.py` | Added `message_i18n` to all `_generate_*_messages()` functions |
| Computations | `computations.py` | Added `_compute_g66_i18n()`, `_compute_g73_i18n()`, `_compute_g75_i18n()` |
| Calculator | `_calculator.py` | Wire i18n into `calculate_score()` |
| Ads Calculator | `ads_keyword.py` | Added `_i18n` variants to output sections |
| API Schemas | `schemas.py` | Added i18n fields to response schemas |
| Frontend Helper | `renderTranslatable.ts` | New utility for i18n fallback rendering |
| Locale Files | `en.json`, `th.json`, `id.json` | Added ~100+ scoring translation keys |
| Dashboard Components | `CategoryMetricCard.tsx`, `KesimpulanSection.tsx`, `DataIntelligence.tsx` | Updated to use `renderTranslatable` |
| Data Hooks | `useEvaluationOrchestrator.ts` | Pass i18n fields to UI |
