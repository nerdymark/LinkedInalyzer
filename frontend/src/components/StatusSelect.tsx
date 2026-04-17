import { useUpdateStatus } from '../hooks/useAuthors';
import type { ReviewStatus } from '../types';

const STATUS_OPTIONS: { value: ReviewStatus; label: string; color: string }[] = [
  { value: 'pending', label: 'Pending', color: 'text-yellow-600' },
  { value: 'reviewed', label: 'Reviewed', color: 'text-blue-600' },
  { value: 'keep', label: 'Keep', color: 'text-green-600' },
  { value: 'unfollowed', label: 'Unfollowed', color: 'text-orange-600' },
  { value: 'disconnected', label: 'Disconnected', color: 'text-red-600' },
];

interface StatusSelectProps {
  authorId: number;
  currentStatus: string;
}

export function StatusSelect({ authorId, currentStatus }: StatusSelectProps) {
  const mutation = useUpdateStatus();

  return (
    <select
      value={currentStatus}
      onChange={(e) => mutation.mutate({ id: authorId, status: e.target.value })}
      disabled={mutation.isPending}
      className="text-sm border border-gray-300 rounded px-2 py-1 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
    >
      {STATUS_OPTIONS.map((opt) => (
        <option key={opt.value} value={opt.value}>
          {opt.label}
        </option>
      ))}
    </select>
  );
}
