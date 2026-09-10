import { useParams, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { EvaluationHeader } from '../components/evaluation/EvaluationHeader';
import { SectionNav } from '../components/evaluation/SectionNav';
import { EvaluationSections } from '../components/evaluation/EvaluationSections';
import { Button } from '../components/ui/button';
import { ArrowLeft } from 'lucide-react';
import { ScorePanel } from '../components/evaluation/scoring';
import { useEvaluationOrchestrator } from '../hooks/useEvaluationOrchestrator';

export const EvaluationPage = () => {
  const { t } = useTranslation();
  const { brandId } = useParams<{ brandId: string }>();
  const navigate = useNavigate();
  const numericBrandId = Number(brandId);
  const isValidBrandId = Number.isInteger(numericBrandId) && numericBrandId > 0;

  const safeBrandId = isValidBrandId ? numericBrandId : 0;

  const {
    brand,
    brandLoading,
    brandError,
    activeSection,
    setActiveSection,
    sectionProgress,
    categoryType,
    manualData,
    handleFieldChange,
    triggerSave,
    retrySave,
    saveStatus,
    lastSaved,
    storeLink,
    activeRules,
    handleCategoryChange,
    generateScore,
    scoringResult,
    isGenerating,
    isStale,
    scoringStep,
    scoringError,
    calculatorResults,
    handleSaveEvaluation,
    isSaving,
    saveStep,
    isSaved,
    saveError,
    storeName,
    brandName,
    marketplace,
    setMarketplace,
    currency,
  } = useEvaluationOrchestrator(safeBrandId);

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
              brand={brand}
              isLoading={brandLoading}
              isError={brandError}
              marketplace={marketplace}
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
                  categoryType={categoryType}
                  rules={activeRules}
                  marketplace={marketplace}
                  currency={currency}
                  onMarketplaceChange={setMarketplace}
                  onCategoryChange={handleCategoryChange}
                  onActiveSection={setActiveSection}
                  manualData={manualData}
                  onFieldChange={handleFieldChange}
                  onFieldBlur={triggerSave}
                  storeLink={storeLink}
                  saveStatus={saveStatus}
                  lastSaved={lastSaved}
                  onRetrySave={retrySave}
                  storeName={storeName}
                  brandName={brandName}
                  onGenerateScore={generateScore}
                  scoringResult={scoringResult}
                  isGenerating={isGenerating}
                  isStale={isStale}
                  scoringError={scoringError}
                  scoringStep={scoringStep}
                  calculatorResults={calculatorResults}
                  onSaveEvaluation={handleSaveEvaluation}
                  isSaving={isSaving}
                  saveStep={saveStep}
                  isSaved={isSaved}
                  saveError={saveError}
                />
              </div>

              {/* Right panel: score summary */}
              <aside className="hidden w-56 shrink-0 lg:block">
                <ScorePanel scoringResult={scoringResult} packageFit={brand?.package_fit} />
              </aside>
            </div>
          </>
        )}
      </div>
    </div>
  );
};
