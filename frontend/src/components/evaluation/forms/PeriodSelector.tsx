import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { Card, CardContent } from '../../ui/card';
import { getIntlLocale } from '../../../lib/languages';

interface PeriodSelectorProps {
  value: string | null;
  onChange: (category: 'business', key: string, value: string | null) => void;
  onBlur: () => void;
}

// The data period anchors every sales-month label downstream, so it lives up in
// Step 1 beside store category — set the window before filling the numbers.
export function PeriodSelector({ value, onChange, onBlur }: PeriodSelectorProps) {
  const { t, i18n } = useTranslation();

  // Last 12 months from now
  const monthOptions = useMemo(() => {
    const options: Array<{ value: string; label: string }> = [];
    const now = new Date();
    for (let i = 0; i < 12; i++) {
      const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
      const val = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
      const label = d.toLocaleDateString(getIntlLocale(i18n.language), { month: 'short', year: 'numeric' });
      options.push({ value: val, label });
    }
    return options;
  }, [i18n.language]);

  return (
    <Card className="mb-4">
      <CardContent className="pt-4">
        <label htmlFor="salesStartMonth" className="mb-1 block text-sm font-medium">
          {t('forms.business.startMonth')}
        </label>
        <select
          id="salesStartMonth"
          className="rounded-md border border-input bg-background px-3 py-2 text-sm"
          value={value ?? ''}
          onChange={(e) => onChange('business', 'salesStartMonth', e.target.value || null)}
          onBlur={onBlur}
        >
          <option value="">{t('forms.business.selectMonth')}</option>
          {monthOptions.map((opt) => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
      </CardContent>
    </Card>
  );
}
