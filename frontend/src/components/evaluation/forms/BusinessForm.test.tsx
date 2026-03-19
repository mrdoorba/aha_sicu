import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { BusinessForm } from './BusinessForm';
import type { BusinessData } from './formConfig';
import type { ScoringRules } from '../../../hooks/useRules';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string, opts?: Record<string, string>) => {
      if (opts) return `${key}::${JSON.stringify(opts)}`;
      return key;
    },
    i18n: { language: 'id' },
  }),
  Trans: ({ i18nKey }: { i18nKey: string }) => i18nKey,
}));

const emptyData: BusinessData = {
  salesStartMonth: null,
  salesMonth0: null,
  salesMonth1: null,
  salesMonth2: null,
  salesMonth3: null,
  salesMonth4: null,
  salesMonth5: null,
  conversionRate: null,
};

function makeRules(overrides: Partial<ScoringRules> = {}): ScoringRules {
  return {
    operational: {},
    business: {
      conversion_rate: { threshold: 3.0, comparison: 'gte' },
    },
    visitors: {},
    promo_tools: {},
    products_status: {},
    ads: {},
    campaign: {},
    stock: {},
    discount: {},
    marketing: {},
    interpretation: { ranges: [] },
    ...overrides,
  };
}

describe('BusinessForm', () => {
  it('renders all 7 business fields', () => {
    render(
      <BusinessForm data={emptyData} onChange={vi.fn()} onBlur={vi.fn()} />,
    );

    // 6 sales month currency fields + 1 conversion rate
    const salesFields = screen.getAllByLabelText(/forms\.business\.salesMonth/);
    expect(salesFields).toHaveLength(6);
    expect(screen.getByLabelText(/forms\.business\.conversionRate/)).toBeInTheDocument();
  });

  it('shows benchmark from rules when rules are provided', () => {
    const rules = makeRules({
      business: {
        conversion_rate: { threshold: 5.0, comparison: 'gte' },
      },
    });
    render(
      <BusinessForm data={emptyData} rules={rules} onChange={vi.fn()} onBlur={vi.fn()} />,
    );
    expect(screen.getByText('Benchmark: >5%')).toBeInTheDocument();
  });

  it('shows static fallback benchmark when rules are not provided', () => {
    render(
      <BusinessForm data={emptyData} onChange={vi.fn()} onBlur={vi.fn()} />,
    );
    expect(screen.getByText('Benchmark: >3%')).toBeInTheDocument();
  });

  it('renders section title with reference link', () => {
    render(
      <BusinessForm data={emptyData} onChange={vi.fn()} onBlur={vi.fn()} />,
    );
    expect(screen.getByText('forms.business.title')).toBeInTheDocument();
  });

  it('renders 6 currency fields for sales months', () => {
    render(
      <BusinessForm data={emptyData} onChange={vi.fn()} onBlur={vi.fn()} />,
    );
    const idrLabels = screen.getAllByText('(IDR)');
    expect(idrLabels).toHaveLength(6);
  });

  it('renders month selector dropdown', () => {
    render(
      <BusinessForm data={emptyData} onChange={vi.fn()} onBlur={vi.fn()} />,
    );
    expect(screen.getByLabelText(/forms\.business\.startMonth/)).toBeInTheDocument();
  });

  it('generates dynamic labels when salesStartMonth is set', () => {
    const dataWithMonth: BusinessData = {
      ...emptyData,
      salesStartMonth: '2026-01',
    };
    render(
      <BusinessForm data={dataWithMonth} onChange={vi.fn()} onBlur={vi.fn()} />,
    );
    // t('forms.business.salesMonth', { month: t('Jan 2026') }) → 'forms.business.salesMonth::{"month":"Jan 2026"}'
    expect(screen.getByLabelText(/forms\.business\.salesMonth.*Jan 2026/)).toBeInTheDocument();
  });

  it('uses generic fallback labels when salesStartMonth is null', () => {
    render(
      <BusinessForm data={emptyData} onChange={vi.fn()} onBlur={vi.fn()} />,
    );
    // t('forms.business.salesMonth', { month: t('generic.thisMonth') }) → 'forms.business.salesMonth::{"month":"generic.thisMonth"}'
    expect(screen.getByLabelText(/forms\.business\.salesMonth.*generic\.thisMonth/)).toBeInTheDocument();
  });

  it('uses generic fallback labels when salesStartMonth is invalid', () => {
    const dataInvalid: BusinessData = {
      ...emptyData,
      salesStartMonth: 'abc',
    };
    render(
      <BusinessForm data={dataInvalid} onChange={vi.fn()} onBlur={vi.fn()} />,
    );
    expect(screen.getByLabelText(/forms\.business\.salesMonth.*generic\.thisMonth/)).toBeInTheDocument();
  });

  it('shows computed average when sales data is present', () => {
    const dataWithSales: BusinessData = {
      ...emptyData,
      salesMonth0: 50000000,
      salesMonth1: 48000000,
      salesMonth2: 45000000,
      salesMonth3: 40000000,
      salesMonth4: 42000000,
      salesMonth5: 44000000,
    };
    render(
      <BusinessForm data={dataWithSales} onChange={vi.fn()} onBlur={vi.fn()} />,
    );
    expect(screen.getByText('forms.business.averageSales')).toBeInTheDocument();
    // Average = 44833333.33... → should show formatted IDR
    expect(screen.getByText(/44,833,333/)).toBeInTheDocument();
  });

  it('shows dash when all sales months are null', () => {
    render(
      <BusinessForm data={emptyData} onChange={vi.fn()} onBlur={vi.fn()} />,
    );
    expect(screen.getByText('forms.business.averageSales')).toBeInTheDocument();
    expect(screen.getByText('—')).toBeInTheDocument();
  });

  it('calls onChange for month selector', async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();
    render(
      <BusinessForm data={emptyData} onChange={onChange} onBlur={vi.fn()} />,
    );

    const select = screen.getByLabelText(/forms\.business\.startMonth/);
    await user.selectOptions(select, select.querySelector('option:nth-child(2)')!);
    expect(onChange).toHaveBeenCalledWith('business', 'salesStartMonth', expect.any(String));
  });
});
