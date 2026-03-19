import { useState, useCallback, useMemo, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useQueryClient } from '@tanstack/react-query';
import { useBrandDetail } from './useBrandDetail';
import { useEvaluationState, useSaveEvaluationInputs, type CategoryType } from './useEvaluation';
import { useAutoSaveForm } from './useAutoSaveForm';
import { computeSectionProgress } from '../components/evaluation/forms/formConfig';
import { useScoring } from './useScoring';
import type { ScoringResult, ScoringRequest, CategoryScore } from './useScoring';
import { useSaveEvaluation } from './useSaveEvaluation';
import { useCalculatorResults, useRunAllCalculators } from './useCalculator';
import type { CalculatorResultsListResponse } from './useCalculator';
import { useRules } from './useRules';
import { toast } from 'sonner';
import { generatePeriodOptions } from '../components/evaluation/scoring/periodOptions';
import { toRecord } from '../lib/typeGuards';

function isCategoryType(value: string): value is CategoryType {
  return value === 'fashion' || value === 'non_fashion';
}

/** Convert CategoryScore[] to the untyped array the save API expects. */
function categoryScoresToRecords(scores: CategoryScore[]): Array<Record<string, unknown>> {
  return scores.map((score) => toRecord(score));
}

export type SaveStep = 'idle' | 'recalculating' | 'scoring' | 'saving';

export function useEvaluationOrchestrator(brandId: number) {
  const { t } = useTranslation();

  // --- Data fetching ---
  const { data: brand, isLoading: brandLoading, isError: brandError } = useBrandDetail(brandId);
  const { data: evaluationState } = useEvaluationState(brandId);
  const saveMutation = useSaveEvaluationInputs(brandId);

  // --- Marketplace state ---
  const [marketplace, setMarketplace] = useState<string>('ID');
  const currency = marketplace === 'TH' ? 'THB' : 'IDR';

  // --- Section navigation ---
  const [activeSection, setActiveSection] = useState('section-1');

  // --- Auto-save form ---
  const {
    manualData,
    handleFieldChange,
    triggerSave,
    retrySave,
    saveStatus,
    lastSaved,
  } = useAutoSaveForm({
    brandId,
    categoryType: evaluationState?.category_type ?? null,
    initialData: evaluationState?.manual_data ?? null,
    marketplace,
  });

  // --- Derived data ---
  const sectionProgress = useMemo(() => computeSectionProgress(manualData), [manualData]);

  const storeLink = useMemo(() => {
    const raw = brand?.raw_data?.['Link Shopee'];
    if (typeof raw === 'string' && raw.startsWith('https://')) return raw;
    return null;
  }, [brand]);

  // --- Calculator ---
  useCalculatorResults(brandId);
  const runAllMutation = useRunAllCalculators(brandId);

  const recalculateAll = useCallback(async () => {
    await runAllMutation.mutateAsync();
  }, [runAllMutation]);

  // --- Scoring ---
  const {
    generateScore,
    scoringResult,
    lastPeriod,
    isStale,
    isGenerating,
    scoringStep,
    error: scoringError,
  } = useScoring(brandId, recalculateAll);

  // --- Rules ---
  const { rules: rulesData } = useRules(marketplace);
  const activeRules = rulesData.length > 0 ? rulesData[0].rules : undefined;

  // --- Save evaluation ---
  const queryClient = useQueryClient();
  const {
    saveEvaluation,
    isSaved,
    error: saveError,
    reset: resetSave,
  } = useSaveEvaluation(brandId);
  const [saveStep, setSaveStep] = useState<SaveStep>('idle');

  // Reset save state when evaluation data changes after a successful save
  // This re-enables the save button for multi-save workflow (AC #2)
  useEffect(() => {
    if (isSaved) {
      resetSave();
    }
    // Only trigger on data changes, not on isSaved/resetSave changes
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [manualData, scoringResult]);

  // --- Handlers ---
  const handleSaveEvaluation = useCallback(async () => {
    const rawCategory = evaluationState?.category_type;
    if (!rawCategory || !isCategoryType(rawCategory)) return;
    // Capture the narrowed value so it stays typed inside the async closure
    const validatedCategory: CategoryType = rawCategory;

    try {
      // Step 1: Recalculate all
      setSaveStep('recalculating');
      await runAllMutation.mutateAsync();

      // Step 2: Score
      setSaveStep('scoring');
      const scoringRequest: ScoringRequest = {
        template: validatedCategory,
        verdict: scoringResult?.verdict ?? '✔️',
        store_name: brand?.brand_name ?? '',
        period: lastPeriod || generatePeriodOptions()[0],
        brand_name: brand?.brand_name ?? '',
      };

      const scoreResponse = await new Promise<ScoringResult>((resolve, reject) => {
        generateScore(scoringRequest, {
          onSuccess: (data) => resolve(data as ScoringResult),
          onError: (err: Error) => reject(err),
        });
      });

      // Step 3: Save — use freshly fetched calculator results
      setSaveStep('saving');

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

      // scoreResponse.template is string from API — narrow it safely
      const saveTemplate: CategoryType = isCategoryType(scoreResponse.template)
        ? scoreResponse.template
        : validatedCategory; // fallback to the already-validated category

      await new Promise<void>((resolve, reject) => {
        saveEvaluation(
          {
            template: saveTemplate,
            final_score: scoreResponse.total_score,
            verdict: scoreResponse.verdict,
            score_breakdown: categoryScoresToRecords(scoreResponse.category_scores),
            calculator_results: calcResults,
            manual_inputs: toRecord(manualData),
            rule_version: scoreResponse.rule_version,
            email_output: scoreResponse.email_body || null,
            period: lastPeriod || generatePeriodOptions()[0],
            marketplace,
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
    manualData, t, marketplace,
  ]);

  const handleCategoryChange = useCallback(
    (value: string) => {
      if (!isCategoryType(value)) return;
      saveMutation.mutate({
        category_type: value,
        manual_data: evaluationState?.manual_data ?? undefined,
        marketplace,
      });
    },
    [saveMutation, evaluationState?.manual_data, marketplace],
  );

  return {
    // Brand
    brand: brand ?? null,
    brandLoading,
    brandError,

    // Marketplace
    marketplace,
    setMarketplace,
    currency,

    // Section nav
    activeSection,
    setActiveSection,
    sectionProgress,

    // Form state
    categoryType: evaluationState?.category_type ?? null,
    manualData,
    handleFieldChange,
    triggerSave,
    retrySave,
    saveStatus,
    lastSaved,
    storeLink,

    // Rules
    activeRules,

    // Category
    handleCategoryChange,

    // Scoring
    generateScore,
    scoringResult,
    isGenerating,
    isStale,
    scoringStep,
    scoringError,

    // Save evaluation
    handleSaveEvaluation,
    isSaving: saveStep !== 'idle',
    saveStep,
    isSaved,
    saveError,

    // Derived brand fields
    storeName: brand?.brand_name ?? '',
    brandName: brand?.brand_name ?? '',
  };
}
