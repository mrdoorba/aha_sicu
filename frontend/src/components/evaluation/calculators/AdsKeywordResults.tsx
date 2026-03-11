import { useTranslation } from 'react-i18next';
import type { CalculatorResult, AdsKeywordDetails, TranslatableI18n, AdListI18n } from '../../../hooks/useCalculator';
import { renderTranslatable } from '../../../utils/renderTranslatable';

interface AdsKeywordResultsProps {
  result: CalculatorResult;
}

function renderAdList(
  fallbackText: string,
  i18n: AdListI18n | null | undefined,
  t: (key: string, vars?: Record<string, string>) => string,
): string {
  if (!i18n) return fallbackText;

  const header = t(i18n.header.key, i18n.header.vars);
  const ads = i18n.ads.map((ad) => t(ad.key, ad.vars)).join('\n');
  return `${header}\n${ads}`;
}

function renderFlagList(
  fallbackText: string,
  i18n: TranslatableI18n[] | null | undefined,
  t: (key: string, vars?: Record<string, string>) => string,
): string {
  if (!i18n) return fallbackText;
  return i18n.map((flag) => t(flag.key, flag.vars)).join('\n');
}

export function AdsKeywordResults({ result }: AdsKeywordResultsProps) {
  const { t } = useTranslation();
  const d = result.details as AdsKeywordDetails;

  const sections: string[] = [];

  // Sheet 1
  sections.push(renderTranslatable(d.ak2, d.ak2_i18n, t));
  sections.push(renderTranslatable(d.ak3, d.ak3_i18n, t));

  const ak4Text = renderFlagList(d.ak4, d.ak4_i18n, t);
  if (ak4Text) sections.push(ak4Text);

  // Sheet 2
  const al2Text = renderAdList(d.al2, d.al2_i18n, t);
  if (al2Text) sections.push(al2Text);

  const al3Text = renderTranslatable(d.al3, d.al3_i18n, t);
  if (al3Text) sections.push(al3Text);

  const al5Text = renderAdList(d.al5, d.al5_i18n, t);
  if (al5Text) sections.push(al5Text);

  // Bottom flags
  for (const key of ['al6', 'al7', 'al8', 'al9'] as const) {
    const i18nKey = `${key}_i18n` as keyof AdsKeywordDetails;
    const text = renderTranslatable(d[key], d[i18nKey] as TranslatableI18n | null | undefined, t);
    if (text) sections.push(text);
  }

  return (
    <div>
      <div className="mb-2 flex items-center justify-between">
        <h4 className="text-sm font-semibold">Ads Keyword Calculator</h4>
        <time className="text-xs text-muted-foreground">
          {new Date(result.calculated_at).toLocaleString('id-ID')}
        </time>
      </div>
      <pre
        role="presentation"
        className="whitespace-pre-wrap break-words rounded-md bg-muted p-3 text-sm leading-relaxed"
      >
        {sections.filter(Boolean).join('\n\n')}
      </pre>
    </div>
  );
}
