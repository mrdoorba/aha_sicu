import { useTranslation } from 'react-i18next';
import { cn } from '../../lib/utils';
import { renderTranslatable, type TranslatableText } from '../../utils/renderTranslatable';

interface CategoryMetricCardProps {
  metric: string;
  value: unknown;
  verdict: string;
  score: number;
  benchmark: string;
  message: string;
  metric_i18n?: TranslatableText | null;
  message_i18n?: TranslatableText | null;
  benchmark_i18n?: TranslatableText | null;
}


export const CategoryMetricCard = ({ metric, value, benchmark, message, metric_i18n, message_i18n, benchmark_i18n }: CategoryMetricCardProps) => {
  const { t } = useTranslation();
  const displayMetric = renderTranslatable(metric, metric_i18n, t);
  const displayMessage = renderTranslatable(message, message_i18n, t);
  const displayBenchmark = renderTranslatable(benchmark, benchmark_i18n, t);

  const displayValue = (() => {
    if (value === null || value === undefined) return '-';
    if (typeof value === 'number') {
      // Use original metric (Indonesian) for format checks — stable across languages
      if (metric.startsWith('%')) {
        return `${(value * 100).toFixed(1)}%`;
      }
      if (metric.includes('Tingkat') || metric.includes('Persentase')) {
        return `${value}%`;
      }
      return value.toLocaleString('en-US');
    }
    return String(value);
  })();

  return (
    <div className="rounded-lg border border-border/80 bg-card p-4 space-y-3">
      <div className="flex items-center justify-between gap-4">
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-foreground truncate">{displayMetric}</p>
        </div>
        <div className={cn(
          'text-sm font-bold tabular-nums text-muted-foreground min-w-0 break-words whitespace-pre-wrap',
          displayValue.includes('\n') ? 'text-left' : 'text-right'
        )}>
          {displayValue}
        </div>
      </div>
      {((benchmark && benchmark !== '-') || message) && (
        <div className="text-xs text-muted-foreground border-t border-border/50 pt-2 space-y-0.5">
          {benchmark && benchmark !== '-' && <p>Benchmark: {displayBenchmark}</p>}
          {message && (() => {
            const colorClass = (displayMessage.includes('✔️') || displayMessage.includes('✅')) ? 'text-green-600' :
              displayMessage.includes('❌') ? 'text-orange-600' : '';

            // Split on ↪ to separate text from URL
            const parts = displayMessage.split('↪');
            const textPart = parts[0].trim();
            const urlPart = parts[1]?.trim();

            return (
              <div className="space-y-1">
                <p className={cn('break-all', colorClass)}>{textPart}</p>
                {urlPart && (
                  <p>
                    <a
                      href={urlPart}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-primary hover:underline break-all"
                    >
                      ↪ {urlPart}
                    </a>
                  </p>
                )}
              </div>
            );
          })()}
        </div>
      )}
    </div>
  );
};
