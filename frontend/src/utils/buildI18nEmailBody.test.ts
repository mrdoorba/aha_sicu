import { describe, it, expect } from 'vitest';
import type { TFunction } from 'i18next';
import type { CategoryScore } from '../hooks/useScoring';
import type { ScoringConclusionData } from './buildI18nEmailBody';
import { buildI18nEmailBody, buildI18nEmailSubject } from './buildI18nEmailBody';

// ---------------------------------------------------------------------------
// Mock t() function — returns the key + serialised vars so assertions can
// verify both the key used and the variables passed.
// ---------------------------------------------------------------------------

function createMockT(): TFunction {
  return ((key: string, vars?: Record<string, string>) => {
    if (vars && Object.keys(vars).length > 0) {
      const pairs = Object.entries(vars)
        .map(([k, v]) => `${k}=${v}`)
        .join(',');
      return `[${key}|${pairs}]`;
    }
    return `[${key}]`;
  }) as unknown as TFunction;
}

// ---------------------------------------------------------------------------
// Factory helpers
// ---------------------------------------------------------------------------

function makeRow(
  row: number,
  message: string,
  messageI18n?: { key: string; vars: Record<string, string> },
) {
  return {
    row,
    metric: `metric-${row}`,
    value: 0,
    benchmark: '',
    verdict: 'pass',
    message,
    score: 1,
    ...(messageI18n ? { message_i18n: messageI18n } : {}),
  };
}

function makeCategory(
  category: string,
  rows: ReturnType<typeof makeRow>[],
): CategoryScore {
  return {
    category,
    score: rows.length,
    max_score: rows.length,
    rows,
    available: true,
  };
}

// ---------------------------------------------------------------------------
// buildI18nEmailSubject
// ---------------------------------------------------------------------------

describe('buildI18nEmailSubject', () => {
  it('returns translated subject with brandName and period', () => {
    const t = createMockT();
    const result = buildI18nEmailSubject('TestBrand', '2026-01', t);
    expect(result).toBe('[sendMailUtils.subject|brandName=TestBrand,period=2026-01]');
  });
});

// ---------------------------------------------------------------------------
// buildI18nEmailBody
// ---------------------------------------------------------------------------

describe('buildI18nEmailBody', () => {
  const t = createMockT();

  // ── Section ordering ─────────────────────────────────────────────

  it('produces sections in correct backend order', () => {
    const categories: CategoryScore[] = [
      makeCategory('Kompetisi TOP Produk', [makeRow(60, 'comp msg')]),
      makeCategory('Kesehatan Operasional Toko', [makeRow(1, 'op msg')]),
      makeCategory('Bisnis Analisis', [makeRow(13, 'biz 13'), makeRow(20, 'biz 20')]),
      makeCategory('Tinjauan Pengunjung', [makeRow(28, 'vis 28'), makeRow(29, 'vis 29')]),
      makeCategory('Promo Toko', [makeRow(31, 'promo 31')]),
      makeCategory('Jumlah Produk & Status Toko', [makeRow(44, 'prod msg')]),
      makeCategory('Data Iklan', [makeRow(50, 'ads 50')]),
      makeCategory('Partisipasi Campaign', [makeRow(57, 'camp 57')]),
    ];

    const body = buildI18nEmailBody(categories, null, t);
    const lines = body.split('\n');

    // Find the section header lines (emoji-prefixed)
    const headers = lines.filter(
      (l) => /^(📊|📈|👥|🏷️|📦|📣|🎯|🏆|📋|📌)/.test(l),
    );

    expect(headers).toEqual([
      '📊 [emailBody.section.operational]',
      '📈 [emailBody.section.business]',
      '👥 [emailBody.section.visitors]',
      '🏷️ [emailBody.section.promoTools]',
      '📦 [emailBody.section.productsStatus]',
      '📣 [emailBody.section.ads]',
      '🎯 [emailBody.section.campaign]',
      '🏆 [emailBody.section.competition]',
    ]);
  });

  // ── Row filtering ────────────────────────────────────────────────

  it('business section only includes rows 13 and 20', () => {
    const categories: CategoryScore[] = [
      makeCategory('Bisnis Analisis', [
        makeRow(10, 'excluded 10'),
        makeRow(13, 'biz 13'),
        makeRow(15, 'excluded 15'),
        makeRow(20, 'biz 20'),
        makeRow(25, 'excluded 25'),
      ]),
    ];

    const body = buildI18nEmailBody(categories, null, t);
    expect(body).toContain('biz 13');
    expect(body).toContain('biz 20');
    expect(body).not.toContain('excluded 10');
    expect(body).not.toContain('excluded 15');
    expect(body).not.toContain('excluded 25');
  });

  it('visitors section only includes rows 28 and 29', () => {
    const categories: CategoryScore[] = [
      makeCategory('Tinjauan Pengunjung', [
        makeRow(27, 'excluded'),
        makeRow(28, 'vis 28'),
        makeRow(29, 'vis 29'),
        makeRow(30, 'excluded 30'),
      ]),
    ];

    const body = buildI18nEmailBody(categories, null, t);
    expect(body).toContain('vis 28');
    expect(body).toContain('vis 29');
    expect(body).not.toContain('excluded');
  });

  it('ads section only includes rows 50, 51, 52, 53', () => {
    const categories: CategoryScore[] = [
      makeCategory('Data Iklan', [
        makeRow(49, 'excluded'),
        makeRow(50, 'ads 50'),
        makeRow(51, 'ads 51'),
        makeRow(52, 'ads 52'),
        makeRow(53, 'ads 53'),
        makeRow(54, 'excluded 54'),
      ]),
    ];

    const body = buildI18nEmailBody(categories, null, t);
    expect(body).toContain('ads 50');
    expect(body).toContain('ads 51');
    expect(body).toContain('ads 52');
    expect(body).toContain('ads 53');
    expect(body).not.toContain('excluded');
  });

  it('campaign section only includes row 57', () => {
    const categories: CategoryScore[] = [
      makeCategory('Partisipasi Campaign', [
        makeRow(56, 'excluded'),
        makeRow(57, 'camp 57'),
        makeRow(58, 'excluded 58'),
      ]),
    ];

    const body = buildI18nEmailBody(categories, null, t);
    expect(body).toContain('camp 57');
    expect(body).not.toContain('excluded');
  });

  it('promo section includes rows 31-41 and summary rows 42, 43', () => {
    const promoRows = [
      makeRow(30, 'excluded 30'),
      makeRow(31, 'promo 31'),
      makeRow(35, 'promo 35'),
      makeRow(41, 'promo 41'),
      makeRow(42, 'summary 42'),
      makeRow(43, 'summary 43'),
      makeRow(44, 'excluded 44'),
    ];

    const categories: CategoryScore[] = [
      makeCategory('Promo Toko', promoRows),
    ];

    const body = buildI18nEmailBody(categories, null, t);
    expect(body).toContain('promo 31');
    expect(body).toContain('promo 35');
    expect(body).toContain('promo 41');
    expect(body).toContain('summary 42');
    expect(body).toContain('summary 43');
    expect(body).not.toContain('excluded 30');
    expect(body).not.toContain('excluded 44');
  });

  it('operational and competition sections include all rows', () => {
    const categories: CategoryScore[] = [
      makeCategory('Kesehatan Operasional Toko', [
        makeRow(1, 'op 1'),
        makeRow(5, 'op 5'),
        makeRow(10, 'op 10'),
      ]),
      makeCategory('Kompetisi TOP Produk', [
        makeRow(58, 'comp 58'),
        makeRow(60, 'comp 60'),
      ]),
    ];

    const body = buildI18nEmailBody(categories, null, t);
    expect(body).toContain('op 1');
    expect(body).toContain('op 5');
    expect(body).toContain('op 10');
    expect(body).toContain('comp 58');
    expect(body).toContain('comp 60');
  });

  // ── i18n translation ─────────────────────────────────────────────

  it('uses translated messages when _i18n fields are present', () => {
    const categories: CategoryScore[] = [
      makeCategory('Kesehatan Operasional Toko', [
        makeRow(1, 'raw fallback', {
          key: 'scoring.opRow1',
          vars: { value: '95%' },
        }),
      ]),
    ];

    const body = buildI18nEmailBody(categories, null, t);
    // Should contain the mock-translated version, not the raw fallback
    expect(body).toContain('[scoring.opRow1|value=95%]');
    expect(body).not.toContain('raw fallback');
  });

  it('falls back to raw messages when _i18n fields are absent', () => {
    const categories: CategoryScore[] = [
      makeCategory('Kesehatan Operasional Toko', [
        makeRow(1, 'raw operational message'),
      ]),
    ];

    const body = buildI18nEmailBody(categories, null, t);
    expect(body).toContain('raw operational message');
  });

  // ── Conclusion section ───────────────────────────────────────────

  it('renders conclusion from conclusion_i18n when available', () => {
    const summary: ScoringConclusionData = {
      conclusion: 'raw conclusion',
      conclusion_i18n: [
        { key: 'conclusion.salesRange', vars: { min: '10', max: '50' } },
        { key: 'conclusion.operationalGood', vars: {} },
      ],
    };

    const body = buildI18nEmailBody([], summary, t);
    expect(body).toContain('📋 [emailBody.section.conclusion]');
    expect(body).toContain('[conclusion.salesRange|min=10,max=50]');
    expect(body).toContain('[conclusion.operationalGood]');
    expect(body).not.toContain('raw conclusion');
  });

  it('falls back to raw conclusion when conclusion_i18n is absent', () => {
    const summary: ScoringConclusionData = {
      conclusion: 'raw conclusion text',
    };

    const body = buildI18nEmailBody([], summary, t);
    expect(body).toContain('📋 [emailBody.section.conclusion]');
    expect(body).toContain('raw conclusion text');
  });

  // ── Marketing estimation ─────────────────────────────────────────

  it('renders marketing estimation from i18n when available', () => {
    const summary: ScoringConclusionData = {
      conclusion: '',
      marketing_estimation: 'raw estimation',
      marketing_estimation_i18n: {
        key: 'marketing.estimate',
        vars: { pct: '5%' },
      },
    };

    const body = buildI18nEmailBody([], summary, t);
    expect(body).toContain('📌 [emailBody.section.marketingEstimation]');
    expect(body).toContain('[marketing.estimate|pct=5%]');
    expect(body).not.toContain('raw estimation');
  });

  it('falls back to raw marketing estimation when i18n is absent', () => {
    const summary: ScoringConclusionData = {
      conclusion: '',
      marketing_estimation: 'raw estimation text',
    };

    const body = buildI18nEmailBody([], summary, t);
    expect(body).toContain('raw estimation text');
  });

  // ── Marketing budget ─────────────────────────────────────────────

  it('renders marketing budget from i18n when available', () => {
    const summary: ScoringConclusionData = {
      conclusion: '',
      marketing_budget: 'raw budget',
      marketing_budget_i18n: {
        key: 'marketing.budgetRecommendation',
        vars: { pct: '3%' },
      },
    };

    const body = buildI18nEmailBody([], summary, t);
    expect(body).toContain('[marketing.budgetRecommendation|pct=3%]');
    expect(body).not.toContain('raw budget');
  });

  // ── Closing message ──────────────────────────────────────────────

  it('renders closing message from i18n when available', () => {
    const summary: ScoringConclusionData = {
      conclusion: '',
      closing_message: 'raw closing',
      closing_message_i18n: {
        key: 'closing.potential',
        vars: { store_name: 'TestStore' },
      },
    };

    const body = buildI18nEmailBody([], summary, t);
    expect(body).toContain('[closing.potential|store_name=TestStore]');
    expect(body).not.toContain('raw closing');
  });

  // ── Null scoringSummary ──────────────────────────────────────────

  it('omits conclusion/marketing/closing sections when scoringSummary is null', () => {
    const categories: CategoryScore[] = [
      makeCategory('Kesehatan Operasional Toko', [makeRow(1, 'op msg')]),
    ];

    const body = buildI18nEmailBody(categories, null, t);
    expect(body).toContain('op msg');
    expect(body).not.toContain('📋');
    expect(body).not.toContain('📌');
    expect(body).not.toContain('conclusion');
    expect(body).not.toContain('marketing');
  });

  // ── Empty categories ─────────────────────────────────────────────

  it('returns empty string when no categories and no summary', () => {
    const body = buildI18nEmailBody([], null, t);
    expect(body).toBe('');
  });

  it('skips category sections with no matching rows', () => {
    // Data Iklan category exists but no rows match the filter [50,51,52,53]
    const categories: CategoryScore[] = [
      makeCategory('Data Iklan', [makeRow(48, 'wrong row')]),
    ];

    const body = buildI18nEmailBody(categories, null, t);
    expect(body).toBe('');
  });

  // ── Full integration ─────────────────────────────────────────────

  it('assembles full body with categories + summary in correct order', () => {
    const categories: CategoryScore[] = [
      makeCategory('Kesehatan Operasional Toko', [makeRow(1, 'op msg')]),
      makeCategory('Kompetisi TOP Produk', [makeRow(60, 'comp msg')]),
    ];
    const summary: ScoringConclusionData = {
      conclusion: 'final conclusion',
      marketing_estimation: 'estimate text',
      marketing_budget: 'budget text',
      closing_message: 'closing text',
    };

    const body = buildI18nEmailBody(categories, summary, t);
    const lines = body.split('\n');

    // Verify ordering: operational → competition → conclusion → marketing → budget → closing
    const opIdx = lines.findIndex((l) => l.includes('📊'));
    const compIdx = lines.findIndex((l) => l.includes('🏆'));
    const conclusionIdx = lines.findIndex((l) => l.includes('📋'));
    const marketingIdx = lines.findIndex((l) => l.includes('📌'));
    const budgetIdx = lines.findIndex((l) => l === 'budget text');
    const closingIdx = lines.findIndex((l) => l === 'closing text');

    expect(opIdx).toBeLessThan(compIdx);
    expect(compIdx).toBeLessThan(conclusionIdx);
    expect(conclusionIdx).toBeLessThan(marketingIdx);
    expect(marketingIdx).toBeLessThan(budgetIdx);
    expect(budgetIdx).toBeLessThan(closingIdx);
  });
});
