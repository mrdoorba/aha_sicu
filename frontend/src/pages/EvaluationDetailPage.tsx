import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, ArrowUpDown, Trash2, ChevronRight, ChevronDown, Mail, Download } from 'lucide-react';
import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import type { TFunction } from 'i18next';
import { toast } from 'sonner';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../components/ui/table';
import { useEvaluationDetail } from '../hooks/useEvaluationDetail';
import { useCurrentUser } from '../hooks/useCurrentUser';
import { useDeleteEvaluation } from '../hooks/useDeleteEvaluation';
import { DeleteEvaluationDialog } from '../components/evaluations/DeleteEvaluationDialog';
import { SendEmailDialog } from '../components/dashboard/SendEmailDialog';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '../components/ui/collapsible';
import { FinalScoreDisplay } from '../components/evaluation/scoring/FinalScoreDisplay';
import {
  MANUAL_DATA_FIELDS,
  generateMonthLabels,
  formatCurrency,
  type FieldDefinition,
} from '../components/evaluation/forms/formConfig';
import { localizeShopeeLink } from '../components/evaluation/forms/competitionUtils';
import { isRecord, isRecordArray } from '../lib/typeGuards';
import { CATEGORY_MAP } from '../lib/categoryMap';
import { getIntlLocale } from '../lib/languages';
import { renderTranslatable, renderAdList, renderFlagList, type TranslatableText } from '../utils/renderTranslatable';
import type { TranslatableI18n, AdListI18n } from '../hooks/useCalculator';

interface ScoringSummary {
  conclusion?: string;
  conclusion_i18n?: TranslatableText[];
  marketing_estimation?: string;
  marketing_budget?: string;
  marketing_budget_i18n?: TranslatableText;
  closing_message?: string;
  closing_message_i18n?: TranslatableText;
}

function isScoringSummary(value: unknown): value is ScoringSummary {
  if (!isRecord(value)) return false;
  const hasContent =
    typeof value.conclusion === 'string' ||
    Array.isArray(value.conclusion_i18n) ||
    typeof value.marketing_budget === 'string' ||
    typeof value.closing_message === 'string';
  return hasContent;
}

function parseBulletPoints(text: string): string[] {
  return text
    .split('\n')
    .map((line) => line.replace(/^[-•]\s*/, '').trim())
    .filter(Boolean);
}

// Build module-level lookup: category key → { displayName, fieldMap }
const CATEGORY_LOOKUP = new Map(
  MANUAL_DATA_FIELDS.map((cat) => [
    cat.key,
    {
      displayName: cat.displayName,
      displayNameKey: cat.displayNameKey,
      fieldMap: new Map(cat.fields.map((f) => [f.key, f])),
    },
  ]),
);

function capitalize(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

function formatDate(dateStr: string, locale: string): string {
  const d = new Date(dateStr);
  return d.toLocaleDateString(locale, {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    timeZoneName: 'short',
  });
}

function formatNumber(value: unknown, marketplace?: string): string {
  if (typeof value !== 'number') return String(value ?? '-');
  return formatCurrency(value, marketplace);
}

function formatManualNumber(value: number, options?: Intl.NumberFormatOptions): string {
  return value.toLocaleString('en-US', {
    maximumFractionDigits: 2,
    ...options,
  });
}

function formatValue(value: unknown, key: string, fieldDef?: FieldDefinition, marketplace?: string): string {
  if (value === null || value === undefined) return '-';
  if (Array.isArray(value)) return value.map((v) => formatNumber(v, marketplace)).join(', ');
  if (typeof value === 'string' && key.endsWith('.link')) {
    return localizeShopeeLink(value, marketplace);
  }

  // Metadata-based formatting when field definition is available
  if (fieldDef && typeof value === 'number') {
    if (fieldDef.inputType === 'currency') {
      return formatCurrency(value, marketplace);
    }
    if (fieldDef.inputType === 'number' && fieldDef.unit === '%') {
      return `${value}%`;
    }
    if (fieldDef.inputType === 'number' && fieldDef.unit === 'count') {
      return formatManualNumber(value, { maximumFractionDigits: 0 });
    }
    return formatManualNumber(value);
  }

  // Fallback heuristics for fields not in config
  if (typeof value === 'number') {
    if (key.includes('rate') || key.includes('percentage') || key.includes('persen')) {
      return `${value}%`;
    }
    if (key.includes('sales') || key.includes('omzet') || key.includes('budget') || key.includes('revenue')) {
      return formatNumber(value, marketplace);
    }
    return String(value);
  }
  return String(value);
}

function LoadingSkeleton() {
  return (
    <div className="space-y-6" data-testid="loading-skeleton">
      <div className="h-8 w-64 animate-pulse rounded bg-muted-foreground/20" />
      <div className="h-32 animate-pulse rounded bg-muted-foreground/20" />
      <div className="h-48 animate-pulse rounded bg-muted-foreground/20" />
      <div className="h-48 animate-pulse rounded bg-muted-foreground/20" />
    </div>
  );
}

function ScoreBreakdownTable({
  breakdown,
  t,
}: {
  breakdown: Array<Record<string, unknown>>;
  t: (key: string) => string;
}) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>{t('evaluationDetail.category')}</TableHead>
          <TableHead className="text-right">{t('evaluationDetail.score')}</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {breakdown.map((cat) => {
          const mapped = CATEGORY_MAP.find(m => m.backend === String(cat.category));
          return (
            <TableRow key={String(cat.category)}>
              <TableCell>{mapped ? t(mapped.labelKey) : String(cat.category)}</TableCell>
              <TableCell className="text-right">
                {Number(cat.score).toFixed(1)}
                {Number(cat.max_score) > 0 ? `/${Number(cat.max_score).toFixed(0)}` : ''}
              </TableCell>
            </TableRow>
          );
        })}
      </TableBody>
    </Table>
  );
}

function AdsKeywordSection({ data, t }: { data: Record<string, unknown>; t: TFunction }) {
  const text = typeof data.output_text === 'string' ? data.output_text : '';
  if (!text) return <p className="text-muted-foreground">{t('common.noData')}</p>;

  const details = isRecord(data.details) ? data.details : undefined;
  const hasI18n = details?.ak2_i18n != null;

  const hasDetailFields = details && (details.ak2 != null || hasI18n);

  if (!hasDetailFields) {
    return <pre className="whitespace-pre-wrap rounded bg-muted p-4 text-sm">{text}</pre>;
  }

  const parts: string[] = [];
  const str = (k: string) => (typeof details![k] === 'string' ? (details![k] as string) : '');

  parts.push(renderTranslatable(str('ak2'), details.ak2_i18n as TranslatableI18n | null, t));
  parts.push(renderTranslatable(str('ak3'), details.ak3_i18n as TranslatableI18n | null, t));

  const ak4Text = renderFlagList(str('ak4'), details.ak4_i18n as TranslatableI18n[] | null, t);
  if (ak4Text) parts.push(ak4Text);

  const al2Text = renderAdList(str('al2'), details.al2_i18n as AdListI18n | null, t);
  if (al2Text) parts.push(al2Text);

  const al3Text = renderTranslatable(str('al3'), details.al3_i18n as TranslatableI18n | null, t);
  if (al3Text) parts.push(al3Text);

  const al5Text = renderAdList(str('al5'), details.al5_i18n as AdListI18n | null, t);
  if (al5Text) parts.push(al5Text);

  for (const key of ['al6', 'al7', 'al8', 'al9']) {
    const i18nKey = `${key}_i18n`;
    const fallback = str(key);
    const val = renderTranslatable(fallback, details[i18nKey] as TranslatableI18n | null, t);
    if (val) parts.push(val);
  }

  const rendered = parts.filter(Boolean).join('\n\n');
  return <pre className="whitespace-pre-wrap rounded bg-muted p-4 text-sm">{rendered}</pre>;
}

type SortDir = 'asc' | 'desc';

function sortRecordArray(data: Record<string, unknown>[], field: string, dir: SortDir): Record<string, unknown>[] {
  return [...data].sort((a, b) => {
    const aVal = a[field];
    const bVal = b[field];
    if (aVal == null || bVal == null) return 0;
    if (aVal < bVal) return dir === 'asc' ? -1 : 1;
    if (aVal > bVal) return dir === 'asc' ? 1 : -1;
    return 0;
  });
}

function TopSkuSection({ data, t, marketplace, brandName, period }: { data: Record<string, unknown>; t: (key: string, vars?: Record<string, string>) => string; marketplace?: string; brandName?: string; period?: string }) {
  const details = isRecord(data.details) ? data.details : undefined;
  const allOutput1 = useMemo(() => isRecordArray(details?.output_1) ? details.output_1 : [], [details]);
  const allOutput2 = useMemo(() => isRecordArray(details?.output_2) ? details.output_2 : [], [details]);
  const avgStock = details?.average_stock;
  const outOfStockPct = details?.out_of_stock_pct;
  const [isOpen, setIsOpen] = useState(false);
  const [showAllSku, setShowAllSku] = useState(false);
  const [revSortField, setRevSortField] = useState<string>('total_omzet');
  const [revSortDir, setRevSortDir] = useState<SortDir>('desc');
  const [stockSortField, setStockSortField] = useState<string | null>(null);
  const [stockSortDir, setStockSortDir] = useState<SortDir>('desc');

  const toggleRevSort = (field: string) => {
    if (revSortField === field) {
      setRevSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
    } else {
      setRevSortField(field);
      setRevSortDir('desc');
    }
    setStockSortField(null);
  };

  const toggleStockSort = (field: string) => {
    if (stockSortField === field) {
      setStockSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
    } else {
      setStockSortField(field);
      setStockSortDir('desc');
    }
  };

  const PREVIEW_COUNT = 5;
  const sortedOutput1 = sortRecordArray(allOutput1, revSortField, revSortDir);
  const output1 = showAllSku ? sortedOutput1 : sortedOutput1.slice(0, PREVIEW_COUNT);

  const sortedOutput2 = useMemo(() => {
    if (stockSortField) {
      return sortRecordArray(allOutput2, stockSortField, stockSortDir);
    }
    // Follow revenue table order by matching kode_variasi
    const revenueOrder = sortedOutput1.map((r) => r.kode_variasi);
    return revenueOrder
      .map((kv) => allOutput2.find((s) => s.kode_variasi === kv))
      .filter(Boolean) as Record<string, unknown>[];
  }, [allOutput2, stockSortField, stockSortDir, sortedOutput1]);
  const output2 = showAllSku ? sortedOutput2 : sortedOutput2.slice(0, PREVIEW_COUNT);
  const hasMoreItems = allOutput1.length > PREVIEW_COUNT || allOutput2.length > PREVIEW_COUNT;

  // Join revenue (output_1: total_omzet) with stock (output_2: varian, stok) by
  // kode_variasi, sorted by Total Omzet desc — the full Top-20% SKU set for export.
  const exportRows = useMemo(() => {
    const stockByKv = new Map(allOutput2.map((s) => [String(s.kode_variasi), s]));
    return sortRecordArray(allOutput1, 'total_omzet', 'desc').map((r) => {
      const stock = stockByKv.get(String(r.kode_variasi));
      return {
        kodeVariasi: String(r.kode_variasi ?? '-'),
        namaProduk: String(r.product_name ?? r.nama_produk ?? stock?.nama_produk ?? '-'),
        varian: String(stock?.varian ?? '-'),
        totalOmzet: Number(r.total_omzet) || 0,
        stok: stock?.stok != null ? Number(stock.stok) || 0 : 0,
      };
    });
  }, [allOutput1, allOutput2]);

  const exportHeaders = [
    t('topSku.kodeVariasi'), t('topSku.namaProduk'), t('topSku.varian'), t('topSku.totalOmzet'), t('topSku.stok'),
  ];

  // e.g. "Cintage-Jun-2026-top-sku-20pct" — slug brand + period, fall back gracefully.
  const exportFilename = [brandName, period, 'top-sku-20pct']
    .filter(Boolean)
    .join('-')
    .replace(/[^a-zA-Z0-9-]+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '');

  const handleExportExcel = async () => {
    try {
      const XLSX = await import('xlsx');
      const aoa = [exportHeaders, ...exportRows.map((r) => [r.kodeVariasi, r.namaProduk, r.varian, r.totalOmzet, r.stok])];
      const ws = XLSX.utils.aoa_to_sheet(aoa);
      const wb = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(wb, ws, 'Top SKU');
      XLSX.writeFile(wb, `${exportFilename}.xlsx`);
    } catch {
      toast.error(t('topSku.exportError'));
    }
  };

  const handleExportPdf = async () => {
    try {
      const { default: jsPDF } = await import('jspdf');
      const autoTable = (await import('jspdf-autotable')).default;
      const doc = new jsPDF();
      doc.text(t('topSku.exportTitle'), 14, 16);
      autoTable(doc, {
        startY: 22,
        head: [exportHeaders],
        body: exportRows.map((r) => [r.kodeVariasi, r.namaProduk, r.varian, formatNumber(r.totalOmzet, marketplace), String(r.stok)]),
        styles: { fontSize: 8 },
      });
      doc.save(`${exportFilename}.pdf`);
    } catch {
      toast.error(t('topSku.exportError'));
    }
  };

  if (allOutput1.length === 0 && allOutput2.length === 0) {
    return <p className="text-muted-foreground">{t('common.noData')}</p>;
  }

  return (
    <div className="space-y-4">
      {avgStock !== undefined && avgStock !== null && (
        <p className="text-sm font-medium">
          {t('evaluationDetail.averageStock')}: <span className="font-bold">{String(avgStock)}</span>
        </p>
      )}
      {outOfStockPct !== undefined && outOfStockPct !== null && (
        <p className="text-sm font-medium">
          {t('evaluationDetail.stockAvailability')}: <span className="font-bold">{typeof outOfStockPct === 'number' ? `${Math.round(outOfStockPct * 100)}%` : String(outOfStockPct)}</span> {t('evaluationDetail.stockAvailability.suffix')}
        </p>
      )}
      {exportRows.length > 0 && (
        <div className="flex flex-wrap gap-2">
          <Button variant="outline" size="sm" onClick={handleExportExcel}>
            <Download className="mr-1.5 size-4" />
            {t('topSku.exportExcel')}
          </Button>
          <Button variant="outline" size="sm" onClick={handleExportPdf}>
            <Download className="mr-1.5 size-4" />
            {t('topSku.exportPdf')}
          </Button>
        </div>
      )}
      <Collapsible open={isOpen} onOpenChange={setIsOpen}>
        <CollapsibleTrigger asChild>
          <button
            type="button"
            className="mb-2 flex items-center gap-1 text-xs font-medium text-primary hover:underline"
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
          {output1.length > 0 && (
            <div>
              <h4 className="mb-2 text-sm font-medium">{t('evaluationDetail.revenueRanking')}</h4>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="cursor-pointer select-none" onClick={() => toggleRevSort('kode_variasi')}>
                      {t('topSku.kodeVariasi')} <ArrowUpDown className="ml-1 inline size-3" />
                    </TableHead>
                    <TableHead className="cursor-pointer select-none" onClick={() => toggleRevSort('product_name')}>
                      {t('topSku.productName')} <ArrowUpDown className="ml-1 inline size-3" />
                    </TableHead>
                    <TableHead className="cursor-pointer select-none text-right" onClick={() => toggleRevSort('total_omzet')}>
                      {t('topSku.totalOmzet')} <ArrowUpDown className="ml-1 inline size-3" />
                    </TableHead>
                    <TableHead className="cursor-pointer select-none text-right" onClick={() => toggleRevSort('rata2_harga_jual')}>
                      {t('topSku.avgPrice')} <ArrowUpDown className="ml-1 inline size-3" />
                    </TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {output1.map((row, i) => (
                    <TableRow key={String(row.kode_variasi ?? i)}>
                      <TableCell>{String(row.kode_variasi ?? '-')}</TableCell>
                      <TableCell>{String(row.product_name ?? row.nama_produk ?? '-')}</TableCell>
                      <TableCell className="text-right">{formatNumber(row.total_omzet, marketplace)}</TableCell>
                      <TableCell className="text-right">{formatNumber(row.rata2_harga_jual, marketplace)}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
          {output2.length > 0 && (
            <div>
              <h4 className="mb-2 mt-4 text-sm font-medium">{t('evaluationDetail.stockRanking')}</h4>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="cursor-pointer select-none" onClick={() => toggleStockSort('kode_variasi')}>
                      {t('topSku.kodeVariasi')} <ArrowUpDown className="ml-1 inline size-3" />
                    </TableHead>
                    <TableHead className="cursor-pointer select-none" onClick={() => toggleStockSort('nama_produk')}>
                      {t('topSku.namaProduk')} <ArrowUpDown className="ml-1 inline size-3" />
                    </TableHead>
                    <TableHead className="cursor-pointer select-none" onClick={() => toggleStockSort('varian')}>
                      {t('topSku.varian')} <ArrowUpDown className="ml-1 inline size-3" />
                    </TableHead>
                    <TableHead className="cursor-pointer select-none text-right" onClick={() => toggleStockSort('stok')}>
                      {t('topSku.stok')} <ArrowUpDown className="ml-1 inline size-3" />
                    </TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {output2.map((row, i) => (
                    <TableRow key={String(row.kode_variasi ?? i)}>
                      <TableCell>{String(row.kode_variasi ?? '-')}</TableCell>
                      <TableCell>{String(row.nama_produk ?? '-')}</TableCell>
                      <TableCell>{String(row.varian ?? '-')}</TableCell>
                      <TableCell className="text-right">{formatNumber(row.stok, marketplace)}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
          {hasMoreItems && (
            <button
              type="button"
              onClick={() => setShowAllSku((prev) => !prev)}
              className="mt-3 flex items-center gap-1 text-xs font-medium text-primary hover:underline"
            >
              {showAllSku ? (
                <ChevronDown className="size-3.5" />
              ) : (
                <ChevronRight className="size-3.5" />
              )}
              {showAllSku
                ? t('topSku.showLess')
                : t('topSku.showAll', { count: String(Math.max(allOutput1.length, allOutput2.length)) })}
            </button>
          )}
        </CollapsibleContent>
      </Collapsible>
    </div>
  );
}

function DiscountSection({ data, t }: { data: Record<string, unknown>; t: TFunction }) {
  const text = typeof data.output_text === 'string' ? data.output_text : '';
  if (!text) return <p className="text-muted-foreground">{t('common.noData')}</p>;

  const details = isRecord(data.details) ? data.details : undefined;
  const i18nDict = isRecord(details?.i18n) ? details.i18n : undefined;

  if (!i18nDict) {
    return <pre className="whitespace-pre-wrap rounded bg-muted p-4 text-sm">{text}</pre>;
  }

  const lines: string[] = [];
  for (const key of ['topSkuDiscount', 'range', 'voucher', 'packageDiscount', 'affiliateCommission', 'fakeDiscount']) {
    const entry = i18nDict[key];
    if (isRecord(entry) && typeof entry.key === 'string') {
      lines.push(t(entry.key as string, entry.vars as Record<string, string>));
    }
  }

  return <pre className="whitespace-pre-wrap rounded bg-muted p-4 text-sm">{lines.join('\n')}</pre>;
}

function ScoringConclusionSection({
  calculatorResults,
  t,
}: {
  calculatorResults: Record<string, unknown>;
  t: TFunction;
}) {
  const summary = isScoringSummary(calculatorResults.scoring_summary)
    ? calculatorResults.scoring_summary
    : undefined;

  if (!summary) return null;

  return (
    <div className="space-y-4">
      <h3 className="text-base font-semibold">{t('presentation.section.kesimpulan')}</h3>

      {/* Conclusion bullet list */}
      {summary.conclusion_i18n ? (
        <ul className="list-disc pl-5 space-y-1">
          {summary.conclusion_i18n.map((item, i) => (
            <li key={i} className="text-sm">{t(item.key, item.vars)}</li>
          ))}
        </ul>
      ) : summary.conclusion ? (
        <ul className="list-disc pl-5 space-y-1">
          {parseBulletPoints(summary.conclusion).map((point, i) => (
            <li key={i} className="text-sm">{point}</li>
          ))}
        </ul>
      ) : null}

      {/* Marketing budget */}
      {(summary.marketing_budget || summary.marketing_budget_i18n) && (
        <div className="rounded-lg border bg-muted/30 p-4">
          <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1">
            {t('presentation.kesimpulan.marketingBudget')}
          </p>
          <p className="text-sm font-bold text-primary">
            {renderTranslatable(summary.marketing_budget || '', summary.marketing_budget_i18n, t)}
          </p>
        </div>
      )}

      {/* Closing message */}
      {(summary.closing_message || summary.closing_message_i18n) && (
        <div className="rounded-lg border-l-4 border-primary/30 bg-primary/5 p-4">
          <p className="text-sm whitespace-pre-line">
            {renderTranslatable(summary.closing_message || '', summary.closing_message_i18n, t)}
          </p>
        </div>
      )}
    </div>
  );
}

function resolveNestedValue(obj: Record<string, unknown>, dotKey: string): unknown {
  const parts = dotKey.split('.');
  let val: unknown = obj;
  for (const part of parts) {
    if (!isRecord(val)) return undefined;
    val = val[part];
  }
  return val;
}

function ManualInputsSection({
  inputs,
  t,
  marketplace,
}: {
  inputs: Record<string, unknown>;
  t: (key: string, options?: Record<string, unknown>) => string;
  marketplace?: string;
}) {
  // manual_inputs is JSONB — Postgres does not preserve key order, so sort by
  // the canonical form order (MANUAL_DATA_FIELDS) to match the evaluation page.
  const order = MANUAL_DATA_FIELDS.map((c) => c.key);
  const rank = (k: string) => (order.indexOf(k) + 1) || 99;
  const categories = Object.entries(inputs).sort(([a], [b]) => rank(a) - rank(b));
  if (categories.length === 0) {
    return <p className="text-muted-foreground">{t('evaluationDetail.noManualInputs')}</p>;
  }

  return (
    <div className="space-y-4">
      {categories.map(([category, values]) => {
        const categoryInfo = CATEGORY_LOOKUP.get(category);
        const categoryLabel = categoryInfo?.displayNameKey ? t(categoryInfo.displayNameKey) : capitalize(category);

        if (!isRecord(values)) {
          return (
            <div key={category}>
              <h3 className="mb-2 text-sm font-semibold">{categoryLabel}</h3>
              <p className="text-sm">{String(values)}</p>
            </div>
          );
        }

        const valuesObj = values;

        // Build entries: [key, value, fieldDef, displayLabel]
        let entries: Array<[string, unknown, FieldDefinition | undefined, string | undefined]>;

        if (category === 'competition' && categoryInfo) {
          // Flatten nested objects using dot-notation keys from COMPETITION_FIELDS
          entries = [];
          for (const [dotKey, fieldDef] of categoryInfo.fieldMap) {
            const val = resolveNestedValue(valuesObj, dotKey);
            entries.push([dotKey, val, fieldDef, undefined]);
          }
        } else {
          // Generate dynamic month labels for business category
          let monthLabels: string[] | undefined;
          if (category === 'business' && valuesObj.salesStartMonth) {
            monthLabels = typeof valuesObj.salesStartMonth === 'string'
              ? generateMonthLabels(valuesObj.salesStartMonth)
              : undefined;
          }

          entries = Object.entries(valuesObj)
            .filter(([key]) => key !== 'salesStartMonth')
            .map(([key, val]) => {
              const fieldDef = categoryInfo?.fieldMap.get(key);
              let dynamicLabel: string | undefined;

              if (monthLabels && key.startsWith('salesMonth')) {
                const idx = parseInt(key.replace('salesMonth', ''), 10);
                if (!isNaN(idx) && idx >= 0 && idx < monthLabels.length) {
                  dynamicLabel = t('evaluation.salesMonthLabel', { month: t(monthLabels[idx]) });
                }
              }

              return [key, val, fieldDef, dynamicLabel] as [string, unknown, FieldDefinition | undefined, string | undefined];
            });
        }

        // Competition section: group by product for a cleaner layout
        if (category === 'competition') {
          const products = ['product1', 'product2', 'product3'] as const;
          const productLabels = [t('evaluation.competitorProduct1'), t('evaluation.competitorProduct2'), t('evaluation.competitorProduct3')];
          // Strip the "Produk Kompetitor N — " prefix from labels for compact display
          const shortLabel = (label: string) => label.replace(/^Produk Kompetitor \d — /, '');

          return (
            <div key={category}>
              <h3 className="mb-2 text-sm font-semibold">{categoryLabel}</h3>
              <div className="grid gap-3 sm:grid-cols-3">
                {products.map((prefix, idx) => {
                  const productEntries = entries.filter(([key]) => key.startsWith(prefix + '.'));
                  return (
                    <div key={prefix} className="rounded-lg border p-3">
                      <h4 className="mb-2 text-xs font-semibold text-muted-foreground">{productLabels[idx]}</h4>
                      <div className="space-y-1 text-sm">
                        {productEntries.map(([key, val, fieldDef]) => {
                          const isLink = key.endsWith('.link');
                          const formatted = formatValue(val, key, fieldDef, marketplace);
                          return (
                            <div key={key} className="border-b border-border/50 py-1">
                              <span className="text-muted-foreground">
                                {shortLabel(fieldDef?.labelKey ? t(fieldDef.labelKey) : (fieldDef?.label ?? key))}
                              </span>
                              <div className="font-medium">
                                {isLink && formatted !== '-' ? (
                                  <a
                                    href={formatted}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-blue-600 underline break-all"
                                  >
                                    {t('evaluation.viewOnShopee')}
                                  </a>
                                ) : (
                                  <span className="break-words">
                                    {formatted}
                                  </span>
                                )}
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          );
        }

        return (
          <div key={category}>
            <h3 className="mb-2 text-sm font-semibold">{categoryLabel}</h3>
            <div className="grid grid-cols-2 gap-3 text-sm sm:grid-cols-3">
              {entries.map(([key, val, fieldDef, dynamicLabel]) => (
                <div key={key} className="rounded-lg border p-3">
                  <span className="text-xs text-muted-foreground">
                    {dynamicLabel ?? (fieldDef?.labelKey ? t(fieldDef.labelKey) : (fieldDef?.label ?? key.replace(/_/g, ' ')))}
                  </span>
                  <div className="font-medium break-words">
                    {formatValue(val, key, fieldDef, marketplace)}
                    {fieldDef?.benchmark && (
                      <span className="ml-1 text-xs text-muted-foreground">({fieldDef.benchmarkKey ? t(fieldDef.benchmarkKey) : fieldDef.benchmark})</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}

export function EvaluationDetailPage() {
  const { t, i18n } = useTranslation();
  const params = useParams<{ id: string }>();
  const navigate = useNavigate();
  const id = Number(params.id);

  const validId = !isNaN(id) && id > 0;
  const { evaluation, isLoading, isError, isNotFound, refetch } = useEvaluationDetail(
    validId ? id : 0,
  );
  const { profile } = useCurrentUser();
  const deleteEvaluation = useDeleteEvaluation();
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [sendMailDialogOpen, setSendMailDialogOpen] = useState(false);

  const canDelete = profile?.role === 'leader' || profile?.role === 'admin';

  const handleDelete = () => {
    deleteEvaluation.mutate(id, {
      onSuccess: () => {
        toast.success(t('evaluationDetail.deleteSuccess'));
        navigate('/history');
      },
      onError: () => {
        toast.error(t('evaluationDetail.deleteError'));
      },
    });
  };

  return (
    <div className="p-8">
      <div
        className="mx-auto max-w-7xl"
      >
        <Button
          variant="ghost"
          size="sm"
          className="mb-4"
          onClick={() => navigate('/history')}
        >
          <ArrowLeft className="size-4" />
          {t('common.backToHistory')}
        </Button>

        {isLoading && <LoadingSkeleton />}

        {!isLoading && (!validId || isNotFound) && (
          <Card>
            <CardContent className="flex flex-col items-center gap-4 py-12">
              <p className="text-muted-foreground">{t('evaluationDetail.notFound')}</p>
              <Button variant="outline" onClick={() => navigate('/history')}>
                {t('common.backToHistory')}
              </Button>
            </CardContent>
          </Card>
        )}

        {!isLoading && isError && !isNotFound && (
          <Card>
            <CardContent className="flex flex-col items-center gap-4 py-12">
              <p className="text-destructive">{t('evaluationDetail.errorLoading')}</p>
              <Button variant="outline" onClick={() => refetch()}>
                {t('common.retry')}
              </Button>
            </CardContent>
          </Card>
        )}

        {evaluation && (
          <div className="space-y-6">
            {/* Brand Info Header */}
            <Card>
              <CardContent className="py-6">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h1 className="text-2xl font-bold">{evaluation.brand_name}</h1>
                    <p className="mt-1 text-sm text-muted-foreground">
                      {evaluation.evaluator_email} &middot; {formatDate(evaluation.created_at, getIntlLocale(i18n.language))}
                      {evaluation.period && (
                        <> &middot; {t('scoring.period')}: {evaluation.period}</>
                      )}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    {evaluation.email_output && (
                      <Button size="sm" onClick={() => setSendMailDialogOpen(true)}>
                        <Mail className="mr-1.5 size-4" />
                        {t('sendMail.send')}
                      </Button>
                    )}
                    <Badge variant={evaluation.template === 'fashion' ? 'default' : 'secondary'}>
                      {evaluation.template === 'fashion' ? 'Fashion' : 'Non-Fashion'}
                    </Badge>
                    {canDelete && (
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={() => setDeleteDialogOpen(true)}
                      >
                        <Trash2 className="mr-1 size-4" />
                        {t('evaluationDetail.deleteEvaluation')}
                      </Button>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>

            {canDelete && evaluation && (
              <DeleteEvaluationDialog
                open={deleteDialogOpen}
                onOpenChange={setDeleteDialogOpen}
                brandName={evaluation.brand_name}
                onConfirm={handleDelete}
                isDeleting={deleteEvaluation.isPending}
              />
            )}

            {/* Score Section */}
            <div className="grid gap-6 md:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">{t('evaluationDetail.finalScore')}</CardTitle>
                </CardHeader>
                <CardContent>
                  <FinalScoreDisplay
                    totalScore={evaluation.final_score}
                    verdict={evaluation.verdict}
                    template={evaluation.template}
                  />
                  <p className="mt-2 text-sm text-muted-foreground">
                    {evaluation.template === 'fashion' ? 'Fashion' : 'Non-Fashion'}
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">{t('evaluationDetail.scoreBreakdown')}</CardTitle>
                </CardHeader>
                <CardContent>
                  <ScoreBreakdownTable breakdown={evaluation.score_breakdown} t={t} />
                </CardContent>
              </Card>
            </div>

            {/* Manual Inputs */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">{t('evaluationDetail.manualInputs')}</CardTitle>
              </CardHeader>
              <CardContent>
                <ManualInputsSection inputs={evaluation.manual_inputs} t={t} marketplace={evaluation.marketplace} />
              </CardContent>
            </Card>

            {/* Calculator Results */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">{t('evaluationDetail.calculatorResults')}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <h3 className="mb-3 text-base font-semibold">{t('evaluationDetail.adsKeywordAnalysis')}</h3>
                  {isRecord(evaluation.calculator_results.ads_keyword) ? (
                    <AdsKeywordSection
                      data={evaluation.calculator_results.ads_keyword}
                      t={t}
                    />
                  ) : (
                    <p className="text-muted-foreground">{t('common.noData')}</p>
                  )}
                </div>

                <div>
                  <h3 className="mb-3 text-base font-semibold">{t('evaluationDetail.topSkuAnalysis')}</h3>
                  {isRecord(evaluation.calculator_results.top_sku) ? (
                    <TopSkuSection
                      data={evaluation.calculator_results.top_sku}
                      t={t}
                      marketplace={evaluation.marketplace}
                      brandName={evaluation.brand_name}
                      period={evaluation.period}
                    />
                  ) : (
                    <p className="text-muted-foreground">{t('common.noData')}</p>
                  )}
                </div>

                <div>
                  <h3 className="mb-3 text-base font-semibold">{t('evaluationDetail.discountCheck')}</h3>
                  {isRecord(evaluation.calculator_results.discount) ? (
                    <DiscountSection
                      data={evaluation.calculator_results.discount}
                      t={t}
                    />
                  ) : (
                    <p className="text-muted-foreground">{t('common.noData')}</p>
                  )}
                </div>

                <ScoringConclusionSection
                  calculatorResults={evaluation.calculator_results}
                  t={t}
                />
              </CardContent>
            </Card>

            {/* Send Email dialog — triggered from the header button */}
            {evaluation.email_output && (
              <SendEmailDialog
                open={sendMailDialogOpen}
                onOpenChange={setSendMailDialogOpen}
                evaluationId={evaluation.id}
                brandName={evaluation.brand_name}
                period={evaluation.period}
                score={Math.round(evaluation.final_score)}
                brandRawData={evaluation.brand_raw_data}
                marketplace={evaluation.marketplace}
              />
            )}
          </div>
        )}
      </div>
    </div>
  );
}
