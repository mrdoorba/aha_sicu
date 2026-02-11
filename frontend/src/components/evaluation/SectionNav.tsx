import { ClipboardList, BarChart3, Tag, Upload, Calculator } from 'lucide-react';
import type { ReactNode } from 'react';

const SECTIONS: Array<{ id: string; label: string; icon: ReactNode }> = [
  { id: 'section-1', label: 'Brand Info & Operational', icon: <ClipboardList className="size-4" aria-hidden="true" /> },
  { id: 'section-2', label: 'Business, Content & Visitors', icon: <BarChart3 className="size-4" aria-hidden="true" /> },
  { id: 'section-3', label: 'Promo Tools & Products/Status', icon: <Tag className="size-4" aria-hidden="true" /> },
  { id: 'section-4', label: 'File Upload', icon: <Upload className="size-4" aria-hidden="true" /> },
  { id: 'section-5', label: 'Ads, Campaign, Competition, Stock, Discount & Review', icon: <Calculator className="size-4" aria-hidden="true" /> },
];

interface SectionNavProps {
  activeSection: string;
  onSectionClick: (sectionId: string) => void;
}

export const SectionNav = ({ activeSection, onSectionClick }: SectionNavProps) => {
  return (
    <nav className="sticky top-6" aria-label="Evaluation sections">
      <ul className="space-y-1">
        {SECTIONS.map((section, index) => {
          const isActive = activeSection === section.id;
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
                <span>
                  <span className="font-medium">Step {index + 1}.</span>{' '}
                  {section.label}
                </span>
              </button>
            </li>
          );
        })}
      </ul>
    </nav>
  );
};

export { SECTIONS };
