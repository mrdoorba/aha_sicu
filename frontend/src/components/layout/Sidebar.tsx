import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Briefcase,
  History,
  Settings,
  Users,
  LogOut,
  ChevronLeft,
  ExternalLink
} from 'lucide-react';

const AHA_BD_URL = 'https://aha-bd.web.app/';
import { cn } from '../../lib/utils';
import { useAuth } from '../../context/AuthContext';
import { useCurrentUser } from '../../hooks/useCurrentUser';
import { Button } from '../ui/button';
import { ThemeToggle } from './ThemeToggle';
import { LanguageToggle } from './LanguageToggle';
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '../ui/dialog';

interface SidebarProps {
  className?: string;
  /** Desktop rail: collapsed at rest, expands on hover, pinnable via the chevron. */
  hoverExpand?: boolean;
}

export const Sidebar = ({ className, hoverExpand = false }: SidebarProps) => {
  const { t } = useTranslation();
  const { user, logout } = useAuth();
  const { profile } = useCurrentUser();
  const location = useLocation();
  const [isPinned, setIsPinned] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  // Hover rail: collapsed unless pinned or hovered. Without hoverExpand (mobile
  // drawer) the sidebar is always expanded.
  const isCollapsed = hoverExpand ? !(isPinned || isHovered) : false;

  const canAccessHistory = profile?.role === 'leader' || profile?.role === 'admin';
  const canAccessRules = canAccessHistory;
  const isAdmin = profile?.role === 'admin';

  const navItems = [
    {
      title: t('header.dashboard'),
      href: '/dashboard',
      icon: LayoutDashboard,
    },
    {
      title: t('header.brand'),
      href: '/brands',
      icon: Briefcase,
    },
    ...(canAccessHistory ? [{
      title: t('header.history'),
      href: '/history',
      icon: History,
    }] : []),
    ...(canAccessRules ? [{
      title: t('header.rules'),
      href: '/rules',
      icon: Settings,
    }] : []),
    ...(isAdmin ? [{
      title: t('header.accounts'),
      href: '/accounts',
      icon: Users,
    }] : []),
  ];

  const handleLogout = async () => {
    setIsLoggingOut(true);
    try {
      await logout();
    } catch (error) {
      console.error('Logout failed:', error);
    } finally {
      setIsLoggingOut(false);
      setShowLogoutConfirm(false);
    }
  };

  return (
    <>
      {/* Reserve the rail's footprint so the expanding panel overlays content instead of reflowing it. */}
      {hoverExpand && <div aria-hidden className="hidden lg:block w-16 shrink-0" />}
      <aside
        className={cn(
          "relative flex flex-col border-r border-sidebar-border bg-sidebar text-sidebar-foreground transition-[width] duration-300 ease-in-out",
          hoverExpand && "lg:absolute lg:inset-y-0 lg:left-0 lg:z-30",
          isCollapsed ? "w-16" : "w-64",
          className
        )}
        onMouseEnter={hoverExpand ? () => setIsHovered(true) : undefined}
        onMouseLeave={hoverExpand ? () => setIsHovered(false) : undefined}
      >
        <div className="flex h-16 items-center justify-between px-2">
          <div className="flex items-center gap-2 min-w-0">
            <button
              className="shrink-0 flex items-center justify-center h-10 w-10 rounded-lg text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground transition-colors"
              onClick={() => setIsPinned((p) => !p)}
            >
              <img src="/images/aha-logo-icon.webp" alt="Store ICU Logo" className="size-7 object-contain" />
            </button>
            <span
              className={cn(
                "text-xl font-bold tracking-tight text-sidebar-primary whitespace-nowrap overflow-hidden transition-all duration-300",
                isCollapsed ? "w-0 opacity-0" : "w-auto opacity-100"
              )}
            >
              Store ICU
            </span>
          </div>
          <Button
            variant="ghost"
            size="icon"
            className={cn(
              "h-8 w-8 shrink-0 text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground transition-all duration-300",
              isCollapsed ? "opacity-0 pointer-events-none w-0" : "opacity-100"
            )}
            onClick={() => setIsPinned((p) => !p)}
            title={isPinned ? t('header.unpinSidebar') : t('header.pinSidebar')}
          >
            <ChevronLeft className={cn("h-4 w-4 transition-transform duration-300", isPinned && "rotate-180")} />
          </Button>
        </div>

        <nav className="flex-1 space-y-1 px-2 py-4 overflow-y-auto scrollbar-hide">
          {navItems.map((item) => {
            const isActive = location.pathname === item.href;
            return (
              <Link
                key={item.href}
                to={item.href}
                className={cn(
                  "group flex items-center rounded-md px-3 py-2 text-sm font-medium transition-colors whitespace-nowrap",
                  isActive
                    ? "bg-sidebar-primary text-sidebar-primary-foreground"
                    : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
                )}
                title={isCollapsed ? item.title : undefined}
              >
                <item.icon
                  className={cn(
                    "h-5 w-5 shrink-0 transition-[margin] duration-300",
                    isCollapsed ? "mr-0" : "mr-3",
                    isActive ? "text-sidebar-primary-foreground" : "text-sidebar-foreground group-hover:text-sidebar-accent-foreground"
                  )}
                />
                <span
                  className={cn(
                    "overflow-hidden transition-all duration-300",
                    isCollapsed ? "w-0 opacity-0" : "w-auto opacity-100"
                  )}
                >
                  {item.title}
                </span>
              </Link>
            );
          })}

          {/* External hop to AHA BD. Plain <a> (no target=_blank) → same-tab nav,
              but right-click "Open in new tab" still works natively. */}
          <a
            href={AHA_BD_URL}
            className="group flex items-center rounded-md px-3 py-2 text-sm font-medium transition-colors whitespace-nowrap text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
            title={isCollapsed ? 'AHA BD' : undefined}
          >
            <ExternalLink
              className={cn(
                "h-5 w-5 shrink-0 transition-[margin] duration-300 text-sidebar-foreground group-hover:text-sidebar-accent-foreground",
                isCollapsed ? "mr-0" : "mr-3"
              )}
            />
            <span
              className={cn(
                "overflow-hidden transition-all duration-300",
                isCollapsed ? "w-0 opacity-0" : "w-auto opacity-100"
              )}
            >
              AHA BD
            </span>
          </a>
        </nav>

        <div className="border-t border-sidebar-border p-4">
          <div
            className={cn(
              "mb-4 flex flex-col overflow-hidden transition-all duration-300",
              isCollapsed ? "h-0 opacity-0 mb-0" : "h-8 opacity-100"
            )}
          >
            <span className="truncate text-xs font-medium text-sidebar-foreground/60">
              {user?.email}
            </span>
            <span className="text-[10px] uppercase text-sidebar-primary font-bold">
              {profile?.role || 'User'}
            </span>
          </div>
          <LanguageToggle isCollapsed={isCollapsed} className="mb-2" />
          {isAdmin && <ThemeToggle isCollapsed={isCollapsed} className="mb-2" />}
          <Button
            variant="ghost"
            className={cn(
              "w-full justify-start text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground whitespace-nowrap"
            )}
            onClick={() => setShowLogoutConfirm(true)}
            title={isCollapsed ? t('header.logout') : undefined}
          >
            <LogOut className={cn("h-5 w-5 shrink-0 transition-[margin] duration-300", isCollapsed ? "mr-0" : "mr-3")} />
            <span
              className={cn(
                "overflow-hidden transition-all duration-300",
                isCollapsed ? "w-0 opacity-0" : "w-auto opacity-100"
              )}
            >
              {t('header.logout')}
            </span>
          </Button>
        </div>
      </aside>

      <Dialog open={showLogoutConfirm} onOpenChange={setShowLogoutConfirm}>
        <DialogContent showCloseButton={false}>
          <DialogHeader>
            <DialogTitle>{t('header.confirmLogout')}</DialogTitle>
            <DialogDescription>{t('header.logoutConfirmation')}</DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <DialogClose asChild>
              <Button variant="outline" disabled={isLoggingOut}>
                {t('common.cancel')}
              </Button>
            </DialogClose>
            <Button variant="destructive" onClick={handleLogout} disabled={isLoggingOut}>
              {isLoggingOut ? t('header.loggingOut') : t('header.logout')}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
};
