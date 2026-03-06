import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { PresentationDashboard } from './PresentationDashboard';
import { MemoryRouter } from 'react-router-dom';

/*
Feature: Partner Dashboard Score Exclusion

  Scenario: Rata² Penjualan is excluded from all counts
    Given the backend provides a score breakdown containing "Rata² Penjualan 6 bulan terakhir"
    When viewing the presentation dashboard
    Then the "Rata² Penjualan 6 bulan terakhir" metric should not be rendered in the Detailed Evaluation
    And its checkmark should not be counted in the Score Overview or Breakdown Chart
*/

vi.mock('../../hooks/useBrandDetail', () => ({
    useBrandDetail: () => ({ data: { brand_name: 'Test Brand' }, isLoading: false }),
}));

vi.mock('../../hooks/useBrandEvaluations', () => ({
    useBrandEvaluations: () => ({ evaluations: [{ id: 1 }], isLoading: false }),
}));

vi.mock('../../hooks/useEvaluationDetail', () => ({
    useEvaluationDetail: () => ({
        evaluation: {
            id: 1,
            brand_name: 'Test Brand',
            final_score: 50,
            verdict: 'Disetujui',
            template: 'non_fashion',
            period: 'Jan 2026',
            score_breakdown: [
                {
                    category: 'Bisnis Analisis',
                    score: 10,
                    max_score: 20,
                    rows: [
                        {
                            metric: 'Rata² Penjualan 6 bulan terakhir',
                            value: 100000000,
                            benchmark: '>100,000,000',
                            verdict: '✔️',
                            message: '✔️ Rata² Penjualan 6 bulan terakhir = IDR 100,000,000 [Sudah Baik]',
                            score: 10
                        },
                        {
                            metric: 'Penjualan Bulan Jan 2026',
                            value: 120000000,
                            benchmark: '-',
                            verdict: '✔️',
                            message: '✔️ Penjualan OK',
                            score: 10
                        }
                    ]
                }
            ],
            calculator_results: {},
            brand_raw_data: { email: null, pic_name: null, store_link: null, kategori: null }
        },
        isLoading: false
    }),
}));

describe('PresentationDashboard BDD', () => {
    it('excludes Rata² Penjualan 6 bulan terakhir from rendering', () => {
        // Arrange
        const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
        render(
            <QueryClientProvider client={queryClient}>
                <MemoryRouter>
                    <PresentationDashboard brandId={123} onBack={vi.fn()} />
                </MemoryRouter>
            </QueryClientProvider>
        );

        // Act (implicit render)

        // Assert
        // Verify that the other metric IS rendered (sanity check)
        expect(screen.getByText('Penjualan Bulan Jan 2026')).toBeInTheDocument();

        // Verify that Rata² Penjualan is strictly NOT rendered anywhere
        expect(screen.queryByText('Rata² Penjualan 6 bulan terakhir')).not.toBeInTheDocument();
    });
});
