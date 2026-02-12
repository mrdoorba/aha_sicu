import { Header } from '../components/layout/Header';
import { Card, CardContent } from '../components/ui/card';
import { EvaluationHistoryTable } from '../components/evaluations/EvaluationHistoryTable';

export const HistoryPage = () => {
  return (
    <div className="min-h-screen bg-muted">
      <Header />
      <main id="main-content" tabIndex={-1} className="mx-auto max-w-7xl py-6 px-4 sm:px-6 lg:px-8">
        <h2 className="mb-6 text-2xl font-semibold text-foreground">
          Evaluation History
        </h2>
        <Card>
          <CardContent className="p-0">
            <EvaluationHistoryTable />
          </CardContent>
        </Card>
      </main>
    </div>
  );
};
