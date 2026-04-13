import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { PromoToolsForm } from './PromoToolsForm';
import type { PromoToolsData } from './formConfig';

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

const emptyData: PromoToolsData = {
  promoToko: null,
  paketDiskon: null,
  komboHemat: null,
  flashSale: null,
  voucher: null,
  shopeeLive: null,
  gameToko: null,
  brandMembership: null,
  gratisOngkir: null,
  chatBroadcast: null,
  programAfiliasi: null,
  komisiProgramAfiliasi: null,
};

describe('PromoToolsForm', () => {
  it('renders all 12 promo tool fields', () => {
    render(<PromoToolsForm data={emptyData} salesMonth0={0} onChange={vi.fn()} onBlur={vi.fn()} />);

    expect(screen.getByLabelText(/fields\.promoTools\.promoToko/)).toBeInTheDocument();
    expect(screen.getByLabelText(/fields\.promoTools\.paketDiskon/)).toBeInTheDocument();
    expect(screen.getByLabelText(/fields\.promoTools\.komboHemat/)).toBeInTheDocument();
    expect(screen.getByLabelText(/fields\.promoTools\.flashSale/)).toBeInTheDocument();
    expect(screen.getByLabelText(/fields\.promoTools\.voucher/)).toBeInTheDocument();
    expect(screen.getByLabelText(/fields\.promoTools\.shopeeLive/)).toBeInTheDocument();
    expect(screen.getByLabelText(/fields\.promoTools\.gameToko/)).toBeInTheDocument();
    expect(screen.getByLabelText(/fields\.promoTools\.brandMembership/)).toBeInTheDocument();
    expect(screen.getByLabelText(/fields\.promoTools\.gratisOngkir/)).toBeInTheDocument();
    expect(screen.getByLabelText(/fields\.promoTools\.chatBroadcast/)).toBeInTheDocument();
    expect(screen.getByLabelText(/fields\.promoTools\.programAfiliasi/)).toBeInTheDocument();
    expect(screen.getByLabelText(/fields\.promoTools\.komisiProgramAfiliasi/)).toBeInTheDocument();
  });

  it('renders affiliate commission immediately after affiliate sales', () => {
    render(<PromoToolsForm data={emptyData} salesMonth0={0} onChange={vi.fn()} onBlur={vi.fn()} />);

    const affiliateSales = screen.getByLabelText(/fields\.promoTools\.programAfiliasi/);
    const affiliateCommission = screen.getByLabelText(/fields\.promoTools\.komisiProgramAfiliasi/);

    expect(affiliateSales.compareDocumentPosition(affiliateCommission)).toBe(Node.DOCUMENT_POSITION_FOLLOWING);
  });

  it('renders benchmarks for promo tools', () => {
    render(<PromoToolsForm data={emptyData} salesMonth0={0} onChange={vi.fn()} onBlur={vi.fn()} />);

    expect(screen.getByText('Benchmark: fields.promoTools.promoToko.benchmark')).toBeInTheDocument();
    expect(screen.getByText('Benchmark: fields.promoTools.paketDiskon.benchmark')).toBeInTheDocument();
    expect(screen.getByText('Benchmark: fields.promoTools.voucher.benchmark')).toBeInTheDocument();
    expect(screen.getByText('Benchmark: fields.promoTools.shopeeLive.benchmark')).toBeInTheDocument();
    expect(screen.getByText('Benchmark: fields.promoTools.programAfiliasi.benchmark')).toBeInTheDocument();
    expect(screen.getByText('Benchmark: >0')).toBeInTheDocument();
    expect(screen.queryByText('Benchmark: fields.promoTools.komisiProgramAfiliasi.benchmark')).not.toBeInTheDocument();
  });

  it('renders section title with reference link', () => {
    render(<PromoToolsForm data={emptyData} salesMonth0={0} onChange={vi.fn()} onBlur={vi.fn()} />);
    expect(screen.getByText('forms.promoTools.title')).toBeInTheDocument();
  });

  it('renders all fields as currency (IDR) inputs', () => {
    render(<PromoToolsForm data={emptyData} salesMonth0={0} onChange={vi.fn()} onBlur={vi.fn()} />);
    const idrLabels = screen.getAllByText('(IDR)');
    expect(idrLabels).toHaveLength(12);
  });

  it('shows % Efektifitas as dash when salesMonth0 is 0', () => {
    render(<PromoToolsForm data={emptyData} salesMonth0={0} onChange={vi.fn()} onBlur={vi.fn()} />);
    expect(screen.getByText('forms.promoTools.effectivenessPct')).toBeInTheDocument();
    // The dash "—" should be in the efektifitas display
    const displays = screen.getAllByText('—');
    expect(displays.length).toBeGreaterThan(0);
  });

  it('computes % Penggunaan correctly', () => {
    const dataWith7MetricTools: PromoToolsData = {
      promoToko: 100,
      paketDiskon: 200,
      komboHemat: 300,
      flashSale: 400,
      voucher: 500,
      shopeeLive: 600,
      gameToko: 700,
      brandMembership: null,
      gratisOngkir: null,
      chatBroadcast: null,
      programAfiliasi: null,
      komisiProgramAfiliasi: 800,
    };
    render(<PromoToolsForm data={dataWith7MetricTools} salesMonth0={100000000} onChange={vi.fn()} onBlur={vi.fn()} />);
    expect(screen.getByText('64%')).toBeInTheDocument();
  });

  it('computes % Efektifitas excluding tools >= 50% of sales (too dependent)', () => {
    // salesMonth0 = 1,000,000. promoToko = 600,000 (60% of sales → too dependent, even though > 8%)
    // gratisOngkir = 1 (passes absolute >0 check)
    // chatBroadcast = 20,000 (2% > 1% threshold → passes)
    // Expected: 2 pass out of 11 metric-bearing tools = round(18.18%) = 18%
    const data: PromoToolsData = {
      promoToko: 600000,      // 60% of sales → too dependent → ❌
      paketDiskon: null,
      komboHemat: null,
      flashSale: null,
      voucher: null,
      shopeeLive: null,
      gameToko: null,
      brandMembership: null,
      gratisOngkir: 1,        // >0 → ✔️
      chatBroadcast: 20000,   // 2% > 1% → ✔️
      programAfiliasi: null,
      komisiProgramAfiliasi: 5000,
    };
    render(<PromoToolsForm data={data} salesMonth0={1000000} onChange={vi.fn()} onBlur={vi.fn()} />);
    expect(screen.getByText('18%')).toBeInTheDocument();
  });
});
