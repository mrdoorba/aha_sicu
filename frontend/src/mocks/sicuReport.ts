/**
 * The SICU report, shaped exactly like the email the app already sends.
 *
 * Source: the Agu 2026 "[ID] AHA Store Internal Check Up (Store ICU)" email, as
 * forwarded by Marwah on 15 Oct 2026. BD asked the results page to match that
 * email's output and format, so this file mirrors its sections, its metric set,
 * its benchmark wording and its verdict strings rather than paraphrasing them —
 * a verdict reworded on the page is a verdict that no longer matches the one
 * the brand already has in their inbox.
 *
 * Every label and verdict is a TRANSLATION KEY, not a finished sentence, and
 * they are the same keys `backend/app/modules/email/template.py` renders from
 * (the backend reads these very locale files). That is the whole point: the
 * brand reads the result in the language the email reached them in, and nobody
 * has to keep two wordings of "Kurang Baik" in step by hand.
 *
 * The numbers are the email's. Only the competition product names are changed,
 * because the sample brand in this preview sells cosmetics and the email's
 * example is a car-care store.
 */

export type MetricStatus =
  /** Meets its benchmark. Green tick. */
  | 'good'
  /** Misses its benchmark. Red cross, amber card. */
  | 'bad'
  /** Context, not a verdict — these carry no tick and no benchmark. */
  | 'info';

/** The values a verdict template interpolates. The email passes the same ones. */
export type VerdictVars = Record<string, string | number>;

export interface ReportMetric {
  /** Key for the metric name, as the email names it. */
  labelKey: string;
  /** Pre-formatted, because the email prints each one its own way. */
  value: string;
  /** Numerals and comparators — language-neutral, so not a key. */
  benchmark?: string;
  /** The coloured line under the rule. Absent on 'info' metrics. */
  verdictKey?: string;
  verdictVars?: VerdictVars;
  status: MetricStatus;
  /** Competition rows link out to the product. */
  link?: boolean;
  /**
   * Which verdict variable carries the row's real title.
   *
   * Competition rows are all named 'Produk Kompetisi'; what distinguishes them
   * is the product, which the email buries inside the verdict sentence. Naming
   * it here lets the row print the product and keep the metric name as a
   * kicker, rather than three identical headings in a column.
   */
  titleVar?: string;
}

export interface ReportGroup {
  titleKey: string;
  metrics: ReportMetric[];
  /** The REAL BENCHMARK aside that sits under Bisnis. */
  note?: { titleKey: string; bodyKey: string };
}

export const REPORT_SCORE = {
  /** The headline evaluation score. */
  value: 42,
  /** Shown beside it in the email as a separate chip — a different number. */
  compatibility: 73,
  verdictKey: 'email.performance_verdict',
};

export const REPORT_META = {
  period: 'Agu 2026',
  category: 'Beauty & Personal Care',
  pic: 'Budi Santoso',
  storeUrl: 'https://shopee.co.id/covermakeofficial',
};

export const REPORT_GROUPS: ReportGroup[] = [
  {
    titleKey: 'email.category.operational',
    metrics: [
      {
        labelKey: 'fields.operational.unfulfilledOrderRate',
        value: '0%',
        benchmark: '<1%',
        verdictKey: 'scoring.unfulfilledOrderRate.pass',
        verdictVars: { value: '0.0%' },
        status: 'good',
      },
      {
        labelKey: 'fields.operational.lateShipmentRate',
        value: '2.33%',
        benchmark: '<1%',
        verdictKey: 'scoring.lateShipmentRate.fail',
        verdictVars: { value: '2.3%', threshold: 1 },
        status: 'bad',
      },
      {
        labelKey: 'scoring.preparationTime',
        value: '0.55',
        benchmark: '<1',
        verdictKey: 'scoring.preparationTime.pass',
        verdictVars: { value: '0.55' },
        status: 'good',
      },
      {
        labelKey: 'fields.operational.chatResponseRate',
        value: '100%',
        benchmark: '>95%',
        verdictKey: 'scoring.chatResponseRate.pass',
        verdictVars: { value: '100%' },
        status: 'good',
      },
      {
        labelKey: 'scoring.overallRating',
        value: '4.91',
        benchmark: '>4.7',
        verdictKey: 'scoring.overallRating.pass',
        verdictVars: { value: '4.91' },
        status: 'good',
      },
    ],
  },
  {
    titleKey: 'email.category.business',
    metrics: [
      { labelKey: 'scoring.avgSales6mo', value: '91,076,096', status: 'info' },
      {
        labelKey: 'scoring.conversionRate',
        value: '0.99%',
        benchmark: '>3%',
        verdictKey: 'scoring.conversionRate.fail',
        verdictVars: { value: '1.0%', benchmark: '>3%' },
        status: 'bad',
      },
    ],
    note: {
      titleKey: 'presentation.salesTrend.realBenchmark.label',
      bodyKey: 'presentation.salesTrend.realBenchmark.note',
    },
  },
  {
    titleKey: 'email.category.visitors',
    metrics: [
      { labelKey: 'fields.visitors.totalVisitors', value: '4,973', status: 'info' },
      { labelKey: 'scoring.returningVisitors', value: '1,253', status: 'info' },
      {
        labelKey: 'scoring.returningVisitorPct',
        value: '25.2%',
        benchmark: '>23%',
        verdictKey: 'scoring.returningVisitorPct.pass',
        verdictVars: { value: '25.2%' },
        status: 'good',
      },
      {
        labelKey: 'scoring.totalFollowers',
        value: '4,100',
        benchmark: '>50000',
        verdictKey: 'scoring.totalFollowers.fail',
        verdictVars: { value: '4,100' },
        status: 'bad',
      },
    ],
  },
  {
    titleKey: 'email.category.promo',
    metrics: [
      {
        labelKey: 'scoring.promoUsageRate',
        value: '27.3%',
        benchmark: '>80%',
        verdictKey: 'scoring.promoUsageRate.fail',
        verdictVars: { value: '27%', threshold: 80 },
        status: 'bad',
      },
      {
        labelKey: 'scoring.promoEffectiveness',
        value: '9.1%',
        benchmark: '>90%',
        verdictKey: 'scoring.promoEffectiveness.fail',
        verdictVars: { value: '9%', threshold: 90 },
        status: 'bad',
      },
    ],
  },
  {
    titleKey: 'email.category.products',
    metrics: [
      {
        labelKey: 'category.products',
        value: '152',
        benchmark: '>=35',
        verdictKey: 'scoring.productCount.pass',
        verdictVars: { value: '152' },
        status: 'good',
      },
      {
        labelKey: 'fields.products.storeStatus',
        value: 'Star+',
        benchmark: 'Shopee Mall',
        verdictKey: 'scoring.storeStatus.pass',
        verdictVars: { value: 'Star+' },
        status: 'good',
      },
    ],
  },
  {
    titleKey: 'email.category.ads',
    metrics: [
      { labelKey: 'fields.ads.adSales', value: '70,336,473', status: 'info' },
      { labelKey: 'fields.ads.adCost', value: '4,306,553', status: 'info' },
      {
        labelKey: 'scoring.adsROI',
        value: '16.3',
        benchmark: '>9',
        verdictKey: 'scoring.adsROI.pass',
        verdictVars: { value: '16.3' },
        status: 'good',
      },
      {
        labelKey: 'scoring.adsGMVPct',
        value: '75.8%',
        benchmark: '<74%',
        verdictKey: 'scoring.adsGMVPct.fail',
        verdictVars: { value: '75.8%', threshold: 74 },
        status: 'bad',
      },
      {
        labelKey: 'scoring.adsCostPct',
        value: '4.6%',
        benchmark: '<10%',
        verdictKey: 'scoring.adsCostPct.tooMinimal',
        verdictVars: { value: '4.6%', min: 5, max: 10 },
        status: 'bad',
      },
    ],
  },
  {
    titleKey: 'email.category.campaign',
    metrics: [
      { labelKey: 'fields.campaign.nominatedSessions', value: '3', status: 'info' },
      { labelKey: 'fields.campaign.availableSessions', value: '10', status: 'info' },
      {
        labelKey: 'categories.campaign',
        value: '30.0%',
        benchmark: '>90%',
        verdictKey: 'scoring.campaignParticipation.fail',
        verdictVars: { value: '30.0%', threshold: 90 },
        status: 'bad',
      },
    ],
  },
  {
    titleKey: 'email.category.competition',
    metrics: [
      {
        labelKey: 'scoring.competitionProduct',
        value: '245,000',
        benchmark: 'IDR 215,027',
        verdictKey: 'scoring.competitionProduct.fail',
        verdictVars: {
          name: 'Covermake Cushion Foundation SPF50 / 15g',
          currency: 'IDR',
          sellingPrice: '245,000',
          marketPrice: '215,027',
        },
        status: 'bad',
        link: true,
        titleVar: 'name',
      },
      {
        labelKey: 'scoring.competitionProduct',
        value: '835,000',
        benchmark: 'IDR 831,364',
        verdictKey: 'scoring.competitionProduct.pass',
        verdictVars: {
          name: 'Covermake Pro Artistry Palette / 24 Shades Limited Edition',
          currency: 'IDR',
          sellingPrice: '835,000',
          marketPrice: '831,364',
        },
        status: 'good',
        link: true,
        titleVar: 'name',
      },
      {
        labelKey: 'scoring.competitionProduct',
        value: '145,000',
        benchmark: 'IDR 166,759',
        verdictKey: 'scoring.competitionProduct.pass',
        verdictVars: {
          name: 'Covermake Hydra Serum Vitamin C - 30ml',
          currency: 'IDR',
          sellingPrice: '145,000',
          marketPrice: '166,759',
        },
        status: 'good',
        link: true,
        titleVar: 'name',
      },
    ],
  },
  {
    titleKey: 'email.category.stock',
    metrics: [
      {
        labelKey: 'scoring.avgStockTop20',
        value: '73',
        benchmark: '>=24',
        verdictKey: 'scoring.avgStockTop20.pass',
        verdictVars: { value: '73' },
        status: 'good',
      },
      {
        labelKey: 'evaluationDetail.stockAvailability',
        value: '5.0%',
        benchmark: '≤10% stok habis',
        verdictKey: 'scoring.stockAvailability.pass',
        verdictVars: { value: '5%' },
        status: 'good',
      },
    ],
  },
];

export const REPORT_CONCLUSIONS: { key: string; vars?: VerdictVars }[] = [
  { key: 'conclusion.salesRange', vars: { min: 62, max: 135 } },
  { key: 'conclusion.operationalGood' },
  { key: 'conclusion.productNaming' },
  { key: 'conclusion.photoBackground' },
  { key: 'conclusion.promoUnderutilized' },
  { key: 'conclusion.campaignLow' },
  { key: 'conclusion.stockNotArchived' },
  { key: 'conclusion.unsoldProducts' },
  { key: 'conclusion.discountRange', vars: { range: '9.6% ~ 10.3%' } },
];

export const REPORT_MARKETING_BUDGET = {
  labelKey: 'email.marketing_budget',
  bodyKey: 'marketing.budgetRecommendation',
  bodyVars: { pct: '10%' },
};

export const REPORT_CLOSING = {
  /**
   * The email writes the closing as one string: body, booking link, outro,
   * separated by blank lines. The page draws them as three things, so it reads
   * the same key and splits on the paragraph breaks rather than keeping a
   * second copy of the wording that would drift from the email's.
   */
  key: 'closing.potential',
  ctaKey: 'email.schedule_consultation',
  signoffKey: 'email.signoff_regards',
};

/** Body / booking link / outro, from the email's single closing string. */
export function splitClosing(text: string): {
  body: string;
  link: string;
  outro: string;
} {
  const parts = text.split('\n\n').map((p) => p.trim());
  return { body: parts[0] ?? '', link: parts[1] ?? '', outro: parts[2] ?? '' };
}
