import { describe, expect, it } from 'vitest';
import { REPORT_GROUPS, REPORT_SCORE } from './sicuReport';

const allMetrics = REPORT_GROUPS.flatMap((g) => g.metrics);

describe('the report mirrors the SICU email', () => {
  it('keeps the email’s section order', () => {
    expect(REPORT_GROUPS.map((g) => g.title)).toEqual([
      'Operasional',
      'Bisnis',
      'Pengunjung',
      'Alat Promo',
      'Produk & Status',
      'Iklan',
      'Campaign',
      'Kompetisi',
      'Stok',
    ]);
  });

  it('carries the same 21 judged metrics the email prints', () => {
    const judged = allMetrics.filter((m) => m.status !== 'info');
    expect(judged).toHaveLength(21);
  });

  it('gives every judged metric both a benchmark and a verdict', () => {
    // A verdict without its benchmark is an assertion the brand can't check.
    for (const m of judged()) {
      expect(m.benchmark, `${m.label} benchmark`).toBeTruthy();
      expect(m.verdict, `${m.label} verdict`).toBeTruthy();
    }
  });

  it('gives info metrics neither, so they never read as a pass', () => {
    for (const m of allMetrics.filter((m) => m.status === 'info')) {
      expect(m.benchmark, `${m.label} benchmark`).toBeUndefined();
      expect(m.verdict, `${m.label} verdict`).toBeUndefined();
    }
  });

  it('keeps the headline score and AHA Compatibility as separate numbers', () => {
    // The email prints both. Collapsing them would misreport one or the other:
    // the headline is the brand's health, compatibility is AHA's own read.
    expect(REPORT_SCORE.value).not.toBe(REPORT_SCORE.compatibility);
    for (const n of [REPORT_SCORE.value, REPORT_SCORE.compatibility]) {
      expect(n).toBeGreaterThanOrEqual(0);
      expect(n).toBeLessThanOrEqual(100);
    }
  });

  it('runs competition rows full width, since they carry a product name', () => {
    const competition = REPORT_GROUPS.find((g) => g.title === 'Kompetisi')!;
    expect(competition.metrics.every((m) => m.wide && m.linkLabel)).toBe(true);
    // Nothing else is full width.
    const others = REPORT_GROUPS.filter((g) => g.title !== 'Kompetisi').flatMap((g) => g.metrics);
    expect(others.some((m) => m.wide)).toBe(false);
  });

  it('attaches the REAL BENCHMARK aside to Bisnis only', () => {
    const withNotes = REPORT_GROUPS.filter((g) => g.note);
    expect(withNotes.map((g) => g.title)).toEqual(['Bisnis']);
    expect(withNotes[0].note?.title).toBe('REAL BENCHMARK');
  });
});

function judged() {
  return allMetrics.filter((m) => m.status !== 'info');
}
