export function buildShopeeSearchUrl(
  sellingPrice: number | null,
  keyword: string | null,
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
  return `https://shopee.co.id/search?${params.toString()}`;
}
