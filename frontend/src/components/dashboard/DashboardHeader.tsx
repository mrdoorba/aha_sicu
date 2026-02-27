import { ArrowLeft, Edit3 } from 'lucide-react';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { cn } from '../../lib/utils';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';

interface DashboardHeaderProps {
  brandName: string;
  brandId: number;
  verdict: string;
  template: string;
  onBack: () => void;
}

export const DashboardHeader = ({ brandName, brandId, verdict, template, onBack }: DashboardHeaderProps) => {
  const { t } = useTranslation();
  const navigate = useNavigate();

  const isApproved = verdict === '✔️';
  const isRejected = verdict.startsWith('❌');

  return (
    <div className="flex items-center justify-between px-2">
      <div className="flex items-center gap-3">
        <Button variant="outline" onClick={onBack} className="text-muted-foreground hover:text-foreground h-10 px-3">
          <ArrowLeft className="mr-2 size-4" />
          {t('presentation.back')}
        </Button>
        <div className="h-4 w-[1px] bg-border hidden sm:block" />
        <h1 className="text-2xl font-black tracking-tight text-foreground hidden sm:block">{brandName}</h1>
        <Badge
          className={cn(
            'px-3 py-1 text-xs font-bold uppercase tracking-widest hidden sm:flex',
            isApproved ? 'bg-success/10 text-success border-success/20' :
            isRejected ? 'bg-destructive/10 text-destructive border-destructive/20' :
            'bg-muted text-muted-foreground border-border'
          )}
          variant="outline"
        >
          {isApproved ? t('presentation.verdict.approved') : isRejected ? t('presentation.verdict.rejected') : t('presentation.verdict.pending')}
        </Badge>
        <Badge variant={template === 'fashion' ? 'default' : 'secondary'} className="px-3 py-0.5 text-xs font-bold uppercase tracking-widest hidden sm:flex">
          {template === 'fashion' ? t('evaluationSections.fashion') : t('evaluationSections.nonFashion')}
        </Badge>
      </div>
      <Button
        onClick={() => navigate(`/evaluation/${brandId}`)}
        className="rounded-xl h-10 px-5 font-bold shadow-lg shadow-primary/10 transition-all hover:scale-[1.03] active:scale-[0.97]"
      >
        <Edit3 className="mr-2 size-4" />
        {t('presentation.editEvaluation')}
      </Button>
    </div>
  );
};
