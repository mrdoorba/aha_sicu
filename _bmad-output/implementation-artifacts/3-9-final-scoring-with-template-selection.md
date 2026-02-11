# Story 3.9: Final Scoring with Scoring System Template

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **system**,
I want **to generate a final score using the 75-row scoring system template (Fashion/Non-Fashion variants)**,
so that **the BD team gets the overall brand qualification assessment with per-category score breakdown, verdict, and generated email/WhatsApp output**.

## Acceptance Criteria

1. **Per-category score computation**
   **Given** calculator results and manual inputs are available for a brand
   **When** the scoring system is executed with Fashion or Non-Fashion template
   **Then** compute per-category scores matching the authoritative spec (`logic/scoring-system-template-sicu.md`):

   | Category | Rows | Max Points | Scoring Logic |
   |----------|------|------------|---------------|
   | Operational | H7-H9 | 10 (can go negative) | Pesanan Tidak Terselesaikan: ✔️=4, >1%=-(value×100). Keterlambatan: ✔️=3, >1%=-(value×100). Pengemasan: ✔️=3, >1 day=-(excess×100) |
   | Business | H13, H19 | 20 | H13: 10 if current month not inflated (avg < current×110%), else 0. H19: 10 if avg >100M IDR, else 0 |
   | Visitors | H28-H29 | 5 | H28: % returning visitors >23% → 3pts. H29: followers >50000 → 2pts |
   | Promo Tools | H42-H43 | 0 to 15 (opportunity) | H42: ❌=5 (usage <80%). H43: ❌=10 (effectiveness <90%) |
   | Products/Status | H45-H46 | 15 | H45: products ≥35 → 5pts. H46: Mall=10, Star+=5, else 0 |
   | Ads | H50-H51 | -5 to 10 | H50: ROI <threshold → 5 (opportunity). H51: GMV ratio <84% → 5pts. Fashion threshold: >8, Non-Fashion: >9 |
   | Campaign | H57 | 0 to 10 (opportunity) | Participation <90% → 10 (opportunity) |
   | Stock | H70 | -5 to 10 | From Calculator 2 average_stock. ≥24=10, ≥12=5, <12=-5 |
   | Discount | H73 | 0 or 5 | From Calculator 3 fake_discount_flag. No flag=5, flag=0 |

2. **Fashion-specific thresholds applied**
   **Given** the user selected "Fashion" template
   **When** scoring is computed
   **Then** apply Fashion-specific thresholds:
   - ROI threshold: >8 (Fashion) vs >9 (Non-Fashion)
   - G72 marketing: +5% for Fashion
   - Conversion benchmark: >2% (Fashion) vs >3% (Non-Fashion)

3. **Derived formulas computed**
   **Given** scoring is computed with discount data available
   **When** generating derived values
   **Then** compute:
   - G68: Marketing cost estimation from discount data (parses D73 text for discount %, range, voucher %, paket %) combined with ad cost %
   - G72: Recommended marketing percentage (complex MIN/MAX formula with Fashion adjustment)
   - G73: Marketing budget recommendation text (monthly sales × G72 percentage)

4. **Final score and verdict**
   **Given** all per-category scores are computed
   **When** generating the final result
   **Then** compute:
   - H4: Total score = SUM of all H-column scores (range: negative to ~100)
   - F75: Verdict — one of "✔️", "❌", "❌ Non Mall", "❌ No Brand", "❌ Opex", "⭕️", or empty (passed as input by user)

5. **G-column output messages generated**
   **Given** per-category scores and verdicts are computed
   **When** generating output
   **Then** produce Indonesian-language text messages for each metric row matching the spec:
   - Operational: "[✔️/❌] [Metric] = [value] [Sudah Baik / Kurang Baik, nilai disarankan: ...]"
   - Business: Sales trend with percentage increase/decrease vs 6-month average, >25% decline warning
   - Promo Tools: Per-tool usage/effectiveness messages with percentage of sales
   - Ads: ROI, GMV ratio, ad cost messages with specific thresholds
   - Competition: Price competitiveness check (selling price vs market price ×110%)
   - G66: Conclusion summary (multi-line text with store analysis)
   - G73: Marketing budget recommendation (if verdict allows)
   - G75: Closing message based on verdict type

6. **Email output generated**
   **Given** all G-column messages are computed
   **When** generating email output
   **Then** produce a structured email body with:
   - Subject: "🏥 AHA Store Internal Check Up (Store ICU) - [Store Name] [Period]"
   - Body sections: Operational → Sales → Content → Visitors → Promo → Ads → Campaign → Competition → Conclusion → Marketing → Budget → Closing
   - All G-column values assembled in order

7. **WhatsApp output generated**
   **Given** the scoring is complete
   **When** generating WhatsApp output
   **Then** produce an `api.whatsapp.com` link with pre-formatted message referencing store name and period

8. **Frontend score panel displays real-time scores**
   **Given** I am on the evaluation page with manual inputs and calculator results
   **When** viewing the Score Summary panel (right sidebar)
   **Then** I see:
   - Final score with verdict icon
   - Per-category score breakdown (Operational, Business, Visitors, Promo Tools, Products, Ads, Campaign, Stock, Discount)
   - Template indicator (Fashion/Non-Fashion)
   - Expandable detail showing full breakdown

9. **Frontend final scoring section in evaluation flow**
   **Given** I am on the evaluation page in the final section
   **When** calculator results and manual inputs are available
   **Then** I see:
   - "Generate Score" button (enabled when minimum data available)
   - Final score display with per-category breakdown table
   - Generated email body (copyable)
   - WhatsApp link (clickable)
   - Verdict selector dropdown (✔️, ❌, ❌ Non Mall, ❌ No Brand, ❌ Opex, ⭕️)

10. **Score recalculation on data change**
    **Given** a final score has been generated
    **When** manual inputs or calculator results change
    **Then** the existing score is marked as "stale" (need recalculation)
    **And** I see a "Recalculate" button

11. **Backend scoring endpoint**
    **Given** I call `POST /api/v1/evaluations/brands/{brand_id}/score`
    **When** authenticated and data is available
    **Then** the scoring calculator runs with current manual inputs + calculator results
    **And** returns the complete scoring result (scores, messages, email, whatsapp)

12. **Missing data handling**
    **Given** required calculator results are missing (no average_stock or no discount data)
    **When** attempting to generate final score
    **Then** show which calculators need to run first
    **And** compute partial scores for categories with available data
    **And** mark missing categories as "N/A"

## Tasks / Subtasks

- [x] Task 1: Create scoring calculator pure function (AC: #1, #2, #3, #4)
  - [x] 1.1 Create `backend/app/calculators/scoring.py` with `ScoringResult` dataclass
  - [x] 1.2 Implement per-category scoring functions matching spec exactly:
    - `_score_operational()` — H7-H9 with negative penalty logic
    - `_score_business()` — H13 (trend), H19 (average threshold)
    - `_score_visitors()` — H28 (returning %), H29 (followers)
    - `_score_promo_tools()` — H42-H43 (usage + effectiveness opportunity)
    - `_score_products()` — H45 (count ≥35), H46 (Mall/Star+)
    - `_score_ads()` — H50 (ROI with Fashion threshold), H51 (GMV ratio)
    - `_score_campaign()` — H57 (participation opportunity)
    - `_score_stock()` — H70 (from Calculator 2 average_stock)
    - `_score_discount()` — H73 (from Calculator 3 fake_discount_flag)
  - [x] 1.3 Implement F-column verdict logic (pass/fail per metric)
  - [x] 1.4 Implement Fashion vs Non-Fashion threshold selection
  - [x] 1.5 Compute total score H4 = SUM(all H scores)

- [x] Task 2: Implement G-column output message generation (AC: #5, #6, #7)
  - [x] 2.1 Implement per-row G-column text generation in Indonesian
  - [x] 2.2 Implement G66 conclusion summary (multi-line)
  - [x] 2.3 Implement G68 marketing cost estimation (parse D73 text)
  - [x] 2.4 Implement G72 recommended marketing percentage (complex formula)
  - [x] 2.5 Implement G73 marketing budget recommendation text
  - [x] 2.6 Implement G75 closing message based on verdict
  - [x] 2.7 Implement email body assembly (G1) — structured sections
  - [x] 2.8 Implement WhatsApp link generation (E1)

- [x] Task 3: Add backend scoring endpoint (AC: #11, #12)
  - [x] 3.1 Add `POST /api/v1/evaluations/brands/{brand_id}/score` endpoint in `evaluations/router.py`
  - [x] 3.2 Add `ScoringRequest` and `ScoringResponse` schemas in `evaluations/schemas.py`
  - [x] 3.3 Add scoring service function that loads manual_data + calculator results, calls scoring calculator
  - [x] 3.4 Handle missing data gracefully (partial scores, missing categories = N/A)

- [x] Task 4: Write backend unit tests for scoring calculator (AC: #1-#7)
  - [x] 4.1 Test per-category scoring with known inputs matching spec examples
  - [x] 4.2 Test Fashion vs Non-Fashion threshold differences
  - [x] 4.3 Test negative score scenarios (operational penalties, stock penalty)
  - [x] 4.4 Test G-column message generation (Indonesian text, formatting)
  - [x] 4.5 Test G68/G72/G73 derived formulas
  - [x] 4.6 Test email body assembly structure
  - [x] 4.7 Test edge cases: missing calculator data, zero values, extreme values

- [x] Task 5: Add backend integration test for scoring endpoint (AC: #11, #12)
  - [x] 5.1 Test scoring endpoint with full data
  - [x] 5.2 Test scoring endpoint with missing calculator results
  - [x] 5.3 Test auth required

- [x] Task 6: Create frontend scoring display components (AC: #8, #9)
  - [x] 6.1 Create `frontend/src/components/evaluation/scoring/ScoreBreakdown.tsx` — per-category breakdown table
  - [x] 6.2 Create `frontend/src/components/evaluation/scoring/FinalScoreDisplay.tsx` — score with verdict
  - [x] 6.3 Create `frontend/src/components/evaluation/scoring/EmailOutput.tsx` — copyable email body
  - [x] 6.4 Create `frontend/src/components/evaluation/scoring/WhatsAppLink.tsx` — clickable WA link
  - [x] 6.5 Create `frontend/src/components/evaluation/scoring/VerdictSelector.tsx` — verdict dropdown
  - [x] 6.6 Create `frontend/src/components/evaluation/scoring/ScoringSection.tsx` — orchestrator with "Generate Score" button
  - [x] 6.7 Create `frontend/src/components/evaluation/scoring/index.ts` — re-exports

- [x] Task 7: Create scoring hook and integrate Score Panel (AC: #8, #10)
  - [x] 7.1 Add `useScoring(brandId)` hook in `frontend/src/hooks/useScoring.ts` — mutation to generate score, query to fetch
  - [x] 7.2 Add path types for scoring endpoint in `apiClient.ts`
  - [x] 7.3 Replace Score Summary placeholder in `EvaluationPage.tsx` with real `ScorePanel` component
  - [x] 7.4 Implement stale detection: mark score stale when manual data or calculator results change

- [x] Task 8: Integrate scoring section into EvaluationSections (AC: #9)
  - [x] 8.1 Add scoring section to `EvaluationSections.tsx` after calculator results
  - [x] 8.2 Add "Final Score" entry in `SectionNav.tsx`
  - [x] 8.3 Wire verdict selection to scoring state

- [x] Task 9: Write frontend component tests (AC: #8, #9)
  - [x] 9.1 Test ScoreBreakdown renders per-category scores
  - [x] 9.2 Test FinalScoreDisplay renders score and verdict
  - [x] 9.3 Test EmailOutput renders copyable email body
  - [x] 9.4 Test ScoringSection shows "Generate Score" button, handles loading/error
  - [x] 9.5 Test VerdictSelector options and change handler

## Dev Notes

### Authoritative Specification

**THE spec for this story is `logic/scoring-system-template-sicu.md`**. Every formula, threshold, text message, and scoring rule MUST match this spec exactly. The epics file (Story 3.9) provides a summary, but the logic file is the ground truth.

### Story Context — Backend-Heavy Scoring Logic + Frontend Display

This story has two major parts:
1. **Backend**: Implement the 75-row scoring system as a pure function in `calculators/scoring.py`. This is the most complex calculator — it combines manual inputs from ALL categories with Calculator 2 (average_stock) and Calculator 3 (fake_discount_flag and discount text) outputs.
2. **Frontend**: Display the scoring results and replace the placeholder Score Panel.

### Scoring Calculator Architecture

The scoring calculator is different from Calculators 1-3:
- **Input**: ManualData (all categories) + Calculator 2 `average_stock` + Calculator 3 `details` (discount_pct, range, voucher_pct, paket_pct, fake_discount_flag) + Calculator 1 `output_text` (for G53 email)
- **Output**: Per-category scores, total score, F-column verdicts, G-column messages, email body, WhatsApp link
- **Template**: Fashion vs Non-Fashion affects specific thresholds (ROI, marketing %, conversion)

The calculator is a **pure function** — no I/O. The service layer loads data and passes it in.

```python
# calculators/scoring.py

@dataclass
class CategoryScore:
    category: str
    score: float
    max_score: float
    rows: list[RowScore]  # Individual row scores (H7, H8, etc.)

@dataclass
class RowScore:
    row: int
    metric: str
    value: Any          # D column: raw value
    benchmark: str      # E column: threshold
    verdict: str        # F column: "✔️" or "❌" or "-"
    message: str        # G column: text output
    score: float        # H column: points

@dataclass
class ScoringResult:
    total_score: float
    category_scores: list[CategoryScore]
    verdict: str                    # F75 value
    conclusion: str                 # G66
    marketing_estimation: str       # G68
    marketing_percentage: str       # G72
    marketing_budget: str           # G73
    closing_message: str            # G75
    email_subject: str
    email_body: str                 # G1 assembled
    whatsapp_link: str              # E1
    template: str                   # "fashion" or "non_fashion"

def calculate_score(
    manual_data: dict,
    calculator_results: dict,     # {calc_type: {details, output_text}}
    template: str,                # "fashion" or "non_fashion"
    verdict: str,                 # F75 user-selected verdict
    store_name: str,
    period: str,
    brand_name: str,
    email: str | None = None,
) -> ScoringResult:
    """Pure function: compute the full scoring system."""
```

### Critical Scoring Rules Reference (from spec)

**Operational (H7-H9) — Can go NEGATIVE:**
```python
# H7: Pesanan Tidak Terselesaikan
if value <= 0.01:  # <1%
    score = 4
else:
    score = -(value * 100)  # Penalty: -1 per 1%

# H8: Keterlambatan
if value <= 0.01:
    score = 3
else:
    score = -(value * 100)

# H9: Masa Pengemasan
if value <= 1:  # days
    score = 3
else:
    score = -((value - 1) * 100)
```

**Business (H13, H19):**
```python
# H13: Current month vs 6-month average
avg_6mo = average(sales_month0..sales_month5)
score_h13 = 10 if avg_6mo < sales_month0 * 1.10 else 0

# H19: Average > 100M IDR
score_h19 = 10 if avg_6mo > 100_000_000 else 0
```

**Promo Tools (H42-H43) — OPPORTUNITY scoring (points when ❌):**
```python
# F column for promo rows 31-41:
# Pass if D > 0 AND D/D13 < 50% AND D >= benchmark% × D13

# H42: Usage rate
usage_rate = count(promo_values > 0) / total_promo_tools
score_h42 = 0 if usage_rate > 0.80 else 5  # Points when underused

# H43: Effectiveness rate
effectiveness_rate = count(promo_pass) / total_promo_tools
score_h43 = 0 if effectiveness_rate > 0.90 else 10  # Points when ineffective
```

**Ads (H50-H51) — Fashion-dependent:**
```python
# H50: ROI
roi = ad_sales / ad_cost if ad_cost > 0 else 0
roi_threshold = 8 if template == "fashion" else 9
score_h50 = 0 if roi >= roi_threshold else 5  # Opportunity

# H51: GMV ratio
gmv_ratio = ad_sales / current_month_sales if sales > 0 else 0
score_h51 = 5 if gmv_ratio < 0.84 else 0
```

**Stock (H70) — From Calculator 2:**
```python
avg_stock = calculator_results["top_sku"]["details"]["average_stock"]
if avg_stock >= 24:
    score_h70 = 10
elif avg_stock >= 12:
    score_h70 = 5
else:
    score_h70 = -5  # Penalty
```

**Discount (H73) — From Calculator 3:**
```python
fake_flag = calculator_results["discount"]["details"]["fake_discount_flag"]
score_h73 = 0 if fake_flag else 5
```

### G68 Marketing Cost Estimation — Complex Text Parsing

G68 parses the discount calculator's D73 text output using regex to extract percentages, then combines with ad cost %:

```python
def _compute_g68(d73_text: str, d52_ad_cost_pct: float) -> str:
    """Parse discount text and compute marketing cost range."""
    # Extract: "% Diskon TOP SKU: X%", "Range: X% ~ Y%", "Voucher X%", "Paket Diskon X%"
    t = extract_pct("% Diskon TOP SKU: ([\d.]+)%", d73_text) / 100
    ra = extract_pct("Range: ([\d.]+)%", d73_text) / 100
    rb = extract_pct("~ ([\d.]+)%", d73_text) / 100
    v = extract_pct("Voucher ([\d.]+)%", d73_text) / 100
    p = extract_pct("Paket Diskon ([\d.]+)%", d73_text) / 100

    low = (ra * t) + v + p + d52_ad_cost_pct + 0.05
    high = (rb * t) + v + p + d52_ad_cost_pct + 0.05
    result = f"{low:.1%} ~ {high:.1%}"

    if "fake discount" in d73_text.lower() or "Berpotensi" in d73_text:
        result += "\n📌 Berpotensi menggunakan 'fake discount'"
    return result
```

### G72 Marketing Percentage — Complex MIN/MAX Formula

```python
def _compute_g72(g68_text: str, d52: float, d73_text: str, is_fashion: bool) -> float:
    """Compute recommended marketing percentage."""
    # Parse percentages from D73
    t, ra, rb, v, p = _parse_d73_percentages(d73_text)

    avg = ((ra*t + v + p + d52) + (rb*t + v + p + d52)) / 2
    base = round_down(avg - 0.03, 2)  # avg - 3%, rounded down to 2 decimals

    upper_limit = 0.20 + (0.05 if is_fashion else 0)  # 25% Fashion, 20% Non-Fashion
    g68_first = parse_first_pct(g68_text)  # First number from G68

    min_val = min(min(base, upper_limit), g68_first)
    result = max(max(min_val, 0.10), 0.15 if is_fashion else 0.12)

    return result
```

### Promo Tool F-Column Logic (Rows 31-41) — Critical Detail

Each promo tool row has special F-column logic:
```python
def _promo_verdict(d_value: float, d13_sales: float, benchmark_pct: float) -> str:
    if d_value == 0:
        return "❌"  # Not used at all
    if d13_sales > 0 and d_value / d13_sales >= 0.50:
        return "❌"  # Too dependent (>50% of sales)
    if d13_sales > 0 and d_value >= benchmark_pct * d13_sales:
        return "✔️"  # Meets benchmark
    return "❌"  # Below benchmark
```

### Verdict (F75) — User-Selected, NOT Computed

The verdict is a **manual user selection**, not computed. The scoring calculator receives it as input and uses it to control G73 (marketing budget) and G75 (closing message).

### How Calculator Results Feed Into Scoring

```
Calculator 1 (Ads Keyword) → output_text → G53 (pasted into email body)
Calculator 2 (Top SKU)     → details.average_stock → D70 → H70 (stock score)
                           → details.output_1[0..2] → C61-C63 (top product prices for competition)
Calculator 3 (Discount)    → details.fake_discount_flag → H73 (discount score)
                           → output_text → D73 (text for G68 parsing)
                           → details.discount_pct, range, voucher, paket → G68 components
```

### Frontend Architecture for Scoring

```
EvaluationPage.tsx
  ├── (left) SectionNav.tsx — add "Final Score" entry
  ├── (center) EvaluationSections.tsx
  │     └── ScoringSection.tsx          ← NEW orchestrator
  │           ├── VerdictSelector.tsx    ← NEW
  │           ├── FinalScoreDisplay.tsx  ← NEW
  │           ├── ScoreBreakdown.tsx     ← NEW
  │           ├── EmailOutput.tsx        ← NEW
  │           └── WhatsAppLink.tsx       ← NEW
  └── (right) ScorePanel.tsx            ← NEW (replaces placeholder)
```

**File placement:** `frontend/src/components/evaluation/scoring/` — new subdirectory.

### State Management for Scoring

```
useScoring(brandId) → {
  generateScore: TanStack Mutation → POST /api/v1/evaluations/brands/{brand_id}/score
  scoringResult: TanStack Query → cached scoring result (or null)
  isStale: boolean → true when manualData or calculatorResults changed after last score
}
```

**Cache invalidation:**
- Scoring result cached with queryKey `['scoring', brandId]`
- When manual data changes (auto-save) → mark scoring as stale (don't auto-invalidate — user must click "Recalculate")
- When calculator results change → mark scoring as stale

### Score Panel Design (Right Sidebar)

Replace the current placeholder in `EvaluationPage.tsx` (lines 105-157) with a real `ScorePanel` component:

```tsx
// ScorePanel shows:
// - Final score (large number) or "—" if not generated
// - Verdict icon
// - Per-category scores in compact format
// - "Generate" or "Recalculate" button
// - Stale indicator when data changed
```

### Existing Code to Integrate With

**Backend (existing):**
- `calculators/engine.py` — add scoring to orchestration (or keep separate since it needs verdict input)
- `modules/evaluations/router.py` — add POST /score endpoint
- `modules/evaluations/schemas.py` — add scoring request/response
- `modules/evaluations/service.py` — add scoring service function
- `modules/evaluations/calculator_service.py` — existing calculator runners (no changes needed)
- `db/queries/evaluations.py` — `get_evaluation_inputs()` for loading manual data
- `db/queries/calculator_results.py` — `get_results_by_brand()` for loading calc results

**Frontend (existing):**
- `EvaluationPage.tsx` — Score Panel placeholder (lines 105-157)
- `EvaluationSections.tsx` — add final scoring section
- `SectionNav.tsx` — add "Final Score" nav entry
- `hooks/useCalculator.ts` — `useCalculatorResults()` for reading calc data
- `hooks/useEvaluation.ts` — `useEvaluationState()` for reading manual data
- `hooks/useAutoSaveForm.ts` — `manualData` state
- `components/evaluation/forms/formConfig.ts` — `ManualData` type, `formatIDR()`

### ManualData Field Mapping to Scoring Rows

| Scoring Row | ManualData Field | Category |
|-------------|-----------------|----------|
| D7 | `operational.unfulfilledOrderRate` | Operational |
| D8 | `operational.lateShipmentRate` | Operational |
| D9 | `operational.preparationTime` | Operational |
| D10 | `operational.chatResponseRate` | Operational |
| D11 | `operational.overallRating` | Operational |
| D13 | `business.salesMonth0` | Business (current month) |
| D14-D18 | `business.salesMonth1..salesMonth5` | Business (past months) |
| D20 | `business.conversionRate` | Business |
| D22 | `content.needsImprovement` | Content |
| D23 | `content.goodQuality` | Content |
| D26 | `visitors.totalVisitors` | Visitors |
| D27 | `visitors.returningVisitors` | Visitors |
| D29 | `visitors.totalFollowers` | Visitors |
| D31-D41 | `promoTools.*` (11 fields) | Promo Tools |
| D45 | `products.productCount` | Products |
| D46 | `products.storeStatus` | Products |
| D48 | `ads.adSales` | Ads |
| D49 | `ads.adCost` | Ads |
| D55 | `campaign.nominatedSessions` | Campaign |
| D56 | `campaign.availableSessions` | Campaign |
| D61-D63 | `competition.product1..3.keyword/marketPrice` | Competition |
| D70 | Calculator 2: `details.average_stock` | Stock |
| D73 | Calculator 3: `output_text` | Discount |

### Promo Tools Benchmark Map

```python
PROMO_BENCHMARKS = {
    "promoToko": 0.08,        # >8%
    "paketDiskon": 0.16,      # >16%
    "komboHemat": 0.01,       # >1%
    "flashSale": 0.01,        # >1%
    "voucher": 0.84,          # >84%
    "shopeeLive": 0.15,       # >15%
    "gameToko": 0.01,         # >1%
    "brandMembership": 0.01,  # >1%
    "gratisOngkir": 0,        # >0 (any amount)
    "chatBroadcast": 0.01,    # >1%
    "programAfiliasi": 0.18,  # >18%
}
```

### Project Structure Notes

**New files to create:**
```
backend/app/calculators/scoring.py                                    ← Main scoring logic
backend/tests/unit/calculators/test_scoring.py                       ← Unit tests
backend/tests/integration/api/test_scoring.py                        ← Integration tests
frontend/src/components/evaluation/scoring/ScoreBreakdown.tsx         ← Per-category table
frontend/src/components/evaluation/scoring/FinalScoreDisplay.tsx      ← Score + verdict
frontend/src/components/evaluation/scoring/EmailOutput.tsx            ← Copyable email
frontend/src/components/evaluation/scoring/WhatsAppLink.tsx           ← WA link
frontend/src/components/evaluation/scoring/VerdictSelector.tsx        ← Verdict dropdown
frontend/src/components/evaluation/scoring/ScoringSection.tsx         ← Orchestrator
frontend/src/components/evaluation/scoring/ScorePanel.tsx             ← Right sidebar panel
frontend/src/components/evaluation/scoring/index.ts                   ← Re-exports
frontend/src/hooks/useScoring.ts                                      ← Scoring hook
```

**Existing files to modify:**
```
backend/app/modules/evaluations/router.py          ← Add POST /score endpoint
backend/app/modules/evaluations/schemas.py         ← Add scoring schemas
backend/app/modules/evaluations/service.py         ← Add scoring service function
frontend/src/services/apiClient.ts                 ← Add scoring path type
frontend/src/pages/EvaluationPage.tsx              ← Replace Score Panel placeholder
frontend/src/components/evaluation/EvaluationSections.tsx ← Add scoring section
frontend/src/components/evaluation/SectionNav.tsx  ← Add "Final Score" nav entry
```

### Architecture Compliance

**Backend Pattern (MUST follow):**
- Scoring calculator is a **pure function** in `calculators/scoring.py` — no database I/O inside
- Service layer (`modules/evaluations/service.py`) loads data from DB, calls calculator, returns result
- New endpoint in `modules/evaluations/router.py` — follows REST convention
- Response schema in `modules/evaluations/schemas.py` — Pydantic model
- Auth required via `Depends(get_current_user)`
- Exception chaining: always `raise ... from e`
- Error codes: `CALC_MISSING_DATA` for missing inputs

**Frontend Pattern (MUST follow):**
- Components in `components/evaluation/scoring/` — feature-organized
- Hook uses `apiClient.ts` (openapi-fetch) — never raw `fetch()`
- TanStack Query for data fetching — throw errors in queryFn
- Error states have visible UI (error message, retry button) — no swallowed errors
- Use shadcn/ui components (Card, Table, Badge, Button, Select, Collapsible)
- camelCase for variables, PascalCase for components

**Calculator Architecture:**
```
Frontend (trigger via button)
    ↓ POST /score with verdict
Backend service loads manual_data + calculator_results from DB
    ↓ passes to pure function
calculators/scoring.py (no I/O)
    ↓ returns ScoringResult
Backend returns response to frontend
```

### Library & Framework Requirements

| Library | Version | Usage in This Story | Status |
|---------|---------|---------------------|--------|
| @tanstack/react-query | existing | Data fetching, cache management | Installed |
| openapi-fetch | existing | Typed API client | Installed |
| shadcn/ui (Card, Table, Badge, Button, Select, Collapsible) | existing | UI components | Installed |
| lucide-react | existing | Icons (CheckCircle, XCircle, AlertTriangle, Copy, ExternalLink) | Installed |
| tailwindcss v4 | existing | Styling | Installed |
| asyncpg | existing | Database queries | Installed |
| pydantic | existing | Request/response schemas | Installed |

**No new dependencies needed.** All required libraries are already installed.

### Testing Requirements

**Backend Unit Tests (pytest) — `tests/unit/calculators/test_scoring.py`:**
- Test each `_score_{category}()` function independently with known inputs
- Test Fashion vs Non-Fashion threshold differences for ROI, marketing
- Test negative score scenarios: operational penalties (H7 value=5% → score=-5), stock <12 → -5
- Test promo tool verdict logic: zero value, >50% dependency, meets benchmark, below benchmark
- Test G-column message generation: check Indonesian text patterns, number formatting
- Test G68 marketing estimation: parse discount text, combine with ad cost %
- Test G72 marketing percentage: complex MIN/MAX with Fashion adjustment
- Test G73 marketing budget text: verdict-dependent suppression
- Test G75 closing messages for each verdict type
- Test email body assembly: all sections present in correct order
- Test edge cases: all zeros, missing calculator data, extreme values (100% rates)

**Backend Integration Tests (pytest) — `tests/integration/api/test_scoring.py`:**
- Test POST /score with full data returns complete ScoringResult
- Test POST /score with missing calculator results returns partial scores
- Test auth required
- Test invalid brand_id returns 400

**Frontend Component Tests (vitest):**
- `ScoreBreakdown.test.tsx`: renders per-category scores, color coding for negative
- `FinalScoreDisplay.test.tsx`: renders score number and verdict icon
- `EmailOutput.test.tsx`: renders email body, copy button works
- `ScoringSection.test.tsx`: Generate button, loading state, results display
- `VerdictSelector.test.tsx`: all verdict options, change callback
- `ScorePanel.test.tsx`: displays score summary, stale indicator

Run commands:
- Backend: `cd backend && uv run python -m pytest -v`
- Frontend: `cd frontend && npx vitest run --reporter=verbose`

### Previous Story Intelligence

**From Story 3.8 (Calculator Results Display):**
- `useCalculatorResults(brandId)` hook exists — returns cached results with queryKey `['calculatorResults', brandId]`
- Cache invalidation wired: upload/run-all → invalidates calculator results and status
- `CalculatorResultsSection` component renders per-calculator display cards
- `formatIDR()` utility available in `formConfig.ts`
- 14 frontend tests + 30 backend tests passing (baseline to maintain)

**From Story 3.7 (Calculator Orchestration):**
- `engine.py` has dependency maps: `CALCULATOR_REQUIRED_FILES`, `FILE_TO_CALCULATORS`
- `calculator_service.py` has individual calculator runners that load data from DB and call pure functions
- Pattern to follow: service loads DB data → calls pure calculator → stores result

**From Story 3.3 (Manual Data Input Form):**
- `ManualData` type defined in `formConfig.ts` with all category interfaces
- `useAutoSaveForm` hook manages manual data with auto-save on blur
- `useEvaluationState(brandId)` returns `{category_type, manual_data, updated_at}`
- `EMPTY_MANUAL_DATA` provides defaults for all fields

**From Code Reviews (all stories):**
- Response schemas MUST match ACs field-by-field
- Frontend hooks MUST use `apiClient.ts` — never raw `fetch()`
- Error states MUST have visible UI
- File List MUST include ALL changed files
- React keys: use stable identifiers, not array indices

### Git Intelligence

Recent commits (Story 3.8 merged to develop):
```
264be4c Merge feature/3-8-calculator-results-display into develop
16f6d8b Fix 6 code review issues for Story 3.8 (3M/3L)
34d0858 Mark Story 3.8 complete — all tasks done, status → review
```

**Patterns to follow:**
- Feature branch naming: `feature/3-9-final-scoring-with-template-selection`
- Atomic commits per task
- Tests committed alongside implementation

### How This Feeds into Story 3.10 (Save Evaluation)

Story 3.10 saves completed evaluations permanently. It will snapshot:
- All manual inputs (from `evaluation_inputs` table)
- All calculator outputs (from `calculator_results` table)
- **Final score, per-category breakdown, verdict** (from this story's scoring result)
- **Email output text** (from this story's G1 assembly)
- Template used (Fashion/Non-Fashion)
- Evaluator and timestamp

The scoring result from this story does NOT need its own persistence table — Story 3.10 will snapshot it into the `evaluations` table.

### References

- [Source: logic/scoring-system-template-sicu.md — AUTHORITATIVE scoring spec, all formulas, thresholds, G-column text]
- [Source: _bmad-output/planning-artifacts/epics.md#Story-3.9 — Story ACs, FR17/FR19-FR22]
- [Source: _bmad-output/planning-artifacts/architecture.md — Calculator pure function pattern, module structure, naming]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md — Score Panel anatomy, component strategy]
- [Source: _bmad-output/planning-artifacts/prd.md — FR17: Combine results, FR19-FR22: Final scoring]
- [Source: _bmad-output/implementation-artifacts/3-8-calculator-results-display.md — Previous story, hooks, data structures]
- [Source: backend/app/modules/evaluations/router.py — Existing endpoints to extend]
- [Source: backend/app/modules/evaluations/schemas.py — Existing schemas (CategoryType, CalculatorResultResponse)]
- [Source: backend/app/modules/evaluations/service.py — Existing service pattern]
- [Source: backend/app/db/queries/evaluations.py — get_evaluation_inputs, get_any_evaluation_inputs]
- [Source: backend/app/db/queries/calculator_results.py — get_results_by_brand]
- [Source: backend/app/calculators/engine.py — Orchestration pattern, dependency maps]
- [Source: frontend/src/hooks/useCalculator.ts — useCalculatorResults, cache invalidation patterns]
- [Source: frontend/src/hooks/useEvaluation.ts — useEvaluationState, useSaveEvaluationInputs]
- [Source: frontend/src/hooks/useAutoSaveForm.ts — ManualData management]
- [Source: frontend/src/components/evaluation/forms/formConfig.ts — ManualData type, formatIDR, field definitions]
- [Source: frontend/src/pages/EvaluationPage.tsx — Score Panel placeholder (lines 105-157)]
- [Source: frontend/src/components/evaluation/EvaluationSections.tsx — Section structure to extend]
- [Source: frontend/src/components/evaluation/SectionNav.tsx — Navigation to extend]
- [Source: _bmad-output/lessons-learned.md — Code review patterns, testing patterns]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6 (claude-opus-4-6)

### Debug Log References

None — no HALT conditions triggered.

### Completion Notes List

- Tasks 1 & 2 combined into single commit since scoring functions and G-column messages are tightly coupled in the same file
- Values stored as percentage numbers (0.5 = 0.5%, not fractions 0.005 = 0.5%) — consistent with how ManualData stores values with `unit: '%'`
- Scoring formulas adjusted accordingly (e.g., operational H7 uses `if value <= 1.0` instead of `if value <= 0.01`)
- Backend: 466 tests pass (92 scoring unit + 8 scoring integration + 366 existing)
- Frontend: 209 tests pass (37 new scoring + 172 existing). 2 pre-existing Firebase config failures in App.test.tsx and EvaluationForms.test.tsx (not related to this story)
- SectionNav updated from 5 to 6 sections; existing tests updated accordingly
- EvaluationPage test updated to mock useScoring hook and verify 6 nav items
- ScorePanel shows live per-category scores in sidebar; ScoringSection is the main scoring UI
- **Code review fixes (commit 8):** Fixed critical ScorePanel category name mismatch (Indonesian→English mapping), added N/A marking for missing calculator data (available field), verdict validation (Literal type), expanded tests

### Change Log

| Commit | Description |
|--------|-------------|
| 1 | Create scoring calculator pure function with G-column messages (Tasks 1-2) |
| 2 | Add backend scoring endpoint with schemas and service (Task 3) |
| 3 | Add 75 unit tests for scoring calculator (Task 4) |
| 4 | Add 5 integration tests for scoring endpoint (Task 5) |
| 5 | Create frontend scoring display components and hook (Tasks 6-7 partial) |
| 6 | Integrate scoring components into EvaluationPage (Tasks 6-8) |
| 7 | Add frontend component tests for scoring (Task 9) |
| 8 | Fix code review findings: ScorePanel category mapping, N/A marking, verdict validation, expanded tests |

### File List

**New files created:**
- `backend/app/calculators/scoring.py` — Main scoring calculator pure function (~1400 lines)
- `backend/tests/unit/calculators/test_scoring.py` — 84 unit tests
- `backend/tests/integration/api/test_scoring.py` — 8 integration tests
- `frontend/src/hooks/useScoring.ts` — Scoring mutation hook with stale detection
- `frontend/src/components/evaluation/scoring/ScoreBreakdown.tsx` — Per-category score table
- `frontend/src/components/evaluation/scoring/FinalScoreDisplay.tsx` — Score + verdict display
- `frontend/src/components/evaluation/scoring/EmailOutput.tsx` — Copyable email body
- `frontend/src/components/evaluation/scoring/WhatsAppLink.tsx` — WhatsApp link button
- `frontend/src/components/evaluation/scoring/VerdictSelector.tsx` — Verdict dropdown
- `frontend/src/components/evaluation/scoring/ScoringSection.tsx` — Scoring orchestrator UI
- `frontend/src/components/evaluation/scoring/ScorePanel.tsx` — Right sidebar score summary
- `frontend/src/components/evaluation/scoring/index.ts` — Barrel re-exports
- `frontend/src/components/evaluation/scoring/ScoringSection.test.tsx` — 9 tests
- `frontend/src/components/evaluation/scoring/FinalScoreDisplay.test.tsx` — 7 tests
- `frontend/src/components/evaluation/scoring/ScoreBreakdown.test.tsx` — 6 tests
- `frontend/src/components/evaluation/scoring/EmailOutput.test.tsx` — 4 tests
- `frontend/src/components/evaluation/scoring/ScorePanel.test.tsx` — 5 tests
- `frontend/src/components/evaluation/scoring/VerdictSelector.test.tsx` — 6 tests

**Modified files:**
- `backend/app/modules/evaluations/schemas.py` — Added ScoringRequest, ScoringResponse, RowScoreItem, CategoryScoreItem
- `backend/app/modules/evaluations/service.py` — Added generate_score() service function
- `backend/app/modules/evaluations/router.py` — Added POST /score endpoint
- `frontend/src/services/apiClient.ts` — Added scoring path type
- `frontend/src/pages/EvaluationPage.tsx` — Replaced Score Panel placeholder with ScorePanel, wired useScoring
- `frontend/src/components/evaluation/EvaluationSections.tsx` — Replaced Final Score placeholder with ScoringSection
- `frontend/src/components/evaluation/SectionNav.tsx` — Added "Final Score" (Step 6) nav entry
- `frontend/src/pages/EvaluationPage.test.tsx` — Updated for 6 sections, mock useScoring
- `frontend/src/components/evaluation/SectionNav.test.tsx` — Updated for 6 sections
