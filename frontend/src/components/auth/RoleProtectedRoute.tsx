import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useCurrentUser } from '../../hooks/useCurrentUser';
import { toast } from 'sonner';
import { useEffect, useRef } from 'react';

interface RoleProtectedRouteProps {
  allowedRoles: string[];
  children: React.ReactNode;
  accessDeniedMessage?: string;
}

export const RoleProtectedRoute = ({
  allowedRoles,
  children,
  accessDeniedMessage = 'Access denied — scoring rules require leader or admin role',
}: RoleProtectedRouteProps) => {
  const { user, loading: authLoading } = useAuth();
  const { profile, isLoading: profileLoading } = useCurrentUser();
  const location = useLocation();
  const toastShown = useRef(false);

  const shouldRedirect = !authLoading && !profileLoading && profile && !allowedRoles.includes(profile.role);

  useEffect(() => {
    if (shouldRedirect && !toastShown.current) {
      toast.error(accessDeniedMessage);
      toastShown.current = true;
    }
  }, [shouldRedirect, accessDeniedMessage]);

  if (authLoading || profileLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-muted">
        <div className="text-muted-foreground">Loading...</div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (shouldRedirect) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
};
