const LOCALE_MAP: Record<string, string> = {
  id: 'id-ID',
  en: 'en-US',
  th: 'th-TH',
};

/** Map an i18next language code to an Intl-compatible locale string. */
export function getIntlLocale(lang: string): string {
  return LOCALE_MAP[lang] ?? 'id-ID';
}
