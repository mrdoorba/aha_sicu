import { useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import i18n from 'i18next';
import { getCurrentUser } from '../services/apiClient';
import { useAuth } from '../context/AuthContext';

export interface UserProfile {
  id: string;
  email: string;
  role: string;
  language: string;
  created_at: string;
  last_login: string;
}

export function useCurrentUser() {
  const { user } = useAuth();

  const query = useQuery({
    queryKey: ['currentUser'],
    queryFn: async () => {
      return await getCurrentUser();
    },
    enabled: !!user,
  });

  useEffect(() => {
    if (query.data?.language && query.data.language !== i18n.language) {
      i18n.changeLanguage(query.data.language);
    }
  }, [query.data?.language]);

  return {
    profile: query.data ?? null,
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error as { code?: string } | null,
  };
}
