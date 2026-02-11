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

export function NumberField({
  name,
  label,
  unit,
  benchmark,
  value,
  onChange,
  onBlur,
}: NumberFieldProps) {
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
        type="number"
        step="any"
        value={value ?? ''}
        onChange={(e) => {
          const raw = e.target.value;
          onChange(raw === '' ? null : Number(raw));
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
