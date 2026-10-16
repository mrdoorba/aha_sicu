import { describe, expect, it } from 'vitest';
import { verdictClause } from './verdict';

describe('verdictClause', () => {
  it('drops the metric and value the row already prints', () => {
    expect(verdictClause('✔️ Tingkat Pesanan Tidak Terselesaikan = 0.0% [Sudah Baik]')).toBe(
      'Sudah Baik',
    );
  });

  it('keeps the part that is actually new — the target', () => {
    expect(
      verdictClause('❌ Tingkat Konversi = 1.0% [Kurang Baik, nilai disarankan: >3%]'),
    ).toBe('Kurang Baik, nilai disarankan: >3%');
  });

  it('handles a verdict that is nothing but its clause', () => {
    expect(
      verdictClause('❌ [Penggunaan iklan terlalu minim (4.6%). Nilai disarankan: 5%-10%.]'),
    ).toBe('Penggunaan iklan terlalu minim (4.6%). Nilai disarankan: 5%-10%.');
  });

  it('keeps nested parentheses inside the clause', () => {
    expect(
      verdictClause(
        'Covermake Hydra Serum / 30ml (IDR 145,000) = ❌[tidak kompetitif (harga kisaran pasaran: IDR 166,759)]',
      ),
    ).toBe('tidak kompetitif (harga kisaran pasaran: IDR 166,759)');
  });

  it('keeps a tip that follows the bracket', () => {
    // Losing this line would lose advice the brand was given.
    expect(
      verdictClause(
        '✔️ Status Toko = Star+ [OK]\n💡 Disarankan Shopee Mall untuk meningkatkan kepercayaan terhadap brand.',
      ),
    ).toBe('OK\n💡 Disarankan Shopee Mall untuk meningkatkan kepercayaan terhadap brand.');
  });

  it('leaves a verdict with no bracket alone', () => {
    expect(verdictClause('✔️ Program Afiliasi (12%) digunakan')).toBe(
      'Program Afiliasi (12%) digunakan',
    );
  });
});
