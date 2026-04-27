import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { RefreshCw, CheckCircle2, XCircle, Clock } from 'lucide-react';
import { toast } from 'sonner';
import { Card, CardContent } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '../ui/dialog';
import {
  type SyncDetailData,
  type SyncStatusData,
  useSyncStatus,
  useTriggerSync,
} from '../../hooks/useSync';

/** Format ISO timestamp as relative time. Assumes server returns UTC timestamps. */
function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString);
  if (isNaN(date.getTime())) return 'unknown';
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  if (diffMs < 0) return 'just now';
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHr = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHr / 24);

  if (diffSec < 60) return 'just now';
  if (diffMin < 60) return `${diffMin} minute${diffMin !== 1 ? 's' : ''} ago`;
  if (diffHr < 24) return `${diffHr} hour${diffHr !== 1 ? 's' : ''} ago`;
  return `${diffDay} day${diffDay !== 1 ? 's' : ''} ago`;
}

export const SyncStatus = () => {
  const { t } = useTranslation();
  const { data: syncStatus, isLoading, isError } = useSyncStatus();
  const triggerSync = useTriggerSync();
  const [driftErrors, setDriftErrors] = useState<SyncDetailData[]>([]);
  const [driftErrorIndex, setDriftErrorIndex] = useState<number | null>(null);

  const columnDriftDetails = (statusData?: SyncStatusData | null) => {
    if (!statusData?.sync_details) return [];
    return Object.values(statusData.sync_details).filter((detail) => detail.status === 'column_drift');
  };

  const openDriftDetails = (details: SyncDetailData[], startIndex = 0) => {
    if (!details.length) return;
    setDriftErrors(details);
    setDriftErrorIndex(startIndex);
  };

  const closeDriftDialog = () => {
    setDriftErrors([]);
    setDriftErrorIndex(null);
  };

  const formatChangedColumn = (detail: SyncDetailData) => {
    if (detail.changed_columns?.length) {
      return detail.changed_columns
        .slice(0, 2)
        .map(({ expected, actual }) => {
          if (expected && actual) return `${expected} → ${actual}`;
          if (expected) return `Missing ${expected}`;
          if (actual) return `Unexpected ${actual}`;
          return 'Header changed';
        })
        .join('; ');
    }
    if (detail.missing?.length || detail.unexpected?.length) {
      return [...(detail.missing ?? []), ...(detail.unexpected ?? [])].join(', ');
    }
    return detail.error ?? t('sync.columnDrift.summary', { defaultValue: 'Column mismatch detected' });
  };

  const driftError =
    driftErrorIndex === null ? null : driftErrors[driftErrorIndex] ?? null;
  const hasNextDriftError =
    driftErrorIndex !== null && driftErrorIndex < driftErrors.length - 1;

  const handleSyncNow = () => {
    triggerSync.mutate(undefined, {
      onSuccess: (data: unknown) => {
        const result = data as SyncStatusData | undefined;
        const details = columnDriftDetails(result);
        if (details.length) {
          openDriftDetails(details);
        } else {
          toast.success(t('sync.startSuccess'));
        }
      },
      onError: (error) => {
        toast.error(error.message);
      },
    });
  };

  const isSyncing =
    syncStatus?.status === 'in_progress' || triggerSync.isPending;

  if (isLoading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-between py-4">
          <div className="h-5 w-48 animate-pulse rounded bg-muted" />
          <div className="h-9 w-24 animate-pulse rounded bg-muted" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent className="flex flex-col gap-3 py-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex flex-col gap-2">
          <div className="flex items-center gap-2" aria-live="polite" aria-atomic="true">
            {isError && (
              <Badge variant="destructive">
                <XCircle className="size-3" aria-hidden="true" />
                {t('sync.errorLoading')}
              </Badge>
            )}
            {!isError && !syncStatus && (
              <Badge variant="outline">
                <Clock className="size-3" aria-hidden="true" />
                {t('sync.neverSynced')}
              </Badge>
            )}
            {syncStatus?.status === 'success' && (
              <Badge className="bg-green-500 text-white hover:bg-green-500/90">
                <CheckCircle2 className="size-3" aria-hidden="true" />
                {t('sync.lastSynced', { time: formatRelativeTime(syncStatus.last_sync) })}
              </Badge>
            )}
            {syncStatus?.status === 'in_progress' && (
              <Badge className="bg-amber-500 text-white hover:bg-amber-500/90">
                <RefreshCw className="size-3 animate-spin" aria-hidden="true" />
                {t('sync.syncing')}
              </Badge>
            )}
            {syncStatus?.status === 'failed' && (
              <Badge variant="destructive" className="max-w-md truncate">
                <XCircle className="size-3 shrink-0" aria-hidden="true" />
                <span className="truncate">{t('sync.lastFailed', { error: syncStatus.error_message })}</span>
              </Badge>
            )}
          </div>

          {syncStatus?.sync_details && syncStatus.status !== 'in_progress' && (
            <div className="flex flex-col gap-2 text-xs text-muted-foreground">
              {Object.entries(syncStatus.sync_details).map(([key, detail]) => (
                <div key={key} className="flex flex-wrap items-center gap-2">
                  <span>
                    {key.toUpperCase()}: {detail.rows_synced ?? 0}{' '}
                    {detail.status === 'success' ? '\u2713' :
                     detail.status === 'column_drift' ? '\u26A0' : '\u2717'}
                  </span>
                  {detail.status === 'column_drift' ? (
                    <Button
                      variant="link"
                      className="h-auto p-0 text-xs text-amber-700"
                      onClick={() => openDriftDetails([detail])}
                    >
                      {formatChangedColumn(detail)}
                    </Button>
                  ) : null}
                </div>
              ))}
            </div>
          )}

        </div>

        <Button
          variant="secondary"
          onClick={handleSyncNow}
          disabled={isSyncing}
        >
          {isSyncing ? (
            <>
              <RefreshCw className="size-4 animate-spin" aria-hidden="true" />
              {t('sync.syncing')}
            </>
          ) : (
            <>
              <RefreshCw className="size-4" aria-hidden="true" />
              {t('sync.syncNow')}
            </>
          )}
        </Button>
      </CardContent>

      <Dialog open={!!driftError} onOpenChange={(open) => { if (!open) closeDriftDialog(); }}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t('sync.columnDrift.title', { defaultValue: 'Column Mismatch Detected' })}</DialogTitle>
            <DialogDescription>
              {t('sync.columnDrift.description', {
                defaultValue: 'Review the exact expected and actual headers before asking the BD team to fix the sheet.',
              })}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-2 text-sm">
            {driftError?.sheet ? (
              <p>{t('sync.columnDrift.sheet', { defaultValue: 'Sheet' })}: <strong>{driftError.sheet}</strong></p>
            ) : null}
            {driftError?.marketplace ? (
              <p>{t('sync.columnDrift.marketplace', { defaultValue: 'Marketplace' })}: <strong>{driftError.marketplace}</strong></p>
            ) : null}
            {driftError?.changed_columns?.length ? (
              <div>
                <p className="font-medium">{t('sync.columnDrift.changed', { defaultValue: 'Changed columns' })}:</p>
                <ul className="list-disc pl-5">
                  {driftError.changed_columns.map((change) => (
                    <li key={`${change.position}-${change.expected ?? 'none'}-${change.actual ?? 'none'}`}>
                      {change.expected && change.actual
                        ? `${change.expected} → ${change.actual}`
                        : change.expected
                          ? `Missing ${change.expected}`
                          : `Unexpected ${change.actual}`}
                    </li>
                  ))}
                </ul>
              </div>
            ) : null}
            {driftError?.missing?.length ? (
              <p>{t('sync.columnDrift.missing', { defaultValue: 'Missing columns' })}: {driftError.missing.join(', ')}</p>
            ) : null}
            {driftError?.unexpected?.length ? (
              <p>{t('sync.columnDrift.unexpected', { defaultValue: 'Unexpected columns' })}: {driftError.unexpected.join(', ')}</p>
            ) : null}
            {driftError?.expected_headers?.length ? (
              <p>{t('sync.columnDrift.expected', { defaultValue: 'Expected headers' })}: {driftError.expected_headers.join(' | ')}</p>
            ) : null}
            {driftError?.actual_headers?.length ? (
              <p>{t('sync.columnDrift.actual', { defaultValue: 'Actual headers' })}: {driftError.actual_headers.join(' | ')}</p>
            ) : null}
          </div>
          <DialogFooter>
            {hasNextDriftError ? (
              <Button onClick={() => setDriftErrorIndex((current) => (current === null ? 0 : current + 1))}>
                {t('sync.columnDrift.next', { defaultValue: 'Next drift' })}
              </Button>
            ) : null}
            <Button onClick={closeDriftDialog}>{hasNextDriftError ? t('common.close', { defaultValue: 'Close' }) : 'OK'}</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </Card>
  );
};
