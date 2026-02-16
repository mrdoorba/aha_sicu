import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { PromoToolsForm } from './PromoToolsForm';
import type { PromoToolsData } from './formConfig';

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
};

describe('PromoToolsForm', () => {
  it('renders all 11 promo tool fields', () => {
    render(<PromoToolsForm data={emptyData} salesMonth0={0} onChange={vi.fn()} onBlur={vi.fn()} />);

    expect(screen.getByLabelText(/Penjualan dari Promo Toko/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Penjualan dari Paket Diskon/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Penjualan dari Kombo Hemat/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Penjualan dari Flash Sale Toko Saya/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Penjualan dari Voucher/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Penjualan dari Shopee Live/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Penjualan dari Game Toko/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Penjualan dari Brand Membership/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Penjualan dari Gratis Ongkir XTRA/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Penjualan dari Chat Broadcast/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Penjualan dari Program Afiliasi/)).toBeInTheDocument();
  });

  it('renders benchmarks for promo tools', () => {
    render(<PromoToolsForm data={emptyData} salesMonth0={0} onChange={vi.fn()} onBlur={vi.fn()} />);

    expect(screen.getByText('Benchmark: >8% dari penjualan')).toBeInTheDocument();
    expect(screen.getByText('Benchmark: >16% dari penjualan')).toBeInTheDocument();
    expect(screen.getByText('Benchmark: >84% dari penjualan')).toBeInTheDocument();
    expect(screen.getByText('Benchmark: >15% dari penjualan')).toBeInTheDocument();
    expect(screen.getByText('Benchmark: >18% dari penjualan')).toBeInTheDocument();
    expect(screen.getByText('Benchmark: >0')).toBeInTheDocument();
  });

  it('renders section title with reference link', () => {
    render(<PromoToolsForm data={emptyData} salesMonth0={0} onChange={vi.fn()} onBlur={vi.fn()} />);
    expect(screen.getByText('Alat Promosi')).toBeInTheDocument();
  });

  it('renders all fields as currency (IDR) inputs', () => {
    render(<PromoToolsForm data={emptyData} salesMonth0={0} onChange={vi.fn()} onBlur={vi.fn()} />);
    const idrLabels = screen.getAllByText('(IDR)');
    expect(idrLabels).toHaveLength(11);
  });

  it('shows % Efektifitas as dash when salesMonth0 is 0', () => {
    render(<PromoToolsForm data={emptyData} salesMonth0={0} onChange={vi.fn()} onBlur={vi.fn()} />);
    expect(screen.getByText('% Efektifitas alat promosi')).toBeInTheDocument();
    // The dash "—" should be in the efektifitas display
    const displays = screen.getAllByText('—');
    expect(displays.length).toBeGreaterThan(0);
  });

  it('computes % Penggunaan correctly', () => {
    const dataWith7Tools: PromoToolsData = {
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
    };
    render(<PromoToolsForm data={dataWith7Tools} salesMonth0={100000000} onChange={vi.fn()} onBlur={vi.fn()} />);
    expect(screen.getByText('64%')).toBeInTheDocument();
  });

  it('computes % Efektifitas excluding tools >= 50% of sales (too dependent)', () => {
    // salesMonth0 = 1,000,000. promoToko = 600,000 (60% of sales → too dependent, even though > 8%)
    // gratisOngkir = 1 (passes absolute >0 check)
    // chatBroadcast = 20,000 (2% > 1% threshold → passes)
    // Expected: 2 pass out of 11 = round(18.18%) = 18%
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
    };
    render(<PromoToolsForm data={data} salesMonth0={1000000} onChange={vi.fn()} onBlur={vi.fn()} />);
    expect(screen.getByText('18%')).toBeInTheDocument();
  });
});
