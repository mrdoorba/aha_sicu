import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import { Button } from '../ui/button';
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '../ui/dialog';

export const Header = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [showConfirm, setShowConfirm] = useState(false);
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  const handleLogoutClick = () => {
    setShowConfirm(true);
  };

  const handleConfirmLogout = async () => {
    setIsLoggingOut(true);
    try {
      await logout();
      navigate('/login', { replace: true });
    } catch (error) {
      console.error('Logout failed:', error);
    } finally {
      setIsLoggingOut(false);
      setShowConfirm(false);
    }
  };

  return (
    <>
      <header className="bg-foreground text-white">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-6">
              <h1 className="text-xl font-semibold">Store ICU</h1>
              <nav className="flex items-center gap-1">
                <Link
                  to="/dashboard"
                  className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
                    location.pathname === '/dashboard'
                      ? 'bg-white/20 text-white'
                      : 'text-gray-300 hover:bg-white/10 hover:text-white'
                  }`}
                >
                  Dashboard
                </Link>
                <Link
                  to="/brands"
                  className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
                    location.pathname === '/brands'
                      ? 'bg-white/20 text-white'
                      : 'text-gray-300 hover:bg-white/10 hover:text-white'
                  }`}
                >
                  Brands
                </Link>
                <Link
                  to="/history"
                  className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
                    location.pathname === '/history'
                      ? 'bg-white/20 text-white'
                      : 'text-gray-300 hover:bg-white/10 hover:text-white'
                  }`}
                >
                  History
                </Link>
              </nav>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-300">{user?.email}</span>
              <button
                onClick={handleLogoutClick}
                className="px-3 py-1.5 text-sm bg-white/10 hover:bg-white/20 rounded-md transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Logout Confirmation Dialog */}
      <Dialog open={showConfirm} onOpenChange={setShowConfirm}>
        <DialogContent showCloseButton={false}>
          <DialogHeader>
            <DialogTitle>Confirm Logout</DialogTitle>
            <DialogDescription>Are you sure you want to log out?</DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <DialogClose asChild>
              <Button variant="outline" disabled={isLoggingOut}>
                Cancel
              </Button>
            </DialogClose>
            <Button variant="destructive" onClick={handleConfirmLogout} disabled={isLoggingOut}>
              {isLoggingOut ? 'Logging out...' : 'Logout'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
};
