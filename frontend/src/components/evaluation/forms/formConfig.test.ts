import { describe, it, expect } from 'vitest';
import { generateMonthLabels, computeSectionProgress, EMPTY_MANUAL_DATA } from './formConfig';
import type { ManualData } from './formConfig';

describe('generateMonthLabels', () => {
  it('returns correct Indonesian month names for "2026-01"', () => {
    const labels = generateMonthLabels('2026-01');
    expect(labels).toEqual([
      'Jan 2026',
      'Des 2025',
      'Nov 2025',
      'Okt 2025',
      'Sep 2025',
      'Agu 2025',
    ]);
  });

  it('returns correct labels for mid-year "2026-06"', () => {
    const labels = generateMonthLabels('2026-06');
    expect(labels).toEqual([
      'Jun 2026',
      'Mei 2026',
      'Apr 2026',
      'Mar 2026',
      'Feb 2026',
      'Jan 2026',
    ]);
  });

  it('returns generic fallback for null', () => {
    const labels = generateMonthLabels(null);
    expect(labels).toEqual([
      'Bulan Ini',
      'Bulan -1',
      'Bulan -2',
      'Bulan -3',
      'Bulan -4',
      'Bulan -5',
    ]);
  });

  it('returns generic fallback for invalid string', () => {
    expect(generateMonthLabels('invalid')).toEqual([
      'Bulan Ini', 'Bulan -1', 'Bulan -2', 'Bulan -3', 'Bulan -4', 'Bulan -5',
    ]);
  });

  it('returns generic fallback for empty string', () => {
    expect(generateMonthLabels('')).toEqual([
      'Bulan Ini', 'Bulan -1', 'Bulan -2', 'Bulan -3', 'Bulan -4', 'Bulan -5',
    ]);
  });

  it('returns generic fallback for invalid month number', () => {
    expect(generateMonthLabels('2026-13')).toEqual([
      'Bulan Ini', 'Bulan -1', 'Bulan -2', 'Bulan -3', 'Bulan -4', 'Bulan -5',
    ]);
  });
});

describe('computeSectionProgress', () => {
  it('excludes content from section 2 progress', () => {
    const data: ManualData = {
      ...EMPTY_MANUAL_DATA,
      content: { needsImprovement: 5, goodQuality: 10 },
    };
    const progress = computeSectionProgress(data);
    // Section 2 = business (7 fields) + visitors (3) = 10 total, content excluded
    expect(progress['section-2'].total).toBe(10);
    expect(progress['section-2'].filled).toBe(0); // content data doesn't count
  });

  it('excludes salesStartMonth from section 2 field count', () => {
    const data: ManualData = {
      ...EMPTY_MANUAL_DATA,
      business: {
        ...EMPTY_MANUAL_DATA.business,
        salesStartMonth: '2026-01',
        salesMonth0: 100,
      },
    };
    const progress = computeSectionProgress(data);
    // 7 business fields (excluding salesStartMonth) + 3 visitors = 10
    expect(progress['section-2'].total).toBe(10);
    expect(progress['section-2'].filled).toBe(1); // only salesMonth0
  });

  it('counts all 5 competition fields per product (15 total)', () => {
    const progress = computeSectionProgress(EMPTY_MANUAL_DATA);
    // Section 5 = ads (2) + campaign (2) + competition (15) = 19
    expect(progress['section-5'].total).toBe(19);
  });
});
