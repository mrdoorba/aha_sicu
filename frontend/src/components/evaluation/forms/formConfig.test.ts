import { describe, it, expect } from 'vitest';
import { generateMonthLabels, computeSectionProgress, EMPTY_MANUAL_DATA } from './formConfig';
import type { ManualData } from './formConfig';

describe('generateMonthLabels', () => {
  it('returns correct month names for "2026-01"', () => {
    const labels = generateMonthLabels('2026-01');
    expect(labels).toEqual([
      'Jan 2026',
      'Dec 2025',
      'Nov 2025',
      'Oct 2025',
      'Sep 2025',
      'Aug 2025',
    ]);
  });

  it('returns correct labels for mid-year "2026-06"', () => {
    const labels = generateMonthLabels('2026-06');
    expect(labels).toEqual([
      'Jun 2026',
      'May 2026',
      'Apr 2026',
      'Mar 2026',
      'Feb 2026',
      'Jan 2026',
    ]);
  });

  it('returns generic fallback for null', () => {
    const labels = generateMonthLabels(null);
    expect(labels).toEqual([
      'generic.thisMonth',
      'generic.month1',
      'generic.month2',
      'generic.month3',
      'generic.month4',
      'generic.month5',
    ]);
  });

  it('returns generic fallback for invalid string', () => {
    expect(generateMonthLabels('invalid')).toEqual([
      'generic.thisMonth', 'generic.month1', 'generic.month2', 'generic.month3', 'generic.month4', 'generic.month5',
    ]);
  });

  it('returns generic fallback for empty string', () => {
    expect(generateMonthLabels('')).toEqual([
      'generic.thisMonth', 'generic.month1', 'generic.month2', 'generic.month3', 'generic.month4', 'generic.month5',
    ]);
  });

  it('returns generic fallback for invalid month number', () => {
    expect(generateMonthLabels('2026-13')).toEqual([
      'generic.thisMonth', 'generic.month1', 'generic.month2', 'generic.month3', 'generic.month4', 'generic.month5',
    ]);
  });
});

describe('computeSectionProgress', () => {
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
