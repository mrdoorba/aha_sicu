import { useMemo, useState } from 'react';
import { ArrowUpDown } from 'lucide-react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../../ui/table';
import { formatIDR } from '../forms/formConfig';
import type { CalculatorResult, TopSkuDetails } from '../../../hooks/useCalculator';

interface TopSkuResultsProps {
  result: CalculatorResult;
}

type SortDir = 'asc' | 'desc';

function sortBy<T>(data: T[], field: keyof T, dir: SortDir): T[] {
  return [...data].sort((a, b) => {
    const aVal = a[field];
    const bVal = b[field];
    if (aVal < bVal) return dir === 'asc' ? -1 : 1;
    if (aVal > bVal) return dir === 'asc' ? 1 : -1;
    return 0;
  });
}

export function TopSkuResults({ result }: TopSkuResultsProps) {
  const details = result.details as TopSkuDetails;

  const [revSortField, setRevSortField] = useState<keyof TopSkuDetails['output_1'][0]>('total_omzet');
  const [revSortDir, setRevSortDir] = useState<SortDir>('desc');
  const [stockSortField, setStockSortField] = useState<keyof TopSkuDetails['output_2'][0]>('stok');
  const [stockSortDir, setStockSortDir] = useState<SortDir>('desc');

  const sortedRevenue = useMemo(
    () => sortBy(details.output_1 ?? [], revSortField, revSortDir),
    [details.output_1, revSortField, revSortDir],
  );

  const sortedStock = useMemo(
    () => sortBy(details.output_2 ?? [], stockSortField, stockSortDir),
    [details.output_2, stockSortField, stockSortDir],
  );

  const toggleRevSort = (field: keyof TopSkuDetails['output_1'][0]) => {
    if (revSortField === field) {
      setRevSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
    } else {
      setRevSortField(field);
      setRevSortDir('desc');
    }
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
        <h4 className="text-sm font-semibold">Top SKU Calculator</h4>
        <time className="text-xs text-muted-foreground">
          {new Date(result.calculated_at).toLocaleString('id-ID')}
        </time>
      </div>

      <p className="mb-3 text-sm font-medium">
        Average Stok: <span data-testid="average-stock">{details.average_stock}</span>
      </p>

      {/* Revenue ranking table */}
      <p className="mb-1 text-xs font-medium text-muted-foreground">Revenue Ranking</p>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead
              className="cursor-pointer select-none"
              onClick={() => toggleRevSort('kode_variasi')}
            >
              Kode Variasi <ArrowUpDown className="ml-1 inline size-3" />
            </TableHead>
            <TableHead
              className="cursor-pointer select-none"
              onClick={() => toggleRevSort('product_name')}
            >
              Product Name <ArrowUpDown className="ml-1 inline size-3" />
            </TableHead>
            <TableHead
              className="cursor-pointer select-none text-right"
              onClick={() => toggleRevSort('total_omzet')}
            >
              Total Omzet <ArrowUpDown className="ml-1 inline size-3" />
            </TableHead>
            <TableHead
              className="cursor-pointer select-none text-right"
              onClick={() => toggleRevSort('rata2_harga_jual')}
            >
              Rata2 Harga Jual <ArrowUpDown className="ml-1 inline size-3" />
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {sortedRevenue.map((row, i) => (
            <TableRow key={i}>
              <TableCell>{row.kode_variasi}</TableCell>
              <TableCell>{row.product_name}</TableCell>
              <TableCell className="text-right">Rp{formatIDR(row.total_omzet)}</TableCell>
              <TableCell className="text-right">Rp{formatIDR(row.rata2_harga_jual)}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      {/* Stock ranking table */}
      <p className="mb-1 mt-4 text-xs font-medium text-muted-foreground">Stock Ranking</p>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead
              className="cursor-pointer select-none"
              onClick={() => toggleStockSort('kode_variasi')}
            >
              Kode Variasi <ArrowUpDown className="ml-1 inline size-3" />
            </TableHead>
            <TableHead
              className="cursor-pointer select-none"
              onClick={() => toggleStockSort('nama_produk')}
            >
              Nama Produk <ArrowUpDown className="ml-1 inline size-3" />
            </TableHead>
            <TableHead
              className="cursor-pointer select-none"
              onClick={() => toggleStockSort('varian')}
            >
              Varian <ArrowUpDown className="ml-1 inline size-3" />
            </TableHead>
            <TableHead
              className="cursor-pointer select-none text-right"
              onClick={() => toggleStockSort('stok')}
            >
              Stok <ArrowUpDown className="ml-1 inline size-3" />
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {sortedStock.map((row, i) => (
            <TableRow key={i}>
              <TableCell>{row.kode_variasi}</TableCell>
              <TableCell>{row.nama_produk}</TableCell>
              <TableCell>{row.varian}</TableCell>
              <TableCell className="text-right">{row.stok}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
