import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { AdsKeywordResults } from './AdsKeywordResults';
import type { CalculatorResult } from '../../../hooks/useCalculator';

const SAMPLE_RESULT: CalculatorResult = {
  calculator_type: 'ads_keyword',
  output_text:
    '34 dari 80 produk (42.5%) sudah beriklan\nIklan Produk: 20\nIklan Toko: 14',
  details: {
    ak2: '34 dari 80 produk',
    ak3: 'breakdown',
    ak4: 'flags',
    al2: '',
    al3: '',
    al5: '',
    al6: '',
    al7: '',
    al8: '',
    al9: '',
    thresholds: { am6: 0, am7: 0, am9: 0, am10: 0 },
  },
  calculated_at: '2026-02-11T10:00:00Z',
};

describe('AdsKeywordResults', () => {
  it('renders output_text preserving line breaks', () => {
    render(<AdsKeywordResults result={SAMPLE_RESULT} />);

    const pre = screen.getByText(/34 dari 80 produk/);
    expect(pre).toBeInTheDocument();
    expect(pre.tagName).toBe('PRE');
    expect(pre.textContent).toContain('Iklan Produk: 20');
    expect(pre.textContent).toContain('Iklan Toko: 14');
  });

  it('renders calculated_at timestamp', () => {
    render(<AdsKeywordResults result={SAMPLE_RESULT} />);

    const time = screen.getByRole('time');
    expect(time).toBeInTheDocument();
  });
});
