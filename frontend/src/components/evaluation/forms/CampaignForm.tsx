import { Card, CardContent } from '../../ui/card';
import { NumberField } from './NumberField';
import type { CampaignData } from './formConfig';
import { CAMPAIGN_FIELDS } from './formConfig';

interface CampaignFormProps {
  data: CampaignData;
  onChange: (category: 'campaign', key: string, value: number | null) => void;
  onBlur: () => void;
}

export function CampaignForm({ data, onChange, onBlur }: CampaignFormProps) {
  return (
    <Card className="mb-4">
      <CardContent className="pt-4">
        <p className="mb-3 text-sm font-semibold">Campaign</p>
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
      </CardContent>
    </Card>
  );
}
