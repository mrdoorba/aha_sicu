import { useTranslation } from 'react-i18next';
import { Card, CardContent } from '../../ui/card';
import { NumberField } from './NumberField';
import { ExternalLink } from 'lucide-react';
import type { CampaignData } from './formConfig';
import { CAMPAIGN_FIELDS, getSectionLinks } from './formConfig';

interface CampaignFormProps {
  data: CampaignData;
  marketplace?: string;
  onChange: (category: 'campaign', key: string, value: number | null) => void;
  onBlur: () => void;
}

export function CampaignForm({ data, marketplace = 'ID', onChange, onBlur }: CampaignFormProps) {
  const { t } = useTranslation();
  const links = getSectionLinks(marketplace);
  const nominated = data.nominatedSessions ?? 0;
  const available = data.availableSessions ?? 0;
  const participationPct = available > 0 ? (nominated / available) * 100 : null;

  return (
    <Card className="mb-4">
      <CardContent className="pt-4">
        <p className="mb-3 flex items-center gap-2 text-sm font-semibold">
          {t('forms.campaign.title')}
          <a href={links.campaign} target="_blank" rel="noopener noreferrer" aria-label={t('common.aria.openSellerCenter')}>
            <ExternalLink className="size-4 text-muted-foreground" aria-hidden="true" />
          </a>
        </p>
        <div className="grid gap-4 sm:grid-cols-2">
          {CAMPAIGN_FIELDS.map((field) => (
            <NumberField
              key={field.key}
              name={`campaign.${field.key}`}
              label={field.label}
              unit={field.unit}
              benchmark={field.benchmark}
              value={data[field.key as keyof CampaignData] as number | null}
              onChange={(v) => onChange('campaign', field.key, v)}
              onBlur={onBlur}
            />
          ))}
        </div>

        {/* Computed: % Partisipasi Campaign */}
        <div className="mt-4">
          <p className="mb-1 text-sm font-medium">{t('forms.campaign.participationPct')}</p>
          <div className="rounded-md bg-muted p-2 text-sm" role="status" aria-live="polite">
            {participationPct == null ? '—' : `${participationPct.toFixed(1)}%`}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
