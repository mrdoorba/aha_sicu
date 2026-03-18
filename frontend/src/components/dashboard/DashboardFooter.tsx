import { useTranslation } from 'react-i18next';
import { getIntlLocale } from '../../lib/localeMap';

interface DashboardFooterProps {
  evaluatorEmail: string;
  createdAt: string;
}

export const DashboardFooter = ({ evaluatorEmail, createdAt }: DashboardFooterProps) => {
  const { t, i18n } = useTranslation();

  return (
    <div className="pt-10 border-t border-border/50 text-center flex flex-col items-center gap-1">
      <p className="text-muted-foreground text-sm font-bold uppercase tracking-widest">
        {t('presentation.footer.title')}
      </p>
      <p className="text-muted-foreground/60 text-xs font-medium">
        {t('presentation.footer.conductedBy')}{' '}
        <span className="text-foreground/80 font-bold">{evaluatorEmail}</span>{' '}
        {t('presentation.footer.onDate')}{' '}
        {new Date(createdAt).toLocaleDateString(getIntlLocale(i18n.language), {
          day: 'numeric',
          month: 'long',
          year: 'numeric',
        })}
      </p>
    </div>
  );
};
