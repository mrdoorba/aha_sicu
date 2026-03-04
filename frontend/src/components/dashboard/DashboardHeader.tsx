import { ArrowLeft, Edit3, Calendar, TrendingUp } from 'lucide-react';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';

interface DashboardHeaderProps {
  brandName: string;
  brandId: number;
  verdict: string;
  template: string;
  period?: string;
  onBack: () => void;
}

export const DashboardHeader = ({ brandName, brandId, template, period, onBack }: DashboardHeaderProps) => {
  const { t } = useTranslation();
  const navigate = useNavigate();

  return (
    <div className="flex items-center justify-between px-2">
      <div className="flex items-center gap-3">
        <Button variant="outline" onClick={onBack} className="text-muted-foreground hover:text-foreground h-10 px-3">
          <ArrowLeft className="mr-2 size-4" />
          {t('presentation.back')}
        </Button>
        <div className="h-4 w-[1px] bg-border hidden sm:block" />
        <h1 className="text-2xl font-black tracking-tight text-foreground hidden sm:block">{brandName}</h1>
        {period && (
          <Badge variant="outline" className="px-3 py-1 text-xs font-bold uppercase tracking-widest hidden sm:flex gap-1.5 bg-primary/5 text-primary border-primary/20">
            <Calendar className="size-3" />
            {period}
          </Badge>
        )}
        <Badge
          className="px-3 py-1 text-xs font-bold tracking-wide hidden sm:flex gap-1.5 bg-primary/10 text-primary border-primary/20"
          variant="outline"
        >
          <TrendingUp className="size-3" />
          Performa dapat Ditingkatkan
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
