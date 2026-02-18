import { ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import type { BrandDetail } from '../../hooks/useBrandDetail';

interface EvaluationHeaderProps {
  brand: BrandDetail | null;
  isLoading: boolean;
  isError: boolean;
}

const META_KEYS = new Set(['id', 'created_at', 'updated_at', 'synced_at']);

function getDisplayFields(rawData: Record<string, unknown>): Array<[string, string]> {
  return Object.entries(rawData)
    .filter(([key]) => !META_KEYS.has(key.toLowerCase()))
    .slice(0, 6)
    .map(([key, value]) => [key, String(value ?? '')]);
}

export const EvaluationHeader = ({ brand, isLoading, isError }: EvaluationHeaderProps) => {
  const navigate = useNavigate();

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
          Back to Brands
        </Button>
        <p className="text-destructive">
          {isError ? 'Failed to load brand data.' : 'Brand not found.'}
        </p>
      </div>
    );
  }

  const vpFields = getDisplayFields(brand.raw_data);
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
        Back to Brands
      </Button>

      <div className="flex items-center gap-3">
        <h2 className="text-2xl font-bold text-foreground">{brand.brand_name}</h2>
        {brand.meeting_raw_data ? (
          <Badge className="bg-green-500 text-white hover:bg-green-500/90">
            Meeting Data
          </Badge>
        ) : null}
      </div>

      {/* VP Data Fields */}
      <div className="flex flex-wrap gap-x-6 gap-y-1 text-sm text-muted-foreground">
        {vpFields.map(([key, value]) => (
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

      {/* Meeting Data */}
      {meetingFields ? (
        <div className="rounded-md border bg-card p-3">
          <p className="mb-1 text-xs font-semibold uppercase text-muted-foreground">
            Meeting Data
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
        <p className="text-sm text-muted-foreground">No meeting data available</p>
      )}
    </div>
  );
};
