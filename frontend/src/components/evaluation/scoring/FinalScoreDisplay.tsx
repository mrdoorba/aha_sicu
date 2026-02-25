import { CheckCircle, XCircle, AlertTriangle } from 'lucide-react';
import { useTranslation } from 'react-i18next';

interface FinalScoreDisplayProps {
  totalScore: number;
  verdict: string;
  template: string;
}

const VERDICT_CONFIG: Record<string, { icon: typeof CheckCircle; color: string; labelKey: string }> = {
  '✔️': { icon: CheckCircle, color: 'text-green-600', labelKey: 'finalScore.verdict.approved' },
  '❌': { icon: XCircle, color: 'text-destructive', labelKey: 'finalScore.verdict.rejected' },
  '❌ Non Mall': { icon: XCircle, color: 'text-destructive', labelKey: 'finalScore.verdict.nonMall' },
  '❌ No Brand': { icon: XCircle, color: 'text-destructive', labelKey: 'finalScore.verdict.noBrand' },
  '❌ Opex': { icon: XCircle, color: 'text-destructive', labelKey: 'finalScore.verdict.opexIssue' },
};

export const FinalScoreDisplay = ({ totalScore, verdict }: FinalScoreDisplayProps) => {
  const { t } = useTranslation();
  const config = VERDICT_CONFIG[verdict] ?? { icon: AlertTriangle, color: 'text-muted-foreground', labelKey: 'finalScore.verdict.noVerdict' };
  const Icon = config.icon;

  return (
    <div className="flex items-center gap-4">
      <div className="text-center">
        <div className="text-4xl font-bold tabular-nums">{Math.round(totalScore)}</div>
        <div className="text-xs text-muted-foreground">{t('finalScore.totalScore')}</div>
      </div>
      <div className="flex items-center gap-1.5">
        <Icon className={`size-5 ${config.color}`} aria-hidden="true" />
        <span className="text-sm font-medium">{t(config.labelKey)}</span>
      </div>
    </div>
  );
};
