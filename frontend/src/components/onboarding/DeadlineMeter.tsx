import { Clock } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { cn } from '../../lib/utils';
import { getIntlLocale } from '../../lib/languages';
import { formatDeadlineTime } from '../../lib/workdays';
import {
  TOTAL_WORKDAYS,
  deadlineMeter,
  remainingLabel,
  type DeadlineUrgency,
} from './deadline';

const TRACK: Record<DeadlineUrgency, string> = {
  calm: 'bg-primary',
  soon: 'bg-gold',
  critical: 'bg-penalti',
};

const TEXT: Record<DeadlineUrgency, string> = {
  calm: 'text-foreground',
  soon: 'text-foreground',
  critical: 'text-penalti',
};

interface DeadlineMeterProps {
  remaining: number;
  /** Working hours left in today, shown alongside the days. */
  hours?: number;
  date: Date;
  total?: number;
}

export const DeadlineMeter = ({
  remaining,
  hours: hoursLeft = 0,
  date,
  total = TOTAL_WORKDAYS,
}: DeadlineMeterProps) => {
  const { t, i18n } = useTranslation();
  const { clamped, hours, urgency, percent } = deadlineMeter(
    remaining,
    total,
    hoursLeft,
  );
  const label = remainingLabel(clamped, hours);
  const remainingText = t(label.key, label.vars);

  return (
    <div className="rounded-2xl border border-border bg-card px-5 py-4">
      <div className="mb-2.5 flex flex-wrap items-center justify-between gap-x-4 gap-y-1">
        <p
          className={cn(
            'flex items-center gap-2 text-[13px] font-bold',
            TEXT[urgency],
          )}
        >
          <Clock className="size-4" aria-hidden="true" />
          {remainingText}
        </p>
        <p className="text-[13px] text-muted-foreground">
          {t('onboarding.deadline.due')}{' '}
          <span className="font-semibold text-foreground">
            {formatDeadlineTime(date, getIntlLocale(i18n.language))}
          </span>
        </p>
      </div>

      <div
        className="h-2 overflow-hidden rounded-full bg-secondary"
        role="progressbar"
        aria-valuenow={clamped}
        aria-valuemin={0}
        aria-valuemax={total}
        aria-valuetext={t('onboarding.deadline.progress', {
          label: remainingText,
          total,
        })}
      >
        <div
          className={cn(
            'h-full rounded-full transition-[width] duration-700',
            TRACK[urgency],
          )}
          style={{ width: `${percent}%` }}
        />
      </div>
    </div>
  );
};
