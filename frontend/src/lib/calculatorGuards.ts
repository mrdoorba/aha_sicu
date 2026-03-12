// ── Calculator detail type guards ────────────────────────────────────────────
// These validate key structural properties from the API's Record<string, unknown>
// response before narrowing to the specific detail types.

import type {
  AdsKeywordDetails,
  DiscountDetails,
  TopSkuDetails,
} from '../hooks/useCalculator';

/**
 * Validates that an unknown value has the structural shape of AdsKeywordDetails.
 * Checks for key string properties that are always present in the response.
 */
export function isAdsKeywordDetails(value: unknown): value is AdsKeywordDetails {
  if (typeof value !== 'object' || value === null) return false;
  const obj = value as Record<string, unknown>;
  return (
    typeof obj.ak2 === 'string' &&
    typeof obj.ak3 === 'string' &&
    typeof obj.thresholds === 'object' &&
    obj.thresholds !== null
  );
}

/**
 * Validates that an unknown value has the structural shape of DiscountDetails.
 * Checks for key properties that distinguish it from other detail types.
 */
export function isDiscountDetails(value: unknown): value is DiscountDetails {
  if (typeof value !== 'object' || value === null) return false;
  const obj = value as Record<string, unknown>;
  return (
    typeof obj.discount_pct === 'string' &&
    typeof obj.range_min === 'string' &&
    typeof obj.range_max === 'string' &&
    typeof obj.fake_discount_flag === 'boolean'
  );
}

/**
 * Validates that an unknown value has the structural shape of TopSkuDetails.
 * Checks for key properties: output arrays and average_stock.
 */
export function isTopSkuDetails(value: unknown): value is TopSkuDetails {
  if (typeof value !== 'object' || value === null) return false;
  const obj = value as Record<string, unknown>;
  return (
    Array.isArray(obj.output_1) &&
    Array.isArray(obj.output_2) &&
    typeof obj.average_stock === 'number'
  );
}
