import { useParams, useNavigate } from 'react-router-dom';
import { Header } from '../components/layout/Header';
import { EvaluationHeader } from '../components/evaluation/EvaluationHeader';
import { SectionNav } from '../components/evaluation/SectionNav';
import { EvaluationSections } from '../components/evaluation/EvaluationSections';
import { useBrandDetail } from '../hooks/useBrandDetail';
import { useEvaluationState, useSaveEvaluationInputs, type CategoryType } from '../hooks/useEvaluation';
import { useAutoSaveForm } from '../hooks/useAutoSaveForm';
import { useState, useCallback, useMemo } from 'react';
import { Button } from '../components/ui/button';
import { ArrowLeft } from 'lucide-react';
import { computeSectionProgress } from '../components/evaluation/forms/formConfig';
import { useScoring } from '../hooks/useScoring';
import { ScorePanel } from '../components/evaluation/scoring';

export const EvaluationPage = () => {
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

  const {
    generateScore,
    scoringResult,
    isStale,
    isGenerating,
    error: scoringError,
  } = useScoring(safeBrandId);

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
    <div className="min-h-screen bg-muted">
      <Header />
      <main id="main-content" tabIndex={-1} className="mx-auto max-w-7xl py-6 px-4 sm:px-6 lg:px-8">
        {!isValidBrandId ? (
          <div className="space-y-3">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigate('/brands')}
            >
              <ArrowLeft className="mr-1 size-4" aria-hidden="true" />
              Back to Brands
            </Button>
            <p className="text-destructive">Invalid brand ID.</p>
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
                  onCategoryChange={handleCategoryChange}
                  onActiveSection={setActiveSection}
                  manualData={manualData}
                  onFieldChange={handleFieldChange}
                  onFieldBlur={triggerSave}
                  saveStatus={saveStatus}
                  lastSaved={lastSaved}
                  onRetrySave={retrySave}
                  storeName={brand?.store_name ?? ''}
                  brandName={brand?.name ?? ''}
                  onGenerateScore={generateScore}
                  scoringResult={scoringResult}
                  isGenerating={isGenerating}
                  isStale={isStale}
                  scoringError={scoringError}
                />
              </div>

              {/* Right panel: score summary */}
              <aside className="hidden w-56 shrink-0 lg:block">
                <ScorePanel scoringResult={scoringResult} />
              </aside>
            </div>
          </>
        )}
      </main>
    </div>
  );
};
