import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { OperationalForm } from './OperationalForm';
import { VisitorsForm } from './VisitorsForm';
import { ProductsStatusForm } from './ProductsStatusForm';
import type { OperationalData, VisitorsData, ProductsData } from './formConfig';
import type { ScoringRules } from '../../../hooks/useRules';

function makeRules(overrides: Partial<ScoringRules> = {}): ScoringRules {
  return {
    operational: {
      unfulfilled_order_rate: { threshold: 2.0, comparison: 'lte' },
      late_shipment_rate: { threshold: 2.0, comparison: 'lte' },
      preparation_time: { threshold: 2, comparison: 'lte' },
      chat_response_rate: { threshold: 90, comparison: 'gte' },
      overall_rating: { threshold: 4.5, comparison: 'gte' },
    },
    business: {
      conversion_rate: { threshold: 5.0, comparison: 'gte' },
    },
    visitors: {
      followers: { threshold: 100000, comparison: 'gte' },
    },
    promo_tools: {},
    products_status: {
      product_count: { threshold: 50, comparison: 'gte' },
    },
    ads: {},
    campaign: {},
    stock: {},
    discount: {},
    marketing: {},
    interpretation: { ranges: [] },
    ...overrides,
  };
}

const emptyOperational: OperationalData = {
  unfulfilledOrderRate: null,
  lateShipmentRate: null,
  preparationTime: null,
  chatResponseRate: null,
  overallRating: null,
};

const emptyVisitors: VisitorsData = {
  totalVisitors: null,
  totalFollowers: null,
  returningVisitors: null,
};

const emptyProducts: ProductsData = {
  productCount: null,
  storeStatus: null,
};

describe('Static fallback benchmarks when rules are not loaded', () => {
  it('OperationalForm shows static benchmarks without rules', () => {
    render(<OperationalForm data={emptyOperational} onChange={vi.fn()} onBlur={vi.fn()} />);

    const lessThan1Pct = screen.getAllByText('Benchmark: <1%');
    expect(lessThan1Pct).toHaveLength(2);
    expect(screen.getByText('Benchmark: <1')).toBeInTheDocument();
    expect(screen.getByText('Benchmark: >95%')).toBeInTheDocument();
    expect(screen.getByText('Benchmark: >4.7')).toBeInTheDocument();
  });

  it('VisitorsForm shows static benchmarks without rules', () => {
    render(<VisitorsForm data={emptyVisitors} storeLink={null} onChange={vi.fn()} onBlur={vi.fn()} />);

    expect(screen.getByText('Benchmark: >50,000')).toBeInTheDocument();
  });

  it('ProductsStatusForm shows static benchmarks without rules', () => {
    render(<ProductsStatusForm data={emptyProducts} storeLink={null} onChange={vi.fn()} onBlur={vi.fn()} />);

    expect(screen.getByText('Benchmark: >=35')).toBeInTheDocument();
    expect(screen.getByText('Benchmark: Shopee Mall')).toBeInTheDocument();
  });
});

describe('Dynamic benchmarks from rules', () => {
  describe('OperationalForm', () => {
    it('displays dynamic benchmarks from rules', () => {
      const rules = makeRules();
      render(<OperationalForm data={emptyOperational} rules={rules} onChange={vi.fn()} onBlur={vi.fn()} />);

      const lessThan2Pct = screen.getAllByText('Benchmark: <2%');
      expect(lessThan2Pct).toHaveLength(2); // unfulfilled + late shipment
      expect(screen.getByText('Benchmark: <2')).toBeInTheDocument(); // preparation time
      expect(screen.getByText('Benchmark: >90%')).toBeInTheDocument(); // chat response
      expect(screen.getByText('Benchmark: >4.5')).toBeInTheDocument(); // overall rating
    });
  });

  describe('VisitorsForm', () => {
    it('displays dynamic follower benchmark from rules', () => {
      const rules = makeRules();
      render(<VisitorsForm data={emptyVisitors} storeLink={null} rules={rules} onChange={vi.fn()} onBlur={vi.fn()} />);

      expect(screen.getByText('Benchmark: >100,000')).toBeInTheDocument();
    });
  });

  describe('ProductsStatusForm', () => {
    it('displays dynamic product count benchmark from rules', () => {
      const rules = makeRules();
      render(<ProductsStatusForm data={emptyProducts} storeLink={null} rules={rules} onChange={vi.fn()} onBlur={vi.fn()} />);

      expect(screen.getByText('Benchmark: >50')).toBeInTheDocument();
    });
  });
});
