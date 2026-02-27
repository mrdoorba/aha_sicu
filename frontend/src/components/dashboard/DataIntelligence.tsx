import { useState } from 'react';
import { Card, CardContent } from '../ui/card';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../ui/tabs';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table';
import { useTranslation } from 'react-i18next';

interface DataIntelligenceProps {
  calculatorResults: Record<string, unknown>;
}

function formatIDR(value: unknown): string {
  if (typeof value !== 'number') return String(value ?? '-');
  return value.toLocaleString('id-ID');
}

function AdsContent({ data, t }: { data: Record<string, unknown>; t: (key: string) => string }) {
  const text = (data.output_text as string) || '';
  if (!text) return <p className="text-sm text-muted-foreground py-6 text-center">{t('common.noData')}</p>;
  return <pre className="whitespace-pre-wrap rounded-lg bg-muted/50 p-4 text-sm font-mono border border-border/50">{text}</pre>;
}

function TopSkuContent({ data, t }: { data: Record<string, unknown>; t: (key: string) => string }) {
  const details = data.details as Record<string, unknown> | undefined;
  const output1 = (details?.output_1 as Array<Record<string, unknown>>) || [];
  const output2 = (details?.output_2 as Array<Record<string, unknown>>) || [];
  const avgStock = details?.average_stock;

  if (output1.length === 0 && output2.length === 0) {
    return <p className="text-sm text-muted-foreground py-6 text-center">{t('common.noData')}</p>;
  }

  return (
    <div className="space-y-6">
      {avgStock !== undefined && avgStock !== null && (
        <div className="inline-flex items-center rounded-lg bg-primary/5 px-4 py-2 border border-primary/10">
          <p className="text-sm font-semibold">
            {t('evaluationDetail.averageStock')}: <span className="text-primary ml-1">{formatIDR(avgStock)}</span>
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
                    <TableCell className="text-right font-bold text-primary">{formatIDR(row.total_omzet)}</TableCell>
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
                    <TableCell className="text-right font-bold text-orange-500">{formatIDR(row.stok)}</TableCell>
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


export const DataIntelligence = ({ calculatorResults }: DataIntelligenceProps) => {
  const { t } = useTranslation();
  const [visitedTabs, setVisitedTabs] = useState<Set<string>>(new Set(['ads']));

  const handleTabChange = (value: string) => {
    setVisitedTabs((prev) => new Set(prev).add(value));
  };

  const adsData = (calculatorResults.ads_keyword as Record<string, unknown>) || {};
  const skuData = (calculatorResults.top_sku as Record<string, unknown>) || {};

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
            <TabsTrigger value="sku">{t('presentation.intelligence.topSku')}</TabsTrigger>
          </TabsList>

          <TabsContent value="ads">
            {visitedTabs.has('ads') && <AdsContent data={adsData} t={t} />}
          </TabsContent>
          <TabsContent value="sku">
            {visitedTabs.has('sku') && <TopSkuContent data={skuData} t={t} />}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};
