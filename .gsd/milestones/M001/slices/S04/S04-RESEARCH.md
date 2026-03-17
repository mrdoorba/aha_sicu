# S04: Frontend Currency and Marketplace UI — Research

**Date:** 2026-03-17
**Depth:** Targeted — known technology (React, Radix Tabs, Intl.NumberFormat), moderate integration across ~10 frontend files with established patterns.

## Summary

The frontend currently hardcodes IDR currency in **5 independent locations** across forms, display components, and detail pages. The backend already fully supports marketplace — the rules API accepts a `?marketplace=TH` query param, the evaluation inputs PUT accepts `marketplace` in the body, and the save evaluation POST accepts `marketplace`. The frontend simply hasn't been wired to use any of this.

The work decomposes into three natural seams: (1) shared currency utilities and `CurrencyField` prop-threading, (2) Rules page marketplace tabs, and (3) evaluation flow marketplace selection + display. All three can be built incrementally and tested independently. The shadcn `Tabs` component already exists at `components/ui/tabs.tsx` and is used in `DataIntelligence.tsx`, so the Rules page tabs are a direct pattern reuse.

The riskiest part is not any single file change — it's **completeness**: ensuring every `IDR` reference and every `formatIDR` call is replaced across all consumer files without missing any. A `grep -rn "IDR\|formatIDR" frontend/src` audit must return zero non-test hits after this slice.

## Recommendation

Build bottom-up: shared utilities first, then components, then pages.

1. **Create `formatCurrency(value, marketplace)` and `parseCurrency(formatted, marketplace)` in `formUtils.ts`** — consolidate the 3 independent `formatIDR` implementations. Both IDR and THB use comma-thousands formatting (same logic), so the function body is nearly identical; only the label/symbol changes. Keep `formatIDR`/`parseIDR` as deprecated re-exports for any callers not yet updated.

2. **Add `currency` prop to `CurrencyField`** — drives the label `(IDR)` vs `(THB)` and delegates to `formatCurrency`/`parseCurrency`. Default to `'IDR'` for backward compatibility.

3. **Wire `useRules` to accept marketplace param** — the API already supports `?marketplace=TH`. The hook currently fetches without marketplace filter. Add marketplace state to RulesPage and pass it through.

4. **Wire `useAutoSaveForm` → `useSaveEvaluationInputs` to pass marketplace** — the PUT body already accepts `marketplace` field but the frontend never sends it. Add marketplace to the auto-save flow.

5. **Wire `useSaveEvaluation` to pass marketplace** — same pattern, the POST body accepts `marketplace` but frontend doesn't send it.

## Implementation Landscape

### Key Files

**Shared utilities (create/extend):**
- `frontend/src/components/evaluation/forms/formUtils.ts` — `formatIDR`/`parseIDR` live here. Add `formatCurrency(value, marketplace)` and `parseCurrency(formatted, marketplace)`. Both IDR and THB use `Intl.NumberFormat('en-US', {maximumFractionDigits: 0})` for the number part; the currency code/symbol is separate. Keep `formatIDR`/`parseIDR` re-exports for backward compat.
- `frontend/src/components/evaluation/forms/formConfig.ts` — barrel re-export, add new exports.

**CurrencyField (extend):**
- `frontend/src/components/evaluation/forms/CurrencyField.tsx` — Add `currency?: 'IDR' | 'THB'` prop (default `'IDR'`). Change `(IDR)` label to `({currency})`. Replace `formatIDR`/`parseIDR` with `formatCurrency`/`parseCurrency`.
- `frontend/src/components/evaluation/forms/CurrencyField.test.tsx` — Add THB variant test.

**Files consuming CurrencyField or formatIDR (thread currency prop):**
- `frontend/src/components/evaluation/forms/BusinessForm.tsx` — uses `CurrencyField` + local `formatCurrencyDisplay` with hardcoded `'IDR'`. Needs `currency` prop from parent.
- `frontend/src/components/evaluation/forms/CompetitionForm.tsx` — uses `CurrencyField`. Needs `currency` prop.
- `frontend/src/components/evaluation/forms/PromoToolsForm.tsx` — uses `CurrencyField`. Needs `currency` prop.
- `frontend/src/components/evaluation/calculators/TopSkuResults.tsx` — hardcodes `IDR {formatIDR(...)}` in table cells. Needs `currency` prop.
- `frontend/src/pages/EvaluationDetailPage.tsx` — has its own local `formatIDR` function. Needs `marketplace`-aware formatting.
- `frontend/src/components/dashboard/DataIntelligence.tsx` — has its own local `formatIDR` function. Needs `marketplace`-aware formatting.

**Rules page (marketplace tabs):**
- `frontend/src/pages/RulesPage.tsx` — Currently selects `rules.find(r => r.template === 'default')`. Must add a marketplace tab switcher (ID | TH) using existing `Tabs` from `components/ui/tabs.tsx`. The `useRules` hook needs a `marketplace` param.
- `frontend/src/hooks/useRules.ts` — Add `marketplace` param to the query. API already supports `GET /api/v1/rules?marketplace=TH`. Include marketplace in the queryKey for correct caching.
- `frontend/src/hooks/useUpdateRule.ts` — Add `marketplace` param to the PUT call. API already supports `PUT /api/v1/rules/{template}?marketplace=TH`. The `UpdateRuleParams` interface needs a `marketplace` field.
- `frontend/src/components/rules/RulesPage.test.tsx` — Add marketplace tab tests.

**Evaluation flow (marketplace selection + save):**
- `frontend/src/hooks/useEvaluation.ts` — `EvaluationInputsUpdate` interface needs `marketplace` field. `useSaveEvaluationInputs` should pass it to the PUT body.
- `frontend/src/hooks/useAutoSaveForm.ts` — Must accept `marketplace` and include it in save calls.
- `frontend/src/hooks/useEvaluationOrchestrator.ts` — Must manage marketplace state. Source: could come from a UI selector or could default from evaluation_inputs.
- `frontend/src/hooks/useSaveEvaluation.ts` — `SaveEvaluationRequest` needs `marketplace` field. API already accepts it.
- `frontend/src/hooks/useScoring.ts` — `ScoringRequest` does NOT need marketplace because `generate_score()` reads it from evaluation_inputs (backend handles this). But the scoring request body in apiClient.ts may need updating.
- `frontend/src/components/evaluation/EvaluationHeader.tsx` — Display marketplace badge (ID 🇮🇩 or TH 🇹🇭).
- `frontend/src/components/evaluation/EvaluationSections.tsx` — Thread `currency` prop to forms.

**API client types (extend):**
- `frontend/src/services/apiClient.ts` — Add `marketplace` field to:
  - `GET /api/v1/rules` query params
  - `PUT /api/v1/rules/{template}` query params
  - `PUT /api/v1/evaluations/brands/{brand_id}` request body
  - `POST /api/v1/evaluations/brands/{brand_id}/save` request body (add `marketplace` and `period` fields)
  - Response types where backend now includes `marketplace` (rules response)

### Build Order

**Phase A: Shared utilities + CurrencyField** (no dependencies, unblocks everything)
1. Add `formatCurrency(value, marketplace)` and `parseCurrency(formatted, marketplace)` to `formUtils.ts`
2. Extend `CurrencyField` with `currency` prop
3. Update tests for CurrencyField

**Phase B: Rules page marketplace tabs** (depends on Phase A only for shared types)
1. Update `apiClient.ts` rules types to include marketplace query param
2. Add `marketplace` param to `useRules` and `useUpdateRule` hooks
3. Add marketplace tab state + Tabs UI to `RulesPage.tsx`
4. Update `RulesPage.test.tsx`

**Phase C: Evaluation flow marketplace selection** (depends on Phase A for currency prop)
1. Update `apiClient.ts` evaluation types to include marketplace in request bodies
2. Add marketplace to `useEvaluation.ts` (EvaluationInputsUpdate), `useAutoSaveForm`, `useSaveEvaluation`
3. Add marketplace state management to `useEvaluationOrchestrator` — expose as `marketplace` + `setMarketplace`
4. Add marketplace selector to EvaluationPage UI (above section nav)
5. Thread `currency` prop through `EvaluationSections` → form components
6. Update `TopSkuResults`, `DataIntelligence`, `EvaluationDetailPage` with marketplace-aware formatting
7. Add marketplace badge to `EvaluationHeader`

### Verification Approach

**Automated tests (vitest):**
```bash
cd frontend && npx vitest run --reporter=verbose
```
- `CurrencyField.test.tsx` — existing 7 tests must pass + new THB test
- `RulesPage.test.tsx` — existing 17+ tests must pass + new marketplace tab tests
- All existing form tests (BusinessForm, CompetitionForm, PromoToolsForm) must pass unchanged (backward compat)

**Manual grep audit:**
```bash
grep -rn "IDR\|formatIDR" frontend/src --include="*.tsx" --include="*.ts" | grep -v test | grep -v node_modules
```
Should return zero hits in non-test production code after completion (excluding the backward-compat re-export in `formConfig.ts`).

**Visual verification (optional):**
- Navigate to Rules page → see ID/TH tabs → switch tabs → see different thresholds
- Navigate to Evaluation page → see marketplace selector → select TH → currency fields show (THB) label

## Constraints

- **Backend API is ready** — `GET /api/v1/rules?marketplace=TH`, `PUT /api/v1/rules/{template}?marketplace=TH`, `PUT /evaluations/brands/{id}` with `marketplace` body field, `POST /evaluations/brands/{id}/save` with `marketplace` body field all work. No backend changes needed for S04.
- **`apiClient.ts` uses hand-written types** — no openapi-typescript generation. Types must be manually updated to match backend schema additions. This is the existing pattern; follow it.
- **`formatIDR`/`parseIDR` are public exports from `formConfig.ts`** — can't remove without checking all consumers. Keep as deprecated re-exports initially.
- **Test framework is vitest with jsdom** — `Intl.NumberFormat` is available in Node.js/jsdom. No polyfill needed.
- **Scoring request does NOT need marketplace** — `generate_score()` on the backend reads marketplace from `evaluation_inputs`, not from the scoring request body. The frontend just needs to ensure marketplace was saved to evaluation_inputs before scoring.
- **The `fields.ts` file has `unit: 'IDR'` on ~16 field definitions** — these drive the FieldDefinition metadata. They need updating to be marketplace-aware or the unit should reflect the dynamic currency. Since fields are static config, the simplest approach is to change `unit: 'IDR'` to `unit: 'currency'` and have the rendering layer resolve the actual label.

## Common Pitfalls

- **Missing `marketplace` in `queryKey` for `useRules`** — If marketplace is added to the fetch but not the queryKey, switching tabs shows stale data from the React Query cache. The queryKey must include marketplace: `['rules', marketplace]`.
- **`useUpdateRule` not passing marketplace to PUT** — The current hook PUTs to `/api/v1/rules/{template}` without a marketplace query param. Without adding `?marketplace=TH`, saving THB rules overwrites IDR rules. The API reads marketplace from the query string, not the body.
- **`useAutoSaveForm` doesn't include marketplace in save** — The auto-save mutation calls `saveMutation.mutate({ category_type, manual_data })` — no marketplace field. If marketplace isn't included, the backend defaults to `"ID"`. This means a TH evaluation would be scored with ID rules.
- **Three local `formatIDR` copies** — `formUtils.ts`, `DataIntelligence.tsx`, and `EvaluationDetailPage.tsx` each have independent `formatIDR` implementations. All three must be replaced, not just the shared one.
- **`TopSkuResults.tsx` hardcodes `IDR` string** — Line 145-146: `IDR {formatIDR(row.total_omzet)}`. This is a string literal, not a function call — easy to miss in a `formatIDR` search.

## Open Risks

- **Marketplace selector UX decision**: The research context says "derive marketplace from brand record" to avoid user error. But the backend currently stores marketplace on `evaluation_inputs`, not `brand_vp_data`. The brand detail response (`BrandDetailResponse`) does NOT include a marketplace field. Decision needed: either add a marketplace selector to the evaluation page (user picks), or add marketplace to the brand API response (auto-derive). Given that the backend schema has marketplace on evaluation_inputs and the evaluation save endpoint accepts it, a **user-selectable marketplace per evaluation** is the correct approach matching the current backend design.
- **`fields.ts` `unit: 'IDR'` on 16+ fields**: These are used by `benchmarkUtils.ts` and form rendering. Changing them affects benchmark display. The safest approach is to not change `fields.ts` and instead have the rendering layer (CurrencyField, BusinessForm) override the unit based on marketplace context. The `unit` field in FieldDefinition is used only for display, not logic.

## Sources

- Direct codebase inspection: all findings from reading the files listed in Key Files section
- Backend API contract: verified by reading `backend/app/modules/rules/router.py`, `backend/app/modules/evaluations/router.py`, `backend/app/modules/evaluations/schemas.py`
- Existing Tabs usage: `frontend/src/components/dashboard/DataIntelligence.tsx` imports from `../ui/tabs` — confirmed shadcn Tabs wrapper exists and works
- Intl.NumberFormat: Web standard, verified available in Node.js/jsdom test environment
