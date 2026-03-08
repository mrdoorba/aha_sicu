import { describe, it, expect } from 'vitest';
import { getBenchmarkFromRules } from './benchmarkUtils';
import type { ScoringRules } from '../../../hooks/useRules';

function makeRules(overrides: Partial<ScoringRules> = {}): ScoringRules {
  return {
    operational: {
      unfulfilled_order_rate: { threshold: 1.0, comparison: 'lte' },
      late_shipment_rate: { threshold: 1.0, comparison: 'lte' },
      preparation_time: { threshold: 1.0, comparison: 'lte' },
      chat_response_rate: { threshold: 95, comparison: 'gte' },
      overall_rating: { threshold: 4.7, comparison: 'gte' },
    },
    business: {
      conversion_rate: { threshold: 3.0, comparison: 'gte' },
    },
    visitors: {
      followers: { threshold: 50000, comparison: 'gte' },
    },
    promo_tools: {},
    products_status: {
      product_count: { threshold: 35, comparison: 'gte' },
    },
    ads: {},
    campaign: {},
    stock: {},
    discount: {},
    marketing: {},
    interpretation: { ranges: [] },
    ...overrides,
  };
}

describe('getBenchmarkFromRules', () => {
  it('returns gte operator as ">"', () => {
    const rules = makeRules();
    expect(getBenchmarkFromRules(rules, 'business', 'conversion_rate', '%')).toBe('>3%');
  });

  it('returns lte operator as "<"', () => {
    const rules = makeRules();
    expect(getBenchmarkFromRules(rules, 'operational', 'unfulfilled_order_rate', '%')).toBe('<1%');
  });

  it('returns gt operator as ">"', () => {
    const rules = makeRules({
      operational: {
        chat_response_rate: { threshold: 95, comparison: 'gt' },
      },
    });
    expect(getBenchmarkFromRules(rules, 'operational', 'chat_response_rate', '%')).toBe('>95%');
  });

  it('returns lt operator as "<"', () => {
    const rules = makeRules({
      operational: {
        preparation_time: { threshold: 1, comparison: 'lt' },
      },
    });
    expect(getBenchmarkFromRules(rules, 'operational', 'preparation_time', 'hari')).toBe('<1');
  });

  it('formats percentage fields with %', () => {
    const rules = makeRules();
    expect(getBenchmarkFromRules(rules, 'operational', 'chat_response_rate', '%')).toBe('>95%');
  });

  it('formats count fields with thousands separator', () => {
    const rules = makeRules();
    expect(getBenchmarkFromRules(rules, 'visitors', 'followers', 'count')).toBe('>50,000');
  });

  it('formats non-percentage non-count fields as plain numbers', () => {
    const rules = makeRules();
    expect(getBenchmarkFromRules(rules, 'operational', 'overall_rating', 'rating')).toBe('>4.7');
  });

  it('returns fallback when rules is undefined', () => {
    expect(getBenchmarkFromRules(undefined, 'business', 'conversion_rate', '%', '>3%')).toBe('>3%');
  });

  it('returns fallback when rule key is missing', () => {
    const rules = makeRules();
    expect(getBenchmarkFromRules(rules, 'business', 'nonexistent', '%', '>5%')).toBe('>5%');
  });

  it('returns fallback when category is missing', () => {
    const rules = makeRules();
    expect(getBenchmarkFromRules(rules, 'nonexistent', 'something', '%', '>5%')).toBe('>5%');
  });

  it('defaults to ">" when comparison field is missing', () => {
    const rules = makeRules({
      business: {
        conversion_rate: { threshold: 3.0 },
      },
    });
    expect(getBenchmarkFromRules(rules, 'business', 'conversion_rate', '%')).toBe('>3%');
  });

  it('returns fallback when threshold is missing', () => {
    const rules = makeRules({
      business: {
        conversion_rate: { comparison: 'gte' },
      },
    });
    expect(getBenchmarkFromRules(rules, 'business', 'conversion_rate', '%', '>3%')).toBe('>3%');
  });

  it('returns undefined fallback when no fallback provided and rules missing', () => {
    expect(getBenchmarkFromRules(undefined, 'business', 'conversion_rate', '%')).toBeUndefined();
  });
});
