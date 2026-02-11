import { useParams, useNavigate } from 'react-router-dom';
import { Header } from '../components/layout/Header';
import { EvaluationHeader } from '../components/evaluation/EvaluationHeader';
import { SectionNav } from '../components/evaluation/SectionNav';
import { EvaluationSections } from '../components/evaluation/EvaluationSections';
import { useBrandDetail } from '../hooks/useBrandDetail';
import { useEvaluationState, useSaveEvaluationInputs, type CategoryType } from '../hooks/useEvaluation';
import { useState, useCallback } from 'react';
import { Button } from '../components/ui/button';
import { ArrowLeft } from 'lucide-react';

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
                />
              </aside>

              {/* Main content: scrollable sections */}
              <div className="min-w-0 flex-1">
                <EvaluationSections
                  categoryType={evaluationState?.category_type ?? null}
                  onCategoryChange={handleCategoryChange}
                  onActiveSection={setActiveSection}
                />
              </div>

              {/* Right panel: score summary placeholder */}
              <aside className="hidden w-56 shrink-0 lg:block">
                <div className="sticky top-6 rounded-lg border bg-card p-4">
                  <h3 className="mb-3 text-sm font-semibold uppercase text-muted-foreground">
                    Score Summary
                  </h3>
                  <div className="space-y-2 text-sm text-muted-foreground">
                    <div className="flex justify-between">
                      <span>Final</span>
                      <span>&mdash;</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Operational</span>
                      <span>&mdash;</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Business</span>
                      <span>&mdash;</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Content</span>
                      <span>&mdash;</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Visitors</span>
                      <span>&mdash;</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Promo Tools</span>
                      <span>&mdash;</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Products</span>
                      <span>&mdash;</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Ads</span>
                      <span>&mdash;</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Campaign</span>
                      <span>&mdash;</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Stock</span>
                      <span>&mdash;</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Discount</span>
                      <span>&mdash;</span>
                    </div>
                  </div>
                </div>
              </aside>
            </div>
          </>
        )}
      </main>
    </div>
  );
};
