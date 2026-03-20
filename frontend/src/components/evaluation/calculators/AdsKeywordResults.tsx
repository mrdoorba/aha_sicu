import { useTranslation } from 'react-i18next';
import type { CalculatorResult, AdsKeywordDetails, TranslatableI18n } from '../../../hooks/useCalculator';
import { renderTranslatable, renderAdList, renderFlagList } from '../../../utils/renderTranslatable';
import { isAdsKeywordDetails } from '../../../lib/calculatorGuards';
import { getIntlLocale } from '../../../lib/languages';

interface AdsKeywordResultsProps {
  result: CalculatorResult;
}

export function AdsKeywordResults({ result }: AdsKeywordResultsProps) {
  const { t, i18n } = useTranslation();
  if (!isAdsKeywordDetails(result.details)) {
    return <p className="text-sm text-muted-foreground">Invalid ads keyword data</p>;
  }
  const d = result.details;

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
        <h4 className="text-sm font-semibold">{t('adsKeyword.title')}</h4>
        <time className="text-xs text-muted-foreground">
          {new Date(result.calculated_at).toLocaleString(getIntlLocale(i18n.language))}
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
