import { useState, useCallback, useMemo, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useBrandDetail } from './useBrandDetail';
import { useEvaluationState, useSaveEvaluationInputs, type CategoryType } from './useEvaluation';
import { useAutoSaveForm } from './useAutoSaveForm';
import { computeSectionProgress } from '../components/evaluation/forms/formConfig';
import { useScoring } from './useScoring';
import { useSaveEvaluation } from './useSaveEvaluation';
import { useCalculatorResults } from './useCalculator';
import { useRules } from './useRules';
import { toast } from 'sonner';

export function useEvaluationOrchestrator(brandId: number) {
  const { t } = useTranslation();

  // --- Data fetching ---
  const { data: brand, isLoading: brandLoading, isError: brandError } = useBrandDetail(brandId);
  const { data: evaluationState } = useEvaluationState(brandId);
  const saveMutation = useSaveEvaluationInputs(brandId);

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
  });

  // --- Derived data ---
  const sectionProgress = useMemo(() => computeSectionProgress(manualData), [manualData]);

  const storeLink = useMemo(() => {
    const raw = brand?.raw_data?.['Link Shopee'];
    if (typeof raw === 'string' && raw.startsWith('https://')) return raw;
    return null;
  }, [brand]);

  // --- Scoring ---
  const {
    generateScore,
    scoringResult,
    lastPeriod,
    isStale,
    isGenerating,
    error: scoringError,
  } = useScoring(brandId);

  // --- Calculator ---
  const { data: calculatorResultsData } = useCalculatorResults(brandId);

  // --- Rules ---
  const { rules: rulesData } = useRules();
  const activeRules = rulesData.length > 0 ? rulesData[0].rules : undefined;

  // --- Save evaluation ---
  const {
    saveEvaluation,
    isSaving,
    isSaved,
    error: saveError,
    reset: resetSave,
  } = useSaveEvaluation(brandId);

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
  const handleSaveEvaluation = useCallback(() => {
    if (!scoringResult) return;

    const calcResults: Record<string, unknown> = {};
    if (calculatorResultsData?.results) {
      for (const r of calculatorResultsData.results) {
        calcResults[r.calculator_type] = {
          details: r.details,
          output_text: r.output_text,
        };
      }
    }

    calcResults['scoring_summary'] = {
      conclusion: scoringResult.conclusion,
      conclusion_i18n: scoringResult.conclusion_i18n,
      marketing_estimation: scoringResult.marketing_estimation,
      marketing_budget: scoringResult.marketing_budget,
      marketing_budget_i18n: scoringResult.marketing_budget_i18n,
      closing_message: scoringResult.closing_message,
      closing_message_i18n: scoringResult.closing_message_i18n,
    };

    saveEvaluation(
      {
        template: scoringResult.template as 'fashion' | 'non_fashion',
        final_score: scoringResult.total_score,
        verdict: scoringResult.verdict,
        score_breakdown: scoringResult.category_scores as unknown as Array<Record<string, unknown>>,
        calculator_results: calcResults,
        manual_inputs: manualData as unknown as Record<string, unknown>,
        rule_version: scoringResult.rule_version,
        email_output: scoringResult.email_body || null,
        period: lastPeriod,
      },
      {
        onSuccess: () => {
          toast.success(t('evaluation.saved'));
        },
        onError: () => {
          toast.error(t('evaluation.saveFailed'));
        },
      },
    );
  }, [scoringResult, calculatorResultsData, manualData, saveEvaluation, t, lastPeriod]);

  const handleCategoryChange = useCallback(
    (value: string) => {
      saveMutation.mutate({
        category_type: value as CategoryType,
        manual_data: evaluationState?.manual_data ?? undefined,
      });
    },
    [saveMutation, evaluationState?.manual_data],
  );

  return {
    // Brand
    brand: brand ?? null,
    brandLoading,
    brandError,

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
    scoringError,

    // Save evaluation
    handleSaveEvaluation,
    isSaving,
    isSaved,
    saveError,

    // Derived brand fields
    storeName: brand?.brand_name ?? '',
    brandName: brand?.brand_name ?? '',
  };
}
