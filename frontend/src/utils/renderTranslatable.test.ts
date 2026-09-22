import { describe, it, expect, vi } from 'vitest';
import type { TFunction } from 'i18next';
import { renderTranslatable, renderFlagList } from './renderTranslatable';

describe('renderTranslatable', () => {
  const mockT: TFunction = vi.fn((key: string, vars?: Record<string, string>) => {
    if (key === 'scoring.preparationTime.pass') {
      return `✔️ Preparation Time = ${vars?.value} days [Good]`;
    }
    return key;
  }) as TFunction;

  it('should use i18n translation when i18n data is provided', () => {
    const result = renderTranslatable(
      'fallback text',
      { key: 'scoring.preparationTime.pass', vars: { value: '0.56' } },
      mockT,
    );
    expect(result).toBe('✔️ Preparation Time = 0.56 days [Good]');
    expect(mockT).toHaveBeenCalledWith('scoring.preparationTime.pass', { value: '0.56' });
  });

  it('should fall back to text when i18n is null', () => {
    const result = renderTranslatable('fallback text', null, mockT);
    expect(result).toBe('fallback text');
  });

  it('should fall back to text when i18n is undefined', () => {
    const result = renderTranslatable('fallback text', undefined, mockT);
    expect(result).toBe('fallback text');
  });
});

describe('renderFlagList', () => {
  // i18next returns the key itself on a miss; a stored evaluation may still
  // carry a flag key that was since retired from the locales.
  const mockT = ((key: string) =>
    key === 'ads.flag.productLow' ? '📌 Partisipasi produk kurang maksimal.' : key) as TFunction;

  it('drops a flag whose key no longer exists in the locale', () => {
    const result = renderFlagList(
      'fallback',
      [{ key: 'ads.flag.productLow' }, { key: 'ads.flag.noShopAd' }],
      mockT,
    );
    expect(result).toBe('📌 Partisipasi produk kurang maksimal.');
  });
});
