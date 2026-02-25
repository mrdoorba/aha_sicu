import { useEvaluationDetail } from '../../hooks/useEvaluationDetail';
import { useBrandEvaluations } from '../../hooks/useBrandEvaluations';
import { useBrandDetail } from '../../hooks/useBrandDetail';
import { Loader2, ArrowLeft, CheckCircle2, XCircle, AlertCircle, Edit3, PlusCircle } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table';
import { EmailOutput } from '../evaluation/scoring/EmailOutput';
import { cn } from '../../lib/utils';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';

interface PresentationDashboardProps {
  brandId: number;
  onBack: () => void;
}

function formatIDR(value: unknown): string {
  if (typeof value !== 'number') return String(value ?? '-');
  return value.toLocaleString('id-ID');
}

function AdsKeywordSection({ data, t }: { data: Record<string, unknown>; t: (key: string) => string }) {
  const text = (data.output_text as string) || '';
  if (!text) return <p className="text-muted-foreground">{t('common.noData')}</p>;
  return <pre className="whitespace-pre-wrap rounded bg-muted/50 p-4 text-sm font-mono border border-border/50">{text}</pre>;
}

function TopSkuSection({ data, t }: { data: Record<string, unknown>; t: (key: string) => string }) {
  const details = data.details as Record<string, unknown> | undefined;
  const output1 = (details?.output_1 as Array<Record<string, unknown>>) || [];
  const output2 = (details?.output_2 as Array<Record<string, unknown>>) || [];
  const avgStock = details?.average_stock;

  if (output1.length === 0 && output2.length === 0) {
    return <p className="text-muted-foreground">{t('common.noData')}</p>;
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

function DiscountSection({ data, t }: { data: Record<string, unknown>; t: (key: string) => string }) {
  const text = (data.output_text as string) || '';
  if (!text) return <p className="text-muted-foreground">{t('common.noData')}</p>;
  return <pre className="whitespace-pre-wrap rounded bg-muted/50 p-4 text-sm font-mono border border-border/50">{text}</pre>;
}

export const PresentationDashboard = ({ brandId, onBack }: PresentationDashboardProps) => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { data: brand, isLoading: brandLoading } = useBrandDetail(brandId);
  const { evaluations, isLoading: evLoading } = useBrandEvaluations(brandId, 1, undefined, undefined, true);
  const latestEvaluationId = evaluations?.[0]?.id;
  const { evaluation, isLoading: detailLoading } = useEvaluationDetail(latestEvaluationId ?? 0);

  const isLoading = brandLoading || evLoading || detailLoading;

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-20 animate-pulse">
        <Loader2 className="size-12 animate-spin text-primary" />
        <p className="mt-6 text-muted-foreground text-xl font-medium tracking-tight">{t('presentation.loading')}</p>
      </div>
    );
  }

  if (!evaluation) {
    return (
      <div className="flex flex-col items-center justify-center py-20 space-y-8 max-w-md mx-auto">
        <div className="relative">
          <div className="absolute inset-0 bg-primary/10 rounded-full blur-2xl animate-pulse" />
          <div className="relative rounded-full bg-card p-8 border border-border shadow-xl">
            <AlertCircle className="size-16 text-muted-foreground/50" />
          </div>
        </div>
        <div className="text-center space-y-3">
          <h2 className="text-3xl font-black tracking-tight text-foreground">{t('presentation.empty.title')}</h2>
          <p className="text-muted-foreground text-lg leading-relaxed">
            {t('presentation.empty.description')}
          </p>
        </div>
        <div className="flex flex-col w-full gap-3">
          <Button onClick={() => navigate(`/evaluation/${brandId}`)} size="lg" className="h-14 rounded-2xl shadow-xl shadow-primary/20 text-lg font-bold transition-all hover:scale-[1.02]">
            <PlusCircle className="mr-2 size-5" />
            {t('presentation.empty.startEvaluation')}
          </Button>
          <Button onClick={onBack} variant="ghost" size="lg" className="h-14 rounded-2xl text-muted-foreground hover:text-foreground">
            <ArrowLeft className="mr-2 size-5" />
            {t('presentation.empty.backToSearch')}
          </Button>
        </div>
      </div>
    );
  }

  const score = Math.round(evaluation.final_score);
  const verdict = evaluation.verdict;
  
  const isApproved = verdict === '✔️';
  const isRejected = verdict.startsWith('❌');

  return (
    <div className="mx-auto max-w-7xl space-y-10 py-6">
      <div className="flex items-center justify-between px-2">
        <div className="flex items-center gap-2">
          <Button variant="ghost" onClick={onBack} className="text-muted-foreground hover:text-foreground h-10 px-3">
            <ArrowLeft className="mr-2 size-4" />
            {t('presentation.back')}
          </Button>
          <div className="h-4 w-[1px] bg-border mx-2 hidden sm:block" />
          <Badge variant={evaluation.template === 'fashion' ? 'default' : 'secondary'} className="px-3 py-0.5 text-xs font-bold uppercase tracking-widest hidden sm:flex">
            {evaluation.template === 'fashion' ? t('evaluationSections.fashion') : t('evaluationSections.nonFashion')}
          </Badge>
        </div>
        <Button 
          onClick={() => navigate(`/evaluation/${brandId}`)} 
          className="rounded-xl h-10 px-5 font-bold shadow-lg shadow-primary/10 transition-all hover:scale-[1.03] active:scale-[0.97]"
        >
          <Edit3 className="mr-2 size-4" />
          {t('presentation.editEvaluation')}
        </Button>
      </div>

      <div className="grid gap-8 lg:grid-cols-3">
        {/* Main Score Card */}
        <Card className="lg:col-span-2 border-none shadow-2xl bg-gradient-to-br from-card to-muted/30 overflow-hidden relative group">
          <div className="absolute top-0 right-0 w-96 h-96 bg-primary/5 rounded-full -mr-48 -mt-48 blur-3xl transition-opacity duration-1000 group-hover:opacity-100 opacity-60 pointer-events-none" />
          <CardContent className="p-10 flex flex-col items-center text-center relative z-10">
            <div className="space-y-2">
              <h1 className="text-4xl font-black tracking-tight text-foreground sm:text-6xl lg:text-7xl leading-tight">
                {brand?.brand_name || evaluation.brand_name}
              </h1>
              <div className="flex items-center justify-center gap-3">
                <div className="h-[2px] w-8 bg-primary/30 rounded-full" />
                <p className="text-lg text-muted-foreground font-bold uppercase tracking-[0.2em]">{t('presentation.partnerVerdict')}</p>
                <div className="h-[2px] w-8 bg-primary/30 rounded-full" />
              </div>
            </div>

            <div className="relative mt-12 mb-10">
              <div className={cn(
                "flex h-56 w-56 items-center justify-center rounded-full border-[14px] shadow-2xl transition-all duration-700 bg-card",
                isApproved ? "border-success shadow-success/10" : 
                isRejected ? "border-destructive shadow-destructive/10" : 
                "border-muted shadow-muted/10"
              )}>
                <span className="text-8xl font-black tabular-nums tracking-tighter">{score}</span>
              </div>
              <div className={cn(
                "absolute -bottom-5 left-1/2 -translate-x-1/2 flex items-center gap-3 px-8 py-3 rounded-full shadow-2xl border text-xl font-black uppercase tracking-widest transition-all duration-700",
                isApproved ? "bg-success text-white border-success" : 
                isRejected ? "bg-destructive text-white border-destructive" : 
                "bg-muted text-muted-foreground border-border"
              )}>
                {isApproved ? <CheckCircle2 className="size-7" /> : isRejected ? <XCircle className="size-7" /> : null}
                {isApproved ? t('presentation.verdict.approved') : isRejected ? t('presentation.verdict.rejected') : t('presentation.verdict.pending')}
              </div>
            </div>

            <div className="mt-8 max-w-xl p-6 rounded-3xl bg-muted/30 backdrop-blur-sm border border-border/20">
              <p className="text-xl text-foreground font-medium italic leading-relaxed text-balance">
                "{evaluation.verdict.replace(/^(✔️|❌)\s*/, '') || (isApproved ? t('presentation.verdict.fallbackApproved') : t('presentation.verdict.fallbackRejected'))}"
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Breakdown Card */}
        <Card className="border-none shadow-xl bg-card">
          <CardHeader className="pb-2">
            <CardTitle className="text-2xl font-black tracking-tight text-foreground">{t('presentation.scoreBreakdown.title')}</CardTitle>
            <p className="text-sm text-muted-foreground font-medium">{t('presentation.scoreBreakdown.subtitle')}</p>
          </CardHeader>
          <CardContent>
            <div className="space-y-8 pt-4">
              {evaluation.score_breakdown.map((cat, idx) => {
                const catScore = Number(cat.score);
                const maxScore = Number(cat.max_score);
                const percent = maxScore > 0 ? (catScore / maxScore) * 100 : 0;
                
                return (
                  <div key={idx} className="space-y-3">
                    <div className="flex items-center justify-between text-sm">
                      <span className="font-bold text-foreground tracking-tight">{String(cat.category)}</span>
                      <span className="font-black tabular-nums text-primary">{catScore.toFixed(1)} <span className="text-muted-foreground/60 font-medium">/ {maxScore.toFixed(0)}</span></span>
                    </div>
                    <div className="h-3 w-full overflow-hidden rounded-full bg-muted shadow-inner">
                      <div 
                        className={cn(
                          "h-full rounded-full transition-all duration-[1500ms] ease-out",
                          percent >= 80 ? "bg-success shadow-[0_0_12px_rgba(34,197,94,0.4)]" : 
                          percent >= 50 ? "bg-primary shadow-[0_0_12px_rgba(50,95,236,0.4)]" : 
                          "bg-orange-500 shadow-[0_0_12px_rgba(249,115,22,0.4)]"
                        )}
                        style={{ width: `${percent}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-8 lg:grid-cols-2">
        {/* Calculator Intelligence */}
        <Card className="border-none shadow-xl bg-card lg:col-span-2 overflow-hidden">
          <CardHeader className="border-b border-border/50 bg-muted/30">
            <CardTitle className="text-2xl font-black tracking-tight">{t('presentation.operationIntelligence.title')}</CardTitle>
            <p className="text-sm text-muted-foreground font-medium">{t('presentation.operationIntelligence.subtitle')}</p>
          </CardHeader>
          <CardContent className="p-0">
            <div className="grid gap-0 md:grid-cols-3 divide-y md:divide-y-0 md:divide-x divide-border/50">
              <div className="p-8 space-y-6">
                <div className="flex items-center gap-2 mb-2">
                  <Badge variant="outline" className="rounded-md bg-primary/5 text-primary border-primary/20">{t('presentation.badge.adsAnalysis')}</Badge>
                </div>
                <AdsKeywordSection
                  data={(evaluation.calculator_results.ads_keyword as Record<string, unknown>) || {}}
                  t={t}
                />
              </div>

              <div className="p-8 space-y-6">
                <div className="flex items-center gap-2 mb-2">
                  <Badge variant="outline" className="rounded-md bg-orange-500/5 text-orange-500 border-orange-500/20">{t('presentation.badge.skuStrategy')}</Badge>
                </div>
                <TopSkuSection
                  data={(evaluation.calculator_results.top_sku as Record<string, unknown>) || {}}
                  t={t}
                />
              </div>

              <div className="p-8 space-y-6">
                <div className="flex items-center gap-2 mb-2">
                  <Badge variant="outline" className="rounded-md bg-purple-500/5 text-purple-500 border-purple-500/20">{t('presentation.badge.discountCompliance')}</Badge>
                </div>
                <DiscountSection
                  data={(evaluation.calculator_results.discount as Record<string, unknown>) || {}}
                  t={t}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Email Output */}
        {evaluation.email_output && (
          <div className="lg:col-span-2">
            <Card className="border-none shadow-2xl bg-card overflow-hidden">
              <CardHeader className="bg-foreground text-white p-8">
                <CardTitle className="text-2xl font-black tracking-tight flex items-center gap-3">
                  <div className="h-2 w-2 rounded-full bg-primary animate-pulse" />
                  {t('presentation.emailOutput.title')}
                </CardTitle>
                <p className="text-sidebar-accent/60 font-medium">{t('presentation.emailOutput.subtitle')}</p>
              </CardHeader>
              <CardContent className="p-0">
                <EmailOutput 
                  subject={t('presentation.emailOutput.subject', { brandName: brand?.brand_name || evaluation.brand_name })}
                  body={evaluation.email_output}
                />
              </CardContent>
            </Card>
          </div>
        )}
      </div>

      <div className="pt-10 border-t border-border/50 text-center flex flex-col items-center gap-1">
        <p className="text-muted-foreground text-sm font-bold uppercase tracking-widest">{t('presentation.footer.title')}</p>
        <p className="text-muted-foreground/60 text-xs font-medium">
          {t('presentation.footer.conductedBy')} <span className="text-foreground/80 font-bold">{evaluation.evaluator_email}</span> {t('presentation.footer.onDate')} {new Date(evaluation.created_at).toLocaleDateString('id-ID', { day: 'numeric', month: 'long', year: 'numeric' })}
        </p>
      </div>
    </div>
  );
};
