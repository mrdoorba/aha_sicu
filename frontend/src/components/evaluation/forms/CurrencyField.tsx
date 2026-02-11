import { useState } from 'react';
import { Input } from '../../ui/input';
import { Label } from '../../ui/label';
import { formatIDR, parseIDR } from './formConfig';

interface CurrencyFieldProps {
  name: string;
  label: string;
  benchmark?: string;
  value: number | null;
  onChange: (value: number | null) => void;
  onBlur?: () => void;
}

export function CurrencyField({
  name,
  label,
  benchmark,
  value,
  onChange,
  onBlur,
}: CurrencyFieldProps) {
  const [focused, setFocused] = useState(false);

  const displayValue = focused
    ? (value != null ? String(value) : '')
    : formatIDR(value);

  return (
    <div className="space-y-1">
      <Label htmlFor={name}>
        {label}
        <span className="ml-1 text-xs font-normal text-muted-foreground">(IDR)</span>
      </Label>
      <Input
        id={name}
        name={name}
        type="text"
        inputMode="numeric"
        value={displayValue}
        onChange={(e) => {
          const parsed = parseIDR(e.target.value);
          onChange(parsed);
        }}
        onFocus={() => setFocused(true)}
        onBlur={() => {
          setFocused(false);
          onBlur?.();
        }}
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
