# Chained Evaluation Flow Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers-extended-cc:executing-plans to implement this plan task-by-task.

**Goal:** Chain calculator recalculation into the scoring and save flows so "Hitung Skor" recalculates all calculators before scoring, and "Simpan Evaluasi" runs the full chain (recalculate → score → save).

**Architecture:** Frontend-only changes. The orchestrator hook (`useEvaluationOrchestrator`) gains a `runAllCalculators` reference and chains it before scoring/saving. The scoring hook gains an optional pre-step. No backend changes needed.

**Tech Stack:** React, TanStack Query, i18next, Vitest

---

### Task 0: Add Indonesian translations for calculator buttons and step-aware loading labels

**Files:**
- Modify: `frontend/src/locales/id.json`
- Modify: `frontend/src/locales/en.json`
- Modify: `frontend/src/locales/th.json`

**Step 1: Update locale files**

In `id.json`, change:
```json
"calculator.calculateAll": "Hitung Semua",
"calculator.recalculateAll": "Hitung Ulang Semua",
```

Add new step-aware loading keys to all 3 locale files:
```json
"scoring.stepRecalculating": "Menghitung ulang data...",
"scoring.stepScoring": "Menghitung skor...",
"evaluationSections.stepRecalculating": "Menghitung ulang data...",
"evaluationSections.stepScoring": "Menghitung skor...",
"evaluationSections.stepSaving": "Menyimpan evaluasi..."
```

English equivalents:
```json
"scoring.stepRecalculating": "Recalculating data...",
"scoring.stepScoring": "Calculating score...",
"evaluationSections.stepRecalculating": "Recalculating data...",
"evaluationSections.stepScoring": "Calculating score...",
"evaluationSections.stepSaving": "Saving evaluation..."
```

Thai equivalents:
```json
"scoring.stepRecalculating": "กำลังคำนวณข้อมูลใหม่...",
"scoring.stepScoring": "กำลังคำนวณคะแนน...",
"evaluationSections.stepRecalculating": "กำลังคำนวณข้อมูลใหม่...",
"evaluationSections.stepScoring": "กำลังคำนวณคะแนน...",
"evaluationSections.stepSaving": "กำลังบันทึกการประเมิน..."
```

**Step 2: Commit**

```bash
git add frontend/src/locales/id.json frontend/src/locales/en.json frontend/src/locales/th.json
git commit -m "Add Indonesian calculator button labels and step-aware loading keys"
```

---

### Task 1: Chain run-all into useScoring's generateScore

**Files:**
- Modify: `frontend/src/hooks/useScoring.ts`
- Modify: `frontend/src/hooks/useEvaluationOrchestrator.ts`

**Step 1: Update useScoring to accept a `preStep` callback**

In `frontend/src/hooks/useScoring.ts`, add an optional `preStep` parameter and a `step` state:

```typescript
// Add to imports
// (no new imports needed)

// Add step type
export type ScoringStep = 'idle' | 'recalculating' | 'scoring';

// Update the hook signature
export function useScoring(brandId: number, preStep?: () => Promise<void>) {
  const queryClient = useQueryClient();
  const [scoringResult, setScoringResult] = useState<ScoringResult | null>(null);
  const [isStale, setIsStale] = useState(false);
  const [lastPeriod, setLastPeriod] = useState('');
  const [step, setStep] = useState<ScoringStep>('idle');

  const mutation = useMutation<ScoringResult, Error, ScoringRequest>({
    mutationFn: async (request) => {
      setLastPeriod(request.period);

      // Run pre-step (recalculate all calculators) if provided
      if (preStep) {
        setStep('recalculating');
        await preStep();
      }

      setStep('scoring');
      const { data, error } = await client.POST(
        '/api/v1/evaluations/brands/{brand_id}/score',
        {
          params: { path: { brand_id: brandId } },
          body: request,
        },
      );
      if (error) throw error;
      return data as ScoringResult;
    },
    onSuccess: (data) => {
      setScoringResult(data);
      setIsStale(false);
      setStep('idle');
      queryClient.setQueryData(['scoring', brandId], data);
    },
    onError: () => {
      setStep('idle');
    },
  });

  // ... (markStale and useEffect unchanged) ...

  return {
    generateScore: mutation.mutate,
    scoringResult,
    lastPeriod,
    isStale,
    markStale,
    isGenerating: mutation.isPending,
    scoringStep: step,
    error: mutation.error,
  };
}
```

**Step 2: Wire up preStep in useEvaluationOrchestrator**

In `frontend/src/hooks/useEvaluationOrchestrator.ts`:

1. Import `useRunAllCalculators`:
```typescript
import { useCalculatorResults, useRunAllCalculators } from './useCalculator';
```

2. Add the hook call and create the preStep:
```typescript
// After the existing useCalculatorResults line:
const { data: calculatorResultsData } = useCalculatorResults(brandId);
// Add:
const runAllMutation = useRunAllCalculators(brandId);

const recalculateAll = useCallback(async () => {
  await runAllMutation.mutateAsync();
}, [runAllMutation]);
```

3. Pass `recalculateAll` as the preStep to `useScoring`:
```typescript
const {
  generateScore,
  scoringResult,
  lastPeriod,
  isStale,
  isGenerating,
  scoringStep,
  error: scoringError,
} = useScoring(brandId, recalculateAll);
```

4. Return `scoringStep` from the hook:
```typescript
return {
  // ... existing fields ...
  scoringStep,
  // ...
};
```

**Step 3: Run tests**

```bash
cd frontend && npx vitest run src/components/evaluation/scoring/ScoringSection.test.tsx
```

Existing tests should still pass since `ScoringSection` receives `isGenerating` as a prop (the chaining is internal to the hook).

**Step 4: Commit**

```bash
git add frontend/src/hooks/useScoring.ts frontend/src/hooks/useEvaluationOrchestrator.ts
git commit -m "Chain run-all calculators into scoring flow via preStep"
```

---

### Task 2: Update ScoringSection to show step-aware loading labels

**Files:**
- Modify: `frontend/src/components/evaluation/scoring/ScoringSection.tsx`
- Modify: `frontend/src/components/evaluation/scoring/ScoringSection.test.tsx`

**Step 1: Update ScoringSection props and button label**

In `frontend/src/components/evaluation/scoring/ScoringSection.tsx`:

1. Import the step type:
```typescript
import type { ScoringResult, ScoringStep } from '../../../hooks/useScoring';
```

2. Add `scoringStep` to props:
```typescript
interface ScoringSectionProps {
  // ... existing props ...
  scoringStep?: ScoringStep;
}
```

3. Add it to destructured props (default `'idle'`):
```typescript
export const ScoringSection = ({
  // ... existing ...
  scoringStep = 'idle',
}: ScoringSectionProps) => {
```

4. Replace the button content logic (lines 88-91):
```typescript
{isGenerating ? (
  <>
    <RefreshCw className="mr-1 size-4 animate-spin" aria-hidden="true" />
    {scoringStep === 'recalculating'
      ? t('scoring.stepRecalculating')
      : t('scoring.stepScoring')}
  </>
) : (
  scoringResult && !isStale ? t('scoring.recalculate') : t('scoring.calculate')
)}
```

**Step 2: Wire up in EvaluationSections**

In `frontend/src/components/evaluation/EvaluationSections.tsx`:

1. Import step type:
```typescript
import type { ScoringStep } from '../../hooks/useScoring';
```

2. Add `scoringStep` to `ScoringProps`:
```typescript
interface ScoringProps {
  // ... existing ...
  scoringStep?: ScoringStep;
}
```

3. Pass it through to `ScoringSection`:
```typescript
<ScoringSection
  onGenerate={onGenerateScore}
  scoringResult={scoringResult}
  isGenerating={isGenerating}
  isStale={isStale}
  error={scoringError}
  categoryType={categoryType}
  storeName={storeName}
  brandName={brandName}
  scoringStep={scoringStep}
/>
```

**Step 3: Wire up in EvaluationPage**

Find where `EvaluationSections` is rendered and pass `scoringStep` from the orchestrator. Check `EvaluationPage.tsx` — add `scoringStep` to the props passed to `EvaluationSections`.

**Step 4: Update test**

In `ScoringSection.test.tsx`, add a test for step-aware loading:

```typescript
it('shows recalculating label during recalculation step', () => {
  render(
    <ScoringSection
      {...defaultProps}
      isGenerating
      scoringStep="recalculating"
    />,
  );
  expect(screen.getByText(/menghitung ulang data/i)).toBeInTheDocument();
});

it('shows scoring label during scoring step', () => {
  render(
    <ScoringSection
      {...defaultProps}
      isGenerating
      scoringStep="scoring"
    />,
  );
  expect(screen.getByText(/menghitung skor/i)).toBeInTheDocument();
});
```

**Step 5: Run tests**

```bash
cd frontend && npx vitest run src/components/evaluation/scoring/ScoringSection.test.tsx
```

**Step 6: Commit**

```bash
git add frontend/src/components/evaluation/scoring/ScoringSection.tsx \
       frontend/src/components/evaluation/scoring/ScoringSection.test.tsx \
       frontend/src/components/evaluation/EvaluationSections.tsx
git commit -m "Show step-aware loading labels in scoring button"
```

---

### Task 3: Chain full flow into Simpan Evaluasi

**Files:**
- Modify: `frontend/src/hooks/useEvaluationOrchestrator.ts`
- Modify: `frontend/src/components/evaluation/EvaluationSections.tsx`

**Step 1: Add save step state and chained save handler**

In `frontend/src/hooks/useEvaluationOrchestrator.ts`:

1. Add a save step state:
```typescript
export type SaveStep = 'idle' | 'recalculating' | 'scoring' | 'saving';
```

2. Add state for tracking save step:
```typescript
const [saveStep, setSaveStep] = useState<SaveStep>('idle');
```

3. Rewrite `handleSaveEvaluation` to chain the full flow:

```typescript
const handleSaveEvaluation = useCallback(async () => {
  if (!evaluationState?.category_type) return;

  try {
    // Step 1: Recalculate all
    setSaveStep('recalculating');
    await runAllMutation.mutateAsync();

    // Step 2: Score
    setSaveStep('scoring');
    const scoringRequest = {
      template: evaluationState.category_type as 'fashion' | 'non_fashion',
      verdict: scoringResult?.verdict ?? '✔️',
      store_name: brand?.brand_name ?? '',
      period: lastPeriod || generatePeriodOptions()[0],
      brand_name: brand?.brand_name ?? '',
    };

    const scoreResponse = await new Promise<ScoringResult>((resolve, reject) => {
      generateScore(scoringRequest, {
        onSuccess: resolve,
        onError: (err: Error) => reject(err),
      });
    });

    // Step 3: Save — use freshly fetched calculator results
    setSaveStep('saving');

    // Wait briefly for React Query cache to update with new calculator results
    await queryClient.invalidateQueries({ queryKey: ['calculatorResults', brandId] });
    const freshCalcData = queryClient.getQueryData<CalculatorResultsListResponse>(
      ['calculatorResults', brandId],
    );

    const calcResults: Record<string, unknown> = {};
    if (freshCalcData?.results) {
      for (const r of freshCalcData.results) {
        calcResults[r.calculator_type] = {
          details: r.details,
          output_text: r.output_text,
        };
      }
    }

    calcResults['scoring_summary'] = {
      conclusion: scoreResponse.conclusion,
      conclusion_i18n: scoreResponse.conclusion_i18n,
      marketing_estimation: scoreResponse.marketing_estimation,
      marketing_budget: scoreResponse.marketing_budget,
      marketing_budget_i18n: scoreResponse.marketing_budget_i18n,
      closing_message: scoreResponse.closing_message,
      closing_message_i18n: scoreResponse.closing_message_i18n,
    };

    await new Promise<void>((resolve, reject) => {
      saveEvaluation(
        {
          template: scoreResponse.template as 'fashion' | 'non_fashion',
          final_score: scoreResponse.total_score,
          verdict: scoreResponse.verdict,
          score_breakdown: scoreResponse.category_scores as unknown as Array<Record<string, unknown>>,
          calculator_results: calcResults,
          manual_inputs: manualData as unknown as Record<string, unknown>,
          rule_version: scoreResponse.rule_version,
          email_output: scoreResponse.email_body || null,
          period: lastPeriod,
        },
        {
          onSuccess: () => {
            toast.success(t('evaluation.saved'));
            resolve();
          },
          onError: (err: Error) => {
            toast.error(t('evaluation.saveFailed'));
            reject(err);
          },
        },
      );
    });
  } catch {
    // Error toasts handled by individual steps
  } finally {
    setSaveStep('idle');
  }
}, [
  evaluationState?.category_type, runAllMutation, scoringResult, brand,
  lastPeriod, generateScore, queryClient, brandId, saveEvaluation,
  manualData, t,
]);
```

4. Import needed types at top:
```typescript
import type { CalculatorResultsListResponse } from './useCalculator';
import { generatePeriodOptions } from '../components/evaluation/scoring/periodOptions';
import type { ScoringResult } from './useScoring';
```

5. Return `saveStep` and update `isSaving` to be derived:
```typescript
return {
  // ...
  handleSaveEvaluation,
  isSaving: saveStep !== 'idle',
  saveStep,
  isSaved,
  saveError,
  // ...
};
```

6. The save button no longer requires `scoringResult` since save now generates its own score. Remove the guard `if (!scoringResult) return;` and instead check `if (!evaluationState?.category_type) return;`.

**Step 2: Update save button in EvaluationSections**

In `frontend/src/components/evaluation/EvaluationSections.tsx`:

1. Add `saveStep` to `SaveProps`:
```typescript
interface SaveProps {
  onSaveEvaluation: () => void;
  isSaving: boolean;
  saveStep?: 'idle' | 'recalculating' | 'scoring' | 'saving';
  isSaved: boolean;
  saveError: Error | null;
}
```

2. Update the save button loading label (lines 271-275):
```typescript
{isSaving ? (
  <>
    <Loader2 className="mr-2 size-4 animate-spin" aria-hidden="true" />
    {saveStep === 'recalculating'
      ? t('evaluationSections.stepRecalculating')
      : saveStep === 'scoring'
        ? t('evaluationSections.stepScoring')
        : t('evaluationSections.stepSaving')}
  </>
)
```

3. Update the disabled condition — no longer require `scoringResult`:
```typescript
disabled={isSaving || isSaved}
```

4. Remove the "generate first" hint (lines 288-292) since save now auto-generates. Replace with a hint about needing category type:
```typescript
{!categoryType && !isSaved && (
  <p className="mt-1 text-center text-sm text-muted-foreground">
    {t('scoring.selectCategory')}
  </p>
)}
```

Wait — we need `categoryType` in the save section. Add it to `SaveProps` or check if it's already available. It IS available in `EvaluationSectionsProps` since it extends `FormProps` which has `categoryType`. So in the button disable logic:
```typescript
disabled={!categoryType || isSaving || isSaved}
```

**Step 3: Run all tests**

```bash
cd frontend && npx vitest run
```

**Step 4: Commit**

```bash
git add frontend/src/hooks/useEvaluationOrchestrator.ts \
       frontend/src/components/evaluation/EvaluationSections.tsx
git commit -m "Chain recalculate → score → save into Simpan Evaluasi button"
```

---

### Task 4: Wire scoringStep and saveStep through EvaluationPage

**Files:**
- Modify: `frontend/src/pages/EvaluationPage.tsx`

**Step 1: Pass the new props from orchestrator to EvaluationSections**

Check `EvaluationPage.tsx` for where `EvaluationSections` is rendered. Pass `scoringStep` and `saveStep` from the orchestrator return values. The exact line references depend on the file, but the pattern is:

```typescript
const {
  // ... existing destructured values ...
  scoringStep,
  saveStep,
} = useEvaluationOrchestrator(brandId);
```

Then in the JSX:
```tsx
<EvaluationSections
  // ... existing props ...
  scoringStep={scoringStep}
  saveStep={saveStep}
/>
```

**Step 2: Run tests**

```bash
cd frontend && npx vitest run
```

**Step 3: Commit**

```bash
git add frontend/src/pages/EvaluationPage.tsx
git commit -m "Wire scoringStep and saveStep to EvaluationSections"
```

---

### Task 5: Final integration test and cleanup

**Step 1: Run full test suite**

```bash
cd frontend && npx vitest run
```

**Step 2: Run lint and type check**

```bash
cd frontend && npm run lint && npx tsc --noEmit
```

**Step 3: Fix any issues found**

**Step 4: Final commit if any fixes needed**

```bash
git add -A && git commit -m "Fix lint and type issues from chained evaluation flow"
```
