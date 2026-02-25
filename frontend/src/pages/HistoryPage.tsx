import { useTranslation } from 'react-i18next';
import { Card, CardContent } from '../components/ui/card';
import { EvaluationHistoryTable } from '../components/evaluations/EvaluationHistoryTable';

export const HistoryPage = () => {
  const { t } = useTranslation();

    return (
      <div className="p-8">
        <div className="mx-auto max-w-7xl">
          <h2 className="mb-6 text-2xl font-semibold text-foreground">{t('history.title')}</h2>
  
        <Card>
          <CardContent className="p-0">
            <EvaluationHistoryTable />
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
