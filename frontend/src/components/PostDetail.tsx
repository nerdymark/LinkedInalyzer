import { useState } from 'react';
import type { Post } from '../types';
import { ScoreBadge } from './ScoreBadge';

interface PostDetailProps {
  post: Post;
}

export function PostDetail({ post }: PostDetailProps) {
  const [expanded, setExpanded] = useState(false);
  const a = post.analysis;
  const truncated = post.content.length > 200 && !expanded;

  return (
    <div className="border border-gray-100 rounded p-3 bg-gray-50 text-sm">
      {post.feed_context && post.feed_context !== 'direct' && (
        <div className="text-xs text-gray-400 mb-1 italic">
          {post.feed_context}
        </div>
      )}
      <p className="text-gray-700 whitespace-pre-wrap">
        {truncated ? post.content.slice(0, 200) + '...' : post.content}
        {post.content.length > 200 && (
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-blue-600 hover:underline ml-1"
          >
            {expanded ? 'less' : 'more'}
          </button>
        )}
      </p>
      {a && (
        <div className="flex gap-2 mt-2 flex-wrap">
          {a.is_political && a.political_confidence != null && (
            <ScoreBadge score={a.political_confidence} label="Political" />
          )}
          {a.is_ai_slop && a.ai_slop_confidence != null && (
            <ScoreBadge score={a.ai_slop_confidence} label="AI Slop" />
          )}
          {a.sentiment_score != null && (
            <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${
              a.sentiment_score < -0.3
                ? 'bg-red-50 text-red-700 border-red-200'
                : a.sentiment_score > 0.3
                ? 'bg-green-50 text-green-700 border-green-200'
                : 'bg-gray-100 text-gray-700 border-gray-200'
            }`}>
              Sentiment: {a.sentiment_score > 0 ? '+' : ''}{a.sentiment_score.toFixed(2)}
            </span>
          )}
          {a.political_topics.length > 0 && (
            <span className="text-xs text-gray-500">
              Topics: {a.political_topics.join(', ')}
            </span>
          )}
        </div>
      )}
    </div>
  );
}
