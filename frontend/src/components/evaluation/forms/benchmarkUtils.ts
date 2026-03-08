import type { ScoringRules, RuleThreshold } from '../../../hooks/useRules';

const COMPARISON_OPERATORS: Record<string, string> = {
  gte: '>',
  lte: '<',
  gt: '>',
  lt: '<',
};

/** Fields whose benchmarks should be formatted as percentages. */
const PERCENTAGE_UNITS = new Set(['%']);

/** Fields whose benchmarks should use thousands separators (count fields). */
const COUNT_UNITS = new Set(['count']);

/**
 * Map from formConfig camelCase keys to { rulesCategory, rulesKey } in the
 * scoring rules JSONB.
 */
export const FORM_TO_RULES_MAP: Record<string, { category: keyof ScoringRules; key: string }> = {
  unfulfilledOrderRate: { category: 'operational', key: 'unfulfilled_order_rate' },
  lateShipmentRate: { category: 'operational', key: 'late_shipment_rate' },
  preparationTime: { category: 'operational', key: 'preparation_time' },
  chatResponseRate: { category: 'operational', key: 'chat_response_rate' },
  overallRating: { category: 'operational', key: 'overall_rating' },
  conversionRate: { category: 'business', key: 'conversion_rate' },
  totalFollowers: { category: 'visitors', key: 'followers' },
  productCount: { category: 'products_status', key: 'product_count' },
};

function formatThreshold(value: number, unit?: string): string {
  if (unit && PERCENTAGE_UNITS.has(unit)) {
    return `${value}%`;
  }
  if (unit && COUNT_UNITS.has(unit)) {
    return new Intl.NumberFormat('en-US').format(value);
  }
  return String(value);
}

/**
 * Extract a benchmark display string from scoring rules.
 *
 * @param rules  The active ScoringRules object (or undefined if not loaded).
 * @param category  The rules category key (e.g. 'operational').
 * @param key  The rules field key (e.g. 'unfulfilled_order_rate').
 * @param unit  The field unit from formConfig (e.g. '%', 'count', 'hari').
 * @param fallback  The static benchmark string from formConfig.
 * @returns A formatted benchmark string like ">3%" or "<1".
 */
export function getBenchmarkFromRules(
  rules: ScoringRules | undefined,
  category: string,
  key: string,
  unit?: string,
  fallback?: string,
): string | undefined {
  if (!rules) return fallback;

  const categoryRules = rules[category as keyof ScoringRules];
  if (!categoryRules || typeof categoryRules !== 'object') return fallback;

  const rule = (categoryRules as Record<string, RuleThreshold>)[key];
  if (!rule || rule.threshold == null) return fallback;

  const operator = rule.comparison ? COMPARISON_OPERATORS[rule.comparison] : '>';
  const prefix = operator ?? '>';

  return `${prefix}${formatThreshold(rule.threshold, unit)}`;
}
