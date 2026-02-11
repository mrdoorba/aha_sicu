import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { CompetitionForm } from './CompetitionForm';
import type { CompetitionData } from './formConfig';

const emptyData: CompetitionData = {
  product1: { keyword: null, marketPrice: null },
  product2: { keyword: null, marketPrice: null },
  product3: { keyword: null, marketPrice: null },
};

describe('CompetitionForm', () => {
  it('renders 3 product groups with keyword + price fields', () => {
    render(<CompetitionForm data={emptyData} onChange={vi.fn()} onBlur={vi.fn()} />);

    expect(screen.getByLabelText(/Produk Kompetitor 1 — Keyword/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Produk Kompetitor 1 — Harga Pasar/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Produk Kompetitor 2 — Keyword/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Produk Kompetitor 2 — Harga Pasar/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Produk Kompetitor 3 — Keyword/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Produk Kompetitor 3 — Harga Pasar/)).toBeInTheDocument();
  });

  it('renders 3 text inputs for keywords and 3 currency inputs for prices', () => {
    render(<CompetitionForm data={emptyData} onChange={vi.fn()} onBlur={vi.fn()} />);

    // 3 keyword text inputs + 3 market price text inputs (currency fields use type="text")
    const textboxes = screen.getAllByRole('textbox');
    expect(textboxes).toHaveLength(6);
  });

  it('renders section title', () => {
    render(<CompetitionForm data={emptyData} onChange={vi.fn()} onBlur={vi.fn()} />);
    expect(screen.getByText('Competition')).toBeInTheDocument();
  });

  it('displays pre-filled data', () => {
    const data: CompetitionData = {
      product1: { keyword: 'sepatu', marketPrice: 250000 },
      product2: { keyword: null, marketPrice: null },
      product3: { keyword: null, marketPrice: null },
    };
    render(<CompetitionForm data={data} onChange={vi.fn()} onBlur={vi.fn()} />);

    const keywordInput = screen.getByLabelText(/Produk Kompetitor 1 — Keyword/);
    expect(keywordInput).toHaveValue('sepatu');
  });

  it('calls onChange with keyword value', async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();
    render(<CompetitionForm data={emptyData} onChange={onChange} onBlur={vi.fn()} />);

    const keywordInput = screen.getByLabelText(/Produk Kompetitor 1 — Keyword/);
    await user.type(keywordInput, 'tas');
    expect(onChange).toHaveBeenCalledWith('competition', 'product1.keyword', 't');
  });
});
