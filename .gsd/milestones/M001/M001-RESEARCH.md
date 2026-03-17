# Project Research Summary

**Project:** AHA SICU — THB Multi-Currency Extension
**Domain:** Marketplace brand evaluation system (adding Shopee Thailand / THB to existing Shopee Indonesia / IDR system)
**Researched:** 2026-03-16
**Confidence:** HIGH — all four research files based on direct codebase inspection; no speculative external research required

## Executive Summary

This is a targeted extension of a working internal evaluation tool, not a new product. The system already evaluates Shopee Indonesia brands using a configurable scoring engine, and the task is to add Shopee Thailand (THB) as a second marketplace. Every required capability — database, migrations, number formatting, UI components, i18n — is already present in the codebase. No new runtime dependencies are needed. The core design decision is to add a `marketplace` VARCHAR column to both `brand_vp_data` and `scoring_rules`, which immediately unlocks parallel IDR/THB rule sets and a clean scoring call chain with no conditional branching.

The recommended implementation is additive and parameterized throughout: `generate_score()` reads `brand.marketplace` and passes it to `get_rules_by_marketplace(template, marketplace)`, which fetches the correct row. Pure calculators receive `marketplace` as a parameter for locale-aware number parsing. The scoring engine itself does not change — only the data-fetch layer gains a new dimension. This design means a third marketplace (e.g., SGD) is a DB row addition and a CSV format check, not a code architecture change.

The most significant risks are pre-existing technical debt: `_clean_price` in `discount.py` and `top_sku.py` strips dots unconditionally (destroys Thai prices), `CurrencyField.tsx` hardcodes IDR labels, and three separate locations (`DEFAULT_RULES`, migration seeds, `messages.py`) must stay in sync for currency labels in scoring output. These debt items must be addressed before THB data flows through the system — they are not "fix later" concerns. Additionally, the project requirements assume Thai CSVs have the same column structure as Indonesian, but this must be verified with a real Shopee Thailand CSV sample before the upload phase begins.

---

## Key Findings

### Recommended Stack

No new packages are required for any part of this extension. All tooling is already installed and pinned. The relevant extensions are: `VARCHAR(2) + CHECK constraint` for the marketplace discriminator (consistent with migration 023's language column pattern), `asyncpg` parameterized queries extended with a `marketplace` argument, `Alembic` two-step migrations (nullable → backfill → NOT NULL) for safety on populated tables, `Intl.NumberFormat` (Web standard) for THB currency display using `en-US` locale with `currency: 'THB'` (avoids Thai numerals unreadable by the Indonesian operations team), and `Radix UI Tabs` (already in `radix-ui` meta-package) for the marketplace tab switcher on the Rules page.

**Core technologies:**
- `PostgreSQL VARCHAR(2) + CHECK` — marketplace discriminator — mirrors existing `chk_users_language` pattern in migration 023
- `Alembic` — migrations — two-step pattern (add nullable → backfill → add NOT NULL) is critical for populated tables
- `asyncpg` — DB queries — `get_rules_by_marketplace(conn, template, marketplace)` replaces current hardcoded `get_rules_by_template(conn, "default")`
- `Intl.NumberFormat` — frontend currency display — `en-US` + `currency: 'THB'` produces `฿191,591`; no library needed
- `Radix UI Tabs` — Rules page marketplace switcher — already in `package.json` via `radix-ui` v1.4.3

### Expected Features

The feature set is well-defined with clear P1/P2/P3 prioritization. All P1 features are LOW-to-MEDIUM complexity; none require architectural changes.

**Must have (table stakes — P1):**
- `marketplace` column on `brand_vp_data` with `DEFAULT 'ID'` backfill — foundation for everything downstream
- `marketplace` column on `scoring_rules` with seeded THB row (IDR 100M → ~THB 191,591 conversion) — enables correct rule selection
- `get_rules_by_marketplace()` query + `generate_score()` threading — ensures TH brands score against THB thresholds
- `_fmt_currency(value, marketplace)` replacing `_fmt_idr()` — correct currency label in scoring output
- `{currency}` placeholder in message templates (three locations: `DEFAULT_RULES`, DB migration, `messages.py`) — eliminates hardcoded IDR in TH evaluation output
- THB CSV numeric parsing — `_parse_price(value, marketplace)` handles comma-thousands/period-decimal (TH) vs dot-thousands/comma-decimal (ID)
- Rules page marketplace tabs (IDR / THB) — admin threshold management

**Should have (differentiators — P2, add once THB brands exist in production):**
- Brand list marketplace filter — `get_brands_with_meeting()` accepts `marketplace` param
- Evaluation history filtered by marketplace — cross-market comparison once data accumulates

**Defer (v2+):**
- Third marketplace (SG/SGD) — the column-based design makes this a DB row + possible CSV format addition; no code changes needed
- Marketplace-aware email closing messages — Thai context in `interpretation.closing_messages` needed only after Thai evaluations are validated in production

**Anti-features to avoid:**
- Live exchange rate API — silently changes pass/fail outcomes on saved evaluations
- Automatic IDR↔THB conversion of raw input data — Thai data must stay in THB end-to-end
- Per-evaluation marketplace selection — derive from brand record to eliminate user error class
- General multi-currency framework — no known requirement beyond IDR and THB

### Architecture Approach

The system is a well-layered monolith; THB slots into existing layers without adding new ones. The scoring engine (`calculators/scoring/_calculator.py`) is already parameterized on `rules` and needs no change. The only structural change is adding `marketplace` as a lookup dimension in the data-fetch layer. `brand_vp_data` carries the marketplace, `scoring_rules` stores one row per `(template, marketplace)` pair, and `generate_score()` joins them. Frontend architecture follows the same pattern: `brand.marketplace` flows from the API response through hooks to components via a new `currency` prop, not through global state or context switching.

**Major components and what changes:**
1. **DB migrations** — add `marketplace VARCHAR(2) DEFAULT 'ID' NOT NULL` to both tables; seed THB row in `scoring_rules`; UNIQUE constraint on `(template, marketplace)`
2. **`rules/queries.py`** — `get_rules_by_marketplace(conn, template, marketplace)` replaces `get_rules_by_template`
3. **`evaluations/service.py` `generate_score()`** — reads `brand.marketplace`, passes to rule lookup (step 2 in existing load sequence)
4. **`calculators/discount.py` + `top_sku.py`** — `_clean_price` → `_parse_price(value, marketplace)` with locale-aware separator handling
5. **`calculators/scoring/helpers.py`** — `_fmt_idr()` → `_fmt_currency(value, marketplace)` with symbol lookup
6. **`calculators/scoring/rules.py` + `messages.py`** — `{currency}` placeholder replaces hardcoded `IDR` literals (three-location sync required)
7. **`RulesPage.tsx`** — Radix Tabs `ID | TH` switcher; `useRules` hook accepts marketplace param
8. **`CurrencyField.tsx`** — `currency: 'IDR' | 'THB'` prop; consolidate three duplicate `formatIDR` functions into shared `formatCurrency` in `formUtils.ts`
9. **`BrandsPage.tsx` + `BrandTable.tsx`** — marketplace badge display
10. **`modules/rules/schemas.py` + `modules/brands/schemas.py`** — add `marketplace` field to response types

### Critical Pitfalls

1. **`_clean_price` destroys THB values** — strips all `.` unconditionally; Thai prices use `.` as decimal separator, so `1,250.50` becomes `125050` (1000x error). Add `marketplace` param before any THB data enters the pipeline.
2. **Hardcoded `IDR` in message templates (three locations)** — `DEFAULT_RULES` in `rules.py`, DB-stored JSONB templates, and `messages.py` inline defaults must all change atomically. The existing `TestMigrationTemplatesDrift` test is the verification gate; extending it for THB is mandatory.
3. **Rules not threaded through scoring call chain** — if `marketplace` is added to the DB but not passed through `generate_score()` → `get_rules_by_marketplace()`, TH brands are evaluated against IDR thresholds silently. The symptom is TH brands always passing or always failing the revenue threshold.
4. **Migration backfill correctness** — two-step pattern required (add nullable → backfill → add NOT NULL). Missing `marketplace` in any SELECT in `brands.py` or `evaluations/service.py` causes `KeyError` after migration.
5. **Shopee Thailand CSV column headers** — the assumption that TH CSVs have same column structure as Indonesian is unverified. Thai Shopee seller center may export Thai-language headers. A real TH CSV sample must be obtained before the upload phase to extend `_COLUMN_RENAME` if needed.
6. **`CurrencyField.tsx` hardcoded IDR** — three independent `formatIDR` implementations across frontend with no `currency` prop; must be consolidated before any THB evaluation form renders.

---

## Implications for Roadmap

Based on the dependency graph in FEATURES.md and the build order in ARCHITECTURE.md, four natural phases emerge. The dependency constraint is strict: the DB migration is the foundation for all other work, and the scoring call chain fix must be in place before THB evaluations can be trusted.

### Phase 1: Data Model Foundation
**Rationale:** Every downstream feature depends on knowing which marketplace a brand belongs to and having a corresponding rule set. This is the non-negotiable first step. Nothing else can be tested end-to-end without it.
**Delivers:** Migrations adding `marketplace` to `brand_vp_data` and `scoring_rules`; THB seed row with IDR-converted thresholds; all existing brands preserved as `ID` with zero regression; schemas and query layer exposing `marketplace` field.
**Addresses features:** Marketplace field on brand, THB scoring rules in DB, initial THB thresholds from IDR conversion, migration safety for existing brands.
**Avoids pitfalls:** Migration backfill correctness (two-step pattern), NULL semantics anti-pattern, `brand_vp_data` vs `brands` table confusion.

### Phase 2: Scoring Engine — Marketplace Awareness
**Rationale:** Once the DB has THB rules, the scoring engine must use them. This phase is the correctness gate: until `generate_score()` reads `brand.marketplace` and fetches the matching rule row, all THB evaluations produce wrong scores.
**Delivers:** `get_rules_by_marketplace()` query; `generate_score()` threading `brand.marketplace`; `_fmt_currency(value, marketplace)` replacing `_fmt_idr()`; `{currency}` placeholder in message templates (all three locations updated atomically); rules router `Literal` allowlist updated.
**Addresses features:** Marketplace-scoped rule selection in engine, THB number formatting, currency label in evaluation messages.
**Avoids pitfalls:** Rules not threaded through scoring call chain, hardcoded `IDR` in message templates (three-location sync), rules router 422 error.

### Phase 3: CSV Upload — THB Parsing
**Rationale:** Calculator correctness depends on correct number parsing at upload time. This phase can be developed in parallel with Phase 2 (independent per FEATURES.md dependency graph) but must complete before THB CSV data enters production. Must be preceded by obtaining a real Shopee Thailand CSV sample to verify column headers.
**Delivers:** `_parse_price(value, marketplace)` replacing `_clean_price` in `discount.py` and `top_sku.py`; locale-aware parsing tested for both ID and TH conventions; CSV column header mapping verified or extended for Thai headers.
**Addresses features:** THB CSV numeric value parsing.
**Avoids pitfalls:** `_clean_price` destroys THB values (the most damaging data-corruption risk), Shopee TH CSV column header assumption.

### Phase 4: Frontend — Currency Abstraction and Marketplace UI
**Rationale:** Frontend work requires the backend APIs to expose `marketplace` fields (Phases 1-2). This phase consolidates all IDR hardcoding in the frontend before adding any THB-specific UI, ensuring `CurrencyField` and formatting utilities are shared rather than duplicated.
**Delivers:** `formatCurrency(value, marketplace)` consolidating three `formatIDR` duplicates in `formUtils.ts`; `CurrencyField` with `currency` prop; `RulesPage.tsx` with IDR/THB Marketplace tabs using Radix Tabs; `BrandsPage` marketplace badge; `EvaluationPage` marketplace context display; `BrandDetailResponse` exposes `marketplace` field.
**Addresses features:** Rules page marketplace tabs, evaluation page marketplace context, brand list marketplace display.
**Avoids pitfalls:** `CurrencyField` hardcoded IDR (consolidate before adding THB UI), IDR references in TSX files, Rules page showing interleaved rule sets without tabs.

### Phase Ordering Rationale

- **Phase 1 first:** Hard dependency — `marketplace` column must exist in DB before any query or service layer can use it.
- **Phase 2 before Phase 4:** Backend API must expose `marketplace` fields before frontend hooks and components can consume them.
- **Phase 3 parallel with Phase 2:** CSV parsing is independent of scoring call chain per the feature dependency graph. Can be developed and reviewed concurrently; must complete before THB uploads are accepted in production.
- **Phase 4 last:** All backend correctness must be established before the frontend is wired to it to avoid masking scoring errors with UI state.

### Research Flags

Phases requiring validation before or during implementation:
- **Phase 3 (CSV Upload):** MUST obtain a real Shopee Thailand CSV sample for each file type (`cpc_ad_report`, `keyword_report`, `order_export`, `mass_update`) before implementing. The "same column structure" assumption in PROJECT.md has not been verified. If Thai headers are present, `_COLUMN_RENAME` must be extended before any other Phase 3 work.
- **Phase 2 (Message Templates):** The three-location sync (`DEFAULT_RULES`, DB migration, `messages.py`) is documented as a known fragility in migration 021 comments. The existing `TestMigrationTemplatesDrift` test must be read and extended before touching message templates.

Phases with established patterns (standard implementation, skip deeper research):
- **Phase 1 (Data Model):** Migration pattern is directly established by migration 023 (`chk_users_language`). Two-step NOT NULL migration is standard PostgreSQL practice with Alembic. No unknowns.
- **Phase 4 (Frontend):** Radix Tabs API is simple and documented. `Intl.NumberFormat` is a Web standard. Component refactoring follows existing shadcn/Radix patterns in the codebase.

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All recommendations verified against existing codebase; no new dependencies; patterns sourced from actual migrations and code |
| Features | HIGH | Derived from direct codebase inspection of every relevant file; dependency graph verified against actual call chain |
| Architecture | HIGH | Component boundaries verified by reading service.py, engine.py, queries; build order reflects confirmed dependency chain |
| Pitfalls | HIGH | All pitfalls identified from direct code reads; `_clean_price` behavior verified, `CurrencyField` hardcoding confirmed, three-location template problem verified in migration 021 comments |

**Overall confidence:** HIGH

### Gaps to Address

- **Real Shopee Thailand CSV sample (CRITICAL before Phase 3):** PROJECT.md states "same structure as Indonesia" but column header language is unverified. Obtain at least one CSV for each report type from a Thai Shopee seller account before Phase 3 begins. If Thai-language headers are present, add them to `_COLUMN_RENAME` as a prerequisite.
- **`source_language` field behavior for TH uploads:** `parsed_data` carries a `source_language` field used by `ads_keyword` language detection. Verify whether this field can carry `marketplace` context for the calculator layer, or whether a separate `marketplace` field should be added to `parsed_data`. Low risk but should be confirmed during Phase 3 design.
- **`brands` vs `brand_vp_data` table confusion:** Migration 002 created a `brands` table with a `marketplace` column that is unused. All actual brand data flows through `brand_vp_data` (migration 004). The migration adding `marketplace` must target `brand_vp_data`, not `brands`. Flag for code reviewer attention.

---

## Sources

### Primary (HIGH confidence — direct codebase inspection)
- `backend/app/db/migrations/versions/023_add_language_to_users.py` — established `VARCHAR + CHECK + server_default` pattern
- `backend/app/db/migrations/versions/021_internationalize_currency_rp_to_idr.py` — three-location template sync problem documented
- `backend/app/modules/evaluations/service.py` — `generate_score()` hardcoded `get_rules_by_template(conn, "default")` at line 339
- `backend/app/calculators/scoring/rules.py` — `DEFAULT_RULES` IDR hardcoding
- `backend/app/calculators/scoring/helpers.py` — `_fmt_idr()`, `_safe_num()` implementations
- `backend/app/calculators/discount.py`, `top_sku.py` — `_clean_price()` IDR-only assumption
- `backend/app/db/queries/rules.py` — `get_rules_by_template()` signature
- `backend/app/db/queries/brands.py` — `brand_vp_data` no marketplace column confirmed
- `frontend/src/components/evaluation/forms/CurrencyField.tsx` — hardcoded IDR label
- `frontend/src/pages/RulesPage.tsx` — single-template view
- `frontend/package.json`, `backend/pyproject.toml` — authoritative version pins
- `.planning/PROJECT.md` — scope, constraints, out-of-scope decisions

### Secondary (MEDIUM confidence)
- [Intl.NumberFormat — MDN](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/NumberFormat) — THB/IDR formatting with en-US locale
- [Radix UI Tabs](https://www.radix-ui.com/primitives/docs/components/tabs) — component API
- [Crunchydata: Enums vs Check Constraints in Postgres](https://www.crunchydata.com/blog/enums-vs-check-constraints-in-postgres) — CHECK constraint rationale (corroborated by codebase pattern)
- Thai Baht number format (period=decimal, comma=thousands): Wikipedia Thai baht, FastSpring currency guide
- Indonesian Rupiah format (comma=decimal, period=thousands): Wikipedia Indonesian rupiah

---

*Research completed: 2026-03-16*
*Ready for roadmap: yes*

# Architecture Research

**Domain:** Multi-currency marketplace evaluation system (adding THB to existing IDR system)
**Researched:** 2026-03-16
**Confidence:** HIGH — based on direct codebase analysis, not external research

---

## Standard Architecture

### System Overview

The existing system is a monolith with clean internal layering. THB support slots into
the existing layers rather than adding new layers.

```
┌──────────────────────────────────────────────────────────────────────┐
│                         Frontend (React + TypeScript)                 │
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────┐  ┌───────────┐   │
│  │  BrandsPage  │  │EvaluationPage│  │  RulesPage │  │HistoryPage│   │
│  └──────┬───────┘  └──────┬───────┘  └─────┬──────┘  └─────┬─────┘   │
│         │                │               │               │          │
│  ┌──────┴───────────────────────────────────────────────────────────┐ │
│  │              Hooks Layer (useRules, useBrands, etc.)             │ │
│  └──────────────────────────────┬───────────────────────────────────┘ │
│                                 │ REST over apiClient.ts              │
└─────────────────────────────────┼────────────────────────────────────┘
                                  │
┌─────────────────────────────────┼────────────────────────────────────┐
│                      Backend (FastAPI + Python)                       │
│                                 │                                     │
│  ┌──────────────────────────────┼───────────────────────────────────┐ │
│  │                      Router layer                                 │ │
│  │  /brands  /evaluations  /rules  /uploads  /calculators            │ │
│  └──────────────────────────────┬───────────────────────────────────┘ │
│                                 │                                     │
│  ┌──────────────────────────────┼───────────────────────────────────┐ │
│  │                     Service layer                                  │ │
│  │  brands/service  evaluations/service  rules/service               │ │
│  └──────┬──────────────────┬────┴──────────────────┬─────────────────┘ │
│         │                  │                       │                   │
│  ┌──────┴──────┐  ┌────────┴───────┐   ┌───────────┴────────────┐     │
│  │  Calculator │  │  Calculator    │   │    Scoring Calculator   │     │
│  │  Engine     │  │  Services      │   │    (pure function)      │     │
│  │  (engine.py)│  │ (calc_service) │   │  calculators/scoring/   │     │
│  └──────┬──────┘  └────────┬───────┘   └───────────┬────────────┘     │
│         │                  │                       │                   │
│  ┌──────┴──────────────────┴───────────────────────┴─────────────────┐ │
│  │                    DB Queries layer (asyncpg)                       │ │
│  │  queries/rules  queries/brands  queries/evaluations  queries/...   │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
                                  │
┌─────────────────────────────────┼─────────────────────────────────────┐
│                         PostgreSQL                                      │
│                                                                        │
│  scoring_rules   brand_vp_data   evaluations   brand_uploads   users  │
└────────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Lives In |
|-----------|---------------|----------|
| **scoring_rules table** | Stores threshold JSONB per template row (currently one `default` row) | DB |
| **rules/service.py** | get_all_rules, update_rules — no marketplace awareness today | `modules/rules/` |
| **calculators/scoring/rules.py** | DEFAULT_RULES dict — runtime fallback when DB rules = None | `calculators/scoring/` |
| **Calculator engine** | Registry of calculator types, readiness checks, runs pure calculators | `calculators/engine.py` |
| **Calculator services** | Loads files/manual data from DB, calls pure calculators, stores results | `modules/evaluations/calculator_service.py` |
| **Pure calculators** | Stateless computation (ads_keyword, discount, top_sku) — no DB I/O | `calculators/*.py` |
| **Scoring calculator** | Computes final score from manual_data + calc results + rules | `calculators/scoring/_calculator.py` |
| **evaluations/service.py** | Orchestrates generate_score: loads rules by template, runs scoring | `modules/evaluations/service.py` |
| **brand_vp_data table** | Brand master data (currently no marketplace column) | DB |
| **RulesPage** | Admin/leader UI for editing thresholds — single template view today | `frontend/pages/RulesPage.tsx` |
| **EvaluationPage** | Per-brand evaluation workflow — derives rules from brand today | `frontend/pages/EvaluationPage.tsx` |

---

## Current State: Where Currency Lives

Understanding the current IDR assumptions is critical for planning the THB additions.

### Hardcoded IDR Points

1. **DB: `scoring_rules.six_month_avg_threshold`** — `"threshold": 100000000` (IDR 100M). This is the only revenue threshold in the entire rules JSONB. All other metrics are percentages, counts, or ratios with no currency unit.

2. **Code: `calculators/scoring/rules.py` DEFAULT_RULES** — Same IDR 100M as runtime fallback. Three places must stay in sync: DB seed, DEFAULT_RULES, and inline per-field fallbacks.

3. **Message templates** — `monthly_sales_trend` messages contain `IDR {idr_val}` / `IDR {idr_avg}` literal strings. Competition messages contain `IDR {selling_price}` / `IDR {market_price}`.

4. **Calculator price parsing** — `discount.py` uses `_clean_price()` which strips `.` as thousands separator (Indonesian convention: `1.250.000`). THB uses `,` as thousands separator (`1,250,000`) — different parsing needed.

### The scoring_rules Table Schema (Current)

```sql
scoring_rules (
  id        SERIAL PK,
  template  VARCHAR,   -- currently one row: 'default'
  rules     JSONB,     -- all thresholds including six_month_avg_threshold
  version   INT,
  updated_by INT,
  updated_at TIMESTAMPTZ
)
```

The `template` column currently holds product-category variants (`fashion`, `non_fashion`, later unified to `default`). It does NOT hold marketplace/currency variants.

---

## Recommended Architecture for THB Addition

### Core Decision: Marketplace as a Dimension on scoring_rules

The cleanest extension is to add a `marketplace` column to `scoring_rules`, giving two rows:
- `(template='default', marketplace='ID')` — existing IDR thresholds
- `(template='default', marketplace='TH')` — new THB thresholds

Brands carry a `marketplace` field. The evaluation engine fetches rules by `(template, marketplace)`.

This avoids schema proliferation while keeping marketplace-specific values independently editable.

### Component Boundaries After THB Addition

```
┌────────────────────────────────────────────────────────────────────────┐
│  brand_vp_data          (add: marketplace VARCHAR(2) DEFAULT 'ID')     │
├────────────────────────────────────────────────────────────────────────┤
│  scoring_rules          (add: marketplace VARCHAR(2) DEFAULT 'ID')     │
│    (template, marketplace) → rules JSONB                               │
│    UNIQUE constraint: (template, marketplace)                          │
└────────────────────────────────────────────────────────────────────────┘
         │                          │
         ▼                          ▼
┌─────────────────┐      ┌──────────────────────────┐
│  brands/service │      │  rules/service             │
│  + schemas      │      │  get_rules_by_marketplace  │
│  exposes        │      │  update_rules (marketplace │
│  marketplace    │      │   as param)                │
└────────┬────────┘      └──────────────┬─────────────┘
         │                             │
         ▼                             ▼
┌─────────────────────────────────────────────────────┐
│  evaluations/service.generate_score()               │
│  1. Load brand → get brand.marketplace              │
│  2. Load rules by (template, marketplace)           │
│  3. Pass rules to calculate_score()                 │
│  Already does steps 1 & 3; step 2 needs update     │
└─────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│  calculators/scoring/_calculator.py                 │
│  calculate_score(rules=...) — already parameterized │
│  No change needed to pure function                  │
└─────────────────────────────────────────────────────┘
```

### Frontend Component Boundaries After THB Addition

```
BrandsPage
  └── BrandTable
        └── [marketplace badge per row — new]

EvaluationPage
  └── EvaluationHeader
        └── [marketplace context display — new]
  (no marketplace selector here: brand.marketplace drives context)

RulesPage
  └── [Marketplace tab switcher: ID | TH — new]
        ├── ID tab → shows IDR rules (existing)
        └── TH tab → shows THB rules (new)
```

---

## Patterns to Follow

### Pattern 1: Marketplace Discriminator on existing tables

**What:** Add `marketplace VARCHAR(2) DEFAULT 'ID' NOT NULL` to `brand_vp_data` and `scoring_rules`. Use migration to backfill all existing rows.

**When to use:** When a simple column addition scopes all existing data correctly without breaking current queries (additive, non-destructive).

**Trade-offs:**
- Pro: Minimal migration complexity, existing queries continue working with `WHERE marketplace = 'ID'` added
- Pro: scoring_rules now has two rows (ID, TH) instead of two separate JSONB blobs
- Con: Requires adding `marketplace` param to `get_rules_by_template`, `update_rules`, `list_brands`, and the evaluation generate_score path

**Example (backend query change):**
```python
# Before
async def get_rules_by_template(conn: Connection, template: str) -> RuleRow | None:
    return await fetch_one(conn, "SELECT ... FROM scoring_rules WHERE template = $1", template)

# After
async def get_rules_by_marketplace(
    conn: Connection, template: str, marketplace: str
) -> RuleRow | None:
    return await fetch_one(
        conn,
        "SELECT ... FROM scoring_rules WHERE template = $1 AND marketplace = $2",
        template, marketplace,
    )
```

### Pattern 2: Pure Calculator Isolation (existing, preserve)

**What:** Calculators in `calculators/*.py` are pure functions with zero DB I/O. The service layer (`calculator_service.py`) handles all DB load/save. The engine (`engine.py`) orchestrates readiness and dispatch.

**When to use:** Always. This separation makes calculators trivially testable and avoids coupling business logic to database shape.

**Trade-offs:** Slightly more indirection but the existing codebase proves this scales well.

**Implication for THB:** The pure calculators (`discount.py`, `ads_keyword.py`, `top_sku.py`) may need locale-aware number parsing. Pass `marketplace` or `locale` as a parameter into the pure function, not injected from DB.

### Pattern 3: DEFAULT_RULES as Fallback, DB as Source of Truth

**What:** `calculators/scoring/rules.py` defines `DEFAULT_RULES` as a Python dict. DB rows override this. Three files must stay in sync: migration seed, DEFAULT_RULES, and per-field inline fallbacks.

**When to use:** Maintained for backwards compatibility. Do not add THB defaults here.

**Trade-offs:**
- The three-place sync requirement is a known fragility (documented in migration 019 comments)
- For THB: only the DB row needs THB thresholds. No DEFAULT_RULES change needed since there is always a DB row for THB after the seeding migration.

### Pattern 4: Frontend Marketplace Tab (new, modeled on RulesPage template switching)

**What:** RulesPage currently shows one template at a time. Extend to show two marketplace tabs (ID/TH) within the same page.

**When to use:** When the same data schema exists for two variants that admins need to compare side-by-side.

**Trade-offs:**
- Pro: Keeps all threshold management in one place
- Pro: Admin can verify THB thresholds relative to IDR before saving
- Con: Slightly more frontend state (active marketplace tab, two rule objects)

---

## Data Flow

### Evaluation Flow (Current)

```
User opens EvaluationPage (/brands/:brandId/evaluate)
    ↓
useEvaluationOrchestrator(brandId)
    ↓
GET /evaluations/:brandId/state     → loads manual_data
GET /calculators/:brandId/status    → which calculators are ready
GET /calculators/:brandId/results   → existing calculator outputs
    ↓
User fills manual data fields (auto-saved)
PUT /evaluations/:brandId/inputs    → upsert evaluation_inputs
    ↓
User triggers score generation
POST /evaluations/:brandId/score    → generate_score()
    ↓ (backend)
  1. load brand
  2. load evaluation_inputs.manual_data
  3. load calculator_results for brand
  4. load scoring_rules WHERE template = 'default'   ← THB CHANGE HERE
  5. calculate_score(manual_data, calc_results, rules)
  6. return ScoringResponse
    ↓
User saves evaluation
POST /evaluations/:brandId/save     → insert into evaluations table
```

### Rules Management Flow (Current → Extended for THB)

```
Admin opens RulesPage
    ↓
GET /rules                          → returns all scoring_rules rows
    ↓ (current: one 'default' row)
    ↓ (after: two rows — ID and TH)
    ↓
Frontend splits into [ID tab] [TH tab]
    ↓
Admin edits threshold in TH tab
    ↓
PATCH /rules/:template              → update_rules(template, marketplace, rules_jsonb)
    ↓ (backend)
  UPDATE scoring_rules
  SET rules = $1, version = version + 1
  WHERE template = $2 AND marketplace = $3
```

### CSV Upload → Calculator Flow (Currency-Sensitive)

```
User uploads Shopee CSV (Thai or Indonesian)
    ↓
Upload parser detects CSV structure
    ↓ (THB: prices formatted as "1,250,000" not "1.250.000")
Parsed data stored in brand_uploads.parsed_data
    ↓
Calculator engine runs affected calculators
    ↓
Calculator service calls pure calculator with parsed data
    ↓ (pure calculator currently assumes IDR dot-separator)
Calculator stores results in calculator_results
```

**Key data flow risk:** The CSV price parser in `discount.py` uses `_clean_price()` which strips `.` as thousands separator. Thai CSVs use `,` as separator. The `source_language` field already exists in `parsed_data` (added for ads_keyword language detection). The same mechanism can carry `marketplace` or `locale` to the parser.

---

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| Current (team of ~10, dozens of brands) | Monolith is appropriate. No changes needed. |
| Many marketplaces (TH, MY, PH, VN...) | `marketplace` column approach generalizes. Each new marketplace = one DB row. No schema changes. |
| Per-brand rule overrides | Would require adding a `brand_id` FK to `scoring_rules` or a separate override table. Out of scope for this milestone. |

### Scaling Priorities

1. **First constraint:** Number of scoring_rules rows grows linearly with marketplaces. At 10 marketplaces this is still a trivially small table. No optimization needed.
2. **Second constraint:** Scoring message templates contain hardcoded language strings (Indonesian). THB evaluation outputs will need Thai message templates in a future milestone if required.

---

## Anti-Patterns

### Anti-Pattern 1: Separate JSONB blob inside existing rules row

**What people do:** Add a `"THB": { ... }` key inside the existing rules JSONB for the `default` template.

**Why it's wrong:** The rules JSONB is deeply nested already. Nesting marketplace inside it means the admin UI must navigate three levels (category → rule → marketplace) to edit a threshold. It also breaks the existing `ScoringRuleResponse` schema which assumes the top level is category names. Migrations that patch the JSONB become exponentially harder.

**Do this instead:** Add `marketplace` as a first-class column on `scoring_rules`. Two rows (ID, TH) with identical structure, independently editable.

### Anti-Pattern 2: Hardcoding marketplace in evaluate flow

**What people do:** Check `if brand.marketplace == 'TH': use_thb_rules()` inline in `generate_score()`.

**Why it's wrong:** Violates Open/Closed. Adding a third marketplace (MY) requires editing existing working code.

**Do this instead:** `generate_score()` loads rules by `(template, brand.marketplace)` generically. The marketplace string flows through as a parameter. Adding Malaysia = adding one DB row and one seeding migration.

### Anti-Pattern 3: Duplicating CSV parsers for THB

**What people do:** Create `discount_th.py`, `top_sku_th.py` with copy-pasted logic and different number parsing.

**Why it's wrong:** Logic drift between ID and TH versions is inevitable. Bug fixes require double application.

**Do this instead:** Pass `locale` (or `marketplace`) to the existing pure calculator functions. Extract number parsing into a locale-aware helper. The core algorithm stays in one place.

### Anti-Pattern 4: Migrating existing brands with `marketplace = NULL`

**What people do:** Add the column nullable, leave existing brands as NULL, handle NULL as "IDR" in code.

**Why it's wrong:** NULL semantics bleed through the codebase. Every query that filters by marketplace must `WHERE marketplace = 'ID' OR marketplace IS NULL`. Inconsistency grows over time.

**Do this instead:** `ALTER TABLE brand_vp_data ADD COLUMN marketplace VARCHAR(2) DEFAULT 'ID' NOT NULL`. PostgreSQL fills all existing rows with `'ID'` atomically. No NULL handling needed anywhere.

---

## Integration Points

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| `evaluations/service` → `rules/queries` | Direct function call | `generate_score()` already calls `rules_queries.get_rules_by_template()`. Add `marketplace` param. |
| `evaluations/service` → `brands/queries` | Direct function call | Already loads brand to validate existence. Extend to read `brand.marketplace`. |
| `calculator_service` → pure calculators | Function call with data | Pass `marketplace` through to enable locale-aware number parsing. |
| RulesPage → `/rules` API | REST GET/PATCH | Currently passes `template` only. Extend to pass `marketplace` for PATCH. |
| EvaluationPage → brand data | `useBrandDetail` hook | Brand already loaded. Expose `marketplace` field in `BrandDetailResponse`. |

### Key Files Requiring Change

| File | Change Type | What Changes |
|------|-------------|--------------|
| `db/migrations/versions/026_*.py` | New migration | Add `marketplace` to `brand_vp_data`, add `marketplace` to `scoring_rules`, seed TH row |
| `db/queries/rules.py` | Extend | `get_rules_by_marketplace(template, marketplace)`, `update_rules(template, marketplace, ...)` |
| `db/queries/brands.py` | Extend | Include `marketplace` in SELECT, add filter support |
| `modules/rules/service.py` | Extend | Pass `marketplace` param through |
| `modules/rules/schemas.py` | Extend | Add `marketplace` field to `ScoringRuleResponse` |
| `modules/brands/schemas.py` | Extend | Add `marketplace` field to `BrandListItem`, `BrandDetailResponse` |
| `modules/evaluations/service.py` | Extend | `generate_score()`: read `brand.marketplace`, call `get_rules_by_marketplace()` |
| `calculators/discount.py` | Extend | `_clean_price()` locale-aware (or accept `locale` param) |
| `calculators/ads_keyword.py` | Potentially extend | Check if price parsing exists |
| `frontend/src/hooks/useRules.ts` | Extend | Handle array with marketplace dimension |
| `frontend/src/pages/RulesPage.tsx` | Extend | Add marketplace tab (ID/TH) |
| `frontend/src/pages/BrandsPage.tsx` | Minor extend | Show marketplace badge |

---

## Suggested Build Order

Dependencies flow as follows:

```
1. DB Migration (marketplace column + THB seed row)
        │
        ▼
2. Backend: brands — expose marketplace field
        │
        ▼
3. Backend: rules — marketplace-scoped queries and API
        │
        ▼
4. Backend: evaluation engine — select rules by brand.marketplace
        │
        ▼
5. Backend: calculators — locale-aware number parsing for THB CSVs
        │
        ▼
6. Frontend: RulesPage — marketplace tabs for threshold management
        │
        ▼
7. Frontend: BrandsPage — marketplace filter/badge display
        │
        ▼
8. Frontend: EvaluationPage — marketplace context display
```

**Rationale:**
- The DB migration must run first; everything reads from it.
- Brands must expose marketplace before evaluation can use it.
- Rules must be marketplace-scoped before evaluation scoring is correct.
- Calculator CSV parsing can be done in parallel with frontend work once DB is done.
- Frontend work can begin after backend APIs expose marketplace fields.

---

## Sources

- Direct codebase analysis: `backend/app/calculators/engine.py`, `modules/rules/service.py`, `modules/evaluations/service.py`, `calculators/scoring/rules.py`, `db/queries/rules.py`, `db/migrations/versions/`
- Project requirements: `.planning/PROJECT.md`
- Frontend analysis: `frontend/src/pages/RulesPage.tsx`, `EvaluationPage.tsx`, `BrandsPage.tsx`
- Confidence: HIGH — all findings from primary source code, no external research required for an existing-system extension

---

*Architecture research for: multi-currency marketplace evaluation (THB addition to AHA SICU)*
*Researched: 2026-03-16*

# Stack Research

**Domain:** Multi-currency extension to an existing evaluation/scoring system (IDR → IDR + THB)
**Researched:** 2026-03-16
**Confidence:** HIGH — all recommendations verified against the existing codebase; no new dependencies required for core work.

---

## Context: This Is an Extension, Not a Greenfield Project

The system already runs on:

| Layer | Technology | Version (pyproject.toml / package.json) |
|-------|------------|------------------------------------------|
| Backend framework | FastAPI | >=0.115.0 |
| Database | PostgreSQL via asyncpg | >=0.30.0 |
| Migrations | Alembic | >=1.13.0 |
| Data processing | Polars | >=1.0.0 |
| Frontend framework | React | ^19.2.0 |
| Component library | Radix UI (via `radix-ui` meta-package) | ^1.4.3 |
| State/data-fetching | TanStack Query | ^5.90.20 |
| Routing | React Router | ^7.13.0 |
| i18n | i18next + react-i18next | ^25 / ^16 |
| Schema validation | Pydantic v2 | (FastAPI dependency) |

**No new runtime dependencies are needed.** Every technique described below uses tooling already installed.

---

## Recommended Stack by Concern

### 1. Brand Marketplace Discriminator (Backend — Database)

**Approach: `VARCHAR(2)` column with `CHECK` constraint, `server_default = 'ID'`, NOT NULL.**

```sql
ALTER TABLE brand_vp_data
  ADD COLUMN marketplace VARCHAR(2) NOT NULL DEFAULT 'ID'
  CONSTRAINT chk_brand_vp_data_marketplace CHECK (marketplace IN ('ID', 'TH'));
```

**Why this instead of a PostgreSQL ENUM type:**
- The existing codebase uses `VARCHAR` + `CHECK` constraints for constrained string columns (see migration 023: `chk_users_language CHECK (language IN ('id', 'en', 'th'))`). Consistency with established pattern.
- `CHECK` constraints are altered with a single `ALTER TABLE … DROP CONSTRAINT … ADD CONSTRAINT` statement. PostgreSQL ENUMs require creating a new type and table rewrite to add values — operationally painful for a two-value discriminator.
- `server_default = 'ID'` means PostgreSQL fills all existing rows at statement time with no table rewrite (PostgreSQL 11+ constant-default optimization). No separate `UPDATE` needed.

**Alembic migration pattern (established in this repo):**

```python
import sqlalchemy as sa
from alembic import op

def upgrade() -> None:
    op.add_column(
        "brand_vp_data",
        sa.Column("marketplace", sa.String(2), server_default="ID", nullable=False),
    )
    op.execute(
        "ALTER TABLE brand_vp_data ADD CONSTRAINT chk_brand_vp_data_marketplace "
        "CHECK (marketplace IN ('ID', 'TH'))"
    )

def downgrade() -> None:
    op.execute("ALTER TABLE brand_vp_data DROP CONSTRAINT IF EXISTS chk_brand_vp_data_marketplace")
    op.drop_column("brand_vp_data", "marketplace")
```

**Confidence:** HIGH — mirrors migration 023 exactly.

---

### 2. Marketplace-Specific Scoring Rules (Backend — Database)

**Approach: Add `marketplace` column to `scoring_rules` table; change primary lookup key from `template` to `(template, marketplace)`.**

Current `scoring_rules` schema:
```
id, template, rules (JSONB), version, updated_by, updated_at
```

Required schema after migration:
```
id, template, marketplace VARCHAR(2), rules (JSONB), version, updated_by, updated_at
UNIQUE (template, marketplace)
```

**Why NOT a separate `scoring_rules_thb` table:**
- The existing `rules_queries.get_rules_by_template(conn, template)` pattern is used in `evaluations/service.py`. Adding a `marketplace` parameter to this single function is a one-line change. A separate table requires a new query file, new schema classes, and branch logic in the service — more surface area with no benefit.
- The admin Rules page already iterates over all rule rows; adding a marketplace dimension means adding a tab, not a new page.

**Seed data strategy for initial THB thresholds:**
Write a migration that reads all existing `(template, 'ID')` rows and INSERTs corresponding `(template, 'TH')` rows with thresholds converted by the IDR→THB exchange factor (≈ 100,000,000 IDR → 191,591 THB at project initialization). Admins adjust after the fact.

**Confidence:** HIGH — the pattern is a direct extension of `get_rules_by_template` with an additional parameter.

---

### 3. Calculator Engine — Marketplace Awareness (Backend — Python)

**Approach: Thread `marketplace` through the evaluation call chain; pass it to `get_rules_by_template`.**

The current call chain:
```
POST /evaluations/score
  → evaluations/service.py: run_scoring()
    → rules_queries.get_rules_by_template(conn, "default")
    → calculate_score(rules=rules_jsonb, ...)
```

After change:
```
POST /evaluations/score  (add marketplace param, derived from brand)
  → evaluations/service.py: run_scoring(marketplace="TH")
    → rules_queries.get_rules_by_template(conn, "default", marketplace="TH")
    → calculate_score(rules=rules_jsonb, ...)
```

The `calculate_score` function and all downstream `_score_*` functions in `calculators/scoring/categories.py` already receive `rules` as a parameter — they are marketplace-agnostic by design. Only the data-fetch layer changes.

**Currency formatting in scoring messages:**
The `_fmt_idr()` helper in `calculators/scoring/helpers.py` formats numbers with comma thousands separators (e.g., `1,000,000`). For THB output, the same formatting applies — Thai Baht also uses comma as a thousands separator and period as decimal. A `_fmt_currency(value, marketplace)` wrapper that calls `_fmt_idr` and prepends the correct symbol/code suffix is sufficient. No new library needed.

**Confidence:** HIGH — the scoring engine is already parameterized on `rules`; marketplace is a new lookup dimension, not a new engine concept.

---

### 4. Currency Number Formatting (Frontend)

**Approach: `Intl.NumberFormat` (Web standard, no library required).**

```typescript
// Utility in src/lib/currency.ts
export function formatCurrency(value: number, marketplace: 'ID' | 'TH'): string {
  if (marketplace === 'TH') {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'THB',
      currencyDisplay: 'symbol',  // outputs ฿
      maximumFractionDigits: 0,
    }).format(value);
  }
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    maximumFractionDigits: 0,
  }).format(value);
}
```

**Why `en-US` locale for THB display instead of `th-TH`:**
`th-TH` with `nu-thai` extension outputs Thai numerals (๑,๒๓๔,๕๖๗.๘๙) which are unreadable to the Indonesian-speaking AHA team. Using `en-US` with `currency: 'THB'` produces `฿191,591` — familiar digit format, correct symbol. This matches how Shopee Thailand itself displays THB amounts in English-language contexts.

**Confidence:** HIGH — `Intl.NumberFormat` is available in all modern browsers; verified via MDN.

---

### 5. Marketplace Tab UI on Rules Page (Frontend)

**Approach: Radix UI `Tabs` primitive, already available via `radix-ui` meta-package.**

The `radix-ui` package (v1.4.3, already in package.json) re-exports all Radix primitives including `@radix-ui/react-tabs`. The Rules page needs an `IDR | THB` tab switcher above the category cards. No new installation required.

```typescript
import { Tabs, TabsList, TabsTrigger, TabsContent } from 'radix-ui';
// or if shadcn Tabs wrapper exists:
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../components/ui/tabs';
```

Check `src/components/ui/` — if a `tabs.tsx` wrapper already exists (common in shadcn setups), use it. If not, use Radix directly.

**Confidence:** HIGH — `radix-ui` is pinned in package.json.

---

### 6. Marketplace Selector on Evaluation Page (Frontend)

**Approach: Controlled `<select>` or Radix `Select`, driven by brand's `marketplace` field from the API.**

The brand detail response (`BrandDetailResponse`) will include `marketplace` after the DB migration. The evaluation page reads the brand, so the marketplace is available without a separate fetch. The selector should default to the brand's marketplace and be overridable if needed (per PROJECT.md: "User selects marketplace on evaluation page").

Use the existing `Select` component from `src/components/ui/` (shadcn Select wraps Radix Select, almost certainly present given `radix-ui` in dependencies).

**Confidence:** MEDIUM — assumes shadcn Select component exists; verify with `ls src/components/ui/`.

---

### 7. CSV Value Handling for THB (Backend)

**No new parser needed.** Per PROJECT.md: "Shopee Thailand CSVs use same structure as Indonesia." The Polars-based parser in `app/modules/upload/parser.py` already handles numeric values. THB values from Shopee Thailand use the same comma-thousands separator format as IDR. The existing `_safe_num()` helper in `calculators/scoring/helpers.py` handles this correctly.

**The one difference:** IDR values are whole numbers (no decimal places for practical amounts). THB values from Shopee may include `.00` decimals. `_safe_num()` already calls `float()` which handles this.

**Confidence:** HIGH — confirmed by reading parser.py and _safe_num() implementation.

---

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| PostgreSQL ENUM type for marketplace | Cannot add values without type rewrite; inconsistent with existing `CHECK` constraint pattern in this codebase | `VARCHAR(2)` with `CHECK` constraint |
| Separate `scoring_rules_thb` table | Doubles query surface, requires new TypedDicts, new router endpoints; no benefit over adding a column | `marketplace` column on `scoring_rules` |
| `babel` / `currency.js` / `dinero.js` | External currency formatting library adds a dependency for something `Intl.NumberFormat` handles natively and correctly | `Intl.NumberFormat` (built-in) |
| `th-TH` locale for number formatting | Outputs Thai numerals (๑,๒,๓) — unreadable for the operations team | `en-US` locale with `currency: 'THB'` |
| Live exchange rate API | Out of scope per PROJECT.md; adds complexity, cost, and failure modes | Hardcoded seed conversion factor in migration, admin-editable after |
| ORM (SQLAlchemy models) | The project uses raw SQL via asyncpg + TypedDicts — consistent with the rest of the codebase | Raw parameterized SQL with asyncpg |

---

## Installation

No new packages required. All needed functionality is covered by:

- `asyncpg` (DB queries with marketplace param)
- `alembic` + `sqlalchemy` (migrations)
- `radix-ui` (Tabs component, already installed)
- `Intl.NumberFormat` (Web standard, no install)

---

## Version Compatibility

| Package | Version in Use | Notes |
|---------|---------------|-------|
| `alembic` | >=1.13.0 | `op.add_column` with `server_default` is stable since Alembic 1.0 |
| `asyncpg` | >=0.30.0 | Parameterized queries with additional `marketplace` arg — no version concern |
| `radix-ui` | ^1.4.3 | Tabs primitive included in meta-package; no separate install |
| PostgreSQL | (inferred >=14 from asyncpg + asyncio usage) | Constant-default column addition (no table rewrite) requires PG11+ |

---

## Sources

- `backend/pyproject.toml` — authoritative version pins for all backend dependencies
- `frontend/package.json` — authoritative version pins for all frontend dependencies
- `backend/app/db/migrations/versions/023_add_language_to_users.py` — established pattern for `VARCHAR + CHECK + server_default`
- `backend/app/db/migrations/versions/002_create_brands_table.py`, `004_replace_brands_with_vp_and_meeting.py` — current `brand_vp_data` schema
- `backend/app/modules/evaluations/service.py` (line 339) — `get_rules_by_template(conn, "default")` call site
- `backend/app/calculators/scoring/helpers.py` — `_fmt_idr`, `_safe_num` implementations
- `backend/app/db/queries/rules.py` — `get_rules_by_template` signature
- [Intl.NumberFormat — MDN](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/NumberFormat) — THB/IDR formatting behavior (HIGH confidence)
- [Radix UI Tabs](https://www.radix-ui.com/primitives/docs/components/tabs) — component API (HIGH confidence)
- [Crunchydata: Enums vs Check Constraints in Postgres](https://www.crunchydata.com/blog/enums-vs-check-constraints-in-postgres) — rationale for CHECK over ENUM (MEDIUM confidence, corroborated by existing codebase pattern)
- [Alembic: `server_default` for column add](https://alembic.sqlalchemy.org/en/latest/ops.html) — zero-downtime migration pattern (HIGH confidence)

---

*Stack research for: THB multi-currency extension to AHA SICU evaluation system*
*Researched: 2026-03-16*

# Feature Research

**Domain:** Multi-currency expansion for a Shopee marketplace brand evaluation system (IDR → IDR + THB)
**Researched:** 2026-03-16
**Confidence:** HIGH — derived from direct codebase inspection, not external research

---

## Context

This is a subsequent milestone on an existing, working internal tool. "Users" are
AHA Commerce analysts (internal, ~10 people). The system evaluates Shopee brand candidates
for management contracts using a scoring engine with ~10 categories and configurable
thresholds. It currently handles Shopee Indonesia (IDR) only. The goal is to add Shopee
Thailand (THB) support.

The codebase is well-structured:
- `scoring_rules` DB table stores thresholds as JSONB keyed by `template` name
- `brand_vp_data` / `brand_meeting_data` tables have no `marketplace` column yet
- `engine.py` uses a registry pattern; `generate_score()` in the evaluation service
  calls `get_rules_by_template(conn, "default")` — hardcoded, marketplace-blind
- `_fmt_idr()` in `helpers.py` formats currency values for IDR only
- Message templates in `rules.py` have hardcoded "IDR" strings (e.g.,
  `"message_pass": "✔️ Penjualan = IDR {idr_val} ..."`)
- CSV parser normalizes English→Indonesian column names; numeric value parsing
  uses Indonesian thousand-separator conventions (`.` for thousands, `,` for decimal)
- i18n already has `th.json` locale file
- `brands` table (migration 002) has a `marketplace` column, but `brand_vp_data`
  (the actual table used via `brands.py` queries) does not

---

## Feature Landscape

### Table Stakes (Users Expect These)

Features that must work correctly or the THB evaluation is unusable / produces wrong scores.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Marketplace field on brand | Without knowing a brand's marketplace, the system cannot select the right scoring thresholds; evaluating a THB brand against IDR thresholds produces nonsense scores | LOW | `brand_vp_data` needs a `marketplace` column (values: `"ID"`, `"TH"`); migration must backfill existing rows as `"ID"` |
| THB scoring rules in DB | `six_month_avg_threshold` (IDR 100,000,000) is the primary gate — the THB equivalent (~191,591 THB) must exist as independently editable rules | LOW | Add new `scoring_rules` rows with a `marketplace` dimension; simplest approach: add a `marketplace` column to `scoring_rules` table and seed THB-converted defaults |
| Marketplace-scoped rule selection in engine | `generate_score()` currently calls `get_rules_by_template(conn, "default")` — this must become `get_rules_by_template_and_marketplace(conn, template, marketplace)` | LOW | Requires: (1) brand lookup carries marketplace, (2) rules query accepts marketplace filter |
| THB number formatting in scoring output | `_fmt_idr()` produces "100,000,000" for IDR; THB needs same comma-thousands format but different symbol context in messages | LOW | THB also uses comma-thousands grouping — same formatter works for the number, but currency label in messages changes from "IDR" to "THB" |
| Currency symbol in evaluation messages | Messages like `"Penjualan = IDR {idr_val}"` have hardcoded "IDR" — THB evaluations must show "THB" | MEDIUM | The `idr_val` variable name and "IDR" literal are scattered across `rules.py` message templates AND `messages.py` generator defaults — three locations must stay in sync (per NOTE in `rules.py`) |
| THB CSV numeric value parsing | Shopee Thailand CSVs use comma (`,`) as thousands separator and period (`.`) as decimal — opposite of Indonesian convention | MEDIUM | The parser currently reads values as strings into Polars; the calculator layer must parse them correctly. Shopee Thailand uses the same column structure so no new file types are needed, but `_safe_num()` and revenue column parsing must handle THB formatting |
| Evaluation page marketplace selector | The evaluation page must load the correct thresholds for the brand being evaluated; analysts need to know which marketplace context they are in | LOW | Can be auto-derived from brand's marketplace field rather than a manual UI selector, eliminating a class of user error |
| Migration safety for existing IDR brands | All ~N existing brands must be preserved as `marketplace="ID"` with no score regression | LOW | `ALTER TABLE brand_vp_data ADD COLUMN marketplace VARCHAR(10) NOT NULL DEFAULT 'ID'` with backfill; existing `scoring_rules` rows remain for IDR |

### Differentiators (Competitive Advantage)

Features beyond correctness that improve the analyst workflow.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Rules page marketplace tabs (IDR / THB side-by-side) | Admins can compare thresholds across markets — useful when deciding if a THB brand is equivalent in scale to an IDR brand | LOW | Existing `RulesPage.tsx` shows one template at a time; adding a tab component to switch marketplace context reuses all existing `RulesCategoryCard` components |
| Initial THB thresholds auto-derived from IDR via conversion | Gives admins a reasonable starting point (IDR 100M → ~THB 191,591) rather than blank fields | LOW | One-time migration seed using a fixed conversion rate; clearly documented as "starting estimate, not a live rate" |
| Brand list filtered by marketplace | Analysts managing Thai brands want to see only Thai brands without scrolling past 100 Indonesian brands | LOW | Add `marketplace` filter parameter to `get_brands_with_meeting()` query and `BrandsPage` UI |

### Anti-Features (Commonly Requested, Often Problematic)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Live exchange rate integration | "Thresholds should auto-update when THB/IDR rate changes" — seems like precision | Exchange rates are volatile; auto-updating thresholds would silently change pass/fail outcomes on saved evaluations and create audit confusion. The business judgment of what constitutes a "good" brand is not purely currency math. | Set thresholds once from a conversion estimate; admins update manually when they judge the market has shifted. Explicit, intentional, auditable. |
| Automatic currency conversion of raw input data | "Just convert THB values to IDR before scoring" — seems simpler | Loses precision, bakes in exchange rate assumptions into stored data, and creates confusion when the analyst sees IDR numbers for a Thai brand. Thai data should stay in THB end-to-end. | Separate threshold sets per marketplace. Raw data stays in original currency. |
| Multi-currency within a single brand | "A brand might sell on both ID and TH Shopee" | One brand, two currency contexts would require the evaluation page to ask "which marketplace is this evaluation for?" on every run — adds friction and makes historical evaluations ambiguous. | One brand = one marketplace. If a brand operates in both markets, it is represented as two brand records. |
| Per-evaluation marketplace selection | "Let the analyst pick marketplace at evaluation time" | Error-prone: analyst could accidentally evaluate a THB brand against IDR thresholds if they misclick. | Derive marketplace from the brand record (set once at brand creation/import). Evaluation inherits it automatically. |
| General multi-currency framework (3+ currencies) | "Let's make it extensible for all future markets" | No known requirement for currencies beyond IDR and THB. Building a generic currency registry now adds DB schema complexity (currency_codes table, conversion_rates table, etc.) with zero near-term payoff. | Design the two-marketplace solution so a third marketplace can be added by: adding a DB row to `scoring_rules` with `marketplace='SG'`, and adding a CSV format handler if needed. No framework needed. |

---

## Feature Dependencies

```
[Marketplace field on brand_vp_data]
    └──required by──> [Marketplace-scoped rule selection in engine]
    └──required by──> [Brand list filtered by marketplace]
    └──required by──> [Evaluation page shows correct marketplace context]

[THB scoring rules in DB]
    └──required by──> [Marketplace-scoped rule selection in engine]
    └──required by──> [Rules page marketplace tabs]

[Marketplace-scoped rule selection in engine]
    └──required by──> [THB number formatting in scoring output]
    └──required by──> [Currency symbol in evaluation messages]

[THB CSV numeric value parsing]
    └──independent──> (can be developed and tested in parallel with DB/rule changes)

[Initial THB thresholds auto-derived from IDR]
    └──feeds──> [THB scoring rules in DB] (provides seed values)
```

### Dependency Notes

- **Marketplace field on brand requires migration first:** Everything downstream — rule
  selection, brand filtering, evaluation context — depends on knowing which marketplace a
  brand belongs to. This is the foundation; it goes in phase 1.

- **THB scoring rules require marketplace column on `scoring_rules`:** The current table
  has `template` as the unique key. Adding `marketplace` as a second dimension (or encoding
  it as `template = "default_TH"`) must happen before rules can be seeded or edited.

- **Currency formatting is a scoring output concern, not a parser concern:** `_fmt_idr()`
  and hardcoded "IDR" in message templates are in the scoring layer, not the upload layer.
  CSV parsing changes are independent of scoring output changes.

- **Rules page tabs conflict with current single-template assumption:** `RulesPage.tsx`
  today selects `rules.find((r) => r.template === 'default')`. After marketplace is added,
  the page must select by `(template, marketplace)` tuple. This is a small but
  breaking change to the rules page — schedule it with rules DB changes, not separately.

---

## MVP Definition

### Launch With (v1 — complete, correct THB evaluation)

- [ ] `marketplace` column on `brand_vp_data` — migration with `DEFAULT 'ID'` backfill
- [ ] `marketplace` column on `scoring_rules` — migration adds column, seeds THB rows from IDR conversion
- [ ] `get_rules_by_template_and_marketplace()` DB query — replaces hardcoded `"default"` lookup
- [ ] `generate_score()` service reads brand's marketplace, passes to rule selection
- [ ] THB number formatting — `_fmt_currency(value, marketplace)` replaces `_fmt_idr()`, handles both conventions (IDR and THB both use comma-thousands; label differs)
- [ ] Currency label in message templates — `"IDR"` → `"{currency}"` placeholder in business/competition message templates; value injected from marketplace context
- [ ] THB CSV numeric parsing — handle comma-thousands / period-decimal convention for Thai Shopee exports
- [ ] Rules page marketplace tabs — IDR tab and THB tab using existing `RulesCategoryCard` components

### Add After Validation (v1.x)

- [ ] Brand list marketplace filter — once THB brands exist in the system, analysts need to filter. Complexity is LOW but value is zero until there are actual THB brands to see.
- [ ] Evaluation history filtered by marketplace — cross-marketplace history comparison. Useful for management reports once data accumulates.

### Future Consideration (v2+)

- [ ] Third marketplace (e.g., SG / SGD) — defer until business requires it. The marketplace-column design makes this a DB seed + possible CSV format addition.
- [ ] Marketplace-aware email templates — closing messages in `interpretation.closing_messages` currently reference Indonesian-context text ("cal-bd2.ahacommerce.net", IDR-specific partnership terms). Thai context would need different closing text. Defer until Thai evaluations are validated in production.

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Marketplace field on brand | HIGH | LOW | P1 |
| THB scoring rules in DB | HIGH | LOW | P1 |
| Marketplace-scoped rule selection in engine | HIGH | LOW | P1 |
| THB CSV numeric parsing | HIGH | MEDIUM | P1 |
| Currency label in evaluation messages | HIGH | MEDIUM | P1 |
| THB number formatting (`_fmt_currency`) | HIGH | LOW | P1 |
| Initial THB thresholds from IDR conversion | MEDIUM | LOW | P1 (done in migration seed) |
| Rules page marketplace tabs | MEDIUM | LOW | P1 |
| Brand list marketplace filter | LOW | LOW | P2 |
| Marketplace-aware closing messages | LOW | MEDIUM | P3 |
| Third marketplace support | LOW | LOW | P3 |

**Priority key:**
- P1: Must have for launch (THB evaluations produce correct results)
- P2: Should have, add once THB brands exist in production
- P3: Nice to have, defer to future milestones

---

## Competitor Feature Analysis

Not applicable — this is a bespoke internal evaluation tool, not a market product.
The relevant "competitors" are the manual spreadsheet workflows this system replaced.

| Feature | Manual Spreadsheet | This System (current) | Our Approach (THB milestone) |
|---------|-------------------|----------------------|------------------------------|
| Threshold management | Edit cells directly | Admin rules page, versioned | Add marketplace tab to existing rules page |
| Currency context | Analyst knows from filename | Implicit (IDR only) | Explicit marketplace field on brand record |
| Number formatting | Analyst formats manually | `_fmt_idr()` hardcoded | `_fmt_currency(marketplace)` with symbol lookup |
| CSV ingestion | Manual copy-paste | Automated upload + parse | Extend parser to handle THB number format |

---

## Implementation Hotspots

These are the specific locations in the existing codebase that need changes per feature.
Included here because they directly inform phase scoping.

| Feature | Backend Location | Frontend Location |
|---------|-----------------|-------------------|
| Marketplace on brand | `brand_vp_data` table migration; `brands.py` queries; `brands/schemas.py` | `BrandsPage.tsx`, `BrandTable.tsx` (add marketplace display) |
| THB rules in DB | New migration (`026_add_marketplace_to_scoring_rules.py`); `rules.py` queries add `marketplace` param | None (backend only) |
| Rule selection in engine | `evaluations/service.py` `generate_score()` — pass `marketplace` to rule lookup | None |
| Currency formatting | `helpers.py` `_fmt_idr()` → `_fmt_currency()`; all callers in `categories.py` and `messages.py` | None (output is in scoring text) |
| Message currency labels | `DEFAULT_RULES` in `rules.py` (idr_val var name, IDR literals); `messages.py` generators | None |
| THB CSV parsing | `parser.py` — `_safe_num()` may need locale-aware parsing; or add a post-parse column transform for THB numeric columns | None |
| Rules page tabs | None | `RulesPage.tsx` — add marketplace tab state; `useRules` hook query must accept marketplace param |

---

## Key Risks

1. **Three-location message template sync:** `rules.py` (`DEFAULT_RULES`), migration seeds, and `messages.py` inline defaults must stay in sync. The codebase already documents this risk and has tests for it. Adding a THB currency label placeholder adds a fourth variant of each message. Failing to update all three locations for THB causes silent fallback to IDR-labeled messages on THB evaluations.

2. **THB numeric parsing:** Shopee Thailand CSV exports use comma as thousands separator (e.g., "1,234,567.89" for THB). The existing `_safe_num()` uses Python's `float()` which handles this correctly. However, revenue columns parsed from order export CSVs need verification — if any pre-processing strips or interprets separators, it must handle both locales. This needs a concrete Shopee Thailand CSV sample to verify (flag as needing validation).

3. **`brand_vp_data` vs `brands` table:** Migration 002 created a `brands` table with a `marketplace` column that is never used — all actual brand data flows through `brand_vp_data` (migration 004). The `marketplace` column must go on `brand_vp_data`, not on the unused `brands` table. Easy to get wrong by looking at migration 002.

---

## Sources

- Direct codebase inspection (HIGH confidence):
  - `/backend/app/calculators/scoring/rules.py` — DEFAULT_RULES, IDR hardcoding
  - `/backend/app/calculators/scoring/helpers.py` — `_fmt_idr()`, `_safe_num()`
  - `/backend/app/calculators/engine.py` — calculator registry
  - `/backend/app/modules/evaluations/service.py` — `generate_score()` hardcoded rule lookup
  - `/backend/app/modules/rules/service.py` — rules update path
  - `/backend/app/db/queries/rules.py` — `get_rules_by_template()` signature
  - `/backend/app/db/queries/brands.py` — `brand_vp_data` table, no marketplace column
  - `/backend/app/modules/upload/parser.py` — CSV parsing, column normalization
  - `/backend/app/db/migrations/versions/002_create_brands_table.py` — unused `brands.marketplace` column
  - `/backend/app/db/migrations/versions/010_create_scoring_rules_table.py` — rules schema
  - `/frontend/src/pages/RulesPage.tsx` — single-template view
  - `/frontend/src/locales/th.json` — confirms `th` locale already exists
- `.planning/PROJECT.md` — project scope, constraints, out-of-scope decisions

---

*Feature research for: Multi-currency (THB) support for Shopee brand evaluation system*
*Researched: 2026-03-16*

# Pitfalls Research

**Domain:** Multi-currency marketplace evaluation system (IDR → IDR + THB)
**Researched:** 2026-03-16
**Confidence:** HIGH — based on direct codebase inspection + verified external sources

---

## Critical Pitfalls

### Pitfall 1: `_clean_price` strips dots without checking marketplace — destroys THB values

**What goes wrong:**
Both `discount.py` and `top_sku.py` implement `_clean_price` that unconditionally removes all `.` characters before parsing to float. This handles the Indonesian format (`1.250.000` → `1250000`). Thai Baht prices from Shopee use the opposite convention: `.` is the decimal separator and `,` is the thousands separator (`1,250,000.50` → `1250000.5`). Running IDR-style stripping on a THB value like `1,250.50` would produce `125050`, a 1000x magnitude error.

**Why it happens:**
The parser was written when only Indonesian data existed. The function name `_clean_price` obscures the IDR-specific assumption. There is no locale/marketplace parameter threading through the calculator layer, so there is no injection point for format variation.

**How to avoid:**
Add a `marketplace: str` parameter to `_clean_price` (or rename to `_parse_price(value, marketplace)`). When `marketplace == "TH"`, strip `,` as thousands separator and keep `.` as decimal. When `marketplace == "ID"`, keep existing behaviour. Add unit tests for both formats before touching the function.

**Warning signs:**
- THB evaluation totals look 10x–1000x too large or too small compared to raw CSV values
- `six_month_avg_threshold` check (THB 191,591 equivalent) is always failing or always passing for TH brands

**Phase to address:**
CSV parsing phase — before any THB data is submitted through the upload pipeline.

---

### Pitfall 2: Migration fails to backfill `marketplace` column — existing brands silently lose their IDR context

**What goes wrong:**
Adding a `marketplace` column to `brand_vp_data` (or equivalent table) with `NOT NULL` and no default will block the migration. Setting a bare `DEFAULT 'ID'` in SQL without verifying the column is used consistently downstream means some query paths skip the column and the frontend shows mixed/null context for old brands. Worse, if calculator rule lookups start selecting by `marketplace` but existing evaluations don't carry the field, historical re-scoring silently uses the wrong rule set.

**Why it happens:**
Alembic migrations on asyncpg/PostgreSQL require care with non-null columns on populated tables. The `brand_vp_data` table is joined by `brand_name` (not `id`) in several queries, and adding a field to one query without updating all join paths leaves gaps.

**How to avoid:**
Write the migration in two steps: (1) add `marketplace VARCHAR(2) DEFAULT 'ID'` (nullable first), (2) backfill `UPDATE brand_vp_data SET marketplace = 'ID' WHERE marketplace IS NULL`, (3) add `NOT NULL` constraint. Audit every query in `brands.py` and `evaluations/service.py` to confirm `marketplace` is returned in all SELECT paths. Add a migration test that asserts row count before/after and that all rows have `marketplace = 'ID'` after upgrade.

**Warning signs:**
- `KeyError: 'marketplace'` or `AttributeError` in existing evaluation flows after migration
- Brand list page shows Thai brands in IDR context after upload
- `get_brand_by_id` missing `marketplace` field in returned dict

**Phase to address:**
Data model phase — the first phase of the milestone.

---

### Pitfall 3: Rules table uses single `default` template — adding marketplace dimension fractures the lookup

**What goes wrong:**
`generate_score` in `evaluations/service.py` (line 339) always loads `rules_queries.get_rules_by_template(conn, "default")`. Adding THB rules as a new row (e.g., template `"default_TH"`) requires threading `marketplace` from brand → evaluation → `generate_score` call. If the brand's marketplace is not passed through the scoring call chain, the engine always loads IDR rules for Thai brands and evaluates them against wrong thresholds (e.g., IDR 100,000,000 six-month threshold vs THB ~191,591).

**Why it happens:**
The `generate_score` function signature and router endpoint do not accept a `marketplace` field. Adding the marketplace dimension to rules without adding it to the scoring call chain means the DB has two rule sets but the code always picks the wrong one for TH brands.

**How to avoid:**
Thread `marketplace` through: `generate_score(conn, brand_id, ..., marketplace)` → `get_rules_by_template(conn, f"default_{marketplace}")`. Alternatively model it as `get_rules_by_marketplace(conn, marketplace)`. Add a test that runs scoring on a TH brand and asserts the `six_month_avg_threshold` threshold used is the THB value, not the IDR value.

**Warning signs:**
- TH brand evaluations pass the 6-month revenue threshold instantly (IDR threshold too low in THB terms)
- Or TH brand evaluations always fail the threshold (if the conversion went wrong)
- Rules page only shows one tab despite two marketplace rule sets existing in DB

**Phase to address:**
Rules + scoring phase — when marketplace-scoped rules are introduced to the DB.

---

### Pitfall 4: Hardcoded `IDR` currency label in scoring output messages leaks into THB evaluations

**What goes wrong:**
`messages.py` (lines 97, 105), `categories.py` (line 531), and `DEFAULT_RULES` in `rules.py` all contain string literals like `"IDR {idr_val}"`, `"IDR {selling_price}"`, `"IDR {market_price}"`. The DB `scoring_rules` table also has these strings stored as JSONB values (set via migrations 021+). When a THB evaluation runs and loads these rules from DB, the output email and scoring display will read "IDR 191,591" for a Thai brand — incorrect and confusing to the client.

**Why it happens:**
The currency label was hardcoded before multi-marketplace existed. Both the Python fallback defaults AND the DB-stored templates contain `IDR`. Changing only the code fallbacks without a migration that updates DB values (or vice versa) creates a split — some evaluations use DB templates (IDR label), some fall back to code (updated label). Migration 021 already showed this three-location problem exists.

**How to avoid:**
Make message templates currency-agnostic using a `{currency}` placeholder: `"{currency} {val}"`. Pass `currency="IDR"` or `currency="฿"` based on marketplace when rendering. This requires updating: (1) `DEFAULT_RULES` constants in `rules.py`, (2) a new migration for DB-stored templates, (3) scoring message rendering functions that accept/inject the `currency` symbol. The code comment in `rules.py` that documents the three-location problem (`# NOTE (source of truth)`) is the exact guide for what to update.

**Warning signs:**
- Test `TestMigrationTemplatesDrift` fails after DB update but before code update
- Scoring output for TH brands contains "IDR" label
- Email body sent to Thai clients says "IDR" amounts

**Phase to address:**
Rules + message rendering phase — same phase as marketplace-scoped rules.

---

### Pitfall 5: `CurrencyField` component is hardcoded to IDR — adding THB requires prop-threading or forking

**What goes wrong:**
`CurrencyField.tsx` hardcodes `(IDR)` in the label and calls `formatIDR`/`parseIDR` from `formConfig`. `DataIntelligence.tsx` and `EvaluationDetailPage.tsx` also define local `formatIDR` functions (duplicate logic). `TopSkuResults.tsx` hardcodes `IDR {formatIDR(...)}` in table cells. If a THB brand's evaluation form is rendered, users see `(IDR)` labels and the input/output formatting uses dot-thousands (IDR style) on THB values.

**Why it happens:**
The component was built for a single-currency system. The currency label is not a prop — it is embedded in JSX. There are three independent `formatIDR` implementations across the frontend with no shared utility.

**How to avoid:**
Extend `CurrencyField` with a `currency: 'IDR' | 'THB'` prop. Extract a shared `formatCurrency(value, currency)` function in `formUtils.ts` that handles both formats. Remove the duplicate local `formatIDR` functions in `DataIntelligence.tsx` and `EvaluationDetailPage.tsx`. Add `TopSkuResults.tsx` to the list of files to audit for hardcoded `IDR` strings. Do this refactor before building the THB evaluation form, not after.

**Warning signs:**
- Thai brand evaluation form shows `(IDR)` label
- THB monetary values display with dot-thousands format (e.g., `191.591`) instead of comma-thousands (e.g., `191,591`)
- `grep -rn "IDR" frontend/src --include="*.tsx"` returns hits in files not yet updated

**Phase to address:**
Frontend currency abstraction phase — before any THB-specific UI is built.

---

### Pitfall 6: Shopee Thailand CSV column headers may differ from Indonesian headers

**What goes wrong:**
The parser's `REQUIRED_COLUMNS` dict contains Indonesian-language column names (`"No. Pesanan"`, `"Harga Awal"`, etc.). The existing `_normalise_english_columns` function handles the known English→Indonesian rename set. However, Shopee Thailand may export CSVs with Thai-language column headers, or a different English column header set than the Indonesian English variant. If Shopee TH uses Thai headers that don't match `REQUIRED_COLUMNS`, every TH file upload fails with `UPLOAD_MISSING_COLUMNS`.

**Why it happens:**
The normalisation layer was written based on observed Indonesian CSV exports only. The assumption "same format" in the project requirements means same data structure, but header language is a separate concern. Shopee localises its seller center per market, so Thai sellers on Shopee Thailand see Thai-language UI and likely Thai-language CSV exports.

**How to avoid:**
Before the milestone starts, obtain a real Shopee Thailand CSV sample for each file type (`cpc_ad_report`, `keyword_report`, `order_export`, `mass_update`). Verify header language. If Thai headers exist, extend `_COLUMN_RENAME` with Thai→Indonesian mappings or generalise to a language-agnostic column key system. Do not assume the "same structure" claim in PROJECT.md extends to header language.

**Warning signs:**
- TH file uploads rejected with `UPLOAD_MISSING_COLUMNS`
- `source_language` returned as `"id"` for all TH uploads (no rename triggered)
- Thai seller reports column headers that look like `ชื่อโฆษณา` instead of `Nama Iklan`

**Phase to address:**
Upload/CSV parsing phase — validate with real TH data before implementing the phase.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Duplicate `_clean_price` in `discount.py` and `top_sku.py` | No change needed now | Two places to add `marketplace` parameter; easy to miss one | Never — fix both at the same time when adding THB |
| Duplicate `formatIDR` in `DataIntelligence.tsx`, `EvaluationDetailPage.tsx`, `formUtils.ts` | Each file self-contained | THB formatting requires updating three files independently; divergence risk | Never — consolidate into `formUtils.ts` before THB work |
| Hardcoded `"IDR"` in `DEFAULT_RULES` string templates | Simple to read | Every multi-currency addition requires a migration + code change + template update | Acceptable for a single-currency system; unacceptable once two currencies exist |
| Adding THB rules as a new DB template row without migration testing | Fast to implement | DB template drift (caught by `TestMigrationTemplatesDrift`) goes undetected if test not extended | Never for production data |
| Converting IDR thresholds to THB once at migration time and leaving them | Reasonable starting values | Thresholds may drift if exchange rate changes significantly; no audit trail | Acceptable — PROJECT.md explicitly states thresholds are manually editable after initial seed |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Shopee Thailand CSV upload | Assuming same column names as Indonesian CSV | Obtain a real TH CSV sample; map headers before assuming column parity |
| PostgreSQL `scoring_rules` JSONB | Updating code `DEFAULT_RULES` without a paired migration (or vice versa) | Always treat the three-location rule: `DEFAULT_RULES`, migration, and rendering code must be updated atomically |
| Alembic migration on populated `brand_vp_data` | Adding `NOT NULL` column in one step on a non-empty table | Two-step: add nullable with default, backfill, then add constraint |
| `generate_score` call chain | Passing `template` (fashion/non_fashion) but forgetting `marketplace` when selecting rules | The `template` parameter controls fashion logic; `marketplace` controls which rules row to load — keep them separate |

---

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Loading all scoring rules for every evaluation (both IDR and THB rows) | Slightly increased DB query time | `get_rules_by_marketplace` loads only the relevant row — one query, filtered | Not a concern at current scale; monitor if rule sets multiply |
| Re-parsing THB number strings on every scoring run (no cached parse) | Negligible at current brand counts | Keep `_parse_price` pure and stateless — acceptable | Not a concern unless brand count reaches tens of thousands |

---

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| `update_rules` endpoint accepts `template` as a path parameter with `Literal["fashion", "non_fashion", "default"]` — THB template name not yet in the allowlist | Rule update for `default_TH` returns 422, not 404 — confusing error | Add new marketplace template names to the `Literal` type annotation in the router before the rules page ships marketplace tabs |
| Conversion rate from IDR→THB hardcoded as a constant in migration | Rate changes mean thresholds silently become stale | Document the exchange rate used and date in the migration comment; admin UI shows "last edited by / when" |

---

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Rules page shows all rule sets without marketplace tabs | Admin sees IDR and THB thresholds interleaved — cannot tell which is which | Add marketplace tab selector (IDR / THB) before exposing multi-marketplace rules in the admin UI |
| Evaluation page shows all brands regardless of marketplace | Evaluator selects a TH brand, IDR rules load silently | Marketplace context must be visible at the top of the evaluation page; auto-select based on brand's `marketplace` field |
| CurrencyField label says `(IDR)` for Thai brands | Thai brand's monetary input field reads IDR — evaluator may enter wrong scale | `currency` prop drives the label; `formatCurrency` drives display |
| Evaluation history mixes IDR and THB scores with no marketplace indicator | Final score is dimensionless, but threshold basis differs — a TH brand with score 65 is not comparable to IDR brand with score 65 unless context is shown | Add marketplace badge to evaluation list and detail views |

---

## "Looks Done But Isn't" Checklist

- [ ] **`_clean_price` migration:** Check both `discount.py` and `top_sku.py` — they have independent copies of the same function. Verify [both updated with `marketplace` parameter].
- [ ] **Currency label in output messages:** Check `DEFAULT_RULES` (code), `scoring_rules` table (DB), and fallback strings in `messages.py`. Verify [all three updated, `TestMigrationTemplatesDrift` passes].
- [ ] **Frontend IDR references:** `grep -rn '"IDR"' frontend/src --include="*.tsx" --include="*.ts"` should return zero hits in files serving THB brands. Verify [all component-level occurrences replaced with currency-aware prop].
- [ ] **Rules router Literal allowlist:** `router.py` `Literal["fashion", "non_fashion", "default"]` must include THB template name. Verify [PUT endpoint accepts new template name without 422].
- [ ] **Existing brands migration:** After migration, `SELECT COUNT(*) FROM brand_vp_data WHERE marketplace IS NULL` should return 0. Verify [migration backfill was applied].
- [ ] **Scoring call chain marketplace threading:** `generate_score(...)` must pass `marketplace` to `get_rules_by_template`. Verify [TH brand evaluation uses THB `six_month_avg_threshold`, not IDR value].

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Wrong `_clean_price` logic processes THB data | HIGH — stored `calculator_results` contain corrupted values | Add migration or script to delete calculator results for TH brands; re-run calculators after parser fix |
| `marketplace` column missing from some SELECT queries | MEDIUM — evaluation page shows stale context | Add `marketplace` to missing query SELECTs; no data loss |
| DB `scoring_rules` templates still contain `IDR` label for TH | LOW — cosmetic error in output text | Write a targeted migration patching only the THB template messages |
| CurrencyField shows IDR label for TH brands | LOW — visual bug, no data corruption | Change prop threading in evaluation form; redeploy frontend |
| Shopee TH CSV columns rejected at upload | MEDIUM — TH brands cannot be evaluated until fixed | Add Thai column mapping to parser and redeploy backend; no stored data affected |

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| `_clean_price` IDR-only assumption | CSV/Upload phase | Unit test: `_parse_price("1,250.50", "TH")` returns `1250.5`; `_parse_price("1.250.000", "ID")` returns `1250000` |
| Migration backfill of existing brands | Data model phase | `SELECT COUNT(*) FROM brand_vp_data WHERE marketplace IS NULL` returns 0 post-migration |
| Rules table marketplace dimension | Rules model phase | `get_rules_by_marketplace("TH")` returns THB thresholds; TH evaluation uses THB `six_month_avg_threshold` |
| Hardcoded `IDR` in message templates | Message/rendering phase | `TestMigrationTemplatesDrift` passes; TH evaluation output contains `฿` not `IDR` |
| `CurrencyField` hardcoded IDR | Frontend currency abstraction phase | TH brand evaluation form label reads `(THB)`; formatted value uses comma-thousands |
| Shopee TH CSV column headers | Upload/CSV phase (validate early) | TH `cpc_ad_report` upload succeeds with real TH CSV; `source_language` reflects correct detection |
| Rules router Literal allowlist | Rules admin phase | PUT `/api/v1/rules/default_TH` returns 200, not 422 |

---

## Sources

- Codebase inspection: `/backend/app/calculators/discount.py`, `top_sku.py`, `scoring/helpers.py`, `scoring/messages.py`, `scoring/rules.py` (DEFAULT_RULES) — HIGH confidence (direct code read)
- Codebase inspection: `/backend/app/modules/rules/router.py`, `service.py`, `evaluations/service.py` — HIGH confidence
- Codebase inspection: `/frontend/src/components/evaluation/forms/CurrencyField.tsx`, `formUtils.ts` — HIGH confidence
- Codebase inspection: `/backend/app/db/migrations/versions/021_internationalize_currency_rp_to_idr.py` — HIGH confidence (three-location problem documented in code itself)
- Thai Baht number format (period=decimal, comma=thousands): Wikipedia Thai baht, FastSpring currency format guide — MEDIUM confidence
- Indonesian Rupiah number format (comma=decimal, period=thousands): Wikipedia Indonesian rupiah, Quora — HIGH confidence (well established)
- Migration two-step pattern for NOT NULL columns: General PostgreSQL best practice — HIGH confidence

---
*Pitfalls research for: THB multi-currency expansion, AHA SICU evaluation system*
*Researched: 2026-03-16*