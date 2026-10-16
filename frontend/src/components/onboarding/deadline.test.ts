import { describe, expect, it } from 'vitest';
import i18n from '../../i18n';
import {
  TOTAL_WORKDAYS,
  deadlineMeter,
  remainingFromSearch,
  remainingLabel,
} from './deadline';

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

describe('remainingLabel', () => {
  // The label is a key plus its numbers now, so the test renders it through the
  // real i18n instance: that pins the Indonesian wording exactly as before AND
  // catches a branch that someone forgets to translate, which a key-only
  // assertion would wave through.
  const render = (days: number, hours: number, lang: string) => {
    const { key, vars } = remainingLabel(days, hours);
    return i18n.getFixedT(lang)(key, vars);
  };

  it('shows days and hours together', () => {
    expect(render(7, 3, 'id')).toBe('Sisa 7 hari kerja 3 jam');
    expect(render(7, 3, 'en')).toBe('7 working days 3 hours left');
  });

  it('drops the hours when there are none left today', () => {
    expect(render(7, 0, 'id')).toBe('Sisa 7 hari kerja');
    expect(render(7, 0, 'en')).toBe('7 working days left');
  });

  it('counts in hours alone on the last day', () => {
    expect(render(0, 4, 'id')).toBe('Sisa 4 jam');
    expect(render(0, 4, 'en')).toBe('4 hours left');
  });

  it('is expired only when both are gone', () => {
    expect(render(0, 0, 'id')).toBe('Waktu klaim habis');
    expect(render(0, 0, 'en')).toBe('Claim window closed');
  });

  it('says something in every language, on every branch', () => {
    for (const lang of ['id', 'en', 'th']) {
      for (const [days, hours] of [
        [7, 3],
        [7, 0],
        [0, 4],
        [0, 0],
      ]) {
        const text = render(days, hours, lang);
        // An untranslated key falls back to the key itself — which would read
        // as 'onboarding.deadline.days' on the brand's screen.
        expect(text, `${lang} ${days}d${hours}h`).not.toContain('onboarding.');
        expect(text, `${lang} ${days}d${hours}h`).not.toContain('{{');
      }
    }
  });
});

describe('deadlineMeter with hours', () => {
  it('is not expired while hours remain on the last day', () => {
    // 0 working days but 4 hours left is a brand that can still finish.
    expect(deadlineMeter(0, TOTAL_WORKDAYS, 4).expired).toBe(false);
    expect(deadlineMeter(0, TOTAL_WORKDAYS, 0).expired).toBe(true);
  });

  it('never reports negative hours', () => {
    expect(deadlineMeter(2, TOTAL_WORKDAYS, -5).hours).toBe(0);
  });
});
