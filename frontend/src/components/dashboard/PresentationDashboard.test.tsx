import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { PresentationDashboard } from './PresentationDashboard';
import { MemoryRouter } from 'react-router-dom';

/*
Feature: Partner Dashboard Rata² Penjualan Card

  Scenario: Rata² Penjualan is displayed as an informational card
    Given the backend provides a score breakdown containing "Rata² Penjualan 6 bulan terakhir"
    When viewing the presentation dashboard
    Then the "Rata² Penjualan 6 bulan terakhir" metric should be rendered in the Detailed Evaluation
*/

const mockUseFeatureFlags = vi.fn();

vi.mock('../../hooks/useFeatureFlags', () => ({
    useFeatureFlags: () => mockUseFeatureFlags(),
}));

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
    beforeEach(() => {
        mockUseFeatureFlags.mockReturnValue({ data: { email_enabled: true } });
    });

    it('renders Rata² Penjualan 6 bulan terakhir as an informational card', () => {
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
        expect(screen.getByText('Penjualan Bulan Jan 2026')).toBeInTheDocument();
        expect(screen.getByText('Rata² Penjualan 6 bulan terakhir')).toBeInTheDocument();
    });

    it('clicking "Kirim Email" button opens SendEmailDialog', () => {
        // Arrange
        const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
        render(
            <QueryClientProvider client={queryClient}>
                <MemoryRouter>
                    <PresentationDashboard brandId={123} onBack={vi.fn()} />
                </MemoryRouter>
            </QueryClientProvider>
        );

        // Act - click the send email button (rendered with actual i18n translation)
        const sendButton = screen.getByRole('button', { name: /Kirim Email/i });
        fireEvent.click(sendButton);

        // Assert - dialog should now be open with its title visible
        // SendEmailDialog uses useTranslation so the title renders as the translated string
        expect(screen.getByText('Kirim Laporan Email')).toBeInTheDocument();
    });

    it('should hide send email button when email_enabled is false', () => {
        // Arrange
        mockUseFeatureFlags.mockReturnValue({ data: { email_enabled: false } });
        const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
        render(
            <QueryClientProvider client={queryClient}>
                <MemoryRouter>
                    <PresentationDashboard brandId={123} onBack={vi.fn()} />
                </MemoryRouter>
            </QueryClientProvider>
        );

        // Assert
        expect(screen.queryByRole('button', { name: /Kirim Email/i })).not.toBeInTheDocument();
    });

    it('should hide send email button when feature flags are loading', () => {
        // Arrange
        mockUseFeatureFlags.mockReturnValue({ data: undefined });
        const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
        render(
            <QueryClientProvider client={queryClient}>
                <MemoryRouter>
                    <PresentationDashboard brandId={123} onBack={vi.fn()} />
                </MemoryRouter>
            </QueryClientProvider>
        );

        // Assert
        expect(screen.queryByRole('button', { name: /Kirim Email/i })).not.toBeInTheDocument();
    });
});
