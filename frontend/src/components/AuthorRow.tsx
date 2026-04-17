import { useState } from 'react';
import { useAuthor } from '../hooks/useAuthors';
import type { Author } from '../types';
import { ScoreBadge } from './ScoreBadge';
import { StatusSelect } from './StatusSelect';
import { PostDetail } from './PostDetail';

interface AuthorRowProps {
  author: Author;
}

export function AuthorRow({ author }: AuthorRowProps) {
  const [expanded, setExpanded] = useState(false);
  const { data: detail, isLoading } = useAuthor(expanded ? author.id : null);

  return (
    <div className="border border-[#e0dfdc] rounded-lg bg-white overflow-hidden">
      <div
        className="p-3 cursor-pointer hover:bg-[#f3f2ef] transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        {/* Top line: name + actions */}
        <div className="flex items-center gap-2 min-w-0">
          <span className="font-semibold text-sm text-[#191919] truncate">{author.name}</span>
          {author.headline && (
            <span className="text-xs text-[#666] truncate hidden md:inline">
              {author.headline}
            </span>
          )}
          <div className="ml-auto flex items-center gap-2 shrink-0">
            <StatusSelect authorId={author.id} currentStatus={author.review_status} />
            <a
              href={author.linkedin_url}
              target="_blank"
              rel="noopener noreferrer"
              onClick={(e) => e.stopPropagation()}
              className="text-[#0a66c2] hover:underline text-xs font-semibold"
            >
              Profile
            </a>
            <span className="text-[#666] text-xs">{expanded ? '\u25B2' : '\u25BC'}</span>
          </div>
        </div>

        {/* Bottom line: badges */}
        <div className="flex items-center gap-2 mt-1.5 flex-wrap">
          {author.political_post_count > 0 && (
            <ScoreBadge score={author.avg_political_score} label={`Political \u00d7${author.political_post_count}`} />
          )}
          {author.ai_slop_post_count > 0 && (
            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-amber-100 text-[#915907] border border-amber-200">
              {`AI Slop ${(author.avg_ai_slop_score * 100).toFixed(0)}% \u00d7${author.ai_slop_post_count}`}
            </span>
          )}
        </div>
      </div>

      {expanded && (
        <div className="border-t border-[#e0dfdc] p-3 space-y-2 bg-[#f9fafb]">
          {isLoading ? (
            <div className="text-sm text-[#666]">Loading posts...</div>
          ) : detail?.posts.length ? (
            detail.posts.map((post) => <PostDetail key={post.id} post={post} />)
          ) : (
            <div className="text-sm text-[#666]">No posts found.</div>
          )}
        </div>
      )}
    </div>
  );
}
