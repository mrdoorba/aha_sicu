import { useTranslation } from 'react-i18next';
import { Check, Loader2, AlertCircle } from 'lucide-react';
import type { SaveStatus } from '../../../hooks/useAutoSaveForm';

interface SaveIndicatorProps {
  status: SaveStatus;
  lastSaved: Date | null;
  onRetry?: () => void;
}

function formatTimeSince(date: Date, t: (key: string, opts?: Record<string, unknown>) => string): string {
  const seconds = Math.floor((Date.now() - date.getTime()) / 1000);
  if (seconds < 60) return t('saveIndicator.savedJustNow');
  const minutes = Math.floor(seconds / 60);
  return t('saveIndicator.savedMinAgo', { minutes });
}

export function SaveIndicator({ status, lastSaved, onRetry }: SaveIndicatorProps) {
  const { t } = useTranslation();

  if (status === 'saving') {
    return (
      <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
        <Loader2 className="size-3 animate-spin" aria-hidden="true" />
        {t('saveIndicator.saving')}
      </span>
    );
  }

  if (status === 'error') {
    return (
      <span className="inline-flex items-center gap-1 text-xs text-destructive">
        <AlertCircle className="size-3" aria-hidden="true" />
        {t('saveIndicator.saveFailed')}
        {onRetry && (
          <button
            type="button"
            onClick={onRetry}
            className="underline hover:no-underline"
          >
            {t('saveIndicator.retry')}
          </button>
        )}
      </span>
    );
  }

  if (status === 'saved' && lastSaved) {
    return (
      <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
        <Check className="size-3" aria-hidden="true" />
        {formatTimeSince(lastSaved, t)}
      </span>
    );
  }

  return null;
}
