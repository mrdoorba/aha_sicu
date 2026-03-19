import { useState } from 'react';
import { Input } from '../../ui/input';
import { Label } from '../../ui/label';
import { formatCurrency, parseCurrency } from './formConfig';

interface CurrencyFieldProps {
  name: string;
  label: string;
  benchmark?: string;
  value: number | null;
  onChange: (value: number | null) => void;
  onBlur?: () => void;
  /** Currency code to display, e.g. 'IDR', 'THB'. Defaults to 'IDR'. */
  currency?: 'IDR' | 'THB' | string;
}

export function CurrencyField({
  name,
  label,
  benchmark,
  value,
  onChange,
  onBlur,
  currency = 'IDR',
}: CurrencyFieldProps) {
  const [focused, setFocused] = useState(false);

  const displayValue = focused
    ? (value != null ? String(value) : '')
    : formatCurrency(value);

  return (
    <div className="space-y-1">
      <Label htmlFor={name}>
        {label}
        <span className="ml-1 text-xs font-normal text-muted-foreground">({currency})</span>
      </Label>
      <Input
        id={name}
        name={name}
        type="text"
        inputMode="numeric"
        value={displayValue}
        onChange={(e) => {
          const parsed = parseCurrency(e.target.value);
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
