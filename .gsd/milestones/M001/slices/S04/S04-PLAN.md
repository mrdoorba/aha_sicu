# S04: Frontend Currency and Marketplace UI

**Goal:** Every currency display and form input in the frontend is marketplace-aware, the Rules page has ID/TH tabs, and the evaluation flow sends marketplace to the backend.
**Demo:** Rules page shows marketplace tabs (ID 🇮🇩 / TH 🇹🇭) — switching tabs loads different thresholds. Evaluation page has a marketplace selector — selecting TH changes all currency labels from (IDR) to (THB). Saving an evaluation sends marketplace to the backend.

## Must-Haves

- `formatCurrency(value, marketplace)` and `parseCurrency(formatted, marketplace)` replace all hardcoded `formatIDR`/`parseIDR` usage in production code
- `CurrencyField` accepts a `currency` prop that drives the label and formatting
- Rules page has marketplace tabs using shadcn `Tabs` component; `useRules` and `useUpdateRule` hooks accept and pass `marketplace` parameter
- Evaluation flow sends `marketplace` in PUT (evaluation_inputs) and POST (save evaluation) requests
- `useEvaluationOrchestrator` exposes `marketplace` / `setMarketplace` state
- All display components (`TopSkuResults`, `DataIntelligence`, `EvaluationDetailPage`, `BusinessForm`) use marketplace-aware formatting
- `grep -rn "IDR\|formatIDR" frontend/src --include="*.tsx" --include="*.ts" | grep -v test | grep -v node_modules` returns zero hits in production code (except deprecated re-exports in `formConfig.ts` and `formUtils.ts`)

## Proof Level

- This slice proves: integration (frontend → backend API contract for marketplace)
- Real runtime required: no (vitest + jsdom sufficient for all assertions)
- Human/UAT required: no (visual verification is optional; test coverage is the acceptance gate)

## Verification

- `cd frontend && npx vitest run --reporter=verbose` — all existing tests pass (no regressions)
- `CurrencyField.test.tsx` — existing 7 tests pass + new THB variant test passes
- `RulesPage.test.tsx` — existing tests pass + new marketplace tab switching test passes
- `formUtils.test.ts` — new test file: `formatCurrency` and `parseCurrency` produce correct output for both ID and TH marketplaces, and handle edge cases (null, NaN, empty string)
- Grep audit: `grep -rn "IDR\|formatIDR" frontend/src --include="*.tsx" --include="*.ts" | grep -v test | grep -v node_modules | grep -v "deprecated"` returns zero hits (or only the backward-compat re-export lines)
- **Failure-path check**: `CurrencyField` with an unknown currency value (e.g. `currency="XX"`) falls back gracefully to showing the raw currency code `(XX)` and uses default number formatting without crashing — verified by a test case

## Observability / Diagnostics

- Runtime signals: React Query cache keys include marketplace dimension (`['rules', marketplace]`) — stale data from wrong marketplace is detectable by inspecting React Query devtools cache entries
- Inspection surfaces: `useEvaluationOrchestrator` exposes `marketplace` in its return value — inspectable via React DevTools component props on the evaluation page; marketplace param visible in network requests (Rules GET `?marketplace=TH`, evaluation PUT body `{ marketplace: "TH" }`)
- Failure visibility: If marketplace is not sent in evaluation save, the backend defaults to `"ID"` — a TH evaluation scored with ID rules produces incorrect results. Detectable by inspecting the POST `/save` request body in network tab for presence of `marketplace` field. `useAutoSaveForm` save error state (`saveStatus: 'error'`) surfaces API failures.
- Redaction constraints: none

## Integration Closure

- Upstream surfaces consumed: Backend API endpoints (`GET /api/v1/rules?marketplace=TH`, `PUT /api/v1/rules/{template}?marketplace=TH`, `PUT /api/v1/evaluations/brands/{id}` with `marketplace` body field, `POST /api/v1/evaluations/brands/{id}/save` with `marketplace` body field) — all verified ready by S01-S03
- New wiring introduced in this slice: `marketplace` state in `useEvaluationOrchestrator` → threaded to `useAutoSaveForm` → `useSaveEvaluationInputs` PUT body; `marketplace` in `useSaveEvaluation` POST body; `marketplace` query param in `useRules`/`useUpdateRule`
- What remains before the milestone is truly usable end-to-end: nothing — S04 is the final slice in M001

## Tasks

- [x] **T01: Add shared currency utilities and extend CurrencyField** `est:30m`
  - Why: Every downstream task needs `formatCurrency`/`parseCurrency` and a currency-aware `CurrencyField`. This is the foundation layer.
  - Files: `frontend/src/components/evaluation/forms/formUtils.ts`, `frontend/src/components/evaluation/forms/formConfig.ts`, `frontend/src/components/evaluation/forms/CurrencyField.tsx`, `frontend/src/components/evaluation/forms/CurrencyField.test.tsx`, `frontend/src/components/evaluation/forms/formUtils.test.ts`
  - Do: (1) Add `formatCurrency(value, marketplace)` and `parseCurrency(formatted, marketplace)` to `formUtils.ts` — both delegate to the same `Intl.NumberFormat` logic; marketplace only determines the currency code label. (2) Keep `formatIDR`/`parseIDR` as deprecated re-exports. (3) Add `currency?: 'IDR' | 'THB'` prop to `CurrencyField` (default `'IDR'`) — change hardcoded `(IDR)` label to dynamic `({currency})`, replace `formatIDR`/`parseIDR` with `formatCurrency`/`parseCurrency`. (4) Add `currency` to barrel exports in `formConfig.ts`. (5) Create `formUtils.test.ts` with tests for both formatters. (6) Add THB variant test to `CurrencyField.test.tsx` + unknown currency fallback test.
  - Verify: `cd frontend && npx vitest run src/components/evaluation/forms/ --reporter=verbose`
  - Done when: All CurrencyField tests pass including THB variant, formUtils tests pass for both marketplaces, and `CurrencyField` renders `(THB)` when `currency="THB"` is passed.

- [x] **T02: Add marketplace tabs to Rules page** `est:45m`
  - Why: Admins need to view and edit THB thresholds independently from IDR. Covers requirements RULES-01 and RULES-02.
  - Files: `frontend/src/services/apiClient.ts`, `frontend/src/hooks/useRules.ts`, `frontend/src/hooks/useUpdateRule.ts`, `frontend/src/pages/RulesPage.tsx`, `frontend/src/components/rules/RulesPage.test.tsx`
  - Do: (1) Update `apiClient.ts` — add `query?: { marketplace?: string }` to `GET /api/v1/rules` and `PUT /api/v1/rules/{template}`. (2) Add `marketplace` param to `useRules` hook — include in queryKey `['rules', marketplace]` and pass as query param. (3) Add `marketplace` param to `useUpdateRule` — append `?marketplace=TH` to PUT URL when marketplace is not 'ID'. (4) Add marketplace tab state to `RulesPage` using existing shadcn `Tabs`/`TabsList`/`TabsTrigger` — tabs labeled "🇮🇩 Indonesia (IDR)" and "🇹🇭 Thailand (THB)", default to "ID". Pass marketplace to `useRules` and `useUpdateRule`. (5) Add marketplace tab test to `RulesPage.test.tsx`.
  - Verify: `cd frontend && npx vitest run src/components/rules/RulesPage.test.tsx --reporter=verbose`
  - Done when: Rules page renders marketplace tabs, switching tabs triggers re-fetch with correct marketplace param in queryKey, updateRule sends marketplace query param, and test for tab switching passes.

- [ ] **T03: Wire marketplace through evaluation flow hooks and UI** `est:45m`
  - Why: The evaluation flow must send marketplace to the backend so evaluations are scored with the correct rules. Covers requirements EVAL-01 and DATA-01.
  - Files: `frontend/src/services/apiClient.ts`, `frontend/src/hooks/useEvaluation.ts`, `frontend/src/hooks/useAutoSaveForm.ts`, `frontend/src/hooks/useSaveEvaluation.ts`, `frontend/src/hooks/useEvaluationOrchestrator.ts`, `frontend/src/components/evaluation/EvaluationSections.tsx`, `frontend/src/components/evaluation/EvaluationHeader.tsx`
  - Do: (1) Update `apiClient.ts` — add `marketplace?: string` to PUT `/evaluations/brands/{brand_id}` request body and add `marketplace?: string` + `period?: string` to POST `/evaluations/brands/{brand_id}/save` request body. (2) Add `marketplace?: string` to `EvaluationInputsUpdate` in `useEvaluation.ts`. (3) Add `marketplace` param to `useAutoSaveForm` — accept it in options, include in `doSave` mutation body. (4) Add `marketplace?: string` to `SaveEvaluationRequest` in `useSaveEvaluation.ts`. (5) Add `marketplace` state (`useState<string>('ID')`) to `useEvaluationOrchestrator` — pass to `useAutoSaveForm`, pass to `useRules` (so scoring uses correct rules), include in `saveEvaluation` call, expose as `marketplace`/`setMarketplace` in return. (6) Add marketplace selector UI to `EvaluationSections` — a simple select/radio above the fashion/non-fashion selector showing "🇮🇩 Indonesia" / "🇹🇭 Thailand". (7) Thread `marketplace` through `EvaluationSections` props to all consumer form components (pass `currency` prop derived from marketplace to `BusinessForm`, `CompetitionForm`, `PromoToolsForm` via their `CurrencyField` instances). (8) Add marketplace badge to `EvaluationHeader` showing the flag and marketplace code.
  - Verify: `cd frontend && npx vitest run --reporter=verbose` (full suite — no regressions)
  - Done when: `useEvaluationOrchestrator` exposes `marketplace`/`setMarketplace`, auto-save includes marketplace in PUT body, save evaluation includes marketplace in POST body, and the evaluation page shows a marketplace selector that changes currency labels.

- [ ] **T04: Update display components and run final IDR audit** `est:30m`
  - Why: Several display components have their own local `formatIDR` functions or hardcoded `IDR` strings. These must all use marketplace-aware formatting to complete the slice.
  - Files: `frontend/src/components/evaluation/calculators/TopSkuResults.tsx`, `frontend/src/components/dashboard/DataIntelligence.tsx`, `frontend/src/pages/EvaluationDetailPage.tsx`, `frontend/src/components/evaluation/forms/BusinessForm.tsx`
  - Do: (1) `TopSkuResults.tsx` — import `formatCurrency` from `formConfig`, add `marketplace` prop (default `'ID'`), replace `IDR {formatIDR(...)}` with `{marketplace === 'TH' ? 'THB' : 'IDR'} {formatCurrency(row.total_omzet, marketplace)}`. Thread `marketplace` from parent (`CalculatorResultsSection` or `EvaluationSections`). (2) `DataIntelligence.tsx` — replace local `formatIDR` with imported `formatCurrency`, add `marketplace` prop, use it in all 3 format calls. (3) `EvaluationDetailPage.tsx` — replace local `formatIDR` with imported `formatCurrency`, detect marketplace from the evaluation data (the saved evaluation includes marketplace), use marketplace-aware formatting for all currency display cells. (4) `BusinessForm.tsx` — replace local `formatCurrencyDisplay` with imported `formatCurrency` for the computed average display. Add `currency` prop threaded from parent. (5) **Final audit**: run `grep -rn "IDR\|formatIDR" frontend/src --include="*.tsx" --include="*.ts" | grep -v test | grep -v node_modules` and fix any remaining hardcoded references. Acceptable survivors: deprecated re-exports in `formConfig.ts`/`formUtils.ts`, and the `unit: 'IDR'` values in `fields.ts` (render layer overrides these). (6) Run full test suite.
  - Verify: `cd frontend && npx vitest run --reporter=verbose` + grep audit returns only acceptable survivors
  - Done when: All local `formatIDR` copies are removed, all `IDR` string literals in production code are marketplace-aware, full test suite passes, and grep audit is clean.

## Files Likely Touched

- `frontend/src/components/evaluation/forms/formUtils.ts`
- `frontend/src/components/evaluation/forms/formUtils.test.ts`
- `frontend/src/components/evaluation/forms/formConfig.ts`
- `frontend/src/components/evaluation/forms/CurrencyField.tsx`
- `frontend/src/components/evaluation/forms/CurrencyField.test.tsx`
- `frontend/src/components/evaluation/forms/BusinessForm.tsx`
- `frontend/src/components/evaluation/forms/CompetitionForm.tsx`
- `frontend/src/components/evaluation/forms/PromoToolsForm.tsx`
- `frontend/src/services/apiClient.ts`
- `frontend/src/hooks/useRules.ts`
- `frontend/src/hooks/useUpdateRule.ts`
- `frontend/src/hooks/useEvaluation.ts`
- `frontend/src/hooks/useAutoSaveForm.ts`
- `frontend/src/hooks/useSaveEvaluation.ts`
- `frontend/src/hooks/useEvaluationOrchestrator.ts`
- `frontend/src/pages/RulesPage.tsx`
- `frontend/src/components/rules/RulesPage.test.tsx`
- `frontend/src/components/evaluation/EvaluationSections.tsx`
- `frontend/src/components/evaluation/EvaluationHeader.tsx`
- `frontend/src/components/evaluation/calculators/TopSkuResults.tsx`
- `frontend/src/components/dashboard/DataIntelligence.tsx`
- `frontend/src/pages/EvaluationDetailPage.tsx`
