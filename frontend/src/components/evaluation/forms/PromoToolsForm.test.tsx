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
    render(<PromoToolsForm data={emptyData} onChange={vi.fn()} onBlur={vi.fn()} />);

    expect(screen.getByLabelText(/Promo Toko/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Paket Diskon/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Kombo Hemat/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Flash Sale Toko Saya/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Voucher/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Shopee Live/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Game Toko/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Brand Membership/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Gratis Ongkir XTRA/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Chat Broadcast/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Program Afiliasi/)).toBeInTheDocument();
  });

  it('renders benchmarks for promo tools', () => {
    render(<PromoToolsForm data={emptyData} onChange={vi.fn()} onBlur={vi.fn()} />);

    expect(screen.getByText('Benchmark: >8% dari penjualan')).toBeInTheDocument();
    expect(screen.getByText('Benchmark: >16% dari penjualan')).toBeInTheDocument();
    expect(screen.getByText('Benchmark: >84% dari penjualan')).toBeInTheDocument();
    expect(screen.getByText('Benchmark: >15% dari penjualan')).toBeInTheDocument();
    expect(screen.getByText('Benchmark: >18% dari penjualan')).toBeInTheDocument();
    expect(screen.getByText('Benchmark: >0')).toBeInTheDocument();
  });

  it('renders section title', () => {
    render(<PromoToolsForm data={emptyData} onChange={vi.fn()} onBlur={vi.fn()} />);
    expect(screen.getByText('Promo Tools')).toBeInTheDocument();
  });

  it('renders all fields as currency (IDR) inputs', () => {
    render(<PromoToolsForm data={emptyData} onChange={vi.fn()} onBlur={vi.fn()} />);
    const idrLabels = screen.getAllByText('(IDR)');
    expect(idrLabels).toHaveLength(11);
  });
});
