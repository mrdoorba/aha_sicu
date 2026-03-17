---
id: T02
parent: S04
milestone: M001
provides:
  - Marketplace tabs (ID / TH) on RulesPage for switching between IDR and THB rule sets
  - useRules(marketplace) hook with marketplace-scoped queryKey ['rules', marketplace]
  - useUpdateRule passes marketplace as query param on PUT to avoid cross-marketplace overwrites
  - apiClient types for rules GET and PUT accept marketplace query parameter
key_files:
  - frontend/src/services/apiClient.ts
  - frontend/src/hooks/useRules.ts
  - frontend/src/hooks/useUpdateRule.ts
  - frontend/src/pages/RulesPage.tsx
  - frontend/src/components/rules/RulesPage.test.tsx
key_decisions:
  - queryKey includes marketplace as second element ['rules', marketplace ?? 'ID'] — prevents stale cross-marketplace cache hits
  - onSuccess invalidation uses prefix queryKey ['rules'] (no marketplace suffix) to refresh all marketplace variants after any edit
  - useEffect cancels edit mode on marketplace change rather than persisting edits across tabs — simpler UX, no risk of saving ID edits to TH
patterns_established:
  - Marketplace tab pattern uses shadcn Tabs with string state ('ID' | 'TH'), threaded to hooks as query param
  - Edit state resets on marketplace switch via useEffect watching marketplace — apply this pattern for any tabbed edit UI
observability_surfaces:
  - React Query cache shows separate entries per marketplace (['rules', 'ID'] and ['rules', 'TH']) — inspect via React Query devtools
  - Network tab shows ?marketplace=TH on GET/PUT requests when Thailand tab is active
  - Active marketplace tab visually indicates which rule set is displayed
duration: 10m
verification_result: passed
completed_at: 2026-03-17
blocker_discovered: false
---

# T02: Add marketplace tabs to Rules page

**Added ID/TH marketplace tabs to the Rules page with marketplace-scoped data fetching and edit state reset on tab switch.**

## What Happened

1. **apiClient.ts**: Added `parameters: { query?: { marketplace?: string } }` to both `GET /api/v1/rules` and `PUT /api/v1/rules/{template}` type definitions.

2. **useRules.ts**: Added `marketplace?: string` parameter. Updated `queryKey` to `['rules', marketplace ?? 'ID']` and passes `marketplace` as query param to `client.GET`. This ensures React Query caches ID and TH rules separately and re-fetches when tabs switch.

3. **useUpdateRule.ts**: Added `marketplace?: string` to `UpdateRuleParams`. Passes marketplace as `query: { marketplace }` in the PUT call alongside the existing `path` param. The `onSuccess` invalidation uses `queryKey: ['rules']` prefix to refresh all marketplace variants.

4. **RulesPage.tsx**: Added `marketplace` state defaulting to `'ID'`. Added shadcn `Tabs` / `TabsList` / `TabsTrigger` between the header and category cards. Threads `marketplace` to `useRules(marketplace)` and `updateRule.mutateAsync({ template, rules, marketplace })`. Added `useEffect` watching `marketplace` that calls `cancelEdit()` when the tab changes during editing.

5. **RulesPage.test.tsx**: Updated the `useRules` mock to forward the `marketplace` argument. Added 4 new tests in a `Marketplace tabs` describe block: renders both tab triggers, defaults to ID, switches to TH on click, and cancels edit mode on tab change.

## Verification

- `npx vitest run src/components/rules/RulesPage.test.tsx --reporter=verbose` — **38/38 passed** (34 existing + 4 new marketplace tab tests)
- `npx vitest run --reporter=verbose` — **536/536 passed** across 63 test files, zero regressions

### Slice-level verification (intermediate — partial pass expected)
- ✅ `CurrencyField.test.tsx` — 9/9 passed (from T01)
- ✅ `formUtils.test.ts` — 19/19 passed (from T01)
- ✅ `RulesPage.test.tsx` — 38/38 passed, marketplace tab switching verified
- ⬜ Grep audit for zero IDR hits — remaining callers in `DataIntelligence.tsx`, `fields.ts`, etc. (T04)
- ✅ Failure-path check — `CurrencyField` with `currency="XX"` renders `(XX)` without crashing (from T01)

## Diagnostics

- **Verify marketplace param in requests**: Open browser Network tab → navigate to Rules page → click Thailand tab → confirm `GET /api/v1/rules?marketplace=TH` fires
- **Inspect React Query cache**: React Query devtools → look for `['rules', 'ID']` and `['rules', 'TH']` entries after switching tabs
- **Confirm edit reset**: Enter edit mode → switch marketplace tab → verify edit mode exits (Cancel/Save buttons disappear)
- **Verify PUT marketplace**: In edit mode on TH tab → save → confirm `PUT /api/v1/rules/{template}?marketplace=TH` in network tab

## Deviations

None.

## Known Issues

None.

## Files Created/Modified

- `frontend/src/services/apiClient.ts` — added `marketplace` query parameter to rules GET and PUT type definitions
- `frontend/src/hooks/useRules.ts` — added `marketplace` param, marketplace-scoped `queryKey`, passes marketplace to API call
- `frontend/src/hooks/useUpdateRule.ts` — added `marketplace` to `UpdateRuleParams`, passes as query param on PUT
- `frontend/src/pages/RulesPage.tsx` — added marketplace tabs UI, marketplace state, useEffect for edit cancellation, threaded marketplace to hooks
- `frontend/src/components/rules/RulesPage.test.tsx` — updated mock to forward marketplace arg, added 4 marketplace tab tests
- `frontend/src/services/apiClient.ts` — (same file, rules type update)
