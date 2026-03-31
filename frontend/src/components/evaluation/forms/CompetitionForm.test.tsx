import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { CompetitionForm } from './CompetitionForm';
import { buildShopeeSearchUrl, localizeShopeeLink } from './competitionUtils';
import type { CompetitionData } from './formConfig';

const emptyData: CompetitionData = {
  product1: { productName: null, sellingPrice: null, keyword: null, link: null, marketPrice: null },
  product2: { productName: null, sellingPrice: null, keyword: null, link: null, marketPrice: null },
  product3: { productName: null, sellingPrice: null, keyword: null, link: null, marketPrice: null },
};

describe('buildShopeeSearchUrl', () => {
  it('returns full URL when both sellingPrice and keyword are present', () => {
    const url = buildShopeeSearchUrl(85000, 'kaos polos');
    expect(url).toBe(
      'https://shopee.co.id/search?keyword=kaos+polos&maxPrice=93500&minPrice=63750&noCorrection=true&page=0&ratingFilter=4&sortBy=sales',
    );
  });

  it('returns thailand domain when marketplace is TH', () => {
    const url = buildShopeeSearchUrl(85000, 'kaos polos', 'TH');
    expect(url).toBe(
      'https://shopee.co.th/search?keyword=kaos+polos&maxPrice=93500&minPrice=63750&noCorrection=true&page=0&ratingFilter=4&sortBy=sales',
    );
  });

  it('returns null when sellingPrice is null', () => {
    expect(buildShopeeSearchUrl(null, 'kaos polos')).toBeNull();
  });

  it('returns null when keyword is null', () => {
    expect(buildShopeeSearchUrl(85000, null)).toBeNull();
  });

  it('returns null when both inputs are null', () => {
    expect(buildShopeeSearchUrl(null, null)).toBeNull();
  });

  it('URL-encodes keyword with spaces', () => {
    const url = buildShopeeSearchUrl(100000, 'kaos polos pria')!;
    expect(url).toContain('keyword=kaos+polos+pria');
  });

  it('URL-encodes keyword with special characters', () => {
    const url = buildShopeeSearchUrl(100000, 'tas & dompet')!;
    expect(url).toContain('keyword=tas+%26+dompet');
  });

  it('rounds maxPrice and minPrice to integers', () => {
    const url = buildShopeeSearchUrl(33333, 'test')!;
    // 33333 * 1.10 = 36666.3 → 36666
    // 33333 * 0.75 = 24999.75 → 25000
    expect(url).toContain('maxPrice=36666');
    expect(url).toContain('minPrice=25000');
  });
});

describe('localizeShopeeLink', () => {
  it('rewrites existing buyer links to thailand domain', () => {
    expect(localizeShopeeLink('https://shopee.co.id/search?keyword=test', 'TH')).toBe(
      'https://shopee.co.th/search?keyword=test',
    );
  });
});

describe('CompetitionForm', () => {
  it('renders 3 product groups with input fields', () => {
    render(<CompetitionForm data={emptyData} onChange={vi.fn()} onBlur={vi.fn()} />);

    // 3 products × (productName + keyword) = 6 text inputs
    // 3 products × (sellingPrice + marketPrice) = 6 currency inputs (type="text")
    // link is now auto-computed (not an input)
    const textboxes = screen.getAllByRole('textbox');
    expect(textboxes).toHaveLength(12);
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
    const linkLabels = screen.getAllByText('LINK');
    expect(linkLabels).toHaveLength(3);
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
    const oldData: CompetitionData = {
      product1: { productName: null, sellingPrice: null, keyword: 'shoes', link: null, marketPrice: 50000 },
      product2: { productName: null, sellingPrice: null, keyword: null, link: null, marketPrice: null },
      product3: { productName: null, sellingPrice: null, keyword: null, link: null, marketPrice: null },
    };

    render(<CompetitionForm data={oldData} onChange={vi.fn()} onBlur={vi.fn()} />);

    const keywordInputs = screen.getAllByLabelText('Kata kunci pencarian');
    expect(keywordInputs[0]).toHaveValue('shoes');
  });

  it('emits computed link when keyword is typed and sellingPrice exists', async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();
    const data: CompetitionData = {
      product1: { productName: null, sellingPrice: 100000, keyword: null, link: null, marketPrice: null },
      product2: { productName: null, sellingPrice: null, keyword: null, link: null, marketPrice: null },
      product3: { productName: null, sellingPrice: null, keyword: null, link: null, marketPrice: null },
    };
    render(<CompetitionForm data={data} onChange={onChange} onBlur={vi.fn()} />);

    const keywordInputs = screen.getAllByLabelText('Kata kunci pencarian');
    await user.type(keywordInputs[0], 'a');

    expect(onChange).toHaveBeenCalledWith(
      'competition',
      'product1.link',
      buildShopeeSearchUrl(100000, 'a'),
    );
  });

  it('emits null link when keyword is typed without sellingPrice', async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();
    render(<CompetitionForm data={emptyData} onChange={onChange} onBlur={vi.fn()} />);

    const keywordInputs = screen.getAllByLabelText('Kata kunci pencarian');
    await user.type(keywordInputs[0], 'a');

    expect(onChange).toHaveBeenCalledWith('competition', 'product1.link', null);
  });

  it('emits computed link when sellingPrice is typed and keyword exists', async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();
    const data: CompetitionData = {
      product1: { productName: null, sellingPrice: null, keyword: 'sepatu', link: null, marketPrice: null },
      product2: { productName: null, sellingPrice: null, keyword: null, link: null, marketPrice: null },
      product3: { productName: null, sellingPrice: null, keyword: null, link: null, marketPrice: null },
    };
    render(<CompetitionForm data={data} onChange={onChange} onBlur={vi.fn()} />);

     
    const priceInput = document.getElementById('competition.product1.sellingPrice')!;
    await user.type(priceInput, '5');

    expect(onChange).toHaveBeenCalledWith(
      'competition',
      'product1.link',
      buildShopeeSearchUrl(5, 'sepatu'),
    );
  });

  it('renders clickable link when link data is present', () => {
    const data: CompetitionData = {
      product1: { productName: null, sellingPrice: 100000, keyword: 'test', link: 'https://shopee.co.id/search?keyword=test', marketPrice: null },
      product2: { productName: null, sellingPrice: null, keyword: null, link: null, marketPrice: null },
      product3: { productName: null, sellingPrice: null, keyword: null, link: null, marketPrice: null },
    };
    render(<CompetitionForm data={data} onChange={vi.fn()} onBlur={vi.fn()} />);

    const link = screen.getByText('Lihat di Shopee');
    expect(link).toBeInTheDocument();
    expect(link.tagName).toBe('A');
    expect(link).toHaveAttribute('href', 'https://shopee.co.id/search?keyword=test');
    expect(link).toHaveAttribute('target', '_blank');
    expect(link).toHaveAttribute('rel', 'noopener noreferrer');
  });

  it('renders thailand marketplace links with shopee.co.th', () => {
    const data: CompetitionData = {
      product1: { productName: null, sellingPrice: 100000, keyword: 'test', link: 'https://shopee.co.id/search?keyword=test', marketPrice: null },
      product2: { productName: null, sellingPrice: null, keyword: null, link: null, marketPrice: null },
      product3: { productName: null, sellingPrice: null, keyword: null, link: null, marketPrice: null },
    };
    render(<CompetitionForm data={data} marketplace="TH" onChange={vi.fn()} onBlur={vi.fn()} />);

    const link = screen.getByText('Lihat di Shopee');
    expect(link).toHaveAttribute('href', 'https://shopee.co.th/search?keyword=test');
  });

  it('renders placeholder text when link is null', () => {
    render(<CompetitionForm data={emptyData} onChange={vi.fn()} onBlur={vi.fn()} />);

    const placeholders = screen.getAllByText('Isi harga jual & kata kunci');
    expect(placeholders).toHaveLength(3);
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
