import { useTranslation } from 'react-i18next';
import { LANGUAGES, type LanguageCode } from '../../lib/languages';
import { writeOnboardingLanguage } from '../../lib/onboardingLanguage';
import { cn } from '../../lib/utils';

/**
 * ID / EN / TH for the onboarding flow.
 *
 * Deliberately not `components/layout/LanguageToggle`: that one persists the
 * choice through `updateLanguage()`, an authenticated API call. A brand
 * choosing a language on the public sign-up page has no account yet, so the
 * choice lives in localStorage until there is a profile to write it to.
 */
export const LanguagePicker = ({ className }: { className?: string }) => {
  const { t, i18n } = useTranslation();

  const select = (code: LanguageCode) => {
    void i18n.changeLanguage(code);
    writeOnboardingLanguage(code);
  };

  return (
    <div
      className={cn(
        'inline-flex items-center gap-0.5 rounded-full bg-secondary p-0.5',
        className,
      )}
      role="group"
      aria-label={t('onboarding.language.label')}
    >
      {LANGUAGES.map((lang) => {
        const active = i18n.language === lang.code;
        return (
          <button
            key={lang.code}
            type="button"
            onClick={() => select(lang.code)}
            aria-pressed={active}
            className={cn(
              'rounded-full px-2.5 py-1 text-xs font-bold transition-colors',
              active
                ? 'bg-card text-foreground shadow-sm'
                : 'text-muted-foreground hover:text-foreground',
            )}
          >
            <span aria-hidden="true">{lang.flag}</span> {lang.label}
          </button>
        );
      })}
    </div>
  );
};
