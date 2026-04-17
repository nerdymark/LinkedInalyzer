import { useState } from 'react';
import { useAuthors } from '../hooks/useAuthors';
import { AuthorRow } from './AuthorRow';

const SORT_OPTIONS = [
  { value: 'avg_political_score', label: 'Political Score' },
  { value: 'political_post_count', label: 'Political Posts' },
  { value: 'avg_ai_slop_score', label: 'AI Slop Score' },
  { value: 'ai_slop_post_count', label: 'AI Slop Posts' },
  { value: 'name', label: 'Name' },
];

const STATUS_FILTERS = [
  { value: '', label: 'All' },
  { value: 'pending', label: 'Pending' },
  { value: 'reviewed', label: 'Reviewed' },
  { value: 'keep', label: 'Keep' },
  { value: 'unfollowed', label: 'Unfollowed' },
  { value: 'disconnected', label: 'Disconnected' },
];

type ViewMode = 'all' | 'political' | 'ai_slop';

const VIEW_MODES: { value: ViewMode; label: string }[] = [
  { value: 'all', label: 'All Flagged' },
  { value: 'political', label: 'Political' },
  { value: 'ai_slop', label: 'AI Slop' },
];

export function Dashboard() {
  const [statusFilter, setStatusFilter] = useState('');
  const [viewMode, setViewMode] = useState<ViewMode>('all');
  const [sortBy, setSortBy] = useState('avg_political_score');
  const [sortDir, setSortDir] = useState('desc');

  const { data: authors, isLoading, error } = useAuthors({
    status: statusFilter || undefined,
    political_only: viewMode === 'political',
    ai_slop_only: viewMode === 'ai_slop',
    flagged_only: viewMode === 'all',
    sort_by: sortBy,
    sort_dir: sortDir,
  });

  return (
    <div>
      <div className="flex items-center gap-4 mb-4 flex-wrap">
        {/* View mode toggle */}
        <div className="flex items-center gap-2">
          <label className="text-sm font-medium text-gray-600">View:</label>
          <div className="flex gap-1">
            {VIEW_MODES.map((m) => (
              <button
                key={m.value}
                onClick={() => setViewMode(m.value)}
                className={`px-3 py-1 text-sm rounded-full border transition-colors ${
                  viewMode === m.value
                    ? 'bg-[#0a66c2] text-white border-[#0a66c2]'
                    : 'bg-white text-[#666] border-[#e0dfdc] hover:border-[#0a66c2]'
                }`}
              >
                {m.label}
              </button>
            ))}
          </div>
        </div>

        {/* Status filter */}
        <div className="flex items-center gap-2">
          <label className="text-sm font-medium text-gray-600">Status:</label>
          <div className="flex gap-1">
            {STATUS_FILTERS.map((f) => (
              <button
                key={f.value}
                onClick={() => setStatusFilter(f.value)}
                className={`px-3 py-1 text-sm rounded-full border transition-colors ${
                  statusFilter === f.value
                    ? 'bg-[#0a66c2] text-white border-[#0a66c2]'
                    : 'bg-white text-[#666] border-[#e0dfdc] hover:border-[#0a66c2]'
                }`}
              >
                {f.label}
              </button>
            ))}
          </div>
        </div>

        {/* Sort controls */}
        <div className="flex items-center gap-2 ml-auto">
          <label className="text-sm font-medium text-gray-600">Sort:</label>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="text-sm border border-gray-300 rounded px-2 py-1 bg-white"
          >
            {SORT_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>{o.label}</option>
            ))}
          </select>
          <button
            onClick={() => setSortDir(sortDir === 'desc' ? 'asc' : 'desc')}
            className="text-sm border border-gray-300 rounded px-2 py-1 bg-white hover:bg-gray-50"
          >
            {sortDir === 'desc' ? '\u2193' : '\u2191'}
          </button>
        </div>
      </div>

      {isLoading && <div className="text-center text-gray-400 py-8">Loading...</div>}
      {error && <div className="text-center text-red-500 py-8">Error loading authors</div>}

      <div className="space-y-2">
        {authors?.map((author) => (
          <AuthorRow key={author.id} author={author} />
        ))}
        {authors && authors.length === 0 && (
          <div className="text-center text-gray-400 py-8">
            No flagged authors found. Run the scraper to collect posts.
          </div>
        )}
      </div>
    </div>
  );
}
