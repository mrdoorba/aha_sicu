import { useTranslation } from 'react-i18next';
import { RefreshCw } from 'lucide-react';
import { toast } from 'sonner';
import { Card, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { EvaluationHistoryTable } from '../components/evaluations/EvaluationHistoryTable';
import { useEvalSheetSync } from '../hooks/useEvalSheetSync';
import { useCurrentUser } from '../hooks/useCurrentUser';

export const HistoryPage = () => {
  const { t } = useTranslation();
  const { profile } = useCurrentUser();
  const { syncEvalSheet, isLoading } = useEvalSheetSync();

  const canSync = profile?.role === 'admin' || profile?.role === 'leader';

  const handleSync = () => {
    syncEvalSheet(undefined, {
      onSuccess: (data) => {
        if (data?.success) {
          toast.success(t('history.syncSuccess', { count: data.brands_synced }));
        } else {
          toast.error(data?.error ?? t('history.syncFailed'));
        }
      },
      onError: () => {
        toast.error(t('history.syncFailed'));
      },
    });
  };

  return (
    <div className="p-8">
      <div className="mx-auto max-w-7xl">
        <div className="mb-6 flex items-center justify-between">
          <h2 className="text-2xl font-semibold text-foreground">{t('history.title')}</h2>
          {canSync && (
            <Button
              variant="outline"
              size="sm"
              onClick={handleSync}
              disabled={isLoading}
            >
              <RefreshCw className={`mr-2 size-4 ${isLoading ? 'animate-spin' : ''}`} />
              {t('history.syncSheet')}
            </Button>
          )}
        </div>

        <Card>
          <CardContent className="p-0">
            <EvaluationHistoryTable />
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
