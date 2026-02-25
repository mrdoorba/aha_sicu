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
  Menu
} from 'lucide-react';
import { cn } from '../../lib/utils';
import { useAuth } from '../../context/AuthContext';
import { useCurrentUser } from '../../hooks/useCurrentUser';
import { Button } from '../ui/button';
import { ThemeToggle } from './ThemeToggle';
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
}

export const Sidebar = ({ className }: SidebarProps) => {
  const { t } = useTranslation();
  const { user, logout } = useAuth();
  const { profile } = useCurrentUser();
  const location = useLocation();
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  const canAccessRules = profile?.role === 'leader' || profile?.role === 'admin';
  const isAdmin = profile?.role === 'admin';

  const navItems = [
    {
      title: 'Dashboard',
      href: '/dashboard',
      icon: LayoutDashboard,
    },
    {
      title: 'Brand',
      href: '/brands',
      icon: Briefcase,
    },
    {
      title: t('header.history'),
      href: '/history',
      icon: History,
    },
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
      <aside
        className={cn(
          "relative flex flex-col border-r border-sidebar-border bg-sidebar text-sidebar-foreground transition-all duration-300 ease-in-out",
          isCollapsed ? "w-16" : "w-64",
          className
        )}
      >
        <div className="flex h-16 items-center justify-between px-4">
          {!isCollapsed && (
            <span className="text-xl font-bold tracking-tight text-sidebar-primary">Store ICU</span>
          )}
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
            onClick={() => setIsCollapsed(!isCollapsed)}
          >
            {isCollapsed ? <Menu className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
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
                  "group flex items-center rounded-md px-3 py-2 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-sidebar-primary text-sidebar-primary-foreground"
                    : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
                  isCollapsed && "justify-center px-2"
                )}
                title={isCollapsed ? item.title : undefined}
              >
                <item.icon
                  className={cn(
                    "h-5 w-5 shrink-0",
                    !isCollapsed && "mr-3",
                    isActive ? "text-sidebar-primary-foreground" : "text-sidebar-foreground group-hover:text-sidebar-accent-foreground"
                  )}
                />
                {!isCollapsed && <span>{item.title}</span>}
              </Link>
            );
          })}
        </nav>

        <div className="border-t border-sidebar-border p-4">
          {!isCollapsed && (
            <div className="mb-4 flex flex-col">
              <span className="truncate text-xs font-medium text-sidebar-foreground/60">
                {user?.email}
              </span>
              <span className="text-[10px] uppercase text-sidebar-primary font-bold">
                {profile?.role || 'User'}
              </span>
            </div>
          )}
          <ThemeToggle isCollapsed={isCollapsed} className="mb-2" />
          <Button
            variant="ghost"
            className={cn(
              "w-full text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
              isCollapsed ? "justify-center p-2" : "justify-start"
            )}
            onClick={() => setShowLogoutConfirm(true)}
            title={isCollapsed ? t('header.logout') : undefined}
          >
            <LogOut className={cn("h-5 w-5 shrink-0", !isCollapsed && "mr-3")} />
            {!isCollapsed && <span>{t('header.logout')}</span>}
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
