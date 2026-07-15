import { useTheme } from 'next-themes';
import { Sun, Moon } from 'lucide-react';
import { Button } from '../ui/button';
import { cn } from '../../lib/utils';
import { useEffect, useState } from 'react';

interface ThemeToggleProps {
  className?: string;
  isCollapsed?: boolean;
}

export const ThemeToggle = ({ className, isCollapsed }: ThemeToggleProps) => {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  // Avoid hydration mismatch
  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setMounted(true);
  }, []);

  if (!mounted) return null;

  const isDark = theme === 'dark';

  return (
    <Button
      variant="ghost"
      className={cn(
        "w-full justify-start px-3 py-2 text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground transition-all duration-300",
        className
      )}
      onClick={() => setTheme(isDark ? 'light' : 'dark')}
      title={isDark ? "Switch to Light Mode" : "Switch to Dark Mode"}
    >
      <div className="relative h-5 w-5 shrink-0">
        <Sun
          className={cn(
            "absolute h-full w-full transition-all duration-500",
            isDark ? "rotate-90 scale-0 opacity-0" : "rotate-0 scale-100 opacity-100"
          )}
        />
        <Moon
          className={cn(
            "absolute h-full w-full transition-all duration-500",
            isDark ? "rotate-0 scale-100 opacity-100" : "-rotate-90 scale-0 opacity-0"
          )}
        />
      </div>
      <span
        className={cn(
          "overflow-hidden whitespace-nowrap transition-all duration-300",
          isCollapsed ? "ml-0 w-0 opacity-0" : "ml-3 w-auto opacity-100"
        )}
      >
        {isDark ? "Light Mode" : "Dark Mode"}
      </span>
    </Button>
  );
};
