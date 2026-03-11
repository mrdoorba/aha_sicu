import type { TFunction } from 'i18next';

export interface TranslatableText {
  key: string;
  vars: Record<string, string>;
}

/**
 * Render a backend field with i18n support.
 * If i18n data exists, use t() for translation. Otherwise, fall back to raw text.
 */
export function renderTranslatable(
  fallbackText: string,
  i18n: TranslatableText | null | undefined,
  t: TFunction,
): string {
  if (i18n) {
    return t(i18n.key, i18n.vars);
  }
  return fallbackText;
}
