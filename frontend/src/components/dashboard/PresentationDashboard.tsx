import { useRef, useState } from 'react';
import { useEvaluationDetail } from '../../hooks/useEvaluationDetail';
import { useBrandEvaluations } from '../../hooks/useBrandEvaluations';
import { useBrandDetail } from '../../hooks/useBrandDetail';
import { Loader2, ArrowLeft, AlertCircle, PlusCircle } from 'lucide-react';
import { Button } from '../ui/button';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { DashboardHeader } from './DashboardHeader';
import { ScoreOverview } from './ScoreOverview';
import { ScoreBreakdownChart } from './ScoreBreakdownChart';
import { DetailedEvaluation } from './DetailedEvaluation';
import { DataIntelligence } from './DataIntelligence';
import { KesimpulanSection } from './KesimpulanSection';
import { DashboardFooter } from './DashboardFooter';
import { SendEmailDialog } from './SendEmailDialog';

interface PresentationDashboardProps {
  brandId: number;
  onBack: () => void;
}

export const PresentationDashboard = ({ brandId, onBack }: PresentationDashboardProps) => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const chartRef = useRef<HTMLDivElement>(null);
  const [sendDialogOpen, setSendDialogOpen] = useState(false);
  const { data: brand, isLoading: brandLoading } = useBrandDetail(brandId);
  const { evaluations, isLoading: evLoading } = useBrandEvaluations(brandId, 1, undefined, undefined, true);
  const latestEvaluationId = evaluations?.[0]?.id;
  const { evaluation, isLoading: detailLoading } = useEvaluationDetail(latestEvaluationId ?? 0);

  const isLoading = brandLoading || evLoading || detailLoading;

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-20 animate-pulse">
        <Loader2 className="size-12 animate-spin text-primary" />
        <p className="mt-6 text-muted-foreground text-xl font-medium tracking-tight">{t('presentation.loading')}</p>
      </div>
    );
  }

  if (!evaluation) {
    return (
      <div className="flex flex-col items-center justify-center py-20 space-y-8 max-w-md mx-auto">
        <div className="relative">
          <div className="absolute inset-0 bg-primary/10 rounded-full blur-2xl animate-pulse" />
          <div className="relative rounded-full bg-card p-8 border border-border shadow-xl">
            <AlertCircle className="size-16 text-muted-foreground/50" />
          </div>
        </div>
        <div className="text-center space-y-3">
          <h2 className="text-3xl font-black tracking-tight text-foreground">{t('presentation.empty.title')}</h2>
          <p className="text-muted-foreground text-lg leading-relaxed">
            {t('presentation.empty.description')}
          </p>
        </div>
        <div className="flex flex-col w-full gap-3">
          <Button onClick={() => navigate(`/evaluation/${brandId}`)} size="lg" className="h-14 rounded-2xl shadow-xl shadow-primary/20 text-lg font-bold transition-all hover:scale-[1.02]">
            <PlusCircle className="mr-2 size-5" />
            {t('presentation.empty.startEvaluation')}
          </Button>
          <Button onClick={onBack} variant="ghost" size="lg" className="h-14 rounded-2xl text-muted-foreground hover:text-foreground">
            <ArrowLeft className="mr-2 size-5" />
            {t('presentation.empty.backToSearch')}
          </Button>
        </div>
      </div>
    );
  }

  const score = Math.round(evaluation.final_score);

  const scoreBreakdown = evaluation.score_breakdown.map((cat) => ({
    category: String(cat.category),
    score: Number(cat.score),
    max_score: Number(cat.max_score),
    rows: ((cat.rows as Array<{
      metric: string;
      value: unknown;
      benchmark: string;
      verdict: string;
      message: string;
      score: number;
    }>) || []).filter((r) => r.metric !== 'Iklan check up'),
  }));

  return (
    <div className="mx-auto max-w-7xl space-y-8 py-6">
      <DashboardHeader
        brandName={brand?.brand_name || evaluation.brand_name}
        brandId={brandId}
        verdict={evaluation.verdict}
        template={evaluation.template}
        period={evaluation.period}
        onBack={onBack}
        onSendEmail={() => setSendDialogOpen(true)}
      />

      <ScoreOverview
        score={score}
        verdict={evaluation.verdict}
        template={evaluation.template}
        scoreBreakdown={scoreBreakdown}
      />

      <DetailedEvaluation scoreBreakdown={scoreBreakdown} />

      <ScoreBreakdownChart ref={chartRef} scoreBreakdown={scoreBreakdown} />

      <DataIntelligence calculatorResults={evaluation.calculator_results} />

      <KesimpulanSection calculatorResults={evaluation.calculator_results} />

      <DashboardFooter
        evaluatorEmail={evaluation.evaluator_email}
        createdAt={evaluation.created_at}
      />

      <SendEmailDialog
        open={sendDialogOpen}
        onOpenChange={setSendDialogOpen}
        evaluationId={evaluation.id}
        brandName={brand?.brand_name || evaluation.brand_name}
        period={evaluation.period}
        score={Math.round(evaluation.final_score)}
        brandRawData={evaluation.brand_raw_data}
        chartRef={chartRef}
      />
    </div>
  );
};
