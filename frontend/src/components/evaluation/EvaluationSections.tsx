import { useEffect, useRef } from 'react';
import { Calculator } from 'lucide-react';
import { Card, CardContent } from '../ui/card';
import { RadioGroup, RadioGroupItem } from '../ui/radio-group';
import { Label } from '../ui/label';
import { Button } from '../ui/button';
import { FileUploadSection } from './FileUploadSection';

interface EvaluationSectionsProps {
  brandId: number;
  categoryType: string | null;
  onCategoryChange: (value: string) => void;
  onActiveSection: (sectionId: string) => void;
}

const CALCULATOR_CARDS = [
  { name: 'Ads Keyword Calculator', description: 'Requires CPC Ad Report + Keyword Placement Report' },
  { name: 'Top SKU Calculator', description: 'Requires Order Export + Mass Update' },
  { name: 'Discount Check Calculator', description: 'Requires Order Export' },
];

export const EvaluationSections = ({
  brandId,
  categoryType,
  onCategoryChange,
  onActiveSection,
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

        <SectionPlaceholder title="Operational" fieldCount={5} />
      </section>

      {/* Section 2: Business, Content & Visitors */}
      <section id="section-2" ref={setSectionRef('section-2')}>
        <h3 className="mb-4 text-lg font-semibold text-foreground">
          Step 2. Business, Content &amp; Visitors
        </h3>
        <SectionPlaceholder title="Business" fieldCount={8} />
        <SectionPlaceholder title="Content" fieldCount={2} />
        <SectionPlaceholder title="Visitors" fieldCount={4} />
      </section>

      {/* Section 3: Promo Tools & Products/Status */}
      <section id="section-3" ref={setSectionRef('section-3')}>
        <h3 className="mb-4 text-lg font-semibold text-foreground">
          Step 3. Promo Tools &amp; Products/Status
        </h3>
        <SectionPlaceholder title="Promo Tools" fieldCount={11} />
        <SectionPlaceholder title="Products/Status" fieldCount={2} />
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
        <SectionPlaceholder title="Ads" fieldCount={5} />
        <SectionPlaceholder title="Campaign" fieldCount={3} />
        <SectionPlaceholder title="Competition" fieldCount={3} subtitle="products" />

        {/* Calculator Results */}
        <div className="mt-4">
          <p className="mb-3 text-sm font-semibold uppercase text-muted-foreground">
            Calculator Results
          </p>
          <div className="grid gap-4 sm:grid-cols-3">
            {CALCULATOR_CARDS.map((calc) => (
              <Card key={calc.name}>
                <CardContent className="flex items-start gap-3 pt-4">
                  <Calculator className="mt-0.5 size-5 text-muted-foreground" aria-hidden="true" />
                  <div>
                    <p className="font-medium">{calc.name}</p>
                    <p className="text-xs text-muted-foreground">{calc.description}</p>
                    <p className="mt-2 text-sm text-amber-600">
                      Pending: upload required files
                    </p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Final Score */}
        <div className="mt-4">
          <Card>
            <CardContent className="pt-4">
              <p className="mb-2 font-semibold">Final Score</p>
              <p className="text-sm text-muted-foreground">Not yet calculated</p>
              <div className="mt-3 space-y-1 text-sm text-muted-foreground">
                {['Operational', 'Business', 'Content', 'Visitors', 'Promo Tools', 'Products/Status', 'Ads', 'Campaign', 'Stock', 'Discount'].map(
                  (category) => (
                    <div key={category} className="flex justify-between">
                      <span>{category}</span>
                      <span>&mdash;</span>
                    </div>
                  ),
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Save Button */}
        <div className="mt-6">
          <Button disabled className="w-full">
            Save Evaluation
          </Button>
        </div>
      </section>
    </div>
  );
};

function SectionPlaceholder({
  title,
  fieldCount,
  subtitle = 'fields',
}: {
  title: string;
  fieldCount: number;
  subtitle?: string;
}) {
  return (
    <Card className="mb-4">
      <CardContent className="pt-4">
        <p className="text-sm font-medium text-muted-foreground">
          {title} &mdash; {fieldCount} {subtitle}
        </p>
        <div className="mt-2 rounded border border-dashed border-muted-foreground/25 p-4 text-center text-sm text-muted-foreground">
          Form fields will be added in Story 3.3
        </div>
      </CardContent>
    </Card>
  );
}
