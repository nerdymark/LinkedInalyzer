export interface Analysis {
  sentiment_score: number | null;
  is_political: boolean | null;
  political_confidence: number | null;
  political_topics: string[];
  is_ai_slop: boolean | null;
  ai_slop_confidence: number | null;
}

export interface Post {
  id: number;
  linkedin_post_id: string | null;
  content: string;
  feed_context: string | null;
  post_url: string | null;
  scraped_at: string;
  analysis: Analysis | null;
}

export interface Author {
  id: number;
  name: string;
  linkedin_url: string;
  headline: string | null;
  political_post_count: number;
  avg_political_score: number;
  ai_slop_post_count: number;
  avg_ai_slop_score: number;
  review_status: string;
  first_seen_at: string;
}

export interface AuthorDetail extends Author {
  posts: Post[];
}

export interface Stats {
  total_authors: number;
  total_posts: number;
  analyzed_posts: number;
  political_posts: number;
  ai_slop_posts: number;
  pending_review: number;
  status_breakdown: Record<string, number>;
}

export type ReviewStatus = 'pending' | 'reviewed' | 'keep' | 'unfollowed' | 'disconnected';
