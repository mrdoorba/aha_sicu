import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Copy, ClipboardCheck } from 'lucide-react';
import { useState } from 'react';
import { toast } from 'sonner';
import { Header } from '../components/layout/Header';
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
}: {
  breakdown: Array<Record<string, unknown>>;
}) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Category</TableHead>
          <TableHead className="text-right">Score</TableHead>
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

function AdsKeywordSection({ data }: { data: Record<string, unknown> }) {
  const text = (data.output_text as string) || '';
  if (!text) return <p className="text-muted-foreground">No data available</p>;
  return <pre className="whitespace-pre-wrap rounded bg-muted p-4 text-sm">{text}</pre>;
}

function TopSkuSection({ data }: { data: Record<string, unknown> }) {
  const details = data.details as Record<string, unknown> | undefined;
  const output1 = (details?.output_1 as Array<Record<string, unknown>>) || [];
  const output2 = (details?.output_2 as Array<Record<string, unknown>>) || [];
  const avgStock = details?.average_stock;

  if (output1.length === 0 && output2.length === 0) {
    return <p className="text-muted-foreground">No data available</p>;
  }

  return (
    <div className="space-y-4">
      {avgStock !== undefined && avgStock !== null && (
        <p className="text-sm font-medium">
          Average Stock: <span className="font-bold">{formatIDR(avgStock)}</span>
        </p>
      )}
      {output1.length > 0 && (
        <div>
          <h4 className="mb-2 text-sm font-medium">Revenue Ranking</h4>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Kode Variasi</TableHead>
                <TableHead>Product Name</TableHead>
                <TableHead className="text-right">Total Omzet</TableHead>
                <TableHead className="text-right">Rata2 Harga Jual</TableHead>
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
          <h4 className="mb-2 text-sm font-medium">Stock Ranking</h4>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Kode Variasi</TableHead>
                <TableHead>Nama Produk</TableHead>
                <TableHead>Varian</TableHead>
                <TableHead className="text-right">Stok</TableHead>
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
    </div>
  );
}

function DiscountSection({ data }: { data: Record<string, unknown> }) {
  const text = (data.output_text as string) || '';
  if (!text) return <p className="text-muted-foreground">No data available</p>;
  return <pre className="whitespace-pre-wrap rounded bg-muted p-4 text-sm">{text}</pre>;
}

function ManualInputsSection({
  inputs,
}: {
  inputs: Record<string, unknown>;
}) {
  const categories = Object.entries(inputs);
  if (categories.length === 0) {
    return <p className="text-muted-foreground">No manual inputs recorded</p>;
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

function EmailOutputSection({ emailOutput }: { emailOutput: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(emailOutput);
      setCopied(true);
      toast.success('Email output copied to clipboard');
      setTimeout(() => setCopied(false), 2000);
    } catch {
      toast.error('Failed to copy to clipboard');
    }
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-lg">Email Output</CardTitle>
        <Button
          variant="outline"
          size="sm"
          onClick={handleCopy}
          aria-label="Copy email output to clipboard"
        >
          {copied ? <ClipboardCheck className="size-4" /> : <Copy className="size-4" />}
          {copied ? 'Copied' : 'Copy'}
        </Button>
      </CardHeader>
      <CardContent>
        <pre className="whitespace-pre-wrap rounded bg-muted p-4 text-sm">{emailOutput}</pre>
      </CardContent>
    </Card>
  );
}

export function EvaluationDetailPage() {
  const params = useParams<{ id: string }>();
  const navigate = useNavigate();
  const id = Number(params.id);

  const validId = !isNaN(id) && id > 0;
  const { evaluation, isLoading, isError, isNotFound, refetch } = useEvaluationDetail(
    validId ? id : 0,
  );

  return (
    <div className="min-h-screen bg-muted">
      <Header />
      <main
        id="main-content"
        tabIndex={-1}
        className="mx-auto max-w-7xl py-6 px-4 sm:px-6 lg:px-8"
      >
        <Button
          variant="ghost"
          size="sm"
          className="mb-4"
          onClick={() => navigate('/history')}
        >
          <ArrowLeft className="size-4" />
          Back to History
        </Button>

        {isLoading && <LoadingSkeleton />}

        {!isLoading && (!validId || isNotFound) && (
          <Card>
            <CardContent className="flex flex-col items-center gap-4 py-12">
              <p className="text-muted-foreground">Evaluation not found</p>
              <Button variant="outline" onClick={() => navigate('/history')}>
                Back to History
              </Button>
            </CardContent>
          </Card>
        )}

        {!isLoading && isError && !isNotFound && (
          <Card>
            <CardContent className="flex flex-col items-center gap-4 py-12">
              <p className="text-destructive">Failed to load evaluation details</p>
              <Button variant="outline" onClick={() => refetch()}>
                Retry
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
                  <Badge variant={evaluation.template === 'fashion' ? 'default' : 'secondary'}>
                    {evaluation.template === 'fashion' ? 'Fashion' : 'Non-Fashion'}
                  </Badge>
                </div>
              </CardContent>
            </Card>

            {/* Score Section */}
            <div className="grid gap-6 md:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Final Score</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-3">
                    <span className="text-4xl font-bold">{evaluation.final_score.toFixed(1)}</span>
                    <span className="text-2xl">{evaluation.verdict}</span>
                  </div>
                  <p className="mt-2 text-sm text-muted-foreground">
                    {evaluation.template === 'fashion' ? 'Fashion' : 'Non-Fashion'} template &middot; Rule v{evaluation.rule_version}
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Score Breakdown</CardTitle>
                </CardHeader>
                <CardContent>
                  <ScoreBreakdownTable breakdown={evaluation.score_breakdown} />
                </CardContent>
              </Card>
            </div>

            {/* Calculator Results */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Calculator Results</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <h3 className="mb-3 text-base font-semibold">Ads Keyword Analysis</h3>
                  {evaluation.calculator_results.ads_keyword ? (
                    <AdsKeywordSection
                      data={evaluation.calculator_results.ads_keyword as Record<string, unknown>}
                    />
                  ) : (
                    <p className="text-muted-foreground">No data available</p>
                  )}
                </div>

                <div>
                  <h3 className="mb-3 text-base font-semibold">Top SKU Analysis</h3>
                  {evaluation.calculator_results.top_sku ? (
                    <TopSkuSection
                      data={evaluation.calculator_results.top_sku as Record<string, unknown>}
                    />
                  ) : (
                    <p className="text-muted-foreground">No data available</p>
                  )}
                </div>

                <div>
                  <h3 className="mb-3 text-base font-semibold">Discount Check</h3>
                  {evaluation.calculator_results.discount ? (
                    <DiscountSection
                      data={evaluation.calculator_results.discount as Record<string, unknown>}
                    />
                  ) : (
                    <p className="text-muted-foreground">No data available</p>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Manual Inputs */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Manual Inputs</CardTitle>
              </CardHeader>
              <CardContent>
                <ManualInputsSection inputs={evaluation.manual_inputs} />
              </CardContent>
            </Card>

            {/* Email Output (conditional) */}
            {evaluation.email_output && (
              <EmailOutputSection emailOutput={evaluation.email_output} />
            )}
          </div>
        )}
      </main>
    </div>
  );
}
