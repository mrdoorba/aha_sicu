import { useParams } from 'react-router-dom';
import { Header } from '../components/layout/Header';
import { EvaluationHeader } from '../components/evaluation/EvaluationHeader';
import { SectionNav } from '../components/evaluation/SectionNav';
import { EvaluationSections } from '../components/evaluation/EvaluationSections';
import { useBrandDetail } from '../hooks/useBrandDetail';
import { useEvaluationState, useSaveEvaluationInputs } from '../hooks/useEvaluation';
import { useState, useCallback } from 'react';

export const EvaluationPage = () => {
  const { brandId } = useParams<{ brandId: string }>();
  const numericBrandId = Number(brandId) || 0;

  const { data: brand, isLoading: brandLoading, isError: brandError } = useBrandDetail(numericBrandId);
  const { data: evaluationState } = useEvaluationState(numericBrandId);
  const saveMutation = useSaveEvaluationInputs(numericBrandId);

  const [activeSection, setActiveSection] = useState('section-1');

  const handleCategoryChange = useCallback(
    (value: string) => {
      saveMutation.mutate({
        category_type: value,
        manual_data: evaluationState?.manual_data ?? undefined,
      });
    },
    [saveMutation, evaluationState?.manual_data],
  );

  return (
    <div className="min-h-screen bg-muted">
      <Header />
      <main id="main-content" tabIndex={-1} className="mx-auto max-w-7xl py-6 px-4 sm:px-6 lg:px-8">
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
      </main>
    </div>
  );
};
