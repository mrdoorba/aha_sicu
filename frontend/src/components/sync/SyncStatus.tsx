import { RefreshCw, CheckCircle2, XCircle, Clock } from 'lucide-react';
import { toast } from 'sonner';
import { Card, CardContent } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { useSyncStatus, useTriggerSync } from '../../hooks/useSync';

function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
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
  const { data: syncStatus, isLoading } = useSyncStatus();
  const triggerSync = useTriggerSync();

  const handleSyncNow = () => {
    triggerSync.mutate(undefined, {
      onSuccess: () => {
        toast.success('Sync started successfully');
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
          <div className="flex items-center gap-2">
            {!syncStatus && (
              <Badge variant="outline">
                <Clock className="size-3" />
                Never synced
              </Badge>
            )}
            {syncStatus?.status === 'success' && (
              <Badge className="bg-green-500 text-white hover:bg-green-500/90">
                <CheckCircle2 className="size-3" />
                Last synced: {formatRelativeTime(syncStatus.last_sync)}
              </Badge>
            )}
            {syncStatus?.status === 'in_progress' && (
              <Badge className="bg-amber-500 text-white hover:bg-amber-500/90">
                <RefreshCw className="size-3 animate-spin" />
                Syncing...
              </Badge>
            )}
            {syncStatus?.status === 'failed' && (
              <Badge variant="destructive">
                <XCircle className="size-3" />
                Last sync failed: {syncStatus.error_message}
              </Badge>
            )}
          </div>

          {syncStatus?.sync_details && syncStatus.status !== 'in_progress' && (
            <div className="flex gap-4 text-xs text-muted-foreground">
              {syncStatus.sync_details.vp_sheet && (
                <span>
                  VP: {syncStatus.sync_details.vp_sheet.rows_synced} brands{' '}
                  {syncStatus.sync_details.vp_sheet.status === 'success'
                    ? '\u2713'
                    : '\u2717'}
                </span>
              )}
              {syncStatus.sync_details.meeting_sheet && (
                <span>
                  Meeting: {syncStatus.sync_details.meeting_sheet.rows_synced}{' '}
                  brands{' '}
                  {syncStatus.sync_details.meeting_sheet.status === 'success'
                    ? '\u2713'
                    : '\u2717'}
                </span>
              )}
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
              <RefreshCw className="size-4 animate-spin" />
              Syncing...
            </>
          ) : (
            <>
              <RefreshCw className="size-4" />
              Sync Now
            </>
          )}
        </Button>
      </CardContent>
    </Card>
  );
};
