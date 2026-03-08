import { useParams, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { EvaluationHeader } from '../components/evaluation/EvaluationHeader';
import { SectionNav } from '../components/evaluation/SectionNav';
import { EvaluationSections } from '../components/evaluation/EvaluationSections';
import { useBrandDetail } from '../hooks/useBrandDetail';
import { useEvaluationState, useSaveEvaluationInputs, type CategoryType } from '../hooks/useEvaluation';
import { useAutoSaveForm } from '../hooks/useAutoSaveForm';
import { useState, useCallback, useMemo, useEffect } from 'react';
import { Button } from '../components/ui/button';
import { ArrowLeft } from 'lucide-react';
import { computeSectionProgress } from '../components/evaluation/forms/formConfig';
import { useScoring } from '../hooks/useScoring';
import { ScorePanel } from '../components/evaluation/scoring';
import { useSaveEvaluation } from '../hooks/useSaveEvaluation';
import { useCalculatorResults } from '../hooks/useCalculator';
import { useRules } from '../hooks/useRules';
import { toast } from 'sonner';

export const EvaluationPage = () => {
  const { t } = useTranslation();
  const { brandId } = useParams<{ brandId: string }>();
  const navigate = useNavigate();
  const numericBrandId = Number(brandId);
  const isValidBrandId = Number.isInteger(numericBrandId) && numericBrandId > 0;

  const safeBrandId = isValidBrandId ? numericBrandId : 0;
  const { data: brand, isLoading: brandLoading, isError: brandError } = useBrandDetail(safeBrandId);
  const { data: evaluationState } = useEvaluationState(safeBrandId);
  const saveMutation = useSaveEvaluationInputs(safeBrandId);

  const [activeSection, setActiveSection] = useState('section-1');

  const {
    manualData,
    handleFieldChange,
    triggerSave,
    retrySave,
    saveStatus,
    lastSaved,
  } = useAutoSaveForm({
    brandId: safeBrandId,
    categoryType: evaluationState?.category_type ?? null,
    initialData: evaluationState?.manual_data ?? null,
  });

  const sectionProgress = useMemo(() => computeSectionProgress(manualData), [manualData]);

  const storeLink = useMemo(() => {
    const raw = brand?.raw_data?.['Link Shopee'];
    if (typeof raw === 'string' && raw.startsWith('https://')) return raw;
    return null;
  }, [brand]);

  const {
    generateScore,
    scoringResult,
    lastPeriod,
    isStale,
    isGenerating,
    error: scoringError,
  } = useScoring(safeBrandId);

  const { data: calculatorResultsData } = useCalculatorResults(safeBrandId);

  const { rules: rulesData } = useRules();
  const activeRules = rulesData.length > 0 ? rulesData[0].rules : undefined;

  const {
    saveEvaluation,
    isSaving,
    isSaved,
    error: saveError,
    reset: resetSave,
  } = useSaveEvaluation(safeBrandId);

  // Reset save state when evaluation data changes after a successful save
  // This re-enables the save button for multi-save workflow (AC #2)
  useEffect(() => {
    if (isSaved) {
      resetSave();
    }
    // Only trigger on data changes, not on isSaved/resetSave changes
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [manualData, scoringResult]);

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

  return (
    <div className="p-8">
      <div className="mx-auto max-w-7xl">
        {!isValidBrandId ? (
          <div className="space-y-3">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigate('/brands')}
            >
              <ArrowLeft className="mr-1 size-4" aria-hidden="true" />
              {t('common.backToBrands')}
            </Button>
            <p className="text-destructive">{t('evaluation.invalidBrandId')}</p>
          </div>
        ) : (
          <>
            <EvaluationHeader
              brand={brand ?? null}
              isLoading={brandLoading}
              isError={brandError}
            />

            <div className="mt-6 flex gap-6">
              {/* Left sidebar: section navigation */}
              <aside className="w-52 shrink-0">
                <SectionNav
                  activeSection={activeSection}
                  onSectionClick={(sectionId) => {
                    document.getElementById(sectionId)?.scrollIntoView({ behavior: 'smooth' });
                  }}
                  progress={sectionProgress}
                />
              </aside>

              {/* Main content: scrollable sections */}
              <div className="min-w-0 flex-1">
                <EvaluationSections
                  brandId={safeBrandId}
                  categoryType={evaluationState?.category_type ?? null}
                  rules={activeRules}
                  onCategoryChange={handleCategoryChange}
                  onActiveSection={setActiveSection}
                  manualData={manualData}
                  onFieldChange={handleFieldChange}
                  onFieldBlur={triggerSave}
                  storeLink={storeLink}
                  saveStatus={saveStatus}
                  lastSaved={lastSaved}
                  onRetrySave={retrySave}
                  storeName={brand?.brand_name ?? ''}
                  brandName={brand?.name ?? ''}
                  onGenerateScore={generateScore}
                  scoringResult={scoringResult}
                  isGenerating={isGenerating}
                  isStale={isStale}
                  scoringError={scoringError}
                  onSaveEvaluation={handleSaveEvaluation}
                  isSaving={isSaving}
                  isSaved={isSaved}
                  saveError={saveError}
                />
              </div>

              {/* Right panel: score summary */}
              <aside className="hidden w-56 shrink-0 lg:block">
                <ScorePanel scoringResult={scoringResult} />
              </aside>
            </div>
          </>
        )}
      </div>
    </div>
  );
};
