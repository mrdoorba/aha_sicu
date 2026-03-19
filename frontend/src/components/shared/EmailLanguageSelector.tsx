import { useTranslation } from 'react-i18next';
import { LANGUAGES } from '../../lib/languages';
import { cn } from '../../lib/utils';

interface EmailLanguageSelectorProps {
  value: string;
  onChange: (lang: string) => void;
  className?: string;
}

export const EmailLanguageSelector = ({
  value,
  onChange,
  className,
}: EmailLanguageSelectorProps) => {
  const { t } = useTranslation();

  return (
    <div className={cn('flex items-center gap-2', className)}>
      <label
        htmlFor="email-language-select"
        className="text-sm font-medium text-muted-foreground whitespace-nowrap"
      >
        {t('emailLanguageSelector.label')}
      </label>
      <select
        id="email-language-select"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="h-8 rounded-md border border-input bg-background px-2 py-1 text-sm shadow-xs focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
        data-testid="email-language-select"
      >
        {LANGUAGES.map((lang) => (
          <option key={lang.code} value={lang.code}>
            {lang.flag} {lang.label}
          </option>
        ))}
      </select>
    </div>
  );
};
