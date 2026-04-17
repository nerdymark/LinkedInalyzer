import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getAuthors, getAuthor, updateAuthorStatus, getStats } from '../api/client';

export function useAuthors(params?: {
  status?: string;
  political_only?: boolean;
  ai_slop_only?: boolean;
  flagged_only?: boolean;
  sort_by?: string;
  sort_dir?: string;
}) {
  return useQuery({
    queryKey: ['authors', params],
    queryFn: () => getAuthors(params),
  });
}

export function useAuthor(id: number | null) {
  return useQuery({
    queryKey: ['author', id],
    queryFn: () => getAuthor(id!),
    enabled: id !== null,
  });
}

export function useStats() {
  return useQuery({
    queryKey: ['stats'],
    queryFn: getStats,
  });
}

export function useUpdateStatus() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) =>
      updateAuthorStatus(id, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['authors'] });
      queryClient.invalidateQueries({ queryKey: ['stats'] });
    },
  });
}
