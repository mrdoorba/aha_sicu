import { describe, expect, it } from 'vitest';
import { TOTAL_WORKDAYS, deadlineMeter, remainingFromSearch } from './deadline';

describe('deadlineMeter', () => {
  it('is full on the day the voucher is claimed', () => {
    const { percent, urgency, expired } = deadlineMeter(TOTAL_WORKDAYS);
    expect(percent).toBe(100);
    expect(urgency).toBe('calm');
    expect(expired).toBe(false);
  });

  it('shrinks as working days are used up', () => {
    const widths = [7, 5, 3, 1].map((d) => deadlineMeter(d).percent);
    const sorted = [...widths].sort((a, b) => b - a);
    expect(widths).toEqual(sorted);
    expect(new Set(widths).size).toBe(widths.length);
  });

  it('escalates at 3 days and again at 1', () => {
    expect(deadlineMeter(4).urgency).toBe('calm');
    expect(deadlineMeter(3).urgency).toBe('soon');
    expect(deadlineMeter(2).urgency).toBe('soon');
    expect(deadlineMeter(1).urgency).toBe('critical');
    expect(deadlineMeter(0).urgency).toBe('critical');
  });

  it('keeps a visible sliver at zero so the bar reads as empty, not broken', () => {
    const { percent, expired } = deadlineMeter(0);
    expect(expired).toBe(true);
    expect(percent).toBeGreaterThan(0);
    expect(percent).toBeLessThan(10);
  });

  it('clamps a count outside the window instead of overflowing the track', () => {
    expect(deadlineMeter(99).percent).toBe(100);
    expect(deadlineMeter(99).clamped).toBe(TOTAL_WORKDAYS);
    // A negative remaining is an expired voucher, not a negative-width bar.
    expect(deadlineMeter(-3).clamped).toBe(0);
    expect(deadlineMeter(-3).expired).toBe(true);
  });

  it('honours a non-default window', () => {
    expect(deadlineMeter(5, 10).percent).toBe(50);
    expect(deadlineMeter(10, 10).percent).toBe(100);
  });
});

describe('remainingFromSearch', () => {
  it('returns null when the preview has no override', () => {
    expect(remainingFromSearch('')).toBeNull();
    expect(remainingFromSearch('?lang=en')).toBeNull();
  });

  it('reads an integer override', () => {
    expect(remainingFromSearch('?sisa=2')).toBe(2);
    expect(remainingFromSearch('?lang=en&sisa=0')).toBe(0);
  });

  it('ignores junk rather than rendering a NaN-wide bar', () => {
    expect(remainingFromSearch('?sisa=abc')).toBeNull();
    expect(remainingFromSearch('?sisa=')).toBeNull();
    expect(remainingFromSearch('?sisa=1.5')).toBeNull();
  });
});
