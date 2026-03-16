import { Input } from '../../ui/input';
import { Label } from '../../ui/label';

interface NumberFieldProps {
  name: string;
  label: string;
  unit?: string;
  benchmark?: string;
  value: number | null;
  onChange: (value: number | null) => void;
  onBlur?: () => void;
}

/** Strip Indonesian thousand separators (periods) and parse as integer. */
function parseCount(raw: string): number | null {
  if (raw === '') return null;
  const stripped = raw.replace(/\./g, '');
  const n = Number(stripped);
  return Number.isNaN(n) ? null : Math.round(n);
}

export function NumberField({
  name,
  label,
  unit,
  benchmark,
  value,
  onChange,
  onBlur,
}: NumberFieldProps) {
  const isCount = unit === 'count';

  return (
    <div className="space-y-1">
      <Label htmlFor={name}>
        {label}
        {unit && unit !== 'count' && (
          <span className="ml-1 text-xs font-normal text-muted-foreground">({unit})</span>
        )}
      </Label>
      <Input
        id={name}
        name={name}
        type={isCount ? 'text' : 'number'}
        inputMode={isCount ? 'numeric' : undefined}
        step={isCount ? undefined : 'any'}
        value={value ?? ''}
        onChange={(e) => {
          const raw = e.target.value;
          if (isCount) {
            onChange(parseCount(raw));
          } else {
            onChange(raw === '' ? null : Number(raw));
          }
        }}
        onBlur={onBlur}
        placeholder="—"
      />
      {benchmark && (
        <p className="text-xs text-muted-foreground">
          Benchmark: {benchmark}
        </p>
      )}
    </div>
  );
}
