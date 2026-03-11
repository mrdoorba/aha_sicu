import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { AdsKeywordResults } from './AdsKeywordResults';
import type { CalculatorResult } from '../../../hooks/useCalculator';

// Mock react-i18next
vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string, vars?: Record<string, string>) => {
      if (key.startsWith('ads.flag.')) return `[${key}]`;
      if (key.startsWith('ads.value.')) return `[${key}]`;
      if (vars && Object.keys(vars).length > 0) {
        let result = key;
        for (const [k, v] of Object.entries(vars)) {
          result += ` ${k}=${v}`;
        }
        return result;
      }
      return key;
    },
  }),
}));

const SAMPLE_RESULT_WITH_I18N: CalculatorResult = {
  calculator_type: 'ads_keyword',
  output_text: '• Total Iklan: 1 Aktif, 0 Dijeda dan 0 Berakhir.\n• Melibatkan 1 produk',
  details: {
    ak2: '• Total Iklan: 1 Aktif',
    ak3: 'breakdown',
    ak4: 'flags',
    al2: '',
    al3: '',
    al5: '',
    al6: '',
    al7: '',
    al8: '',
    al9: '',
    ak2_i18n: { key: 'ads.summary', vars: { active: '1', paused: '0', ended: '0', unique_count: '1', product_pct: '10.0%', total_products: '10' } },
    ak3_i18n: { key: 'ads.typeBreakdown', vars: { semua_total: '1', toko_total: '0', toko_auto: '0', toko_manual: '0' } },
    ak4_i18n: [{ key: 'ads.flag.productLow', vars: {} }],
    al2_i18n: null,
    al3_i18n: null,
    al5_i18n: null,
    al6_i18n: null,
    al7_i18n: null,
    al8_i18n: null,
    al9_i18n: null,
    thresholds: { am6: 0, am7: 0, am9: 0, am10: 0 },
  },
  calculated_at: '2026-02-11T10:00:00Z',
};

describe('AdsKeywordResults', () => {
  it('should render pre element with presentation role', () => {
    render(<AdsKeywordResults result={SAMPLE_RESULT_WITH_I18N} />);
    const pre = screen.getByRole('presentation');
    expect(pre).toBeInTheDocument();
    expect(pre.tagName).toBe('PRE');
  });

  it('should render translated content when i18n data is present', () => {
    render(<AdsKeywordResults result={SAMPLE_RESULT_WITH_I18N} />);
    expect(screen.getByRole('presentation').textContent).toContain('ads.summary');
  });

  it('should render calculated_at timestamp', () => {
    render(<AdsKeywordResults result={SAMPLE_RESULT_WITH_I18N} />);
    const time = screen.getByRole('time');
    expect(time).toBeInTheDocument();
  });

  it('should fall back to raw text when no i18n data', () => {
    const resultNoI18n: CalculatorResult = {
      ...SAMPLE_RESULT_WITH_I18N,
      details: {
        ak2: 'raw ak2 text',
        ak3: 'raw ak3',
        ak4: 'raw ak4',
        al2: '', al3: '', al5: '', al6: '', al7: '', al8: '', al9: '',
        thresholds: { am6: 0, am7: 0, am9: 0, am10: 0 },
      },
    };
    render(<AdsKeywordResults result={resultNoI18n} />);
    expect(screen.getByRole('presentation').textContent).toContain('raw ak2 text');
  });
});
