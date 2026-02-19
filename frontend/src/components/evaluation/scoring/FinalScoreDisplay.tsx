import { CheckCircle, XCircle, AlertTriangle, Circle } from 'lucide-react';

interface FinalScoreDisplayProps {
  totalScore: number;
  verdict: string;
  template: string;
}

const VERDICT_CONFIG: Record<string, { icon: typeof CheckCircle; color: string; label: string }> = {
  '✔️': { icon: CheckCircle, color: 'text-green-600', label: 'Approved' },
  '❌': { icon: XCircle, color: 'text-destructive', label: 'Rejected' },
  '❌ Non Mall': { icon: XCircle, color: 'text-destructive', label: 'Non Mall' },
  '❌ No Brand': { icon: XCircle, color: 'text-destructive', label: 'No Brand' },
  '❌ Opex': { icon: XCircle, color: 'text-destructive', label: 'Opex Issue' },
  '⭕️': { icon: Circle, color: 'text-yellow-600', label: 'Special' },
  '': { icon: AlertTriangle, color: 'text-muted-foreground', label: 'No Verdict' },
};

export const FinalScoreDisplay = ({ totalScore, verdict }: FinalScoreDisplayProps) => {
  const config = VERDICT_CONFIG[verdict] ?? VERDICT_CONFIG[''];
  const Icon = config.icon;

  return (
    <div className="flex items-center gap-4">
      <div className="text-center">
        <div className="text-4xl font-bold tabular-nums">{Math.round(totalScore)}</div>
        <div className="text-xs text-muted-foreground">Total Score</div>
      </div>
      <div className="flex items-center gap-1.5">
        <Icon className={`size-5 ${config.color}`} aria-hidden="true" />
        <span className="text-sm font-medium">{config.label}</span>
      </div>
    </div>
  );
};
