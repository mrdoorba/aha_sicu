import { ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import type { BrandDetail } from '../../hooks/useBrandDetail';

interface EvaluationHeaderProps {
  brand: BrandDetail | null;
  isLoading: boolean;
  isError: boolean;
  marketplace?: string;
}

// Unified "Brands Data" schema — ID and TH share the same column names.
const VP_DISPLAY_FIELDS: readonly string[] = ['PIC', 'Phones', 'Emails', 'Category', 'Store Link'];

const META_KEYS = new Set(['id', 'created_at', 'updated_at', 'synced_at']);

function getDisplayFields(rawData: Record<string, unknown>): Array<[string, string]> {
  return Object.entries(rawData)
    .filter(([key]) => !META_KEYS.has(key.toLowerCase()))
    .slice(0, 6)
    .map(([key, value]) => [key, String(value ?? '')]);
}

export const EvaluationHeader = ({ brand, isLoading, isError, marketplace }: EvaluationHeaderProps) => {
  const { t } = useTranslation();
  const navigate = useNavigate();

  const getFieldLabel = (key: string): string => {
    const labelMap: Record<string, string> = {
      PIC: t('evaluationHeader.fieldLabel.namaPic'),
      Phones: t('evaluationHeader.fieldLabel.noWa'),
      'Store Link': t('evaluationHeader.fieldLabel.linkToko'),
    };
    return labelMap[key] ?? key;
  };

  if (isLoading) {
    return (
      <div aria-busy="true" className="space-y-3">
        <div className="h-5 w-24 animate-pulse rounded bg-muted" />
        <div className="h-8 w-64 animate-pulse rounded bg-muted" />
        <div className="flex gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-4 w-32 animate-pulse rounded bg-muted" />
          ))}
        </div>
      </div>
    );
  }

  if (isError || !brand) {
    return (
      <div className="space-y-3">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigate('/brands')}
        >
          <ArrowLeft className="mr-1 size-4" aria-hidden="true" />
          {t('common.backToBrands')}
        </Button>
        <p className="text-destructive">
          {isError ? t('evaluationHeader.errorLoading') : t('evaluationHeader.brandNotFound')}
        </p>
      </div>
    );
  }

  const fit = brand.package_fit;
  const packageBadges = fit ? (
    <>
      <Badge
        className={
          fit.bar !== null
            ? 'bg-primary text-primary-foreground hover:bg-primary/90'
            : 'bg-muted text-muted-foreground hover:bg-muted'
        }
      >
        {fit.package ?? t('evaluationHeader.packageUnknown')}
      </Badge>
      {fit.vp !== null && fit.bar !== null ? (
        <Badge
          variant="outline"
          className={
            fit.met
              ? 'border-green-600/40 font-semibold tabular-nums text-green-700 dark:text-green-400'
              : 'border-destructive/40 font-semibold tabular-nums text-destructive'
          }
        >
          {t('evaluationHeader.vpAgainstBar', {
            vp: Math.round(fit.vp),
            bar: Math.round(fit.bar),
          })}{' '}
          {fit.met ? '\u2713' : '\u2717'}
        </Badge>
      ) : (
        <Badge variant="outline" className="text-muted-foreground">
          {t('evaluationHeader.vpUnjudged')}
        </Badge>
      )}
    </>
  ) : null;

  const vpFields = VP_DISPLAY_FIELDS
    .filter((key) => {
      const val = brand.raw_data[key];
      return val !== undefined && val !== null && val !== '';
    })
    .map((key) => [key, String(brand.raw_data[key])] as [string, string]);
  const meetingFields = brand.meeting_raw_data
    ? getDisplayFields(brand.meeting_raw_data)
    : null;

  return (
    <div className="space-y-3">
      <Button
        variant="ghost"
        size="sm"
        onClick={() => navigate('/brands')}
      >
        <ArrowLeft className="mr-1 size-4" aria-hidden="true" />
        {t('common.backToBrands')}
      </Button>

      <div className="flex items-center gap-3">
        <h2 className="text-2xl font-bold text-foreground">{brand.brand_name}</h2>
        <Badge variant="outline">{marketplace === 'TH' ? '🇹🇭 TH' : '🇮🇩 ID'}</Badge>
        {brand.meeting_raw_data ? (
          <Badge className="bg-green-500 text-white hover:bg-green-500/90">
            {t('evaluationHeader.meetingData')}
          </Badge>
        ) : null}
        {packageBadges}
      </div>

      {/* VP Data Fields */}
      <div className="flex flex-wrap gap-x-6 gap-y-1 text-sm text-muted-foreground">
        {vpFields.map(([key, value]) => (
          <span key={key}>
            <span className="font-medium text-foreground">{getFieldLabel(key)}:</span>{' '}
            {value.startsWith('https://') || value.startsWith('http://') ? (
              <a href={value} target="_blank" rel="noopener noreferrer" className="text-primary underline hover:text-primary/80">
                {value}
              </a>
            ) : (
              value
            )}
          </span>
        ))}
      </div>

      {/* Meeting Data */}
      {meetingFields ? (
        <div className="rounded-md border bg-card p-3">
          <p className="mb-1 text-xs font-semibold uppercase text-muted-foreground">
            {t('evaluationHeader.meetingData')}
          </p>
          <div className="flex flex-wrap gap-x-6 gap-y-1 text-sm text-muted-foreground">
            {meetingFields.map(([key, value]) => (
              <span key={key}>
                <span className="font-medium text-foreground">{key}:</span>{' '}
                {value.startsWith('https://') || value.startsWith('http://') ? (
                  <a href={value} target="_blank" rel="noopener noreferrer" className="text-primary underline hover:text-primary/80">
                    {value}
                  </a>
                ) : (
                  value
                )}
              </span>
            ))}
          </div>
        </div>
      ) : (
        <p className="text-sm text-muted-foreground">{t('evaluationHeader.noMeetingData')}</p>
      )}
    </div>
  );
};
