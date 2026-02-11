import type { CalculatorResult } from '../../../hooks/useCalculator';

interface AdsKeywordResultsProps {
  result: CalculatorResult;
}

export function AdsKeywordResults({ result }: AdsKeywordResultsProps) {
  return (
    <div>
      <div className="mb-2 flex items-center justify-between">
        <h4 className="text-sm font-semibold">Ads Keyword Calculator</h4>
        <time className="text-xs text-muted-foreground">
          {new Date(result.calculated_at).toLocaleString('id-ID')}
        </time>
      </div>
      <pre className="whitespace-pre-wrap break-words rounded-md bg-muted p-3 text-sm leading-relaxed">
        {result.output_text}
      </pre>
    </div>
  );
}
