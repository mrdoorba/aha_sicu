import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Copy, ClipboardCheck, Trash2, ChevronRight, ChevronDown } from 'lucide-react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
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
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '../components/ui/collapsible';
import { FinalScoreDisplay } from '../components/evaluation/scoring/FinalScoreDisplay';

function formatDate(dateStr: string): string {
  const d = new Date(dateStr);
  return d.toLocaleDateString('id-ID', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    timeZoneName: 'short',
  });
}

function formatIDR(value: unknown): string {
  if (typeof value !== 'number') return String(value ?? '-');
  return value.toLocaleString('id-ID');
}

function formatValue(value: unknown, key: string): string {
  if (value === null || value === undefined) return '-';
  if (Array.isArray(value)) return value.map((v) => formatIDR(v)).join(', ');
  if (typeof value === 'number') {
    if (key.includes('rate') || key.includes('percentage') || key.includes('persen')) {
      return `${value}%`;
    }
    if (key.includes('sales') || key.includes('omzet') || key.includes('budget') || key.includes('revenue')) {
      return formatIDR(value);
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
        {breakdown.map((cat) => (
          <TableRow key={String(cat.category)}>
            <TableCell>{String(cat.category)}</TableCell>
            <TableCell className="text-right">
              {Number(cat.score).toFixed(1)}
              {Number(cat.max_score) > 0 ? `/${Number(cat.max_score).toFixed(0)}` : ''}
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

function AdsKeywordSection({ data, t }: { data: Record<string, unknown>; t: (key: string) => string }) {
  const text = (data.output_text as string) || '';
  if (!text) return <p className="text-muted-foreground">{t('common.noData')}</p>;
  return <pre className="whitespace-pre-wrap rounded bg-muted p-4 text-sm">{text}</pre>;
}

function TopSkuSection({ data, t }: { data: Record<string, unknown>; t: (key: string) => string }) {
  const details = data.details as Record<string, unknown> | undefined;
  const output1 = ((details?.output_1 as Array<Record<string, unknown>>) || []).slice(0, 5);
  const output2 = ((details?.output_2 as Array<Record<string, unknown>>) || []).slice(0, 5);
  const avgStock = details?.average_stock;
  const [isOpen, setIsOpen] = useState(false);

  if (output1.length === 0 && output2.length === 0) {
    return <p className="text-muted-foreground">{t('common.noData')}</p>;
  }

  return (
    <div className="space-y-4">
      {avgStock !== undefined && avgStock !== null && (
        <p className="text-sm font-medium">
          {t('evaluationDetail.averageStock')}: <span className="font-bold">{String(avgStock)}</span>
        </p>
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
                    <TableHead>{t('topSku.kodeVariasi')}</TableHead>
                    <TableHead>{t('topSku.productName')}</TableHead>
                    <TableHead className="text-right">{t('topSku.totalOmzet')}</TableHead>
                    <TableHead className="text-right">{t('topSku.avgPrice')}</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {output1.map((row, i) => (
                    <TableRow key={String(row.kode_variasi ?? i)}>
                      <TableCell>{String(row.kode_variasi ?? '-')}</TableCell>
                      <TableCell>{String(row.product_name ?? row.nama_produk ?? '-')}</TableCell>
                      <TableCell className="text-right">{formatIDR(row.total_omzet)}</TableCell>
                      <TableCell className="text-right">{formatIDR(row.rata2_harga_jual)}</TableCell>
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
                    <TableHead>{t('topSku.kodeVariasi')}</TableHead>
                    <TableHead>{t('topSku.namaProduk')}</TableHead>
                    <TableHead>{t('topSku.varian')}</TableHead>
                    <TableHead className="text-right">{t('topSku.stok')}</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {output2.map((row, i) => (
                    <TableRow key={String(row.kode_variasi ?? i)}>
                      <TableCell>{String(row.kode_variasi ?? '-')}</TableCell>
                      <TableCell>{String(row.nama_produk ?? '-')}</TableCell>
                      <TableCell>{String(row.varian ?? '-')}</TableCell>
                      <TableCell className="text-right">{formatIDR(row.stok)}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CollapsibleContent>
      </Collapsible>
    </div>
  );
}

function DiscountSection({ data, t }: { data: Record<string, unknown>; t: (key: string) => string }) {
  const text = (data.output_text as string) || '';
  if (!text) return <p className="text-muted-foreground">{t('common.noData')}</p>;
  return <pre className="whitespace-pre-wrap rounded bg-muted p-4 text-sm">{text}</pre>;
}

function ManualInputsSection({
  inputs,
  t,
}: {
  inputs: Record<string, unknown>;
  t: (key: string) => string;
}) {
  const categories = Object.entries(inputs);
  if (categories.length === 0) {
    return <p className="text-muted-foreground">{t('evaluationDetail.noManualInputs')}</p>;
  }

  return (
    <div className="space-y-4">
      {categories.map(([category, values]) => (
        <div key={category}>
          <h3 className="mb-2 text-sm font-semibold capitalize">{category}</h3>
          {typeof values === 'object' && values !== null ? (
            <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-sm sm:grid-cols-3">
              {Object.entries(values as Record<string, unknown>).map(([key, val]) => (
                <div key={key} className="flex justify-between gap-2 border-b border-border/50 py-1">
                  <span className="text-muted-foreground">{key.replace(/_/g, ' ')}</span>
                  <span className="font-medium">{formatValue(val, key)}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm">{String(values)}</p>
          )}
        </div>
      ))}
    </div>
  );
}

function EmailOutputSection({ emailOutput, t }: { emailOutput: string; t: (key: string) => string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(emailOutput);
      setCopied(true);
      toast.success(t('evaluationDetail.emailCopied'));
      setTimeout(() => setCopied(false), 2000);
    } catch {
      toast.error(t('evaluationDetail.copyFailed'));
    }
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-lg">{t('evaluationDetail.emailOutput')}</CardTitle>
        <Button
          variant="outline"
          size="sm"
          onClick={handleCopy}
          aria-label={t('evaluationDetail.emailOutput')}
        >
          {copied ? <ClipboardCheck className="size-4" /> : <Copy className="size-4" />}
          {copied ? t('common.copied') : t('common.copy')}
        </Button>
      </CardHeader>
      <CardContent>
        <pre className="whitespace-pre-wrap rounded bg-muted p-4 text-sm">{emailOutput}</pre>
      </CardContent>
    </Card>
  );
}

export function EvaluationDetailPage() {
  const { t } = useTranslation();
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
                      {evaluation.evaluator_email} &middot; {formatDate(evaluation.created_at)}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
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

            {/* Calculator Results */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">{t('evaluationDetail.calculatorResults')}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <h3 className="mb-3 text-base font-semibold">{t('evaluationDetail.adsKeywordAnalysis')}</h3>
                  {evaluation.calculator_results.ads_keyword ? (
                    <AdsKeywordSection
                      data={evaluation.calculator_results.ads_keyword as Record<string, unknown>}
                      t={t}
                    />
                  ) : (
                    <p className="text-muted-foreground">{t('common.noData')}</p>
                  )}
                </div>

                <div>
                  <h3 className="mb-3 text-base font-semibold">{t('evaluationDetail.topSkuAnalysis')}</h3>
                  {evaluation.calculator_results.top_sku ? (
                    <TopSkuSection
                      data={evaluation.calculator_results.top_sku as Record<string, unknown>}
                      t={t}
                    />
                  ) : (
                    <p className="text-muted-foreground">{t('common.noData')}</p>
                  )}
                </div>

                <div>
                  <h3 className="mb-3 text-base font-semibold">{t('evaluationDetail.discountCheck')}</h3>
                  {evaluation.calculator_results.discount ? (
                    <DiscountSection
                      data={evaluation.calculator_results.discount as Record<string, unknown>}
                      t={t}
                    />
                  ) : (
                    <p className="text-muted-foreground">{t('common.noData')}</p>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Manual Inputs */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">{t('evaluationDetail.manualInputs')}</CardTitle>
              </CardHeader>
              <CardContent>
                <ManualInputsSection inputs={evaluation.manual_inputs} t={t} />
              </CardContent>
            </Card>

            {/* Email Output (conditional) */}
            {evaluation.email_output && (
              <EmailOutputSection emailOutput={evaluation.email_output} t={t} />
            )}
          </div>
        )}
      </div>
    </div>
  );
}
