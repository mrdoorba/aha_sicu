import { useState, useEffect, useRef } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useNavigate, Link, useLocation } from 'react-router-dom';

export const Header = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [showConfirm, setShowConfirm] = useState(false);
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const modalRef = useRef<HTMLDivElement>(null);
  const cancelButtonRef = useRef<HTMLButtonElement>(null);

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

  const handleCancelLogout = () => {
    setShowConfirm(false);
  };

  const handleBackdropClick = (e: React.MouseEvent) => {
    // Close modal when clicking backdrop (not modal content)
    if (e.target === e.currentTarget) {
      setShowConfirm(false);
    }
  };

  // Handle Escape key to close modal
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (showConfirm && e.key === 'Escape') {
        setShowConfirm(false);
      }
    };

    if (showConfirm) {
      document.addEventListener('keydown', handleKeyDown);
      // Focus the cancel button when modal opens
      cancelButtonRef.current?.focus();
    }

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [showConfirm]);

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

      {/* Logout Confirmation Modal */}
      {showConfirm && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
          onClick={handleBackdropClick}
          role="dialog"
          aria-modal="true"
          aria-labelledby="logout-modal-title"
          aria-describedby="logout-modal-description"
        >
          <div
            ref={modalRef}
            className="bg-white rounded-lg shadow-lg p-6 max-w-sm w-full mx-4"
          >
            <h2
              id="logout-modal-title"
              className="text-lg font-semibold text-foreground mb-2"
            >
              Confirm Logout
            </h2>
            <p id="logout-modal-description" className="text-muted-foreground mb-4">
              Are you sure you want to log out?
            </p>
            <div className="flex gap-3 justify-end">
              <button
                ref={cancelButtonRef}
                onClick={handleCancelLogout}
                disabled={isLoggingOut}
                className="px-4 py-2 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmLogout}
                disabled={isLoggingOut}
                className="px-4 py-2 text-sm font-medium bg-destructive text-white rounded-lg hover:bg-destructive/85 disabled:opacity-50 transition-colors"
              >
                {isLoggingOut ? 'Logging out...' : 'Logout'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
