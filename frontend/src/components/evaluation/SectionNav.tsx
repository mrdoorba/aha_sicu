import { ClipboardList, BarChart3, Tag, Upload, Calculator, Check, Trophy } from 'lucide-react';
import type { ReactNode } from 'react';
import { useTranslation } from 'react-i18next';
import type { SectionProgress } from './forms/formConfig';

const SECTIONS: Array<{ id: string; labelKey: string; icon: ReactNode }> = [
  { id: 'section-1', labelKey: 'sectionNav.brandInfoOperational', icon: <ClipboardList className="size-4" aria-hidden="true" /> },
  { id: 'section-2', labelKey: 'sectionNav.businessVisitors', icon: <BarChart3 className="size-4" aria-hidden="true" /> },
  { id: 'section-3', labelKey: 'sectionNav.promoProducts', icon: <Tag className="size-4" aria-hidden="true" /> },
  { id: 'section-4', labelKey: 'sectionNav.fileUpload', icon: <Upload className="size-4" aria-hidden="true" /> },
  { id: 'section-5', labelKey: 'sectionNav.adsCompetition', icon: <Calculator className="size-4" aria-hidden="true" /> },
  { id: 'section-6', labelKey: 'sectionNav.finalScore', icon: <Trophy className="size-4" aria-hidden="true" /> },
];

interface SectionNavProps {
  activeSection: string;
  onSectionClick: (sectionId: string) => void;
  progress?: Record<string, SectionProgress>;
}

export const SectionNav = ({ activeSection, onSectionClick, progress }: SectionNavProps) => {
  const { t } = useTranslation();
  return (
    <nav className="sticky top-6" aria-label="Evaluation sections">
      <ul className="space-y-1">
        {SECTIONS.map((section, index) => {
          const isActive = activeSection === section.id;
          const sectionProgress = progress?.[section.id];
          const isComplete = sectionProgress && sectionProgress.filled === sectionProgress.total && sectionProgress.total > 0;

          return (
            <li key={section.id}>
              <button
                onClick={() => onSectionClick(section.id)}
                className={`flex w-full items-center gap-2 rounded-md px-3 py-2 text-left text-sm transition-colors ${
                  isActive
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                }`}
              >
                {section.icon}
                <span className="flex-1">
                  <span className="font-medium">Step {index + 1}.</span>{' '}
                  {t(section.labelKey)}
                </span>
                {sectionProgress && (
                  isComplete ? (
                    <Check className="size-4 shrink-0 text-green-600" aria-label="Complete" />
                  ) : (
                    <span
                      className={`shrink-0 text-xs tabular-nums ${
                        isActive ? 'text-primary-foreground/70' : 'text-muted-foreground'
                      }`}
                      aria-label={`${sectionProgress.filled} of ${sectionProgress.total} fields filled`}
                    >
                      {sectionProgress.filled}/{sectionProgress.total}
                    </span>
                  )
                )}
              </button>
            </li>
          );
        })}
      </ul>
    </nav>
  );
};

export { SECTIONS };
