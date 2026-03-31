function getShopeeBuyerBaseUrl(marketplace: string = 'ID'): string {
  return marketplace === 'TH'
    ? 'https://shopee.co.th'
    : 'https://shopee.co.id';
}

export function localizeShopeeLink(link: string, marketplace: string = 'ID'): string {
  try {
    const url = new URL(link);
    if (url.hostname.startsWith('seller.shopee.')) {
      url.hostname = marketplace === 'TH' ? 'seller.shopee.co.th' : 'seller.shopee.co.id';
      return url.toString();
    }
    if (url.hostname.startsWith('shopee.')) {
      url.hostname = marketplace === 'TH' ? 'shopee.co.th' : 'shopee.co.id';
      return url.toString();
    }
    return link;
  } catch {
    return link;
  }
}

export function buildShopeeSearchUrl(
  sellingPrice: number | null,
  keyword: string | null,
  marketplace: string = 'ID',
): string | null {
  if (sellingPrice == null || keyword == null) return null;
  const params = new URLSearchParams({
    keyword,
    maxPrice: String(Math.round(sellingPrice * 1.1)),
    minPrice: String(Math.round(sellingPrice * 0.75)),
    noCorrection: 'true',
    page: '0',
    ratingFilter: '4',
    sortBy: 'sales',
  });
  return `${getShopeeBuyerBaseUrl(marketplace)}/search?${params.toString()}`;
}
