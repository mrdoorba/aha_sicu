import { useTranslation } from 'react-i18next';
import { AlertTriangle, Clock, Loader2, RefreshCw } from 'lucide-react';
import { Card, CardContent } from '../../ui/card';
import { Button } from '../../ui/button';
import {
  useCalculatorResults,
  useCalculatorStatus,
  useRunAllCalculators,
  useRunCalculator,
  useAutoCalcErrors,
} from '../../../hooks/useCalculator';
import type { CalculatorResult } from '../../../hooks/useCalculator';
import { AdsKeywordResults } from './AdsKeywordResults';
import { TopSkuResults } from './TopSkuResults';
import { DiscountResults } from './DiscountResults';

interface CalculatorResultsSectionProps {
  brandId: number;
  marketplace?: string;
}

const FILE_LABELS: Record<string, string> = {
  cpc_ad_report: 'calculator.file.cpcAdReport',
  keyword_report: 'calculator.file.keywordReport',
  order_export: 'calculator.file.orderExport',
  mass_update: 'calculator.file.massUpdate',
};

const CALCULATOR_LABELS: Record<string, string> = {
  ads_keyword: 'calculator.label.adsKeyword',
  top_sku: 'calculator.label.topSku',
  discount: 'calculator.label.discount',
};

const CALCULATOR_ORDER = ['ads_keyword', 'top_sku', 'discount'] as const;

function ResultRenderer({ result, marketplace }: { result: CalculatorResult; marketplace?: string }) {
  switch (result.calculator_type) {
    case 'ads_keyword':
      return <AdsKeywordResults result={result} />;
    case 'top_sku':
      return <TopSkuResults result={result} marketplace={marketplace} />;
    case 'discount':
      return <DiscountResults result={result} />;
    default:
      return null;
  }
}

function PendingState({ missingFiles }: { missingFiles: string[] }) {
  const { t } = useTranslation();
  return (
    <div className="flex items-start gap-2 text-sm text-amber-600">
      <Clock className="mt-0.5 size-4 shrink-0" />
      <div>
        <p className="font-medium">{t('calculator.waitingFor')}</p>
        <ul className="mt-1 list-inside list-disc text-xs">
          {missingFiles.map((f) => (
            <li key={f}>{t(FILE_LABELS[f] ?? f)}</li>
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
  const { t } = useTranslation();
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
          {t('calculator.retry')}
        </Button>
      </div>
    </div>
  );
}

function AutoCalcWarning({
  reason,
  onRetry,
  isRetrying,
}: {
  reason?: string;
  onRetry: () => void;
  isRetrying: boolean;
}) {
  const { t } = useTranslation();
  return (
    <div className="mb-2 flex items-start gap-2 rounded-md bg-amber-50 p-2 text-sm text-amber-700">
      <AlertTriangle className="mt-0.5 size-4 shrink-0" />
      <div className="flex-1">
        <p>{reason ? t('calculator.autoCalcFailedReason', { reason }) : t('calculator.autoCalcFailed')}</p>
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
          {t('calculator.calculate')}
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
  autoCalcError,
  marketplace,
}: {
  calcType: string;
  brandId: number;
  result?: CalculatorResult;
  status?: { status: string; has_result: boolean; missing_files: string[]; missing_manual: string[] };
  autoCalcError?: { reason?: string };
  marketplace?: string;
}) {
  const { t } = useTranslation();
  const runCalc = useRunCalculator(brandId, calcType as 'ads_keyword' | 'discount' | 'top_sku');

  // Has result → show it
  if (result) {
    return (
      <Card>
        <CardContent className="pt-4">
          <ResultRenderer result={result} marketplace={marketplace} />
        </CardContent>
      </Card>
    );
  }

  // Error from a previous run attempt (tracked via mutation state)
  if (runCalc.isError) {
    return (
      <Card>
        <CardContent className="pt-4">
          <h4 className="mb-2 text-sm font-semibold">{t(CALCULATOR_LABELS[calcType] ?? calcType)}</h4>
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
          <h4 className="mb-2 text-sm font-semibold">{t(CALCULATOR_LABELS[calcType] ?? calcType)}</h4>
          <PendingState missingFiles={missingFiles} />
        </CardContent>
      </Card>
    );
  }

  // Ready but no result yet — may have auto-calc error
  return (
    <Card>
      <CardContent className="pt-4">
        <h4 className="mb-2 text-sm font-semibold">{t(CALCULATOR_LABELS[calcType] ?? calcType)}</h4>
        {autoCalcError ? (
          <AutoCalcWarning
            reason={autoCalcError.reason}
            onRetry={() => runCalc.mutate()}
            isRetrying={runCalc.isPending}
          />
        ) : (
          <>
            <p className="text-sm text-muted-foreground">{t('calculator.readyToCalculate')}</p>
            <Button
              variant="outline"
              size="sm"
              className="mt-2"
              onClick={() => runCalc.mutate()}
              disabled={runCalc.isPending}
            >
              {runCalc.isPending ? (
                <Loader2 className="mr-1 size-3 animate-spin" />
              ) : (
                <RefreshCw className="mr-1 size-3" />
              )}
              {t('calculator.calculate')}
            </Button>
          </>
        )}
      </CardContent>
    </Card>
  );
}

export function CalculatorResultsSection({ brandId, marketplace }: CalculatorResultsSectionProps) {
  const { t } = useTranslation();
  const { data: resultsData, isLoading: resultsLoading } = useCalculatorResults(brandId);
  const { data: statusData, isLoading: statusLoading } = useCalculatorStatus(brandId);
  const runAll = useRunAllCalculators(brandId);
  const autoCalcErrors = useAutoCalcErrors(brandId);
  const autoCalcErrorsByType: Record<string, { reason?: string }> = {};
  for (const err of autoCalcErrors) {
    autoCalcErrorsByType[err.calculator_type] = { reason: err.reason };
  }

  if (resultsLoading || statusLoading) {
    return (
      <div className="mt-4">
        <p className="mb-3 text-sm font-semibold uppercase text-muted-foreground">
          {t('calculator.resultsTitle')}
        </p>
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Loader2 className="size-4 animate-spin" />
          {t('calculator.loading')}
        </div>
      </div>
    );
  }

  const resultsByType: Record<string, CalculatorResult> = {};
  for (const r of resultsData?.results ?? []) {
    resultsByType[r.calculator_type] = r;
  }

  const hasAnyResult = Object.keys(resultsByType).length > 0;
  const hasAnyReadyWithoutResult = CALCULATOR_ORDER.some(
    (ct) => statusData?.calculators[ct]?.status === 'ready' && !resultsByType[ct],
  );
  const showCalcAllButton = hasAnyResult || hasAnyReadyWithoutResult;

  return (
    <div className="mt-4">
      <div className="mb-3 flex items-center justify-between">
        <p className="text-sm font-semibold uppercase text-muted-foreground">
          {t('calculator.resultsTitle')}
        </p>
        {showCalcAllButton && (
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
            {hasAnyResult ? t('calculator.recalculateAll') : t('calculator.calculateAll')}
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
            autoCalcError={autoCalcErrorsByType[calcType]}
            marketplace={marketplace}
          />
        ))}
      </div>
    </div>
  );
}
