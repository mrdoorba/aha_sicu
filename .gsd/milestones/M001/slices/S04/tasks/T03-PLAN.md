---
estimated_steps: 8
estimated_files: 7
---

# T03: Wire marketplace through evaluation flow hooks and UI

**Slice:** S04 — Frontend Currency and Marketplace UI
**Milestone:** M001

## Description

Wire the `marketplace` parameter through the evaluation flow so that saving evaluation inputs and saving the final evaluation both send marketplace to the backend. Add a marketplace selector to the evaluation UI. Thread the `currency` prop to all form components that use `CurrencyField`.

The backend API already accepts `marketplace` in the PUT body (evaluation_inputs) and POST body (save evaluation). The frontend just hasn't been sending it. This task connects the frontend state management to those API fields.

**Key architectural decision (from research)**: Marketplace is a user-selectable per-evaluation setting (not derived from brand data). The backend stores it on `evaluation_inputs`. The orchestrator manages it as local state, defaulting to `'ID'`.

**Critical pitfalls**:
- `useAutoSaveForm` must include `marketplace` in the save mutation body. Without it, backend defaults to `'ID'` and TH evaluations get scored with ID rules.
- `useSaveEvaluation` POST body must include `marketplace`. Same consequence if missing.
- The `useRules` call in `useEvaluationOrchestrator` should pass marketplace so the correct rules are used for scoring display.

**Relevant skill**: `test` — vitest with jsdom.

## Steps

1. **Update `apiClient.ts` evaluation types**:
   - `PUT /api/v1/evaluations/brands/{brand_id}` — add `marketplace?: string` to the request body type (alongside existing `category_type` and `manual_data`).
   - `POST /api/v1/evaluations/brands/{brand_id}/save` — add `marketplace?: string` and `period?: string` to the request body type.

2. **Update `useEvaluation.ts`**:
   - Add `marketplace?: string` to the `EvaluationInputsUpdate` interface.
   - The `useSaveEvaluationInputs` mutation doesn't need changes — it already passes the full body object through.

3. **Update `useAutoSaveForm.ts`**:
   - Add `marketplace?: string` to `UseAutoSaveFormOptions` interface.
   - In `doSave()`, include `marketplace` in the mutation body: `{ category_type: ..., manual_data: ..., marketplace }`.
   - Accept `marketplace` from options in the hook signature.

4. **Update `useSaveEvaluation.ts`**:
   - Add `marketplace?: string` to `SaveEvaluationRequest` interface.
   - The `useMutation` mutationFn already spreads the request to `body` — no additional changes needed since the type now includes marketplace.

5. **Update `useEvaluationOrchestrator.ts`**:
   - Add marketplace state: `const [marketplace, setMarketplace] = useState<string>('ID')`.
   - Pass `marketplace` to `useAutoSaveForm({ brandId, categoryType, initialData, marketplace })`.
   - Pass `marketplace` to `useRules(marketplace)` so `activeRules` reflects the correct marketplace.
   - In `handleSaveEvaluation`, include `marketplace` in the `saveEvaluation()` call body.
   - In `handleCategoryChange`, include `marketplace` in the `saveMutation.mutate()` body.
   - Derive `currency` from marketplace: `const currency = marketplace === 'TH' ? 'THB' : 'IDR'`.
   - Expose `marketplace`, `setMarketplace`, and `currency` in the return object.

6. **Update `EvaluationSections.tsx`**:
   - Add `marketplace: string`, `currency: string`, `onMarketplaceChange: (value: string) => void` to `FormProps` interface.
   - Add marketplace selector UI — a simple card above the fashion/non-fashion selector:
     ```tsx
     <Card className="mb-4">
       <CardContent className="pt-4">
         <p className="mb-3 text-sm font-medium">Marketplace</p>
         <RadioGroup value={marketplace} onValueChange={onMarketplaceChange} className="flex gap-6">
           <div className="flex items-center gap-2">
             <RadioGroupItem value="ID" id="mp-id" />
             <Label htmlFor="mp-id">🇮🇩 Indonesia (IDR)</Label>
           </div>
           <div className="flex items-center gap-2">
             <RadioGroupItem value="TH" id="mp-th" />
             <Label htmlFor="mp-th">🇹🇭 Thailand (THB)</Label>
           </div>
         </RadioGroup>
       </CardContent>
     </Card>
     ```
   - Thread `currency` prop to `BusinessForm`, `PromoToolsForm`, and `CompetitionForm` (these use `CurrencyField`).
   - Note: The form components themselves need a `currency` prop added. For `BusinessForm`, add `currency?: string` to `BusinessFormProps` and pass it to each `<CurrencyField currency={currency} .../>`. Same for `PromoToolsForm` and `CompetitionForm`. Read each form file to understand its exact interface before modifying.

7. **Update form components to accept and thread `currency` prop**:
   - `BusinessForm.tsx` — add `currency?: string` to `BusinessFormProps`, pass to `<CurrencyField currency={currency} />`.
   - `PromoToolsForm.tsx` — add `currency?: string` to props, pass to `<CurrencyField currency={currency} />`.
   - `CompetitionForm.tsx` — add `currency?: string` to props, pass to `<CurrencyField currency={currency} />`.
   - All three default to `'IDR'` if not provided (backward compat).

8. **Update `EvaluationHeader.tsx`**:
   - Add `marketplace?: string` to `EvaluationHeaderProps`.
   - After the brand name heading, render a marketplace badge:
     ```tsx
     <Badge variant="outline">{marketplace === 'TH' ? '🇹🇭 TH' : '🇮🇩 ID'}</Badge>
     ```

## Must-Haves

- [ ] `apiClient.ts` evaluation PUT and POST types include `marketplace` field
- [ ] `useAutoSaveForm` sends `marketplace` in the PUT body
- [ ] `useSaveEvaluation` request type includes `marketplace`
- [ ] `useEvaluationOrchestrator` manages marketplace state and threads it through
- [ ] Evaluation page shows marketplace selector (ID / TH)
- [ ] Changing marketplace updates currency labels on all CurrencyField instances
- [ ] Evaluation header shows marketplace badge
- [ ] All existing tests pass (no regressions)

## Verification

- `cd frontend && npx vitest run --reporter=verbose` — full test suite passes
- Grep check: `grep -n "marketplace" frontend/src/hooks/useEvaluationOrchestrator.ts` shows marketplace in state, return value, and save calls

## Inputs

- `frontend/src/services/apiClient.ts` — evaluation endpoint types (lines 426-474, 651-687) currently lack marketplace
- `frontend/src/hooks/useEvaluation.ts` — `EvaluationInputsUpdate` interface currently has only `category_type` and `manual_data`
- `frontend/src/hooks/useAutoSaveForm.ts` — `doSave` builds mutation body without marketplace (line ~65)
- `frontend/src/hooks/useSaveEvaluation.ts` — `SaveEvaluationRequest` lacks marketplace
- `frontend/src/hooks/useEvaluationOrchestrator.ts` — no marketplace awareness
- `frontend/src/components/evaluation/EvaluationSections.tsx` — no marketplace prop or selector
- `frontend/src/components/evaluation/EvaluationHeader.tsx` — no marketplace badge
- T01 output: `CurrencyField` accepts `currency` prop; `formatCurrency`/`getCurrencyCode` available

## Expected Output

- `frontend/src/services/apiClient.ts` — evaluation PUT body gains `marketplace?: string`, POST body gains `marketplace?: string` + `period?: string`
- `frontend/src/hooks/useEvaluation.ts` — `EvaluationInputsUpdate` gains `marketplace?: string`
- `frontend/src/hooks/useAutoSaveForm.ts` — accepts and sends `marketplace` in save body
- `frontend/src/hooks/useSaveEvaluation.ts` — `SaveEvaluationRequest` gains `marketplace?: string`
- `frontend/src/hooks/useEvaluationOrchestrator.ts` — manages marketplace state, threads to all hooks, exposes in return
- `frontend/src/components/evaluation/EvaluationSections.tsx` — renders marketplace selector, threads currency to forms
- `frontend/src/components/evaluation/EvaluationHeader.tsx` — shows marketplace badge
- `frontend/src/components/evaluation/forms/BusinessForm.tsx` — accepts `currency` prop, threads to CurrencyField
- `frontend/src/components/evaluation/forms/PromoToolsForm.tsx` — accepts `currency` prop, threads to CurrencyField
- `frontend/src/components/evaluation/forms/CompetitionForm.tsx` — accepts `currency` prop, threads to CurrencyField
