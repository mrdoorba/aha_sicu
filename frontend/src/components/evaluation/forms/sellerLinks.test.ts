import { describe, it, expect } from 'vitest';
import { getSectionLinks, getSellerBaseUrl, localizeSellerLink } from './fields';

describe('getSellerBaseUrl', () => {
  it('should return co.id for ID marketplace', () => {
    expect(getSellerBaseUrl('ID')).toBe('https://seller.shopee.co.id');
  });

  it('should return co.th for TH marketplace', () => {
    expect(getSellerBaseUrl('TH')).toBe('https://seller.shopee.co.th');
  });

  it('should default to co.id when no marketplace provided', () => {
    expect(getSellerBaseUrl()).toBe('https://seller.shopee.co.id');
  });
});

describe('localizeSellerLink', () => {
  it('should keep co.id link unchanged for ID marketplace', () => {
    const link = 'https://seller.shopee.co.id/portal/accounthealth/home';
    expect(localizeSellerLink(link, 'ID')).toBe(link);
  });

  it('should replace co.id with co.th for TH marketplace', () => {
    const link = 'https://seller.shopee.co.id/portal/accounthealth/home';
    expect(localizeSellerLink(link, 'TH')).toBe('https://seller.shopee.co.th/portal/accounthealth/home');
  });

  it('should preserve query parameters when localizing', () => {
    const link = 'https://seller.shopee.co.id/portal/marketing/pas/assembly?&type=all&group=last-thirty-days';
    expect(localizeSellerLink(link, 'TH')).toBe(
      'https://seller.shopee.co.th/portal/marketing/pas/assembly?&type=all&group=last-thirty-days'
    );
  });

  it('should default to ID when no marketplace provided', () => {
    const link = 'https://seller.shopee.co.id/datacenter/dashboard';
    expect(localizeSellerLink(link)).toBe(link);
  });
});

describe('getSectionLinks', () => {
  it('should return co.id links for ID marketplace', () => {
    const links = getSectionLinks('ID');
    expect(links.operational).toBe('https://seller.shopee.co.id/portal/accounthealth/home');
    expect(links.business).toBe('https://seller.shopee.co.id/datacenter/dashboard');
  });

  it('should return co.th links for TH marketplace', () => {
    const links = getSectionLinks('TH');
    expect(links.operational).toBe('https://seller.shopee.co.th/portal/accounthealth/home');
    expect(links.business).toBe('https://seller.shopee.co.th/datacenter/dashboard');
    expect(links.visitors).toBe('https://seller.shopee.co.th/datacenter/traffic/overview');
    expect(links.promoTools).toBe('https://seller.shopee.co.th/datacenter/marketing/tools/discount');
    expect(links.ads).toBe('https://seller.shopee.co.th/portal/marketing/pas/assembly?&type=all&group=last-thirty-days');
    expect(links.campaign).toBe('https://seller.shopee.co.th/portal/marketing/cmt-product/campaign?tab=AllCampaign');
  });

  it('should default to ID when no marketplace provided', () => {
    const links = getSectionLinks();
    expect(links.operational).toContain('co.id');
  });
});
