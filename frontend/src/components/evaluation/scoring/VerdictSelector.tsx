import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../ui/select';

const VERDICT_OPTIONS = [
  { value: '✔️', label: '✔️ Approved' },
  { value: '❌', label: '❌ Rejected' },
  { value: '❌ Non Mall', label: '❌ Non Mall' },
  { value: '❌ No Brand', label: '❌ No Brand' },
  { value: '❌ Opex', label: '❌ Opex Issue' },
  { value: '⭕️', label: '⭕️ Special' },
];

interface VerdictSelectorProps {
  value: string;
  onChange: (value: string) => void;
}

export const VerdictSelector = ({ value, onChange }: VerdictSelectorProps) => {
  return (
    <div className="space-y-1">
      <label className="text-sm font-medium" htmlFor="verdict-select">
        Verdict
      </label>
      <Select value={value} onValueChange={onChange}>
        <SelectTrigger id="verdict-select" className="w-48">
          <SelectValue placeholder="Select verdict" />
        </SelectTrigger>
        <SelectContent>
          {VERDICT_OPTIONS.map((opt) => (
            <SelectItem key={opt.value} value={opt.value}>
              {opt.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
};

export { VERDICT_OPTIONS };
