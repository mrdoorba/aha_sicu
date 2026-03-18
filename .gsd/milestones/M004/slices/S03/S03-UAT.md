# S03: Verification sweep and test hardening — UAT

**Milestone:** M004
**Written:** 2026-03-18

## UAT Type

- UAT mode: mixed (artifact-driven verification commands + human-experience language switching)
- Why this mode is sufficient: The rg sweep, tsc, and test suite prove zero rendered Indonesian strings at the code level. Human language switching confirms the runtime experience matches — no stray Indonesian text visible when switching to EN or TH.

## Preconditions

- Frontend dev server running (`cd frontend && npm run dev`)
- At least one evaluation exists in the system (any brand, any period)
- User is logged in with an account that has access to at least one brand

## Smoke Test

Switch UI language to English via the language toggle in the header. Navigate to any evaluation page. All visible text should be in English — no Indonesian strings visible.

## Test Cases

### 1. Language switch — all pages render in Thai

1. Click the language toggle in the header and select **TH** (Thai)
2. Navigate to the Brands page
3. Navigate to an Evaluation page (click any brand → start/continue evaluation)
4. Check the sidebar section navigation labels (Brand Info, Operations, Business, etc.)
5. Check the form field labels in each section
6. Check benchmark descriptions below currency fields (e.g., ">8% จากยอดขาย" not ">8% dari penjualan")
7. Navigate to the History page
8. Open a completed evaluation's dashboard
9. Check the evaluation header field labels (PIC name, Date, Period)
10. **Expected:** Every visible string on every page renders in Thai. Zero Indonesian strings visible.

### 2. Language switch — all pages render in English

1. Click the language toggle and select **EN** (English)
2. Repeat the same navigation path as Test 1 (Brands → Evaluation → History → Dashboard)
3. Check sidebar navigation labels, form labels, benchmark descriptions, header labels
4. **Expected:** Every visible string renders in English. Zero Indonesian strings visible.

### 3. Access denied message in selected language

1. Switch to TH language
2. Log in with an account that has restricted brand access
3. Attempt to access a brand URL directly (modify URL to a brand ID the user doesn't have access to)
4. **Expected:** The access denied message renders in Thai, not "Akses ditolak"

### 4. Login page banner alt text

1. Switch to EN language
2. Log out and view the login page
3. Inspect the banner image alt text (right-click → Inspect, or hover)
4. **Expected:** Alt text is in English (the i18n key `login.bannerAlt` resolves to English text)

### 5. Evaluation dashboard metric comparisons (new evaluation)

1. Complete a new evaluation (post-M002, has metric_i18n data)
2. Navigate to the dashboard for this evaluation
3. Switch language to EN
4. Check the DetailedEvaluation metric table
5. **Expected:** Metric names render in English via metric_i18n keys

### 6. Evaluation dashboard metric comparisons (old evaluation)

1. Navigate to a dashboard for a pre-M002 evaluation (if any exist)
2. Switch language to EN
3. Check the DetailedEvaluation metric table
4. **Expected:** Metric names display in Indonesian (fallback to row.metric) — this is expected and correct for old data. The rest of the UI should still be in English.

### 7. Promo Tools form benchmarks in Thai

1. Switch to TH language
2. Navigate to an evaluation's Promo Tools section (Section 4)
3. Check benchmark text below each currency input field
4. **Expected:** Benchmark descriptions show Thai text (e.g., ">8% จากยอดขาย"), not Indonesian (">8% dari penjualan")

### 8. Operational form unit labels

1. Switch to EN language
2. Navigate to an evaluation's Operations section
3. Find the "Preparation Time" field
4. **Expected:** Unit label shows "days", not "hari"

## Edge Cases

### Old evaluation without metric_i18n

1. View a pre-M002 evaluation dashboard
2. Switch languages between ID, EN, TH
3. **Expected:** Category metric cards still render (fallback to Indonesian metric strings). No blank cards or errors. Non-metric UI text (headers, buttons, labels) switches correctly.

### Rapid language switching

1. Open an evaluation page
2. Rapidly click through ID → EN → TH → ID
3. **Expected:** All text updates reactively without page reload. Date formats change locale (id-ID → en-US → th-TH → id-ID). No stale text from previous language visible.

### Missing translation key (defensive)

1. If any key is missing from a locale file, react-i18next returns the key string itself (e.g., "fields.promoTools.promoToko")
2. **Expected:** Key strings are visible but not Indonesian text. This is a development-time signal, not a user-facing issue in production.

## Failure Signals

- Any Indonesian text visible when UI language is set to EN or TH (e.g., "dari penjualan", "Akses ditolak", "Garansi Omzet", "Nama PIC", "hari")
- Benchmark descriptions showing Indonesian when language is TH/EN
- Section navigation labels not translating when language changes
- Date formats not changing when language switches (e.g., still showing "id-ID" formatted dates in EN mode)
- Blank or missing text where a label should appear (indicates broken t() call)
- Console errors related to i18next (missing namespace, failed interpolation)

## Requirements Proved By This UAT

- R031 — Zero hardcoded Indonesian UI text: visual confirmation across all pages in EN/TH mode
- R032 — All frontend tests pass: test suite verification (612/612)
- R027 — History page i18n: History table renders in selected language
- R028 — No hardcoded id-ID locale: dates format per selected language
- R029 — Field labels i18n: evaluation form labels render in selected language
- R030 — INDO_MONTHS removed: month abbreviations show English (Jan-Dec) regardless of language

## Not Proven By This UAT

- Backend API responses (still return Indonesian category/metric names — this is by design, not in M004 scope)
- Email rendering in selected language (covered by M002 UAT, not re-tested here)
- Backend scoring engine i18n (out of scope — backend TranslatableText keys are generated correctly per M002)

## Notes for Tester

- **Inert Indonesian in source code is expected.** If you inspect source files, `fields.ts` still contains Indonesian in `label`, `benchmark`, and `displayName` properties. These are never rendered — they serve as code documentation and fallback text. The `labelKey`, `benchmarkKey`, and `displayNameKey` properties are what form components actually use.
- **Pre-M002 evaluation dashboards will show some Indonesian metric names.** This is correct — old evaluations lack `metric_i18n` data. The fallback to `row.metric` (Indonesian strings) is by design.
- **Backend column matchers** in files like `categoryMap.ts` and `DetailedEvaluation.tsx` match Indonesian strings from the API. These are not bugs — they map backend response values to i18n keys for display.
- **720 locale keys** should be in sync across all 3 JSON files. If any file has fewer, there's a missing extraction.
