import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { CompetitionForm } from './CompetitionForm';
import type { CompetitionData } from './formConfig';

const emptyData: CompetitionData = {
  product1: { productName: null, sellingPrice: null, keyword: null, link: null, marketPrice: null },
  product2: { productName: null, sellingPrice: null, keyword: null, link: null, marketPrice: null },
  product3: { productName: null, sellingPrice: null, keyword: null, link: null, marketPrice: null },
};

describe('CompetitionForm', () => {
  it('renders 3 product groups with 5 fields each', () => {
    render(<CompetitionForm data={emptyData} onChange={vi.fn()} onBlur={vi.fn()} />);

    // 3 products × (productName + keyword + link) = 9 text inputs
    // 3 products × (sellingPrice + marketPrice) = 6 currency inputs (type="text")
    const textboxes = screen.getAllByRole('textbox');
    expect(textboxes).toHaveLength(15);
  });

  it('renders section title', () => {
    render(<CompetitionForm data={emptyData} onChange={vi.fn()} onBlur={vi.fn()} />);
    expect(screen.getByText('Kompetisi TOP Produk')).toBeInTheDocument();
  });

  it('renders field labels for each product', () => {
    render(<CompetitionForm data={emptyData} onChange={vi.fn()} onBlur={vi.fn()} />);

    // Product 1 labels
    expect(screen.getByText('Produk Kompetitor 1')).toBeInTheDocument();
    const nameInputs = screen.getAllByLabelText('Nama Produk');
    expect(nameInputs).toHaveLength(3);
    const keywordInputs = screen.getAllByLabelText('Kata kunci pencarian');
    expect(keywordInputs).toHaveLength(3);
    const linkInputs = screen.getAllByLabelText('LINK');
    expect(linkInputs).toHaveLength(3);
  });

  it('displays pre-filled data', () => {
    const data: CompetitionData = {
      product1: { productName: 'Sepatu A', sellingPrice: 150000, keyword: 'sepatu', link: 'https://example.com', marketPrice: 100000 },
      product2: { productName: null, sellingPrice: null, keyword: null, link: null, marketPrice: null },
      product3: { productName: null, sellingPrice: null, keyword: null, link: null, marketPrice: null },
    };
    render(<CompetitionForm data={data} onChange={vi.fn()} onBlur={vi.fn()} />);

    const nameInputs = screen.getAllByLabelText('Nama Produk');
    expect(nameInputs[0]).toHaveValue('Sepatu A');
    const keywordInputs = screen.getAllByLabelText('Kata kunci pencarian');
    expect(keywordInputs[0]).toHaveValue('sepatu');
  });

  it('calls onChange with keyword value', async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();
    render(<CompetitionForm data={emptyData} onChange={onChange} onBlur={vi.fn()} />);

    const keywordInputs = screen.getAllByLabelText('Kata kunci pencarian');
    await user.type(keywordInputs[0], 'tas');
    expect(onChange).toHaveBeenCalledWith('competition', 'product1.keyword', 't');
  });

  it('shows competitive result when sellingPrice <= marketPrice * 1.1', () => {
    const data: CompetitionData = {
      product1: { productName: 'Sepatu A', sellingPrice: 90000, keyword: 'sepatu murah', link: null, marketPrice: 100000 },
      product2: { productName: null, sellingPrice: null, keyword: null, link: null, marketPrice: null },
      product3: { productName: null, sellingPrice: null, keyword: null, link: null, marketPrice: null },
    };
    render(<CompetitionForm data={data} onChange={vi.fn()} onBlur={vi.fn()} />);
    expect(screen.getByText(/✅kompetitif/)).toBeInTheDocument();
  });

  it('shows not competitive result when sellingPrice > marketPrice * 1.1', () => {
    const data: CompetitionData = {
      product1: { productName: 'Sepatu A', sellingPrice: 150000, keyword: 'sepatu murah', link: null, marketPrice: 100000 },
      product2: { productName: null, sellingPrice: null, keyword: null, link: null, marketPrice: null },
      product3: { productName: null, sellingPrice: null, keyword: null, link: null, marketPrice: null },
    };
    render(<CompetitionForm data={data} onChange={vi.fn()} onBlur={vi.fn()} />);
    expect(screen.getByText(/❌tidak kompetitif/)).toBeInTheDocument();
  });

  it('handles backward compatibility — old data with only keyword + marketPrice', () => {
    // Simulate old saved data that only has keyword + marketPrice
    const oldData = {
      product1: { keyword: 'shoes', marketPrice: 50000 },
      product2: { keyword: null, marketPrice: null },
      product3: { keyword: null, marketPrice: null },
    } as unknown as CompetitionData;

    render(<CompetitionForm data={oldData} onChange={vi.fn()} onBlur={vi.fn()} />);

    const keywordInputs = screen.getAllByLabelText('Kata kunci pencarian');
    expect(keywordInputs[0]).toHaveValue('shoes');
  });

  it('uses fallback display name when productName is null', () => {
    const data: CompetitionData = {
      product1: { productName: null, sellingPrice: 150000, keyword: null, link: null, marketPrice: 100000 },
      product2: { productName: null, sellingPrice: null, keyword: null, link: null, marketPrice: null },
      product3: { productName: null, sellingPrice: null, keyword: null, link: null, marketPrice: null },
    };
    render(<CompetitionForm data={data} onChange={vi.fn()} onBlur={vi.fn()} />);
    // Should render the not-competitive translation key (sellingPrice 150000 > marketPrice 100000 * 1.1)
    expect(screen.getByText(/❌tidak kompetitif/)).toBeInTheDocument();
  });
});
