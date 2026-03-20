export const LANGUAGES = [
  { code: 'id' as const, flag: '🇮🇩', label: 'ID', intlLocale: 'id-ID' },
  { code: 'en' as const, flag: '🇬🇧', label: 'EN', intlLocale: 'en-US' },
  { code: 'th' as const, flag: '🇹🇭', label: 'TH', intlLocale: 'th-TH' },
];

export type LanguageCode = (typeof LANGUAGES)[number]['code'];

/** Map an i18next language code to an Intl-compatible locale string. */
export function getIntlLocale(lang: string): string {
  return LANGUAGES.find((l) => l.code === lang)?.intlLocale ?? 'id-ID';
}
