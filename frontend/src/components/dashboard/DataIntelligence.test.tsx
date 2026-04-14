import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect } from 'vitest';
import { DataIntelligence } from './DataIntelligence';

describe('DataIntelligence', () => {
  it('renders affiliate commission in the dashboard discount tab', async () => {
    const user = userEvent.setup();

    render(
      <DataIntelligence
        calculatorResults={{
          ads_keyword: { output_text: 'Ads output' },
          discount: {
            output_text: '% Diskon TOP SKU: 2.7%\n% Komisi Afiliasi: 1.5%',
            details: {
              i18n: {
                topSkuDiscount: { key: 'discount.output.topSkuDiscount', vars: { value: '2.7%' } },
                range: { key: 'discount.output.range', vars: { min: '0%', max: '10%' } },
                voucher: { key: 'discount.output.voucher', vars: { value: '5%' } },
                packageDiscount: { key: 'discount.output.packageDiscount', vars: { value: '3%' } },
                affiliateCommission: { key: 'discount.output.affiliateCommission', vars: { value: '1.5%' } },
              },
            },
          },
          top_sku: {},
        }}
        marketplace="ID"
      />,
    );

    await user.click(screen.getByRole('tab', { name: /Diskon|Discount|ส่วนลด/i }));

    expect(screen.getByText(/Komisi Afiliasi.*1\.5%|Affiliate Commission.*1\.5%/)).toBeInTheDocument();
  });
});
