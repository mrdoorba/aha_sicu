---
id: S04
parent: M001
milestone: M001
provides:
  - formatCurrency(value, marketplace) and parseCurrency(formatted, marketplace) centralized utilities
  - getCurrencyCode(marketplace) helper mapping TH→THB, ID→IDR with graceful unknown fallback
  - CurrencyField currency prop for marketplace-aware label rendering
  - Marketplace tabs (ID/TH) on RulesPage with marketplace-scoped React Query caching
  - useRules(marketplace) and useUpdateRule with marketplace query param
  - marketplace state in useEvaluationOrchestrator with currency derivation
  - marketplace field in PUT evaluation_inputs and POST save evaluation request bodies
  - Marketplace radio selector on evaluation page
  - Marketplace badge in EvaluationHeader
  - All display components use shared formatCurrency — zero local formatting copies remain
requires:
  - slice: S01
    provides: Backend marketplace column on scoring_rules/evaluation_inputs/evaluations tables, rules API with ?marketplace= param
  - slice: S02
    provides: Backend scoring engine selects rules by marketplace, message templates use {currency} placeholder
affects: []
key_files:
  - frontend/src/components/evaluation/forms/formUtils.ts
  - frontend/src/components/evaluation/forms/formUtils.test.ts
  - frontend/src/components/evaluation/forms/formConfig.ts
  - frontend/src/components/evaluation/forms/CurrencyField.tsx
  - frontend/src/components/evaluation/forms/CurrencyField.test.tsx
  - frontend/src/services/apiClient.ts
  - frontend/src/hooks/useRules.ts
  - frontend/src/hooks/useUpdateRule.ts
  - frontend/src/hooks/useEvaluation.ts
  - frontend/src/hooks/useAutoSaveForm.ts
  - frontend/src/hooks/useSaveEvaluation.ts
  - frontend/src/hooks/useEvaluationOrchestrator.ts
  - frontend/src/pages/RulesPage.tsx
  - frontend/src/components/rules/RulesPage.test.tsx
  - frontend/src/components/evaluation/EvaluationSections.tsx
  - frontend/src/components/evaluation/EvaluationHeader.tsx
  - frontend/src/components/evaluation/forms/BusinessForm.tsx
  - frontend/src/components/evaluation/forms/PromoToolsForm.tsx
  - frontend/src/components/evaluation/forms/CompetitionForm.tsx
  - frontend/src/pages/EvaluationPage.tsx
  - frontend/src/components/evaluation/calculators/TopSkuResults.tsx
  - frontend/src/components/evaluation/calculators/CalculatorResultsSection.tsx
  - frontend/src/components/dashboard/DataIntelligence.tsx
  - frontend/src/components/dashboard/PresentationDashboard.tsx
  - frontend/src/pages/EvaluationDetailPage.tsx
  - frontend/src/hooks/useEvaluationDetail.ts
key_decisions:
  - Currency formatting centralized in formUtils.ts (D016) — single formatCurrency replaces all local copies; formatIDR/parseIDR kept as deprecated re-exports
  - React Query queryKey includes marketplace dimension ['rules', marketplace] (D017) — prevents stale cross-marketplace cache
  - Marketplace is explicit user selection in orchestrator, not derived from brand data (D018)
  - getCurrencyCode returns uppercased unknown codes as-is — graceful fallback, no crash on bad data
  - Edit state resets on marketplace tab switch — prevents saving ID edits to TH rules
  - currency derivation in orchestrator uses inline ternary rather than getCurrencyCode — simpler for two-case mapping
patterns_established:
  - Currency formatting uses formatCurrency/parseCurrency with marketplace param — all downstream consumers import from formConfig barrel
  - CurrencyField accepts currency prop defaulting to 'IDR' — form components thread marketplace→getCurrencyCode→currency
  - Marketplace tab pattern uses shadcn Tabs with string state threaded to hooks as query param
  - marketplace state flows top-down from useEvaluationOrchestrator to hooks and UI — same pattern as categoryType
  - Display components accept marketplace prop with default 'ID' for backward compatibility
observability_surfaces:
  - React Query cache keys ['rules', marketplace] — inspect via React Query devtools for cross-marketplace isolation
  - marketplace field in PUT/POST request bodies — visible in browser Network tab
  - useEvaluationOrchestrator exposes marketplace/currency in return value — inspectable via React DevTools
  - All currency formatting funnels through formUtils.ts:formatCurrency — single breakpoint captures all formatting
  - Marketplace badge in EvaluationHeader provides visual feedback of active marketplace
  - grep audit command detects regressions: `grep -rn "formatIDR\|formatCurrencyDisplay" frontend/src --include="*.tsx" --include="*.ts" | grep -v test | grep -v deprecated`
drill_down_paths:
  - .gsd/milestones/M001/slices/S04/tasks/T01-SUMMARY.md
  - .gsd/milestones/M001/slices/S04/tasks/T02-SUMMARY.md
  - .gsd/milestones/M001/slices/S04/tasks/T03-SUMMARY.md
  - .gsd/milestones/M001/slices/S04/tasks/T04-SUMMARY.md
duration: ~70min across 4 tasks
verification_result: passed
completed_at: 2026-03-17
---

# S04: Frontend Currency and Marketplace UI

**Marketplace-aware currency formatting, Rules page marketplace tabs, evaluation flow marketplace wiring, and display component migration — completing the full-stack THB marketplace expansion.**

## What Happened

**T01 — Currency utilities foundation.** Added `formatCurrency(value, marketplace)`, `parseCurrency(formatted, marketplace)`, and `getCurrencyCode(marketplace)` to `formUtils.ts`. These replace all hardcoded `formatIDR`/`parseIDR` usage. The old functions are kept as deprecated one-liner re-exports for backward compatibility. Extended `CurrencyField` with a `currency` prop that renders dynamic `({currency})` labels instead of hardcoded `(IDR)`. Created `formUtils.test.ts` with 19 tests covering all utilities plus backward compatibility. Added THB variant and unknown currency fallback tests to `CurrencyField.test.tsx`.

**T02 — Rules page marketplace tabs.** Added `marketplace` query parameter support to apiClient types for rules GET and PUT. Updated `useRules` with marketplace-scoped queryKey `['rules', marketplace]` and `useUpdateRule` to send marketplace as a query param. Built marketplace tabs on `RulesPage` using shadcn Tabs — "🇮🇩 Indonesia (IDR)" and "🇹🇭 Thailand (THB)" — with a useEffect that cancels edit mode on tab switch to prevent cross-marketplace overwrites. Added 4 new tests verifying tab rendering, default state, switching, and edit cancellation.

**T03 — Evaluation flow wiring.** Added `marketplace` to apiClient PUT and POST body types. Threaded marketplace through the full hook chain: `useEvaluationOrchestrator` → `useAutoSaveForm` → `useSaveEvaluationInputs` PUT body, and `useSaveEvaluation` POST body. Added marketplace state (`useState<string>('ID')`) with currency derivation to the orchestrator. Built marketplace radio selector in `EvaluationSections` and marketplace badge in `EvaluationHeader`. Threaded `currency` prop to `BusinessForm`, `PromoToolsForm`, and `CompetitionForm` → all their `CurrencyField` instances.

**T04 — Display component migration and audit.** Replaced all local `formatIDR`/`formatCurrencyDisplay` functions in `TopSkuResults`, `DataIntelligence`, `EvaluationDetailPage`, and `BusinessForm` with shared `formatCurrency` from `formConfig`. Added `marketplace` prop threading through `CalculatorResultsSection → TopSkuResults`, `PresentationDashboard → DataIntelligence`, and evaluation data → `EvaluationDetailPage`. Added `marketplace?: string` to `EvaluationDetail` interface. Final grep audit confirmed zero local formatting copies remain — all IDR references are acceptable survivors (defaults, type annotations, field definitions, UI labels, deprecated re-exports).

## Verification

- **Full test suite**: `cd frontend && npx vitest run --reporter=verbose` — **63 test files, 536 tests passed, 1 skipped, 0 failures**
- **formUtils.test.ts**: 19/19 passed — formatCurrency (6), parseCurrency (6), getCurrencyCode (5), backward compat (2)
- **CurrencyField.test.tsx**: 9/9 passed — 7 existing + THB variant + unknown currency fallback
- **RulesPage.test.tsx**: 38/38 passed — 34 existing + 4 marketplace tab tests
- **formatCurrencyDisplay grep**: `grep -rn "formatCurrencyDisplay" frontend/src --include="*.tsx"` — zero hits
- **IDR audit**: `grep -rn "IDR\|formatIDR" frontend/src --include="*.tsx" --include="*.ts" | grep -v test | grep -v node_modules | grep -v deprecated` — all remaining hits are acceptable survivors: defaults (`currency = 'IDR'`), type annotations, `fields.ts` unit definitions, `getCurrencyCode` mapping logic, UI labels, and formConfig barrel re-exports
- **Failure-path**: CurrencyField with `currency="XX"` renders `(XX)` without crashing — verified by test

## Requirements Advanced

- SCORE-03 — Frontend now passes marketplace to useRules, ensuring scoring uses correct rule set. Full end-to-end validation requires live runtime test with a TH brand evaluation.

## Requirements Validated

- DATA-01 — Evaluation stores marketplace: backend schema (S01) + frontend sends marketplace in PUT/POST bodies (S04). 536 tests pass.
- RULES-01 — Rules page has marketplace tabs: RulesPage renders ID/TH tabs, tab switch triggers re-fetch. 4 dedicated tests pass.
- RULES-02 — Admin can edit THB thresholds independently: useUpdateRule sends marketplace query param. Edit state resets on tab switch. Backend PUT ready (S01).
- EVAL-01 — User can select marketplace: Radio selector on evaluation page, orchestrator exposes marketplace/setMarketplace. Marketplace sent in all save requests.
- EVAL-02 — Currency formatting shows code prefix: getCurrencyCode maps marketplace→code, CurrencyField renders dynamic label. 9 tests including THB and unknown fallback.
- EVAL-03 — Evaluation results display correct format: All local formatIDR removed, single shared formatCurrency used everywhere. 19 formUtils tests verify both marketplaces.

## New Requirements Surfaced

- none

## Requirements Invalidated or Re-scoped

- none

## Deviations

- **BusinessForm average display**: Plan called for `getCurrencyCode(marketplace)` but the `currency` prop is already the code string — used it directly as prefix. Simpler, avoids unnecessary function call.
- **EvaluationDetailPage marketplace**: Plan expected backend API to include marketplace in evaluation detail response. Added `marketplace?: string` to `EvaluationDetail` interface as optional with graceful undefined fallback, since the field may not be present in older evaluation data.

## Known Limitations

- **fields.ts `unit: 'IDR'` values**: Static field definitions in `fields.ts` still have `unit: 'IDR'` hardcoded. The render layer overrides these with the `currency` prop, so this is cosmetic — the correct currency is always displayed. A future cleanup could make these marketplace-aware at the definition level.
- **SCORE-03 not fully validated**: While the frontend now sends marketplace to all the right places, full end-to-end proof (start a TH evaluation, score it, verify THB thresholds applied) requires a live runtime test — not covered by vitest/jsdom tests.
- **No runtime marketplace persistence**: The marketplace selector defaults to 'ID' on page load. If a brand is known to be Thai, the user must re-select TH each time. A future enhancement could persist marketplace on the brand or derive it from brand metadata.

## Follow-ups

- none — S04 is the final slice in M001. All planned work is complete.

## Files Created/Modified

- `frontend/src/components/evaluation/forms/formUtils.ts` — added getCurrencyCode, formatCurrency, parseCurrency; deprecated formatIDR/parseIDR
- `frontend/src/components/evaluation/forms/formUtils.test.ts` — **created** — 19 tests for all utilities
- `frontend/src/components/evaluation/forms/formConfig.ts` — added formatCurrency, parseCurrency, getCurrencyCode to barrel exports
- `frontend/src/components/evaluation/forms/CurrencyField.tsx` — added currency prop, dynamic label, switched to formatCurrency/parseCurrency
- `frontend/src/components/evaluation/forms/CurrencyField.test.tsx` — added 2 new tests (THB variant, unknown fallback)
- `frontend/src/services/apiClient.ts` — added marketplace query param to rules types, marketplace body field to evaluation types
- `frontend/src/hooks/useRules.ts` — marketplace param, marketplace-scoped queryKey, marketplace query param in API call
- `frontend/src/hooks/useUpdateRule.ts` — marketplace in UpdateRuleParams, passes as query param on PUT
- `frontend/src/hooks/useEvaluation.ts` — marketplace in EvaluationInputsUpdate
- `frontend/src/hooks/useAutoSaveForm.ts` — accepts and sends marketplace in save body
- `frontend/src/hooks/useSaveEvaluation.ts` — marketplace in SaveEvaluationRequest
- `frontend/src/hooks/useEvaluationOrchestrator.ts` — marketplace state, currency derivation, threaded to all hooks, exposed in return
- `frontend/src/hooks/useEvaluationDetail.ts` — marketplace in EvaluationDetail interface
- `frontend/src/pages/RulesPage.tsx` — marketplace tabs UI, marketplace state, edit cancellation on tab switch
- `frontend/src/components/rules/RulesPage.test.tsx` — 4 new marketplace tab tests
- `frontend/src/components/evaluation/EvaluationSections.tsx` — marketplace radio selector, currency threading to forms
- `frontend/src/components/evaluation/EvaluationHeader.tsx` — marketplace badge
- `frontend/src/components/evaluation/forms/BusinessForm.tsx` — currency prop, removed local formatCurrencyDisplay
- `frontend/src/components/evaluation/forms/PromoToolsForm.tsx` — currency prop threading to CurrencyField
- `frontend/src/components/evaluation/forms/CompetitionForm.tsx` — currency prop threading to CurrencyField
- `frontend/src/pages/EvaluationPage.tsx` — wired marketplace/currency from orchestrator
- `frontend/src/components/evaluation/calculators/TopSkuResults.tsx` — marketplace prop, formatCurrency/getCurrencyCode
- `frontend/src/components/evaluation/calculators/CalculatorResultsSection.tsx` — marketplace prop threading
- `frontend/src/components/dashboard/DataIntelligence.tsx` — removed local formatIDR, marketplace prop, shared formatCurrency
- `frontend/src/components/dashboard/PresentationDashboard.tsx` — passes marketplace to DataIntelligence
- `frontend/src/pages/EvaluationDetailPage.tsx` — removed local formatIDR, marketplace-aware formatting

## Forward Intelligence

### What the next slice should know
- M001 is complete. All four slices (S01–S04) delivered the full-stack THB marketplace expansion. Backend: marketplace column + rules API + scoring engine + CSV parsing. Frontend: currency utilities + Rules page tabs + evaluation flow + display components.
- The `formatCurrency` function currently uses identical formatting for both IDR and THB (no decimals, comma thousands). If a future marketplace requires different formatting (e.g., decimals), the `_marketplace` param is already threaded but unused — add locale-specific `Intl.NumberFormat` options there.
- `fields.ts` still has `unit: 'IDR'` hardcoded on ~25 field definitions. The render layer correctly overrides this with the `currency` prop, but if anyone reads `unit` directly from field config, they'll get 'IDR'.

### What's fragile
- **Marketplace default 'ID'** is hardcoded in multiple places (useEvaluationOrchestrator, CurrencyField, form components, display components). Adding a third marketplace requires touching all these defaults. Consider a config constant.
- **getCurrencyCode mapping** is a simple switch statement in formUtils.ts. Adding marketplaces requires updating this AND the orchestrator's inline ternary for currency derivation.
- **RulesPage edit cancellation** uses a useEffect watching marketplace to call cancelEdit(). If cancelEdit's identity changes on re-render (not memoized), this could cause infinite loops — currently stable because cancelEdit is defined with useCallback.

### Authoritative diagnostics
- `cd frontend && npx vitest run --reporter=verbose` — **536 tests** is the baseline. Any regression from this number indicates a problem introduced after S04.
- `grep -rn "formatIDR\|formatCurrencyDisplay" frontend/src --include="*.tsx" --include="*.ts" | grep -v test | grep -v deprecated` — should return only formUtils.ts and formConfig.ts barrel lines. Any other hit is a regression.
- React Query devtools → look for `['rules', 'ID']` and `['rules', 'TH']` cache keys — confirms marketplace isolation is working.

### What assumptions changed
- **Plan assumed backend evaluation detail API includes marketplace field** — it currently doesn't. The `EvaluationDetail` interface has `marketplace?: string` as optional to handle this gracefully. Older evaluations without marketplace render with default IDR formatting.
