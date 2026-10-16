import { describe, expect, it } from 'vitest';
import i18n from '../i18n';
import {
  REPORT_CLOSING,
  REPORT_CONCLUSIONS,
  REPORT_GROUPS,
  REPORT_MARKETING_BUDGET,
  REPORT_SCORE,
  splitClosing,
} from './sicuReport';

const LANGUAGES = ['id', 'en', 'th'];
const allMetrics = REPORT_GROUPS.flatMap((g) => g.metrics);

function judged() {
  return allMetrics.filter((m) => m.status !== 'info');
}

/** Every key the page will ask for, so one sweep can prove they all resolve. */
function everyKey(): string[] {
  return [
    REPORT_SCORE.verdictKey,
    REPORT_CLOSING.key,
    REPORT_CLOSING.ctaKey,
    REPORT_CLOSING.signoffKey,
    REPORT_MARKETING_BUDGET.labelKey,
    REPORT_MARKETING_BUDGET.bodyKey,
    ...REPORT_GROUPS.flatMap((g) => [
      g.titleKey,
      ...(g.note ? [g.note.titleKey, g.note.bodyKey] : []),
    ]),
    ...allMetrics.flatMap((m) => [m.labelKey, ...(m.verdictKey ? [m.verdictKey] : [])]),
    ...REPORT_CONCLUSIONS.map((c) => c.key),
  ];
}

describe('the report mirrors the SICU email', () => {
  it('keeps the email’s section order', () => {
    expect(REPORT_GROUPS.map((g) => g.titleKey)).toEqual([
      'email.category.operational',
      'email.category.business',
      'email.category.visitors',
      'email.category.promo',
      'email.category.products',
      'email.category.ads',
      'email.category.campaign',
      'email.category.competition',
      'email.category.stock',
    ]);
  });

  it('carries the same 21 judged metrics the email prints', () => {
    expect(judged()).toHaveLength(21);
  });

  it('gives every judged metric both a benchmark and a verdict', () => {
    // A verdict without its benchmark is an assertion the brand can't check.
    for (const m of judged()) {
      expect(m.benchmark, `${m.labelKey} benchmark`).toBeTruthy();
      expect(m.verdictKey, `${m.labelKey} verdict`).toBeTruthy();
    }
  });

  it('gives info metrics neither, so they never read as a pass', () => {
    for (const m of allMetrics.filter((m) => m.status === 'info')) {
      expect(m.benchmark, `${m.labelKey} benchmark`).toBeUndefined();
      expect(m.verdictKey, `${m.labelKey} verdict`).toBeUndefined();
    }
  });

  it('keeps the headline score and AHA Compatibility as separate numbers', () => {
    // The email prints both. Collapsing them would misreport one or the other:
    // the headline is the brand's health, compatibility is AHA's own read.
    expect(REPORT_SCORE.value).not.toBe(REPORT_SCORE.compatibility);
    for (const n of [REPORT_SCORE.value, REPORT_SCORE.compatibility]) {
      expect(n).toBeGreaterThanOrEqual(0);
      expect(n).toBeLessThanOrEqual(100);
    }
  });

  it('runs competition rows full width, since they carry a product name', () => {
    const competition = REPORT_GROUPS.find((g) => g.titleKey === 'email.category.competition')!;
    expect(competition.metrics.every((m) => m.wide && m.link)).toBe(true);
    // Nothing else is full width.
    const others = REPORT_GROUPS.filter(
      (g) => g.titleKey !== 'email.category.competition',
    ).flatMap((g) => g.metrics);
    expect(others.some((m) => m.wide)).toBe(false);
  });

  it('attaches the REAL BENCHMARK aside to Bisnis only', () => {
    const withNotes = REPORT_GROUPS.filter((g) => g.note);
    expect(withNotes.map((g) => g.titleKey)).toEqual(['email.category.business']);
    expect(withNotes[0].note?.titleKey).toBe('presentation.salesTrend.realBenchmark.label');
  });
});

describe('the report reads in all three languages', () => {
  it('resolves every key it asks for, in every language', () => {
    // A missing key falls back to the key itself, which would print
    // 'scoring.adsROI.pass' on the brand's result page. The email and this page
    // read the same locale files, so a key deleted on the backend's side shows
    // up here too — which is the point of sharing them.
    for (const lang of LANGUAGES) {
      const t = i18n.getFixedT(lang);
      for (const key of everyKey()) {
        expect(t(key), `${lang}: ${key}`).not.toBe(key);
      }
    }
  });

  it('leaves no placeholder unfilled in a verdict', () => {
    for (const lang of LANGUAGES) {
      const t = i18n.getFixedT(lang);
      for (const m of judged()) {
        const text = t(m.verdictKey!, m.verdictVars);
        expect(text, `${lang}: ${m.verdictKey}`).not.toContain('{{');
      }
      for (const c of REPORT_CONCLUSIONS) {
        expect(t(c.key, c.vars), `${lang}: ${c.key}`).not.toContain('{{');
      }
    }
  });

  it('still prints the email’s exact Indonesian verdicts', () => {
    // The whole exercise was matching the email the brand already has. These
    // four are the awkward shapes: a threshold, a benchmark string, a range,
    // and the one with no metric name in it at all.
    const t = i18n.getFixedT('id');
    const byKey = (key: string) => judged().find((m) => m.verdictKey === key)!;
    expect(t('scoring.lateShipmentRate.fail', byKey('scoring.lateShipmentRate.fail').verdictVars))
      .toBe('❌ Tingkat Keterlambatan Pengiriman = 2.3% [Kurang Baik, nilai disarankan: <1%]');
    expect(t('scoring.conversionRate.fail', byKey('scoring.conversionRate.fail').verdictVars))
      .toBe('❌ Tingkat Konversi = 1.0% [Kurang Baik, nilai disarankan: >3%]');
    expect(t('scoring.adsCostPct.tooMinimal', byKey('scoring.adsCostPct.tooMinimal').verdictVars))
      .toBe('❌ [Penggunaan iklan terlalu minim (4.6%). Nilai disarankan: 5%-10%.]');
    expect(t('scoring.stockAvailability.pass', byKey('scoring.stockAvailability.pass').verdictVars))
      .toBe('✔️ % Ketersediaan Stok = 5% stok habis [Sudah Baik]');
  });

  it('splits the email’s closing into its body, link and outro', () => {
    for (const lang of LANGUAGES) {
      const closing = splitClosing(
        i18n.getFixedT(lang)(REPORT_CLOSING.key, { store_name: 'Covermake' }),
      );
      expect(closing.body, lang).toContain('Covermake');
      expect(closing.link, lang).toBe('cal-bd2.ahacommerce.net');
      expect(closing.outro, lang).not.toBe('');
    }
  });
});
