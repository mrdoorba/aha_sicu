---
estimated_steps: 5
estimated_files: 5
---

# T02: Add marketplace tabs to Rules page

**Slice:** S04 — Frontend Currency and Marketplace UI
**Milestone:** M001

## Description

Add marketplace tab switching (ID / TH) to the Rules page so admins can view and edit THB thresholds independently from IDR. This involves: updating the API client types for rules endpoints to accept `marketplace` query params, updating the `useRules` and `useUpdateRule` hooks to thread marketplace, and adding a Tabs UI to `RulesPage.tsx`.

The backend already fully supports `GET /api/v1/rules?marketplace=TH` and `PUT /api/v1/rules/{template}?marketplace=TH`. The frontend just needs to pass the parameter.

**Critical pitfall**: The `marketplace` MUST be included in the React Query `queryKey` — e.g. `['rules', marketplace]`. Without this, switching tabs shows stale cached data from the wrong marketplace. Similarly, `useUpdateRule` must pass `?marketplace=TH` as a query param on the PUT URL — without this, saving THB rules would overwrite IDR rules.

**Relevant skill**: `test` — vitest with jsdom.

## Steps

1. **Update `apiClient.ts` rules types**:
   - `GET /api/v1/rules` — add `parameters: { query?: { marketplace?: string } }` alongside the existing response type.
   - `PUT /api/v1/rules/{template}` — add `query?: { marketplace?: string }` to `parameters` alongside the existing `path` parameter.

2. **Update `useRules` hook** (`frontend/src/hooks/useRules.ts`):
   - Add `marketplace?: string` parameter to `useRules(marketplace?: string)`.
   - Update `queryKey` to `['rules', marketplace ?? 'ID']`.
   - Pass `marketplace` as query param: `client.GET('/api/v1/rules', { params: { query: { marketplace } } })`.

3. **Update `useUpdateRule` hook** (`frontend/src/hooks/useUpdateRule.ts`):
   - Add `marketplace?: string` to `UpdateRuleParams` interface.
   - Pass marketplace as query param in the PUT call: `client.PUT('/api/v1/rules/{template}', { params: { path: { template }, query: { marketplace } }, body: { rules } })`.
   - Update `onSuccess` invalidation to include marketplace in queryKey: `queryClient.invalidateQueries({ queryKey: ['rules'] })` (invalidate all rules queries, since both ID and TH might need refresh after edit).

4. **Add marketplace tabs to `RulesPage.tsx`**:
   - Import `Tabs`, `TabsList`, `TabsTrigger` from `../components/ui/tabs`.
   - Add `marketplace` state: `const [marketplace, setMarketplace] = useState<string>('ID')`.
   - Pass `marketplace` to `useRules(marketplace)`.
   - Pass `marketplace` to `updateRule.mutateAsync({ template, rules, marketplace })`.
   - Add Tabs UI above the rules content (between the header and the category cards):
     ```tsx
     <Tabs value={marketplace} onValueChange={setMarketplace}>
       <TabsList>
         <TabsTrigger value="ID">🇮🇩 Indonesia (IDR)</TabsTrigger>
         <TabsTrigger value="TH">🇹🇭 Thailand (THB)</TabsTrigger>
       </TabsList>
     </Tabs>
     ```
   - Reset edit state when marketplace changes (cancel any in-progress editing): add `useEffect` watching `marketplace` that calls `cancelEdit()` if `isEditing` is true.
   - Include marketplace in `editedRules` key and validation error key prefix.

5. **Add marketplace tab test to `RulesPage.test.tsx`**:
   - The existing test mock `mockUseRules` returns rules for a single marketplace. Add a test that:
     - Renders the page, verifies both tab triggers ("Indonesia" and "Thailand") are visible.
     - Clicks the "Thailand" tab.
     - Verifies `mockUseRules` was called with `'TH'` marketplace.
   - Ensure all existing 17+ tests still pass (they should — existing tests don't interact with tabs, and the default tab is "ID" which maps to the existing behavior).

## Must-Haves

- [ ] `apiClient.ts` rules GET and PUT accept `marketplace` query parameter
- [ ] `useRules` includes marketplace in queryKey and passes it to API call
- [ ] `useUpdateRule` passes marketplace as query param on PUT
- [ ] RulesPage renders marketplace tabs (ID / TH) using shadcn Tabs component
- [ ] Switching tabs triggers re-fetch with correct marketplace param
- [ ] Edit mode resets when marketplace tab changes
- [ ] All existing RulesPage tests pass (no regression)
- [ ] New marketplace tab test passes

## Verification

- `cd frontend && npx vitest run src/components/rules/RulesPage.test.tsx --reporter=verbose` — all existing + new tests pass
- `cd frontend && npx vitest run --reporter=verbose` — full suite passes (no regressions from apiClient changes)

## Inputs

- `frontend/src/services/apiClient.ts` — current rules type definitions (lines 688-735) have no marketplace parameter
- `frontend/src/hooks/useRules.ts` — current hook fetches without marketplace filter, queryKey is `['rules']`
- `frontend/src/hooks/useUpdateRule.ts` — current hook PUTs without marketplace query param
- `frontend/src/pages/RulesPage.tsx` — current page has no marketplace awareness
- `frontend/src/components/rules/RulesPage.test.tsx` — existing 17+ tests with mock patterns
- `frontend/src/components/ui/tabs.tsx` — shadcn Tabs component (already exists, used in DataIntelligence.tsx)
- T01 output: `formatCurrency`/`getCurrencyCode` available in `formConfig.ts` (not directly needed in RulesPage, but establishes the marketplace type pattern)

## Expected Output

- `frontend/src/services/apiClient.ts` — rules GET and PUT types include `marketplace` query param
- `frontend/src/hooks/useRules.ts` — accepts marketplace param, includes in queryKey and API call
- `frontend/src/hooks/useUpdateRule.ts` — accepts marketplace in params, passes as query param
- `frontend/src/pages/RulesPage.tsx` — renders marketplace tabs, manages marketplace state, threads to hooks
- `frontend/src/components/rules/RulesPage.test.tsx` — gains marketplace tab switching test

## Observability Impact

- **React Query cache keys**: `queryKey` changes from `['rules']` to `['rules', marketplace]`. Stale cross-marketplace data is now impossible — inspect via React Query devtools to see separate cache entries per marketplace.
- **Network requests**: `GET /api/v1/rules` now includes `?marketplace=TH` query param when Thailand tab is active. `PUT /api/v1/rules/{template}` also includes `?marketplace=TH`. Verify in browser Network tab that the param is present.
- **Tab state inspection**: The active marketplace tab is visible in the UI (`🇮🇩 Indonesia (IDR)` / `🇹🇭 Thailand (THB)`). React DevTools shows `marketplace` state on the `RulesPage` component.
- **Failure visibility**: If marketplace is not passed on PUT, THB rules would silently overwrite IDR rules (backend defaults to ID). Detectable by inspecting the PUT request URL in network tab for presence of `?marketplace=TH`. The `onSuccess` invalidation uses `queryKey: ['rules']` (prefix match) to refresh all marketplace variants after any edit.
