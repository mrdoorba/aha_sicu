import { useTranslation } from 'react-i18next';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../ui/select';
import { generatePeriodOptions } from './periodOptions';

interface PeriodSelectorProps {
  value: string;
  onChange: (value: string) => void;
}

export const PeriodSelector = ({ value, onChange }: PeriodSelectorProps) => {
  const { t } = useTranslation();
  const options = generatePeriodOptions();

  return (
    <div className="space-y-1">
      <label className="text-sm font-medium" htmlFor="period-select">
        {t('scoring.period')}
      </label>
      <Select value={value} onValueChange={onChange}>
        <SelectTrigger id="period-select" className="w-48">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {options.map((opt) => (
            <SelectItem key={opt} value={opt}>
              {opt}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
};
