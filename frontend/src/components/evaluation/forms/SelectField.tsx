import { useTranslation } from 'react-i18next';
import { Label } from '../../ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../../ui/select';
import type { SelectOption } from './formConfig';

interface SelectFieldProps {
  name: string;
  label: string;
  options: SelectOption[];
  benchmark?: string;
  value: string | null;
  onChange: (value: string) => void;
}

export function SelectField({
  name,
  label,
  options,
  benchmark,
  value,
  onChange,
}: SelectFieldProps) {
  const { t } = useTranslation();
  return (
    <div className="space-y-1">
      <Label htmlFor={name}>{label}</Label>
      <Select value={value ?? ''} onValueChange={onChange}>
        <SelectTrigger id={name}>
          <SelectValue placeholder={t('common.select')} />
        </SelectTrigger>
        <SelectContent>
          {options.map((opt) => (
            <SelectItem key={opt.value} value={opt.value}>
              {opt.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      {benchmark && (
        <p className="text-xs text-muted-foreground">
          Benchmark: {benchmark}
        </p>
      )}
    </div>
  );
}
