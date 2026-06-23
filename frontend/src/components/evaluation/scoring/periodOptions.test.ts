import { describe, it, expect } from 'vitest';
import { generatePeriodOptions, periodLabelFromMonth } from './periodOptions';

describe('periodLabelFromMonth', () => {
  it('maps a YYYY-MM start month to the Indonesian period label', () => {
    expect(periodLabelFromMonth('2026-05')).toBe('Mei 2026');
    expect(periodLabelFromMonth('2026-01')).toBe('Jan 2026');
  });

  it('falls back to the current month when unset or malformed', () => {
    const current = generatePeriodOptions()[0];
    expect(periodLabelFromMonth(null)).toBe(current);
    expect(periodLabelFromMonth('2026-13')).toBe(current);
    expect(periodLabelFromMonth('garbage')).toBe(current);
  });
});
