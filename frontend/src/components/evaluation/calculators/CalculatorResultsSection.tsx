import { AlertTriangle, Clock, Loader2, RefreshCw } from 'lucide-react';
import { Card, CardContent } from '../../ui/card';
import { Button } from '../../ui/button';
import {
  useCalculatorResults,
  useCalculatorStatus,
  useRunAllCalculators,
  useRunCalculator,
} from '../../../hooks/useCalculator';
import type { CalculatorResult } from '../../../hooks/useCalculator';
import { AdsKeywordResults } from './AdsKeywordResults';
import { TopSkuResults } from './TopSkuResults';
import { DiscountResults } from './DiscountResults';

interface CalculatorResultsSectionProps {
  brandId: number;
}

const FILE_LABELS: Record<string, string> = {
  cpc_ad_report: 'Iklan Check Up V2A (.csv)',
  keyword_report: 'Iklan Check Up V2B (.csv)',
  order_export: 'Order Export (.xlsx)',
  mass_update: 'Mass Update / Sales Info (.xlsx)',
};

const CALCULATOR_LABELS: Record<string, string> = {
  ads_keyword: 'Ads Keyword Calculator',
  top_sku: 'Top SKU Calculator',
  discount: 'Discount Check Calculator',
};

const CALCULATOR_ORDER = ['ads_keyword', 'top_sku', 'discount'] as const;

function ResultRenderer({ result }: { result: CalculatorResult }) {
  switch (result.calculator_type) {
    case 'ads_keyword':
      return <AdsKeywordResults result={result} />;
    case 'top_sku':
      return <TopSkuResults result={result} />;
    case 'discount':
      return <DiscountResults result={result} />;
    default:
      return null;
  }
}

function PendingState({ missingFiles }: { missingFiles: string[] }) {
  return (
    <div className="flex items-start gap-2 text-sm text-amber-600">
      <Clock className="mt-0.5 size-4 shrink-0" />
      <div>
        <p className="font-medium">Waiting for:</p>
        <ul className="mt-1 list-inside list-disc text-xs">
          {missingFiles.map((f) => (
            <li key={f}>{FILE_LABELS[f] ?? f}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}

function ErrorState({
  message,
  onRetry,
  isRetrying,
}: {
  message: string;
  onRetry: () => void;
  isRetrying: boolean;
}) {
  return (
    <div className="flex items-start gap-2 text-sm text-destructive">
      <AlertTriangle className="mt-0.5 size-4 shrink-0" />
      <div className="flex-1">
        <p>{message}</p>
        <Button
          variant="outline"
          size="sm"
          className="mt-2"
          onClick={onRetry}
          disabled={isRetrying}
        >
          {isRetrying ? (
            <Loader2 className="mr-1 size-3 animate-spin" />
          ) : (
            <RefreshCw className="mr-1 size-3" />
          )}
          Retry
        </Button>
      </div>
    </div>
  );
}

function CalculatorCard({
  calcType,
  brandId,
  result,
  status,
}: {
  calcType: string;
  brandId: number;
  result?: CalculatorResult;
  status?: { status: string; has_result: boolean; missing_files: string[]; missing_manual: string[] };
}) {
  const runCalc = useRunCalculator(brandId, calcType as 'ads_keyword' | 'discount' | 'top_sku');

  // Has result → show it
  if (result) {
    return (
      <Card>
        <CardContent className="pt-4">
          <ResultRenderer result={result} />
        </CardContent>
      </Card>
    );
  }

  // Error from a previous run attempt (tracked via mutation state)
  if (runCalc.isError) {
    return (
      <Card>
        <CardContent className="pt-4">
          <h4 className="mb-2 text-sm font-semibold">{CALCULATOR_LABELS[calcType] ?? calcType}</h4>
          <ErrorState
            message={String(runCalc.error)}
            onRetry={() => runCalc.mutate()}
            isRetrying={runCalc.isPending}
          />
        </CardContent>
      </Card>
    );
  }

  // Pending — missing files
  const missingFiles = [...(status?.missing_files ?? []), ...(status?.missing_manual ?? [])];
  if (missingFiles.length > 0) {
    return (
      <Card>
        <CardContent className="pt-4">
          <h4 className="mb-2 text-sm font-semibold">{CALCULATOR_LABELS[calcType] ?? calcType}</h4>
          <PendingState missingFiles={missingFiles} />
        </CardContent>
      </Card>
    );
  }

  // Ready but no result yet
  return (
    <Card>
      <CardContent className="pt-4">
        <h4 className="mb-2 text-sm font-semibold">{CALCULATOR_LABELS[calcType] ?? calcType}</h4>
        <p className="text-sm text-muted-foreground">Ready to calculate</p>
      </CardContent>
    </Card>
  );
}

export function CalculatorResultsSection({ brandId }: CalculatorResultsSectionProps) {
  const { data: resultsData, isLoading: resultsLoading } = useCalculatorResults(brandId);
  const { data: statusData, isLoading: statusLoading } = useCalculatorStatus(brandId);
  const runAll = useRunAllCalculators(brandId);

  if (resultsLoading || statusLoading) {
    return (
      <div className="mt-4">
        <p className="mb-3 text-sm font-semibold uppercase text-muted-foreground">
          Calculator Results
        </p>
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Loader2 className="size-4 animate-spin" />
          Loading calculator results...
        </div>
      </div>
    );
  }

  const resultsByType: Record<string, CalculatorResult> = {};
  for (const r of resultsData?.results ?? []) {
    resultsByType[r.calculator_type] = r;
  }

  const hasAnyResult = Object.keys(resultsByType).length > 0;

  return (
    <div className="mt-4">
      <div className="mb-3 flex items-center justify-between">
        <p className="text-sm font-semibold uppercase text-muted-foreground">
          Calculator Results
        </p>
        {hasAnyResult && (
          <Button
            variant="outline"
            size="sm"
            onClick={() => runAll.mutate()}
            disabled={runAll.isPending}
          >
            {runAll.isPending ? (
              <Loader2 className="mr-1 size-3 animate-spin" />
            ) : (
              <RefreshCw className="mr-1 size-3" />
            )}
            Recalculate All
          </Button>
        )}
      </div>

      <div className="grid gap-4">
        {CALCULATOR_ORDER.map((calcType) => (
          <CalculatorCard
            key={calcType}
            calcType={calcType}
            brandId={brandId}
            result={resultsByType[calcType]}
            status={statusData?.calculators[calcType]}
          />
        ))}
      </div>
    </div>
  );
}
