---
id: T03
parent: S04
milestone: M001
provides:
  - marketplace state management in useEvaluationOrchestrator (state, setter, currency derivation)
  - marketplace param sent in PUT evaluation_inputs body and POST save evaluation body
  - marketplace radio selector UI on evaluation page (ID / TH)
  - currency prop threading from orchestrator → EvaluationSections → BusinessForm/PromoToolsForm/CompetitionForm → CurrencyField
  - marketplace badge in EvaluationHeader
key_files:
  - frontend/src/services/apiClient.ts
  - frontend/src/hooks/useEvaluation.ts
  - frontend/src/hooks/useAutoSaveForm.ts
  - frontend/src/hooks/useSaveEvaluation.ts
  - frontend/src/hooks/useEvaluationOrchestrator.ts
  - frontend/src/components/evaluation/EvaluationSections.tsx
  - frontend/src/components/evaluation/EvaluationHeader.tsx
  - frontend/src/components/evaluation/forms/BusinessForm.tsx
  - frontend/src/components/evaluation/forms/PromoToolsForm.tsx
  - frontend/src/components/evaluation/forms/CompetitionForm.tsx
  - frontend/src/pages/EvaluationPage.tsx
key_decisions:
  - marketplace is user-selectable local state in orchestrator defaulting to 'ID', not derived from brand data
  - currency derivation is inline ternary (marketplace === 'TH' ? 'THB' : 'IDR') in orchestrator rather than using getCurrencyCode — keeps it simple and avoids import for a two-case mapping
patterns_established:
  - marketplace state flows orchestrator → hooks (useAutoSaveForm, useRules, useSaveEvaluation) and UI (EvaluationSections, EvaluationHeader) — same top-down threading pattern used for categoryType
  - currency prop defaults to 'IDR' in all form components for backward compatibility
observability_surfaces:
  - marketplace field in PUT/POST request bodies visible in browser Network tab
  - useEvaluationOrchestrator exposes marketplace/currency in return value — inspectable via React DevTools
  - useRules(marketplace) uses query key ['rules', marketplace] — visible in React Query devtools
  - Marketplace badge in EvaluationHeader provides visual feedback
duration: 18 minutes
verification_result: passed
completed_at: 2026-03-17T08:47:00+07:00
blocker_discovered: false
---

# T03: Wire marketplace through evaluation flow hooks and UI

**Wired marketplace parameter through the entire evaluation flow — API types, auto-save, final save, rules fetching, and UI selector with currency threading to all CurrencyField instances.**

## What Happened

Implemented all 8 plan steps sequentially:

1. **apiClient.ts**: Added `marketplace?: string` to the PUT evaluation_inputs request body type and `marketplace?: string` + `period?: string` to the POST save evaluation request body type.

2. **useEvaluation.ts**: Added `marketplace?: string` to `EvaluationInputsUpdate` interface. The mutation function already passes the full body object, so no logic changes needed.

3. **useAutoSaveForm.ts**: Extended `UseAutoSaveFormOptions` with `marketplace?: string`, destructured it in the hook, and included it in the `doSave` mutation body alongside `category_type` and `manual_data`. Updated `doSave` dependency array.

4. **useSaveEvaluation.ts**: Added `marketplace?: string` to `SaveEvaluationRequest` interface. The mutation already spreads the request to body.

5. **useEvaluationOrchestrator.ts**: Added `useState<string>('ID')` for marketplace, derived `currency` via ternary, threaded marketplace to `useAutoSaveForm`, `useRules(marketplace)`, `handleSaveEvaluation` body, and `handleCategoryChange` body. Exposed `marketplace`, `setMarketplace`, and `currency` in return value.

6. **EvaluationSections.tsx**: Added `marketplace`, `currency`, `onMarketplaceChange` to `FormProps` interface. Rendered marketplace radio selector card (ID/TH) above the fashion/non-fashion selector. Threaded `currency` to `BusinessForm`, `PromoToolsForm`, and `CompetitionForm`.

7. **Form components**: Added `currency?: string` prop with `'IDR'` default to `BusinessFormProps`, `PromoToolsFormProps`, and `CompetitionFormProps`. Threaded to all `<CurrencyField currency={currency} />` instances.

8. **EvaluationHeader.tsx**: Added `marketplace?: string` to props, rendered `<Badge variant="outline">` with marketplace flag emoji after brand name.

9. **EvaluationPage.tsx**: Destructured `marketplace`, `setMarketplace`, `currency` from orchestrator and wired to `EvaluationHeader` and `EvaluationSections`.

## Verification

- **Full test suite**: `cd frontend && npx vitest run --reporter=verbose` — 63 test files, 536 tests passed, 0 failures
- **Grep check**: `grep -n "marketplace" frontend/src/hooks/useEvaluationOrchestrator.ts` — shows marketplace in state (L38), currency derivation (L39), useAutoSaveForm (L56), useRules (L88), saveEvaluation body (L185), handleCategoryChange (L216), and return value (L229)
- **Slice-level verification**: formUtils.test.ts passes (formatCurrency, parseCurrency, getCurrencyCode), CurrencyField.test.tsx passes (9 tests including THB and unknown currency), RulesPage.test.tsx passes (marketplace tab tests from T02)
- **IDR/formatIDR grep audit**: Remaining hits are backward-compat re-exports, static field definitions in fields.ts (T04 scope), display-only helpers, label text, and components outside S04 scope — all expected at T03 stage

## Diagnostics

- **Verify marketplace in auto-save**: Open evaluation page → switch to Thailand → edit any field → inspect PUT request body in Network tab → should contain `"marketplace": "TH"`
- **Verify marketplace in final save**: Click Save Evaluation → inspect POST `/save` body → should contain `"marketplace": "TH"`
- **Verify rules scoping**: Switch marketplace → inspect React Query devtools → `['rules', 'TH']` cache key should appear
- **Verify currency labels**: Switch to Thailand → all CurrencyField labels should show (THB) instead of (IDR)
- **Verify marketplace badge**: EvaluationHeader should show 🇹🇭 TH badge when Thailand selected

## Deviations

None — all 8 steps executed as planned.

## Known Issues

None.

## Files Created/Modified

- `frontend/src/services/apiClient.ts` — added `marketplace?: string` to evaluation PUT and POST body types
- `frontend/src/hooks/useEvaluation.ts` — added `marketplace?: string` to `EvaluationInputsUpdate`
- `frontend/src/hooks/useAutoSaveForm.ts` — accepts and sends `marketplace` in save body
- `frontend/src/hooks/useSaveEvaluation.ts` — added `marketplace?: string` to `SaveEvaluationRequest`
- `frontend/src/hooks/useEvaluationOrchestrator.ts` — manages marketplace state, derives currency, threads to all hooks, exposes in return
- `frontend/src/components/evaluation/EvaluationSections.tsx` — marketplace radio selector, currency threading to forms
- `frontend/src/components/evaluation/EvaluationHeader.tsx` — marketplace badge
- `frontend/src/components/evaluation/forms/BusinessForm.tsx` — accepts `currency` prop, threads to CurrencyField
- `frontend/src/components/evaluation/forms/PromoToolsForm.tsx` — accepts `currency` prop, threads to CurrencyField
- `frontend/src/components/evaluation/forms/CompetitionForm.tsx` — accepts `currency` prop, threads to CurrencyField
- `frontend/src/pages/EvaluationPage.tsx` — destructures and wires marketplace/currency from orchestrator
- `.gsd/milestones/M001/slices/S04/tasks/T03-PLAN.md` — added Observability Impact section
