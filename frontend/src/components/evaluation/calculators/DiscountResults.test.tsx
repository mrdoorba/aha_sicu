import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { DiscountResults } from './DiscountResults';
import type { CalculatorResult } from '../../../hooks/useCalculator';

function makeResult(fakeDiscountFlag: boolean): CalculatorResult {
  return {
    calculator_type: 'discount',
    output_text: '% Diskon TOP SKU: 2.7%\nRange: 0.0% ~ 6.7%',
    details: {
      discount_pct: '2.7%',
      range_min: '0.0%',
      range_max: '6.7%',
      voucher_pct: '0.3%',
      paket_pct: '0.0%',
      fake_discount_flag: fakeDiscountFlag,
      product_summary: [],
      top_sku: [],
      totals: { sum_n: 0, sum_p: 0, sum_voucher: 0, sum_paket: 0, sum_harga_setelah_diskon: 0 },
    },
    calculated_at: '2026-02-11T10:30:00Z',
  };
}

describe('DiscountResults', () => {
  it('renders 5 text values', () => {
    render(<DiscountResults result={makeResult(false)} />);

    expect(screen.getByText('2.7%')).toBeInTheDocument();
    expect(screen.getByText('0.0% ~ 6.7%')).toBeInTheDocument();
    expect(screen.getByText('0.3%')).toBeInTheDocument();
    expect(screen.getByText('0.0%')).toBeInTheDocument();
    expect(screen.getByText('% Diskon TOP SKU')).toBeInTheDocument();
  });

  it('renders fake discount warning when flag true', () => {
    render(<DiscountResults result={makeResult(true)} />);

    expect(screen.getByText('Fake Discount Detected')).toBeInTheDocument();
  });

  it('hides warning when flag false', () => {
    render(<DiscountResults result={makeResult(false)} />);

    expect(screen.queryByText('Fake Discount Detected')).not.toBeInTheDocument();
  });
});
