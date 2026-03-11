import { useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { Card, CardContent } from '../ui/card';
import { RadioGroup, RadioGroupItem } from '../ui/radio-group';
import { Label } from '../ui/label';
import { Button } from '../ui/button';
import { Save, Check, Loader2 } from 'lucide-react';
import { FileDownloadSection } from './FileDownloadSection';
import { FileUploadSection } from './FileUploadSection';
import { OperationalForm } from './forms/OperationalForm';
import { BusinessForm } from './forms/BusinessForm';
import { VisitorsForm } from './forms/VisitorsForm';
import { PromoToolsForm } from './forms/PromoToolsForm';
import { ProductsStatusForm } from './forms/ProductsStatusForm';
import { AdsForm } from './forms/AdsForm';
import { CampaignForm } from './forms/CampaignForm';
import { CompetitionForm } from './forms/CompetitionForm';
import { SaveIndicator } from './forms/SaveIndicator';
import { CalculatorResultsSection } from './calculators';
import { ScoringSection } from './scoring';
import type { ManualData } from './forms/formConfig';
import type { SaveStatus } from '../../hooks/useAutoSaveForm';
import type { ScoringResult, ScoringStep } from '../../hooks/useScoring';
import type { ScoringRules } from '../../hooks/useRules';
import { useBrandUploads } from '../../hooks/useUpload';

interface FormProps {
  brandId: number;
  categoryType: string | null;
  rules?: ScoringRules;
  onCategoryChange: (value: string) => void;
  onActiveSection: (sectionId: string) => void;
  manualData: ManualData;
  onFieldChange: (category: string, key: string, value: number | string | null) => void;
  onFieldBlur: () => void;
  storeLink: string | null;
}

interface ScoringProps {
  storeName: string;
  brandName: string;
  onGenerateScore: (request: {
    template: 'fashion' | 'non_fashion';
    verdict: string;
    store_name: string;
    period: string;
    brand_name: string;
  }) => void;
  scoringResult: ScoringResult | null;
  isGenerating: boolean;
  isStale: boolean;
  scoringError: Error | null;
  scoringStep?: ScoringStep;
}

interface SaveProps {
  onSaveEvaluation: () => void;
  isSaving: boolean;
  saveStep?: 'idle' | 'recalculating' | 'scoring' | 'saving';
  isSaved: boolean;
  saveError: Error | null;
}

interface StatusProps {
  saveStatus: SaveStatus;
  lastSaved: Date | null;
  onRetrySave: () => void;
}

interface EvaluationSectionsProps extends FormProps, ScoringProps, SaveProps, StatusProps {}

export const EvaluationSections = ({
  brandId,
  categoryType,
  rules,
  onCategoryChange,
  onActiveSection,
  manualData,
  onFieldChange,
  onFieldBlur,
  storeLink,
  saveStatus,
  lastSaved,
  onRetrySave,
  storeName,
  brandName,
  onGenerateScore,
  scoringResult,
  isGenerating,
  isStale,
  scoringError,
  scoringStep,
  onSaveEvaluation,
  isSaving,
  saveStep,
  isSaved,
  saveError,
}: EvaluationSectionsProps) => {
  const { t } = useTranslation();
  const { data: brandUploadsData } = useBrandUploads(brandId);
  const sectionRefs = useRef<Map<string, HTMLElement>>(new Map());

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            onActiveSection(entry.target.id);
          }
        });
      },
      { rootMargin: '-20% 0px -80% 0px' },
    );

    sectionRefs.current.forEach((el) => observer.observe(el));

    return () => observer.disconnect();
  }, [onActiveSection]);

  const setSectionRef = (id: string) => (el: HTMLElement | null) => {
    if (el) {
      sectionRefs.current.set(id, el);
    } else {
      sectionRefs.current.delete(id);
    }
  };

  const salesMonth0 = manualData.business?.salesMonth0 ?? 0;

  return (
    <div className="space-y-8">
      {/* Save status indicator */}
      <div className="flex justify-end">
        <SaveIndicator status={saveStatus} lastSaved={lastSaved} onRetry={onRetrySave} />
      </div>

      {/* Section 1: Brand Info & Operational */}
      <section id="section-1" ref={setSectionRef('section-1')}>
        <h3 className="mb-4 text-lg font-semibold text-foreground">
          {t('evaluationSections.step1')}
        </h3>

        {/* Fashion/Non-Fashion Selector */}
        <Card className="mb-4">
          <CardContent className="pt-4">
            <p className="mb-3 text-sm font-medium">{t('evaluationSections.categoryLabel')}</p>
            <RadioGroup
              value={categoryType ?? ''}
              onValueChange={onCategoryChange}
              className="flex gap-6"
            >
              <div className="flex items-center gap-2">
                <RadioGroupItem value="fashion" id="cat-fashion" />
                <Label htmlFor="cat-fashion">{t('evaluationSections.fashion')}</Label>
              </div>
              <div className="flex items-center gap-2">
                <RadioGroupItem value="non_fashion" id="cat-non-fashion" />
                <Label htmlFor="cat-non-fashion">{t('evaluationSections.nonFashion')}</Label>
              </div>
            </RadioGroup>
          </CardContent>
        </Card>

        <OperationalForm
          data={manualData.operational}
          rules={rules}
          onChange={onFieldChange}
          onBlur={onFieldBlur}
        />
      </section>

      {/* Section 2: Bisnis Analisis & Tinjauan Pengunjung */}
      <section id="section-2" ref={setSectionRef('section-2')}>
        <h3 className="mb-4 text-lg font-semibold text-foreground">
          {t('evaluationSections.step2')}
        </h3>
        <BusinessForm
          data={manualData.business}
          rules={rules}
          onChange={onFieldChange}
          onBlur={onFieldBlur}
        />
        <VisitorsForm
          data={manualData.visitors}
          storeLink={storeLink}
          rules={rules}
          onChange={onFieldChange}
          onBlur={onFieldBlur}
        />
      </section>

      {/* Section 3: Promo Tools & Products/Status */}
      <section id="section-3" ref={setSectionRef('section-3')}>
        <h3 className="mb-4 text-lg font-semibold text-foreground">
          {t('evaluationSections.step3')}
        </h3>
        <PromoToolsForm
          data={manualData.promoTools}
          salesMonth0={salesMonth0}
          onChange={onFieldChange}
          onBlur={onFieldBlur}
        />
        <ProductsStatusForm
          data={manualData.products}
          storeLink={storeLink}
          rules={rules}
          onChange={onFieldChange}
          onBlur={onFieldBlur}
        />
      </section>

      {/* Section 4: File Upload */}
      <section id="section-4" ref={setSectionRef('section-4')}>
        <h3 className="mb-4 text-lg font-semibold text-foreground">
          {t('evaluationSections.step4')}
        </h3>
        <FileUploadSection brandId={brandId} />

        {/* Section 4b: File Downloads */}
        <FileDownloadSection
          brandId={brandId}
          uploads={brandUploadsData?.uploads ?? []}
        />
      </section>

      {/* Section 5: Data Iklan, Campaign, Kompetisi & Review */}
      <section id="section-5" ref={setSectionRef('section-5')}>
        <h3 className="mb-4 text-lg font-semibold text-foreground">
          {t('evaluationSections.step5')}
        </h3>
        <AdsForm
          data={manualData.ads}
          salesMonth0={salesMonth0}
          onChange={onFieldChange}
          onBlur={onFieldBlur}
        />
        <CampaignForm
          data={manualData.campaign}
          onChange={onFieldChange}
          onBlur={onFieldBlur}
        />
        <CompetitionForm
          data={manualData.competition}
          onChange={onFieldChange}
          onBlur={onFieldBlur}
        />

        {/* Calculator Results */}
        <CalculatorResultsSection brandId={brandId} />

        {/* Final Score */}
        <section id="section-6" ref={setSectionRef('section-6')} className="mt-4">
          <h3 className="mb-4 text-lg font-semibold text-foreground">
            {t('evaluationSections.step6')}
          </h3>
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
        </section>

        {/* Save Button */}
        <div className="mt-6">
          <Button
            className="w-full"
            disabled={!categoryType || isSaving || isSaved}
            onClick={onSaveEvaluation}
          >
            {isSaving ? (
              <>
                <Loader2 className="mr-2 size-4 animate-spin" aria-hidden="true" />
                {saveStep === 'recalculating'
                  ? t('evaluationSections.stepRecalculating')
                  : saveStep === 'scoring'
                    ? t('evaluationSections.stepScoring')
                    : t('evaluationSections.stepSaving')}
              </>
            ) : isSaved ? (
              <>
                <Check className="mr-2 size-4" aria-hidden="true" />
                {t('evaluationSections.saved')}
              </>
            ) : (
              <>
                <Save className="mr-2 size-4" aria-hidden="true" />
                {t('evaluationSections.saveEvaluation')}
              </>
            )}
          </Button>
          {!categoryType && !isSaved && (
            <p className="mt-1 text-center text-sm text-muted-foreground">
              {t('scoring.selectCategory')}
            </p>
          )}
          {saveError && (
            <p className="mt-1 text-center text-sm text-destructive">
              {t('evaluationSections.saveFailed')}
            </p>
          )}
        </div>
      </section>
    </div>
  );
};
