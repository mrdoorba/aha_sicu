import { useState } from 'react';
import type { TFunction } from 'i18next';
import { Card, CardContent } from '../ui/card';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../ui/tabs';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table';
import { useTranslation } from 'react-i18next';
import type { AdsKeywordDetails, TranslatableI18n } from '../../hooks/useCalculator';
import { renderTranslatable, renderAdList, renderFlagList } from '../../utils/renderTranslatable';
import { isRecord, isRecordArray } from '../../lib/typeGuards';
import { isAdsKeywordDetails } from '../../lib/calculatorGuards';
import { formatCurrency } from '../evaluation/forms/formConfig';

interface DataIntelligenceProps {
  calculatorResults: Record<string, unknown>;
  marketplace?: string;
}

function formatValue(value: unknown, marketplace?: string): string {
  if (typeof value !== 'number') return String(value ?? '-');
  return formatCurrency(value, marketplace);
}

function AdsContent({ data, t }: { data: Record<string, unknown>; t: TFunction }) {
  const text = typeof data.output_text === 'string' ? data.output_text : '';
  const details = isAdsKeywordDetails(data.details) ? data.details : undefined;

  if (!details) {
    if (!text) return <p className="text-sm text-muted-foreground py-6 text-center">{t('common.noData')}</p>;
    return <pre className="whitespace-pre-wrap rounded-lg bg-muted/50 p-4 text-sm font-mono border border-border/50">{text}</pre>;
  }

  const sections: string[] = [];

  // Sheet 1
  sections.push(renderTranslatable(details.ak2, details.ak2_i18n, t));
  sections.push(renderTranslatable(details.ak3, details.ak3_i18n, t));
  const ak4Text = renderFlagList(details.ak4, details.ak4_i18n, t);
  if (ak4Text) sections.push(ak4Text);

  // Sheet 2
  const al2Text = renderAdList(details.al2, details.al2_i18n, t);
  if (al2Text) sections.push(al2Text);
  const al3Text = renderTranslatable(details.al3, details.al3_i18n, t);
  if (al3Text) sections.push(al3Text);
  const al5Text = renderAdList(details.al5, details.al5_i18n, t);
  if (al5Text) sections.push(al5Text);

  // Bottom flags
  for (const key of ['al6', 'al7', 'al8', 'al9'] as const) {
    const i18nKey = `${key}_i18n` as keyof AdsKeywordDetails;
    const val = renderTranslatable(details[key], details[i18nKey] as TranslatableI18n | null | undefined, t);
    if (val) sections.push(val);
  }

  const combined = sections.filter(Boolean).join('\n\n');
  if (!combined) return <p className="text-sm text-muted-foreground py-6 text-center">{t('common.noData')}</p>;

  return (
    <pre className="whitespace-pre-wrap break-words rounded-lg bg-muted/50 p-4 text-sm font-mono leading-relaxed border border-border/50">
      {combined}
    </pre>
  );
}

function TopSkuContent({ data, t, marketplace }: { data: Record<string, unknown>; t: TFunction; marketplace?: string }) {
  const details = isRecord(data.details) ? data.details : undefined;
  const output1 = isRecordArray(details?.output_1) ? details.output_1 : [];
  const output2 = isRecordArray(details?.output_2) ? details.output_2 : [];
  const avgStock = details?.average_stock;

  if (output1.length === 0 && output2.length === 0) {
    return <p className="text-sm text-muted-foreground py-6 text-center">{t('common.noData')}</p>;
  }

  return (
    <div className="space-y-6">
      {avgStock !== undefined && avgStock !== null && (
        <div className="inline-flex items-center rounded-lg bg-primary/5 px-4 py-2 border border-primary/10">
          <p className="text-sm font-semibold">
            {t('evaluationDetail.averageStock')}: <span className="text-primary ml-1">{formatValue(avgStock, marketplace)}</span>
          </p>
        </div>
      )}
      {output1.length > 0 && (
        <div className="space-y-3">
          <h4 className="text-sm font-bold uppercase tracking-wider text-muted-foreground">{t('evaluationDetail.revenueRanking')}</h4>
          <div className="overflow-hidden rounded-xl border border-border/50">
            <Table>
              <TableHeader className="bg-muted/50">
                <TableRow>
                  <TableHead className="font-bold">{t('topSku.kodeVariasi')}</TableHead>
                  <TableHead className="font-bold">{t('topSku.productName')}</TableHead>
                  <TableHead className="text-right font-bold">{t('topSku.totalOmzet')}</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {output1.slice(0, 5).map((row, i) => (
                  <TableRow key={String(row.kode_variasi ?? i)} className="hover:bg-muted/30">
                    <TableCell className="font-medium">{String(row.kode_variasi ?? '-')}</TableCell>
                    <TableCell className="max-w-[200px] truncate">{String(row.product_name ?? row.nama_produk ?? '-')}</TableCell>
                    <TableCell className="text-right font-bold text-primary">{formatValue(row.total_omzet, marketplace)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </div>
      )}
      {output2.length > 0 && (
        <div className="space-y-3">
          <h4 className="text-sm font-bold uppercase tracking-wider text-muted-foreground">{t('evaluationDetail.stockRanking')}</h4>
          <div className="overflow-hidden rounded-xl border border-border/50">
            <Table>
              <TableHeader className="bg-muted/50">
                <TableRow>
                  <TableHead className="font-bold">{t('topSku.kodeVariasi')}</TableHead>
                  <TableHead className="font-bold">{t('topSku.namaProduk')}</TableHead>
                  <TableHead className="text-right font-bold">{t('topSku.stok')}</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {output2.slice(0, 5).map((row, i) => (
                  <TableRow key={String(row.kode_variasi ?? i)} className="hover:bg-muted/30">
                    <TableCell className="font-medium">{String(row.kode_variasi ?? '-')}</TableCell>
                    <TableCell className="max-w-[200px] truncate">{String(row.nama_produk ?? '-')}</TableCell>
                    <TableCell className="text-right font-bold text-orange-500">{formatValue(row.stok, marketplace)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </div>
      )}
    </div>
  );
}

function DiscountContent({ data, t }: { data: Record<string, unknown>; t: TFunction }) {
  const text = typeof data.output_text === 'string' ? data.output_text : '';
  if (!text) return <p className="text-sm text-muted-foreground py-6 text-center">{t('common.noData')}</p>;

  const details = isRecord(data.details) ? data.details : undefined;
  const i18nDict = isRecord(details?.i18n) ? details.i18n : undefined;

  if (!i18nDict) {
    return (
      <pre className="whitespace-pre-wrap break-words rounded-lg bg-muted/50 p-4 text-sm font-mono leading-relaxed border border-border/50">
        {text}
      </pre>
    );
  }

  const lines: string[] = [];
  for (const key of ['topSkuDiscount', 'range', 'voucher', 'packageDiscount', 'affiliateCommission', 'fakeDiscount']) {
    const entry = i18nDict[key];
    if (isRecord(entry) && typeof entry.key === 'string') {
      lines.push(t(entry.key as string, entry.vars as Record<string, string>));
    }
  }

  return (
    <pre className="whitespace-pre-wrap break-words rounded-lg bg-muted/50 p-4 text-sm font-mono leading-relaxed border border-border/50">
      {lines.join('\n')}
    </pre>
  );
}

export const DataIntelligence = ({ calculatorResults, marketplace }: DataIntelligenceProps) => {
  const { t } = useTranslation();
  const [visitedTabs, setVisitedTabs] = useState<Set<string>>(new Set(['ads']));

  const handleTabChange = (value: string) => {
    setVisitedTabs((prev) => new Set(prev).add(value));
  };

  const adsData = isRecord(calculatorResults.ads_keyword) ? calculatorResults.ads_keyword : {};
  const discountData = isRecord(calculatorResults.discount) ? calculatorResults.discount : {};
  const skuData = isRecord(calculatorResults.top_sku) ? calculatorResults.top_sku : {};

  return (
    <Card className="border-none shadow-xl bg-card overflow-hidden">
      <CardContent className="p-8">
        <div className="flex items-center gap-2 mb-6">
          <span className="text-xs font-black text-primary/40 tracking-widest">04</span>
          <h2 className="text-lg font-bold tracking-tight text-foreground">{t('presentation.section.dataIntelligence')}</h2>
        </div>

        <Tabs defaultValue="ads" onValueChange={handleTabChange}>
          <TabsList variant="line" className="mb-6">
            <TabsTrigger value="ads">{t('presentation.intelligence.adsAnalysis')}</TabsTrigger>
            <TabsTrigger value="discount">{t('presentation.intelligence.discount')}</TabsTrigger>
            <TabsTrigger value="sku">{t('presentation.intelligence.topSku')}</TabsTrigger>
          </TabsList>

          <TabsContent value="ads">
            {visitedTabs.has('ads') && <AdsContent data={adsData} t={t} />}
          </TabsContent>
          <TabsContent value="discount">
            {visitedTabs.has('discount') && <DiscountContent data={discountData} t={t} />}
          </TabsContent>
          <TabsContent value="sku">
            {visitedTabs.has('sku') && <TopSkuContent data={skuData} t={t} marketplace={marketplace} />}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};
