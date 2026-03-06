import { useState } from 'react';
import { X } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { cn } from '../../lib/utils';

export interface EmailChipInputProps {
  id: string;
  emails: string[];
  onChange: (emails: string[]) => void;
  disabled?: boolean;
  placeholder?: string;
  maxTotal?: number;
  currentTotal?: number;
}

const isValidEmail = (email: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

export function EmailChipInput({
  id,
  emails,
  onChange,
  disabled,
  placeholder,
  maxTotal,
  currentTotal,
}: EmailChipInputProps) {
  const { t } = useTranslation();
  const [inputValue, setInputValue] = useState('');
  const [error, setError] = useState('');

  const addEmail = (raw: string) => {
    const email = raw.trim().replace(/,$/, '');
    if (!email) return;
    if (!isValidEmail(email)) {
      setError(t('sendEmail.invalidEmail'));
      return;
    }
    if (emails.includes(email)) {
      setError(t('sendEmail.duplicateEmail'));
      return;
    }
    if (currentTotal !== undefined && maxTotal !== undefined && currentTotal >= maxTotal) {
      setError(t('sendEmail.maxRecipients'));
      return;
    }
    onChange([...emails, email]);
    setInputValue('');
    setError('');
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();
      addEmail(inputValue);
    }
    if (e.key === 'Backspace' && !inputValue && emails.length > 0) {
      onChange(emails.slice(0, -1));
    }
  };

  return (
    <div>
      <div
        className={cn(
          'flex flex-wrap items-center gap-1 rounded-md border p-1.5 min-h-[38px]',
          error && 'border-destructive',
        )}
      >
        {emails.map((email) => (
          <span
            key={email}
            className="inline-flex items-center gap-1 rounded bg-muted px-2 py-0.5 text-sm"
          >
            {email}
            <button
              type="button"
              onClick={() => onChange(emails.filter((e) => e !== email))}
              disabled={disabled}
            >
              <X className="size-3" />
            </button>
          </span>
        ))}
        <input
          id={id}
          type="email"
          value={inputValue}
          onChange={(e) => {
            setInputValue(e.target.value);
            setError('');
          }}
          onKeyDown={handleKeyDown}
          onBlur={() => inputValue && addEmail(inputValue)}
          placeholder={emails.length === 0 ? placeholder : undefined}
          disabled={disabled}
          className="flex-1 min-w-[120px] outline-none bg-transparent text-sm"
        />
      </div>
      {error && <p className="w-full text-xs text-destructive mt-1">{error}</p>}
    </div>
  );
}
