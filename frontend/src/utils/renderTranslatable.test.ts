import { describe, it, expect, vi } from 'vitest';
import type { TFunction } from 'i18next';
import { renderTranslatable } from './renderTranslatable';

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
