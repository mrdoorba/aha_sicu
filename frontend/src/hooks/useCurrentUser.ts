import { useQuery } from '@tanstack/react-query';
import { getCurrentUser } from '../services/apiClient';
import { useAuth } from '../context/AuthContext';

export interface UserProfile {
  id: string;
  email: string;
  role: string;
  created_at: string;
  last_login: string;
}

export function useCurrentUser() {
  const { user } = useAuth();

  const query = useQuery<UserProfile>({
    queryKey: ['currentUser'],
    queryFn: async () => {
      return await getCurrentUser() as UserProfile;
    },
    enabled: !!user,
  });

  return {
    profile: query.data ?? null,
    isLoading: query.isLoading,
    isError: query.isError,
  };
}
