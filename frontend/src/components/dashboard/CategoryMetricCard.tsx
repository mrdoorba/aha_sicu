import { cn } from '../../lib/utils';

interface CategoryMetricCardProps {
  metric: string;
  value: unknown;
  verdict: string;
  score: number;
  benchmark: string;
  message: string;
}

/** Render message text with colored emoji marks (✔️ green, ❌ red). */
const renderMessage = (message: string) => {
  const parts = message.split(/(✔️|❌)/);
  return parts.map((part, i) => {
    if (part === '✔️') return <span key={i} className="text-green-600">✔️</span>;
    if (part === '❌') return <span key={i} className="text-red-600">❌</span>;
    return part;
  });
};

export const CategoryMetricCard = ({ metric, value, benchmark, message }: CategoryMetricCardProps) => {
  const displayValue = (() => {
    if (value === null || value === undefined) return '-';
    if (typeof value === 'number') {
      // Metrics starting with "%" store raw fractions (e.g., 0.15 = 15%)
      if (metric.startsWith('%')) {
        return `${(value * 100).toFixed(1)}%`;
      }
      // Metrics whose benchmark contains "%" are already in percentage form
      if (benchmark?.includes('%')) {
        return `${value.toLocaleString('en-US')}%`;
      }
      return value.toLocaleString('en-US');
    }
    return String(value);
  })();

  return (
    <div className="rounded-lg border border-border/80 bg-card p-4 space-y-3">
      <div className="flex items-center justify-between gap-4">
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-foreground truncate">{metric}</p>
        </div>
        <div className={cn(
          'text-sm font-bold tabular-nums text-muted-foreground min-w-0 break-words whitespace-pre-wrap',
          displayValue.includes('\n') ? 'text-left' : 'text-right'
        )}>
          {displayValue}
        </div>
      </div>
      {(benchmark || message) && (
        <div className="text-xs text-muted-foreground border-t border-border/50 pt-2 space-y-0.5">
          {benchmark && <p>Benchmark: {benchmark}</p>}
          {message && <p className="break-all">{renderMessage(message)}</p>}
        </div>
      )}
    </div>
  );
};
