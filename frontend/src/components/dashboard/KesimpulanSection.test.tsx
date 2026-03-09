import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { KesimpulanSection } from './KesimpulanSection';

describe('KesimpulanSection', () => {
  it('should render conclusion bullet points and both cards when full data provided', () => {
    const calculatorResults = {
      scoring_summary: {
        conclusion: '- Finding A\n- Finding B\n- Finding C',
        marketing_estimation: '22.4% ~ 26.2%',
        marketing_budget: '23%',
      },
    };

    render(<KesimpulanSection calculatorResults={calculatorResults} />);

    expect(screen.getByText('Kesimpulan')).toBeInTheDocument();
    expect(screen.getByText('Finding A')).toBeInTheDocument();
    expect(screen.getByText('Finding B')).toBeInTheDocument();
    expect(screen.getByText('Finding C')).toBeInTheDocument();
    expect(screen.getByText('22.4% ~ 26.2%')).toBeInTheDocument();
    expect(screen.getByText('23%')).toBeInTheDocument();
    expect(screen.getByText('Est. Biaya Marketing')).toBeInTheDocument();
    expect(screen.getByText('Min. Anggaran Marketing')).toBeInTheDocument();
  });

  it('should show no data message when scoring_summary is missing', () => {
    const calculatorResults = {
      ads_keyword: { output_text: 'some data' },
    };

    render(<KesimpulanSection calculatorResults={calculatorResults} />);

    expect(screen.getByText('Kesimpulan')).toBeInTheDocument();
    expect(screen.getByText('Tidak ada data')).toBeInTheDocument();
  });

  it('should hide budget card when marketing_budget is empty', () => {
    const calculatorResults = {
      scoring_summary: {
        conclusion: '- Finding A',
        marketing_estimation: '22.4% ~ 26.2%',
        marketing_budget: '',
      },
    };

    render(<KesimpulanSection calculatorResults={calculatorResults} />);

    expect(screen.getByText('Finding A')).toBeInTheDocument();
    expect(screen.getByText('22.4% ~ 26.2%')).toBeInTheDocument();
    expect(screen.getByText('Est. Biaya Marketing')).toBeInTheDocument();
    expect(screen.queryByText('Min. Anggaran Marketing')).not.toBeInTheDocument();
  });
});
