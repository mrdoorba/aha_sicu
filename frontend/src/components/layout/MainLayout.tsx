import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Menu, X } from 'lucide-react';
import { Button } from '../ui/button';
import { cn } from '../../lib/utils';

export const MainLayout = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  return (
    <div className="relative flex h-screen bg-background text-foreground transition-colors duration-500 overflow-hidden">
      {/* Desktop Sidebar — collapsed rail that expands on hover */}
      <Sidebar className="hidden lg:flex" hoverExpand />

      {/* Mobile Sidebar Overlay */}
      <div 
        className={cn(
          "fixed inset-0 z-50 lg:hidden bg-background/80 backdrop-blur-sm transition-opacity duration-300",
          isMobileMenuOpen ? "opacity-100" : "opacity-0 pointer-events-none"
        )}
        onClick={() => setIsMobileMenuOpen(false)}
      >
        <div 
          className={cn(
            "fixed inset-y-0 left-0 w-64 bg-sidebar border-r border-sidebar-border transition-transform duration-300 ease-in-out",
            isMobileMenuOpen ? "translate-x-0" : "-translate-x-full"
          )}
          onClick={(e) => e.stopPropagation()}
        >
          <div className="flex h-16 items-center justify-between px-4">
            <span className="text-xl font-bold tracking-tight text-sidebar-primary">Store ICU</span>
            <Button variant="ghost" size="icon" onClick={() => setIsMobileMenuOpen(false)}>
              <X className="h-5 w-5" />
            </Button>
          </div>
          <Sidebar className="w-full border-none h-[calc(100%-4rem)]" />
        </div>
      </div>

      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Mobile Header */}
        <header className="flex h-16 shrink-0 items-center justify-between border-b border-border bg-card px-4 lg:hidden">
          <span className="text-lg font-bold tracking-tight text-primary">Store ICU</span>
          <Button variant="ghost" size="icon" onClick={() => setIsMobileMenuOpen(true)}>
            <Menu className="h-5 w-5" />
          </Button>
        </header>

        <main id="main-content" tabIndex={-1} className="flex-1 overflow-auto outline-none">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
