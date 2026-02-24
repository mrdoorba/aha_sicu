import { useTranslation } from 'react-i18next';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../ui/select';

const VERDICT_OPTIONS = [
  { value: '✔️', labelKey: 'verdict.approved' },
  { value: '❌', labelKey: 'verdict.rejected' },
  { value: '❌ Non Mall', labelKey: 'verdict.nonMall' },
  { value: '❌ No Brand', labelKey: 'verdict.noBrand' },
  { value: '❌ Opex', labelKey: 'verdict.opexIssue' },
  { value: '⭕️', labelKey: 'verdict.special' },
];

interface VerdictSelectorProps {
  value: string;
  onChange: (value: string) => void;
}

export const VerdictSelector = ({ value, onChange }: VerdictSelectorProps) => {
  const { t } = useTranslation();

  return (
    <div className="space-y-1">
      <label className="text-sm font-medium" htmlFor="verdict-select">
        {t('verdict.label')}
      </label>
      <Select value={value} onValueChange={onChange}>
        <SelectTrigger id="verdict-select" className="w-48">
          <SelectValue placeholder={t('verdict.placeholder')} />
        </SelectTrigger>
        <SelectContent>
          {VERDICT_OPTIONS.map((opt) => (
            <SelectItem key={opt.value} value={opt.value}>
              {t(opt.labelKey)}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
};

export { VERDICT_OPTIONS };
