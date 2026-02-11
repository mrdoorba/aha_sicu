import { useEffect, useRef } from 'react';
import { Card, CardContent } from '../ui/card';
import { RadioGroup, RadioGroupItem } from '../ui/radio-group';
import { Label } from '../ui/label';
import { Button } from '../ui/button';
import { Save, Check, Loader2 } from 'lucide-react';
import { FileUploadSection } from './FileUploadSection';
import { OperationalForm } from './forms/OperationalForm';
import { BusinessForm } from './forms/BusinessForm';
import { ContentForm } from './forms/ContentForm';
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
import type { ScoringResult } from '../../hooks/useScoring';

interface EvaluationSectionsProps {
  brandId: number;
  categoryType: string | null;
  onCategoryChange: (value: string) => void;
  onActiveSection: (sectionId: string) => void;
  manualData: ManualData;
  onFieldChange: (category: string, key: string, value: number | string | null) => void;
  onFieldBlur: () => void;
  saveStatus: SaveStatus;
  lastSaved: Date | null;
  onRetrySave: () => void;
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
  onSaveEvaluation: () => void;
  isSaving: boolean;
  isSaved: boolean;
  saveError: Error | null;
  onResetSave: () => void;
}

export const EvaluationSections = ({
  brandId,
  categoryType,
  onCategoryChange,
  onActiveSection,
  manualData,
  onFieldChange,
  onFieldBlur,
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
  onSaveEvaluation,
  isSaving,
  isSaved,
  saveError,
  onResetSave,
}: EvaluationSectionsProps) => {
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

  return (
    <div className="space-y-8">
      {/* Save status indicator */}
      <div className="flex justify-end">
        <SaveIndicator status={saveStatus} lastSaved={lastSaved} onRetry={onRetrySave} />
      </div>

      {/* Section 1: Brand Info & Operational */}
      <section id="section-1" ref={setSectionRef('section-1')}>
        <h3 className="mb-4 text-lg font-semibold text-foreground">
          Step 1. Brand Info &amp; Operational
        </h3>

        {/* Fashion/Non-Fashion Selector */}
        <Card className="mb-4">
          <CardContent className="pt-4">
            <p className="mb-3 text-sm font-medium">Category Type</p>
            <RadioGroup
              value={categoryType ?? ''}
              onValueChange={onCategoryChange}
              className="flex gap-6"
            >
              <div className="flex items-center gap-2">
                <RadioGroupItem value="fashion" id="cat-fashion" />
                <Label htmlFor="cat-fashion">Fashion</Label>
              </div>
              <div className="flex items-center gap-2">
                <RadioGroupItem value="non_fashion" id="cat-non-fashion" />
                <Label htmlFor="cat-non-fashion">Non-Fashion</Label>
              </div>
            </RadioGroup>
          </CardContent>
        </Card>

        <OperationalForm
          data={manualData.operational}
          onChange={onFieldChange}
          onBlur={onFieldBlur}
        />
      </section>

      {/* Section 2: Business, Content & Visitors */}
      <section id="section-2" ref={setSectionRef('section-2')}>
        <h3 className="mb-4 text-lg font-semibold text-foreground">
          Step 2. Business, Content &amp; Visitors
        </h3>
        <BusinessForm
          data={manualData.business}
          categoryType={categoryType}
          onChange={onFieldChange}
          onBlur={onFieldBlur}
        />
        <ContentForm
          data={manualData.content}
          onChange={onFieldChange}
          onBlur={onFieldBlur}
        />
        <VisitorsForm
          data={manualData.visitors}
          onChange={onFieldChange}
          onBlur={onFieldBlur}
        />
      </section>

      {/* Section 3: Promo Tools & Products/Status */}
      <section id="section-3" ref={setSectionRef('section-3')}>
        <h3 className="mb-4 text-lg font-semibold text-foreground">
          Step 3. Promo Tools &amp; Products/Status
        </h3>
        <PromoToolsForm
          data={manualData.promoTools}
          onChange={onFieldChange}
          onBlur={onFieldBlur}
        />
        <ProductsStatusForm
          data={manualData.products}
          onChange={onFieldChange}
          onBlur={onFieldBlur}
        />
      </section>

      {/* Section 4: File Upload */}
      <section id="section-4" ref={setSectionRef('section-4')}>
        <h3 className="mb-4 text-lg font-semibold text-foreground">
          Step 4. File Upload
        </h3>
        <FileUploadSection brandId={brandId} />
      </section>

      {/* Section 5: Ads, Campaign, Competition & Review */}
      <section id="section-5" ref={setSectionRef('section-5')}>
        <h3 className="mb-4 text-lg font-semibold text-foreground">
          Step 5. Ads, Campaign, Competition &amp; Review
        </h3>
        <AdsForm
          data={manualData.ads}
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
            Step 6. Final Score
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
          />
        </section>

        {/* Save Button */}
        <div className="mt-6">
          <Button
            className="w-full"
            disabled={!scoringResult || isSaving || isSaved}
            onClick={onSaveEvaluation}
          >
            {isSaving ? (
              <>
                <Loader2 className="mr-2 size-4 animate-spin" aria-hidden="true" />
                Saving...
              </>
            ) : isSaved ? (
              <>
                <Check className="mr-2 size-4" aria-hidden="true" />
                Saved ✓
              </>
            ) : (
              <>
                <Save className="mr-2 size-4" aria-hidden="true" />
                Save Evaluation
              </>
            )}
          </Button>
          {!scoringResult && !isSaved && (
            <p className="mt-1 text-center text-sm text-muted-foreground">
              Generate a score first to save
            </p>
          )}
          {saveError && (
            <p className="mt-1 text-center text-sm text-destructive">
              Failed to save evaluation. Please try again.
            </p>
          )}
        </div>
      </section>
    </div>
  );
};
