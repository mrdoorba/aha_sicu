import type { TFunction } from 'i18next';
import type { TranslatableI18n, AdListI18n } from '../hooks/useCalculator';

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

export function renderAdList(
  fallbackText: string,
  i18n: AdListI18n | null | undefined,
  t: TFunction,
): string {
  if (!i18n) return fallbackText;
  const header = t(i18n.header.key, i18n.header.vars);
  const ads = i18n.ads.map((ad) => t(ad.key, ad.vars)).join('\n');
  return `${header}\n${ads}`;
}

export function renderFlagList(
  fallbackText: string,
  i18n: TranslatableI18n[] | null | undefined,
  t: TFunction,
): string {
  if (!i18n) return fallbackText;
  // A retired flag key still lives in evaluations stored before it was
  // removed; i18next returns the key itself on a miss, so drop those lines
  // rather than show a raw key.
  return i18n
    .map((flag) => t(flag.key, flag.vars))
    .filter((line, i) => line !== i18n[i].key)
    .join('\n');
}
