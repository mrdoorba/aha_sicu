import { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Globe } from 'lucide-react';
import { toast } from 'sonner';
import { Button } from '../ui/button';
import { cn } from '../../lib/utils';
import { updateLanguage } from '../../services/apiClient';
import { LANGUAGES, type LanguageCode } from '../../lib/languages';

interface LanguageToggleProps {
  className?: string;
  isCollapsed?: boolean;
}

export const LanguageToggle = ({ className, isCollapsed }: LanguageToggleProps) => {
  const { i18n } = useTranslation();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  const current = LANGUAGES.find((l) => l.code === i18n.language) ?? LANGUAGES[0];

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (ref.current && e.target instanceof Node && !ref.current.contains(e.target)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = async (code: LanguageCode) => {
    if (code === i18n.language) {
      setOpen(false);
      return;
    }

    const previousLang = i18n.language;
    i18n.changeLanguage(code);
    setOpen(false);

    try {
      await updateLanguage(code);
    } catch {
      i18n.changeLanguage(previousLang);
      toast.error('Failed to save language preference');
    }
  };

  return (
    <div ref={ref} className={cn('relative', className)}>
      <Button
        variant="ghost"
        size={isCollapsed ? 'icon' : 'default'}
        className={cn(
          'w-full text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground transition-all duration-300',
          isCollapsed ? 'justify-center p-2' : 'justify-start px-3 py-2',
        )}
        onClick={() => setOpen(!open)}
        data-testid="language-toggle"
      >
        <Globe className="h-5 w-5 shrink-0" />
        {!isCollapsed && (
          <span className="ml-3 truncate">
            {current.flag} {current.label}
          </span>
        )}
      </Button>

      {open && (
        <div
          className={cn(
            "absolute rounded-md border border-sidebar-border bg-sidebar shadow-lg z-50",
            isCollapsed
              ? "left-full bottom-0 ml-2 min-w-[120px]"
              : "bottom-full left-0 mb-1 w-full min-w-[120px]"
          )}
          data-testid="language-dropdown"
        >
          {LANGUAGES.map((lang) => (
            <button
              key={lang.code}
              className={cn(
                'flex w-full items-center gap-2 px-3 py-2 text-sm text-sidebar-foreground hover:bg-sidebar-accent transition-colors',
                lang.code === i18n.language && 'bg-sidebar-accent font-medium',
              )}
              onClick={() => handleSelect(lang.code)}
              data-testid={`language-option-${lang.code}`}
            >
              <span>{lang.flag}</span>
              <span>{lang.label}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
};
