import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { OperationalForm } from './OperationalForm';
import type { OperationalData } from './formConfig';

const emptyData: OperationalData = {
  unfulfilledOrderRate: null,
  lateShipmentRate: null,
  preparationTime: null,
  chatResponseRate: null,
  overallRating: null,
};

describe('OperationalForm', () => {
  it('renders all 5 operational fields', () => {
    render(<OperationalForm data={emptyData} onChange={vi.fn()} onBlur={vi.fn()} />);

    expect(screen.getByLabelText(/Pesanan Tidak Terselesaikan/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Keterlambatan/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Masa Pengemasan/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Chat Dibalas/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Penilaian/)).toBeInTheDocument();
  });

  it('renders benchmarks for each field', () => {
    render(<OperationalForm data={emptyData} onChange={vi.fn()} onBlur={vi.fn()} />);

    // <1% appears twice (unfulfilledOrderRate + lateShipmentRate)
    const lessThan1Pct = screen.getAllByText('Benchmark: <1%');
    expect(lessThan1Pct).toHaveLength(2);
    expect(screen.getByText('Benchmark: <1')).toBeInTheDocument();
    expect(screen.getByText('Benchmark: >95%')).toBeInTheDocument();
    expect(screen.getByText('Benchmark: >4.7')).toBeInTheDocument();
  });

  it('renders section title', () => {
    render(<OperationalForm data={emptyData} onChange={vi.fn()} onBlur={vi.fn()} />);
    expect(screen.getByText('Operational')).toBeInTheDocument();
  });

  it('displays pre-filled values', () => {
    const data: OperationalData = {
      unfulfilledOrderRate: 0.5,
      lateShipmentRate: 0.3,
      preparationTime: 0.8,
      chatResponseRate: 97,
      overallRating: 4.8,
    };
    render(<OperationalForm data={data} onChange={vi.fn()} onBlur={vi.fn()} />);

    const inputs = screen.getAllByRole('spinbutton');
    expect(inputs[0]).toHaveValue(0.5);
    expect(inputs[4]).toHaveValue(4.8);
  });
});
