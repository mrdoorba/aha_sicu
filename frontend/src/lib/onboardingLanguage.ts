import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { LANGUAGES, getIntlLocale } from './languages';

/**
 * Where the onboarding language picker remembers its choice.
 *
 * A brand picking a language on the public sign-up page has no account yet, so
 * there is no profile to write it to — unlike the authed `LanguageToggle`,
 * which persists through `updateLanguage()`. The key is namespaced so the two
 * never read each other's value.
 */
export const ONBOARDING_LANG_KEY = 'sicu.onboarding.lang';

/** The saved onboarding language, or null if there isn't a usable one. */
export function readOnboardingLanguage(): string | null {
  try {
    const saved = localStorage.getItem(ONBOARDING_LANG_KEY);
    return saved && LANGUAGES.some((l) => l.code === saved) ? saved : null;
  } catch {
    // Private browsing or blocked storage — fall back to the default language.
    return null;
  }
}

export function writeOnboardingLanguage(code: string): void {
  try {
    localStorage.setItem(ONBOARDING_LANG_KEY, code);
  } catch {
    // The picker still works for this session, it just won't be remembered.
    // Not worth interrupting the brand over.
  }
}

/**
 * Restore the picked language, and hand back the Intl locale that goes with it.
 *
 * Every onboarding surface calls this, not just the first: a brand who picks
 * English on the claim page and then reloads on step 4 would otherwise land
 * back in Indonesian, having already told us once.
 */
export function useOnboardingLanguage(): { language: string; intlLocale: string } {
  const { i18n } = useTranslation();

  useEffect(() => {
    const saved = readOnboardingLanguage();
    if (saved && saved !== i18n.language) void i18n.changeLanguage(saved);
  }, [i18n]);

  return { language: i18n.language, intlLocale: getIntlLocale(i18n.language) };
}
