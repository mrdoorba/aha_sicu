import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { ArrowUpDown, ChevronRight, ChevronDown } from 'lucide-react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../../ui/table';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '../../ui/collapsible';
import { formatCurrency, getCurrencyCode } from '../forms/formConfig';
import type { CalculatorResult, TopSkuDetails } from '../../../hooks/useCalculator';
import { isTopSkuDetails } from '../../../lib/calculatorGuards';
import { getIntlLocale } from '../../../lib/languages';

interface TopSkuResultsProps {
  result: CalculatorResult;
  marketplace?: string;
}

type SortDir = 'asc' | 'desc';

const TOP_N = 5;

function sortBy<T>(data: T[], field: keyof T, dir: SortDir): T[] {
  return [...data].sort((a, b) => {
    const aVal = a[field];
    const bVal = b[field];
    if (aVal < bVal) return dir === 'asc' ? -1 : 1;
    if (aVal > bVal) return dir === 'asc' ? 1 : -1;
    return 0;
  });
}

export function TopSkuResults({ result, marketplace = 'ID' }: TopSkuResultsProps) {
  const { t, i18n } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const [revSortField, setRevSortField] = useState<keyof TopSkuDetails['output_1'][0]>('total_omzet');
  const [revSortDir, setRevSortDir] = useState<SortDir>('desc');
  const [stockSortField, setStockSortField] = useState<keyof TopSkuDetails['output_2'][0] | null>(null);
  const [stockSortDir, setStockSortDir] = useState<SortDir>('desc');

  const details: TopSkuDetails | null = isTopSkuDetails(result.details)
    ? result.details
    : null;

  const sortedRevenue = useMemo(
    () => details ? sortBy(details.output_1 ?? [], revSortField, revSortDir).slice(0, TOP_N) : [],
    [details, revSortField, revSortDir],
  );

  const sortedStock = useMemo(() => {
    if (!details) return [];
    const stockItems = details.output_2 ?? [];
    if (stockSortField) {
      return sortBy(stockItems, stockSortField, stockSortDir).slice(0, TOP_N);
    }
    // Follow revenue table order by matching kode_variasi
    const revenueOrder = sortedRevenue.map((r) => r.kode_variasi);
    const matched = revenueOrder
      .map((kv) => stockItems.find((s) => s.kode_variasi === kv))
      .filter(Boolean) as typeof stockItems;
    return matched.slice(0, TOP_N);
  }, [details, stockSortField, stockSortDir, sortedRevenue]);

  if (!details) {
    return <p className="text-sm text-muted-foreground">Invalid top SKU data</p>;
  }

  const toggleRevSort = (field: keyof TopSkuDetails['output_1'][0]) => {
    if (revSortField === field) {
      setRevSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
    } else {
      setRevSortField(field);
      setRevSortDir('desc');
    }
    // Reset stock sort so it follows revenue order
    setStockSortField(null);
  };

  const toggleStockSort = (field: keyof TopSkuDetails['output_2'][0]) => {
    if (stockSortField === field) {
      setStockSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
    } else {
      setStockSortField(field);
      setStockSortDir('desc');
    }
  };

  return (
    <div>
      <div className="mb-2 flex items-center justify-between">
        <h4 className="text-sm font-semibold">{t('topSku.title')}</h4>
        <time className="text-xs text-muted-foreground">
          {new Date(result.calculated_at).toLocaleString(getIntlLocale(i18n.language))}
        </time>
      </div>

      <p className="mb-3 text-sm font-medium">
        {t('topSku.averageStock')}: <span data-testid="average-stock">{details.average_stock}</span>
      </p>

      <Collapsible open={isOpen} onOpenChange={setIsOpen}>
        <CollapsibleTrigger asChild>
          <button
            type="button"
            className="mb-2 flex items-center gap-1 text-xs font-medium text-primary hover:underline"
            data-testid="detail-toggle"
          >
            {isOpen ? (
              <ChevronDown className="size-3.5" />
            ) : (
              <ChevronRight className="size-3.5" />
            )}
            {isOpen ? t('topSku.hideDetail') : t('topSku.showDetail')}
          </button>
        </CollapsibleTrigger>

        <CollapsibleContent>
          {/* Revenue ranking table */}
          <p className="mb-1 text-xs font-medium text-muted-foreground">{t('topSku.revenueRanking')}</p>
          <Table data-testid="revenue-table">
            <TableHeader>
              <TableRow>
                <TableHead
                  className="cursor-pointer select-none"
                  onClick={() => toggleRevSort('kode_variasi')}
                >
                  {t('topSku.kodeVariasi')} <ArrowUpDown className="ml-1 inline size-3" />
                </TableHead>
                <TableHead
                  className="cursor-pointer select-none"
                  onClick={() => toggleRevSort('product_name')}
                >
                  {t('topSku.productName')} <ArrowUpDown className="ml-1 inline size-3" />
                </TableHead>
                <TableHead
                  className="cursor-pointer select-none text-right"
                  onClick={() => toggleRevSort('total_omzet')}
                >
                  {t('topSku.totalOmzet')} <ArrowUpDown className="ml-1 inline size-3" />
                </TableHead>
                <TableHead
                  className="cursor-pointer select-none text-right"
                  onClick={() => toggleRevSort('rata2_harga_jual')}
                >
                  {t('topSku.avgPrice')} <ArrowUpDown className="ml-1 inline size-3" />
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {sortedRevenue.map((row) => (
                <TableRow key={row.kode_variasi}>
                  <TableCell>{row.kode_variasi}</TableCell>
                  <TableCell>{row.product_name}</TableCell>
                  <TableCell className="text-right">{getCurrencyCode(marketplace)} {formatCurrency(row.total_omzet, marketplace)}</TableCell>
                  <TableCell className="text-right">{getCurrencyCode(marketplace)} {formatCurrency(row.rata2_harga_jual, marketplace)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>

          {/* Stock ranking table */}
          <p className="mb-1 mt-4 text-xs font-medium text-muted-foreground">{t('topSku.stockRanking')}</p>
          <Table data-testid="stock-table">
            <TableHeader>
              <TableRow>
                <TableHead
                  className="cursor-pointer select-none"
                  onClick={() => toggleStockSort('kode_variasi')}
                >
                  {t('topSku.kodeVariasi')} <ArrowUpDown className="ml-1 inline size-3" />
                </TableHead>
                <TableHead
                  className="cursor-pointer select-none"
                  onClick={() => toggleStockSort('nama_produk')}
                >
                  {t('topSku.namaProduk')} <ArrowUpDown className="ml-1 inline size-3" />
                </TableHead>
                <TableHead
                  className="cursor-pointer select-none"
                  onClick={() => toggleStockSort('varian')}
                >
                  {t('topSku.varian')} <ArrowUpDown className="ml-1 inline size-3" />
                </TableHead>
                <TableHead
                  className="cursor-pointer select-none text-right"
                  onClick={() => toggleStockSort('stok')}
                >
                  {t('topSku.stok')} <ArrowUpDown className="ml-1 inline size-3" />
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {sortedStock.map((row) => (
                <TableRow key={row.kode_variasi}>
                  <TableCell>{row.kode_variasi}</TableCell>
                  <TableCell>{row.nama_produk}</TableCell>
                  <TableCell>{row.varian}</TableCell>
                  <TableCell className="text-right">{row.stok}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CollapsibleContent>
      </Collapsible>
    </div>
  );
}
