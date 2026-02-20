import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import client from '../services/apiClient';

export interface Account {
  id: number;
  email: string;
  role: string;
  created_at: string;
  last_login: string | null;
}

export function useAccounts() {
  const query = useQuery<Account[]>({
    queryKey: ['accounts'],
    queryFn: async () => {
      const { data, error } = await client.GET('/api/v1/accounts');
      if (error) throw new Error('Failed to fetch accounts');
      return data as Account[];
    },
  });

  return {
    accounts: query.data ?? [],
    isLoading: query.isLoading,
    isError: query.isError,
    refetch: query.refetch,
  };
}

export function useCreateAccount() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (params: {
      email: string;
      password: string;
      role: 'member' | 'leader' | 'admin';
    }) => {
      const { data, error } = await client.POST('/api/v1/accounts', {
        body: params,
      });
      if (error) throw error;
      return data as Account;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['accounts'] });
    },
  });
}

export function useUpdateRole() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (params: {
      userId: number;
      role: 'member' | 'leader' | 'admin';
    }) => {
      const { data, error } = await client.PATCH(
        '/api/v1/accounts/{user_id}/role',
        {
          params: { path: { user_id: params.userId } },
          body: { role: params.role },
        },
      );
      if (error) throw error;
      return data as Account;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['accounts'] });
    },
  });
}

export function useResetPassword() {
  return useMutation({
    mutationFn: async (params: { userId: number; password: string }) => {
      const { error } = await client.POST(
        '/api/v1/accounts/{user_id}/reset-password',
        {
          params: { path: { user_id: params.userId } },
          body: { password: params.password },
        },
      );
      if (error) throw error;
    },
  });
}

export function useDeleteAccount() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (userId: number) => {
      const { error } = await client.DELETE('/api/v1/accounts/{user_id}', {
        params: { path: { user_id: userId } },
      });
      if (error) throw error;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['accounts'] });
    },
  });
}
