import { describe, it, expect } from 'vitest';
import { addWorkdays, isWorkday, workdaysBetween, formatDeadline } from './workdays';

// 2026-10-13 is a Tuesday. Local-time constructor on purpose: the helper uses
// getDay(), so a UTC-parsed date would shift the weekday in non-UTC zones.
const TUE = new Date(2026, 9, 13);
const FRI = new Date(2026, 9, 16);
const SAT = new Date(2026, 9, 17);
const SUN = new Date(2026, 9, 18);

describe('isWorkday', () => {
  it('counts Monday to Friday', () => {
    expect(isWorkday(TUE)).toBe(true);
    expect(isWorkday(FRI)).toBe(true);
  });

  it('excludes the weekend', () => {
    expect(isWorkday(SAT)).toBe(false);
    expect(isWorkday(SUN)).toBe(false);
  });

  it('counts a public holiday as a working day', () => {
    // 17 Aug 2026 is Indonesian Independence Day, a Monday. Confirmed with
    // Alfiano that holidays are NOT observed — this test pins that decision.
    const independenceDay = new Date(2026, 7, 17);
    expect(independenceDay.getDay()).toBe(1);
    expect(isWorkday(independenceDay)).toBe(true);
  });
});

describe('addWorkdays', () => {
  it('skips the weekend', () => {
    // Tue + 7 working days = Thu of the following week (2 weekend days skipped).
    const result = addWorkdays(TUE, 7);
    expect(result.getDay()).toBe(4);
    expect(result.getDate()).toBe(22);
  });

  it('lands on Monday when starting Friday with one day', () => {
    const result = addWorkdays(FRI, 1);
    expect(result.getDay()).toBe(1);
    expect(result.getDate()).toBe(19);
  });

  it('never returns a weekend date', () => {
    for (let n = 1; n <= 20; n += 1) {
      expect(isWorkday(addWorkdays(TUE, n))).toBe(true);
    }
  });

  it('does not count the start date itself', () => {
    expect(addWorkdays(TUE, 1).getDate()).toBe(14);
  });
});

describe('workdaysBetween', () => {
  it('round-trips with addWorkdays', () => {
    const deadline = addWorkdays(TUE, 7);
    expect(workdaysBetween(TUE, deadline)).toBe(7);
  });

  it('returns 0 for a deadline already passed, so callers need no second check', () => {
    expect(workdaysBetween(FRI, TUE)).toBe(0);
  });

  it('returns 0 for the same instant', () => {
    expect(workdaysBetween(TUE, TUE)).toBe(0);
  });

  it('ignores weekend days in the span', () => {
    // Fri → Mon spans 3 calendar days but only 1 working day.
    expect(workdaysBetween(FRI, new Date(2026, 9, 19))).toBe(1);
  });
});

describe('formatDeadline', () => {
  it('renders an Indonesian short date', () => {
    const out = formatDeadline(TUE);
    expect(out).toMatch(/13/);
    expect(out).toMatch(/2026/);
  });
});
