import type { TFunction } from 'i18next';
import type { CategoryScore } from '../hooks/useScoring';
import type { TranslatableI18n, AdListI18n } from '../hooks/useCalculator';
import type { TranslatableText } from './renderTranslatable';
import { renderTranslatable, renderAdList, renderFlagList } from './renderTranslatable';
import { isRecord } from '../lib/typeGuards';

/**
 * Scoring summary data shape used for the conclusion, marketing, and closing
 * sections of the email body. Mirrors the backend ScoringResult fields that
 * are relevant to email assembly.
 */
export interface ScoringConclusionData {
  conclusion: string;
  conclusion_i18n?: TranslatableText[];
  marketing_estimation?: string;
  marketing_estimation_i18n?: TranslatableText;
  marketing_percentage?: string;
  marketing_budget?: string;
  marketing_budget_i18n?: TranslatableText;
  closing_message?: string;
  closing_message_i18n?: TranslatableText;
}

/**
 * Build a translated email subject line.
 *
 * Uses the provided `t` function (typically `i18n.getFixedT(lang)`) so
 * the subject renders in the email language, independent of the UI language.
 */
export function buildI18nEmailSubject(
  brandName: string,
  period: string,
  t: TFunction,
): string {
  return t('sendMailUtils.subject', { brandName, period });
}

// ---------------------------------------------------------------------------
// Internal constants — must match backend _assemble_email_body ordering
// ---------------------------------------------------------------------------

/** Promo tool rows in the backend start at row 31 and span 11 tools (31-41). */
const PROMO_START_ROW = 31;
const PROMO_TOOL_COUNT = 11; // 11 promo tools → rows 31..41
const PROMO_SUMMARY_ROWS = [42, 43];

/**
 * Section definitions in exact backend order.
 * Each entry specifies the backend category name, the emoji prefix,
 * the i18n section header key, and an optional row filter.
 *
 * When `rows` is undefined every row in the category is included.
 * When `rows` is an array only those row numbers are included.
 * When `promoRange` is true the special promo logic applies (31-41 + 42,43).
 */
interface SectionDef {
  category: string;
  emoji: string;
  sectionKey: string;
  rows?: number[];
  promoRange?: boolean;
}

const SECTION_DEFS: SectionDef[] = [
  {
    category: 'Kesehatan Operasional Toko',
    emoji: '📊',
    sectionKey: 'emailBody.section.operational',
  },
  {
    category: 'Bisnis Analisis',
    emoji: '📈',
    sectionKey: 'emailBody.section.business',
    rows: [13, 20],
  },
  {
    category: 'Tinjauan Pengunjung',
    emoji: '👥',
    sectionKey: 'emailBody.section.visitors',
    rows: [28, 29],
  },
  {
    category: 'Promo Toko',
    emoji: '🏷️',
    sectionKey: 'emailBody.section.promoTools',
    promoRange: true,
  },
  {
    category: 'Jumlah Produk & Status Toko',
    emoji: '📦',
    sectionKey: 'emailBody.section.productsStatus',
  },
  {
    category: 'Data Iklan',
    emoji: '📣',
    sectionKey: 'emailBody.section.ads',
    rows: [50, 51, 52, 53],
  },
  {
    category: 'Partisipasi Campaign',
    emoji: '🎯',
    sectionKey: 'emailBody.section.campaign',
    rows: [57],
  },
  {
    category: 'Kompetisi TOP Produk',
    emoji: '🏆',
    sectionKey: 'emailBody.section.competition',
  },
];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function getCategoryByName(
  categories: CategoryScore[],
  name: string,
): CategoryScore | undefined {
  return categories.find((c) => c.category === name);
}

/**
 * Resolve a translated section header.
 * Uses CATEGORY_MAP to find the i18n label key, falling back to the raw
 * backend Indonesian name when no mapping exists.
 */
function translateSectionHeader(
  sectionKey: string,
  _backendName: string,
  t: TFunction,
): string {
  return t(sectionKey);
}

/**
 * Extract messages from a category, optionally filtering by row numbers.
 * Each message is rendered via `renderTranslatable` so i18n fields are used
 * when available, with raw message as fallback.
 *
 * Row 53 is special: it contains the full ads keyword output text from the
 * backend with no message_i18n. When calculatorResults are provided, we
 * build translated text from the ads_keyword details i18n fields instead.
 */
function getMessages(
  cat: CategoryScore,
  t: TFunction,
  rowFilter?: number[],
  calculatorResults?: Record<string, unknown>,
): string[] {
  const msgs: string[] = [];
  for (const r of cat.rows) {
    if (rowFilter && !rowFilter.includes(r.row)) continue;
    // Row 53: ads keyword output — use calculator details i18n if available
    if (r.row === 53 && !r.message_i18n && calculatorResults) {
      const translated = buildAdsKeywordI18nText(calculatorResults, t);
      if (translated) {
        msgs.push(translated);
        continue;
      }
    }
    const text = renderTranslatable(r.message, r.message_i18n, t);
    if (!text) continue;
    // Append product link for competition rows when i18n rendering drops it
    const link = r.message_i18n?.vars.link;
    msgs.push(link ? `${text}\n↪${link}` : text);
  }
  return msgs;
}

/**
 * Special promo extraction: rows PROMO_START_ROW..PROMO_START_ROW+10 (31-41)
 * plus summary rows 42, 43.
 */
function getPromoMessages(cat: CategoryScore, t: TFunction): string[] {
  const msgs: string[] = [];

  // Promo tool rows (31-41)
  for (const r of cat.rows) {
    if (
      r.row >= PROMO_START_ROW &&
      r.row <= PROMO_START_ROW + PROMO_TOOL_COUNT - 1
    ) {
      const text = renderTranslatable(r.message, r.message_i18n, t);
      if (text) msgs.push(text);
    }
  }

  // Summary rows (42, 43)
  for (const r of cat.rows) {
    if (PROMO_SUMMARY_ROWS.includes(r.row)) {
      const text = renderTranslatable(r.message, r.message_i18n, t);
      if (text) msgs.push(text);
    }
  }

  return msgs;
}

// ---------------------------------------------------------------------------
// Ads keyword i18n rendering for email row 53
// ---------------------------------------------------------------------------

/**
 * Build translated ads keyword analysis text from calculator details i18n fields.
 * Mirrors AdsKeywordSection rendering in EvaluationDetailPage.
 * Returns empty string if i18n fields are not available.
 */
function buildAdsKeywordI18nText(
  calculatorResults: Record<string, unknown>,
  t: TFunction,
): string {
  const akResult = isRecord(calculatorResults.ads_keyword)
    ? calculatorResults.ads_keyword
    : undefined;
  if (!akResult) return '';

  const details = isRecord(akResult.details) ? akResult.details : undefined;
  if (!details?.ak2_i18n) return '';

  const parts: string[] = [];
  parts.push(renderTranslatable('', details.ak2_i18n as TranslatableI18n | null, t));
  parts.push(renderTranslatable('', details.ak3_i18n as TranslatableI18n | null, t));
  if (details.ak4_i18n != null) {
    parts.push(renderFlagList('', details.ak4_i18n as TranslatableI18n[] | null, t));
  }
  parts.push(renderAdList('', details.al2_i18n as AdListI18n | null, t));
  parts.push(renderTranslatable('', details.al3_i18n as TranslatableI18n | null, t));
  parts.push(renderAdList('', details.al5_i18n as AdListI18n | null, t));
  for (const key of ['al6_i18n', 'al7_i18n', 'al8_i18n', 'al9_i18n']) {
    if (details[key] != null) {
      parts.push(renderTranslatable('', details[key] as TranslatableI18n | null, t));
    }
  }

  return parts.filter(Boolean).join('\n\n');
}

/**
 * Translate the fake discount line embedded in marketing estimation text.
 * The backend hardcodes "📌 Berpotensi menggunakan 'fake discount'" into g68.
 * We detect and replace it with the translated version.
 */
const FAKE_DISCOUNT_PATTERN = /📌\s*Berpotensi menggunakan 'fake discount'/;

function translateMarketingEstimation(
  raw: string,
  t: TFunction,
): string {
  if (!FAKE_DISCOUNT_PATTERN.test(raw)) return raw;
  return raw.replace(
    FAKE_DISCOUNT_PATTERN,
    t('discount.output.fakeDiscount'),
  );
}

// ---------------------------------------------------------------------------
// Main email body builder
// ---------------------------------------------------------------------------

/**
 * Build the full email body text from category scores and scoring summary.
 *
 * Mirrors the backend `_assemble_email_body` function in
 * `backend/app/calculators/scoring/computations.py`.
 *
 * The `t` parameter should be a fixed-language TFunction obtained via
 * `i18n.getFixedT(selectedLanguage)` so the email body renders in the
 * chosen email language independently of the UI language.
 */
export function buildI18nEmailBody(
  categoryScores: CategoryScore[],
  scoringSummary: ScoringConclusionData | null,
  t: TFunction,
  calculatorResults?: Record<string, unknown>,
): string {
  const sections: string[] = [];

  // ── Category sections (1-8) ──────────────────────────────────────
  for (const def of SECTION_DEFS) {
    const cat = getCategoryByName(categoryScores, def.category);
    if (!cat) continue;

    let msgs: string[];
    if (def.promoRange) {
      msgs = getPromoMessages(cat, t);
    } else {
      msgs = getMessages(cat, t, def.rows, calculatorResults);
    }

    if (msgs.length === 0) continue;

    const header = translateSectionHeader(def.sectionKey, def.category, t);
    sections.push(`${def.emoji} ${header}`);
    sections.push(...msgs);
    sections.push('');
  }

  // ── Conclusion & summary sections (9-12) ─────────────────────────
  if (scoringSummary) {
    // 9. Conclusion
    const conclusionText = renderConclusionI18n(scoringSummary, t);
    if (conclusionText) {
      sections.push(`📋 ${t('emailBody.section.conclusion')}`);
      sections.push(conclusionText);
      sections.push('');
    }

    // 10. Marketing estimation (translate embedded fake discount line)
    const rawMarketing = scoringSummary.marketing_estimation
      ? translateMarketingEstimation(scoringSummary.marketing_estimation, t)
      : undefined;
    const marketingText = renderFieldI18n(
      rawMarketing,
      scoringSummary.marketing_estimation_i18n,
      t,
    );
    if (marketingText) {
      sections.push(`📌 ${t('emailBody.section.marketingEstimation')}`);
      sections.push(marketingText);
      sections.push('');
    }

    // 11. Marketing budget
    const budgetText = renderFieldI18n(
      scoringSummary.marketing_budget,
      scoringSummary.marketing_budget_i18n,
      t,
    );
    if (budgetText) {
      sections.push(budgetText);
      sections.push('');
    }

    // 12. Closing message
    const closingText = renderFieldI18n(
      scoringSummary.closing_message,
      scoringSummary.closing_message_i18n,
      t,
    );
    if (closingText) {
      sections.push(closingText);
    }
  }

  return sections.join('\n');
}

// ---------------------------------------------------------------------------
// Conclusion rendering
// ---------------------------------------------------------------------------

/**
 * Render the conclusion from an array of TranslatableText (one per paragraph)
 * or fall back to the raw conclusion string.
 */
function renderConclusionI18n(
  summary: ScoringConclusionData,
  t: TFunction,
): string {
  if (summary.conclusion_i18n && summary.conclusion_i18n.length > 0) {
    return summary.conclusion_i18n
      .map((item) => `- ${t(item.key, item.vars)}`)
      .join('\n');
  }
  return summary.conclusion || '';
}

/**
 * Render a single TranslatableText field with raw fallback.
 */
function renderFieldI18n(
  raw: string | undefined,
  i18n: TranslatableText | undefined,
  t: TFunction,
): string {
  if (i18n) {
    return t(i18n.key, i18n.vars);
  }
  return raw || '';
}
