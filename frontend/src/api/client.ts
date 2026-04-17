import type { Author, AuthorDetail, Post, Stats } from '../types';

const BASE = '/api';

async function fetchJSON<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${url}`, init);
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export async function getAuthors(params?: {
  status?: string;
  political_only?: boolean;
  ai_slop_only?: boolean;
  flagged_only?: boolean;
  sort_by?: string;
  sort_dir?: string;
  limit?: number;
  offset?: number;
}): Promise<Author[]> {
  const searchParams = new URLSearchParams();
  if (params?.status) searchParams.set('status', params.status);
  if (params?.political_only !== undefined) searchParams.set('political_only', String(params.political_only));
  if (params?.ai_slop_only !== undefined) searchParams.set('ai_slop_only', String(params.ai_slop_only));
  if (params?.flagged_only !== undefined) searchParams.set('flagged_only', String(params.flagged_only));
  if (params?.sort_by) searchParams.set('sort_by', params.sort_by);
  if (params?.sort_dir) searchParams.set('sort_dir', params.sort_dir);
  if (params?.limit) searchParams.set('limit', String(params.limit));
  if (params?.offset) searchParams.set('offset', String(params.offset));
  const qs = searchParams.toString();
  return fetchJSON<Author[]>(`/authors${qs ? `?${qs}` : ''}`);
}

export async function getAuthor(id: number): Promise<AuthorDetail> {
  return fetchJSON<AuthorDetail>(`/authors/${id}`);
}

export async function updateAuthorStatus(id: number, review_status: string): Promise<Author> {
  return fetchJSON<Author>(`/authors/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ review_status }),
  });
}

export async function getPosts(params?: {
  author_id?: number;
  political_only?: boolean;
  ai_slop_only?: boolean;
  limit?: number;
  offset?: number;
}): Promise<Post[]> {
  const searchParams = new URLSearchParams();
  if (params?.author_id) searchParams.set('author_id', String(params.author_id));
  if (params?.political_only) searchParams.set('political_only', 'true');
  if (params?.ai_slop_only) searchParams.set('ai_slop_only', 'true');
  if (params?.limit) searchParams.set('limit', String(params.limit));
  if (params?.offset) searchParams.set('offset', String(params.offset));
  const qs = searchParams.toString();
  return fetchJSON<Post[]>(`/posts${qs ? `?${qs}` : ''}`);
}

export async function getStats(): Promise<Stats> {
  return fetchJSON<Stats>('/stats');
}

export async function getScoreDistribution() {
  return fetchJSON<{ buckets: string[]; political: number[]; ai_slop: number[] }>('/stats/score-distribution');
}

export async function getFeedContext() {
  return fetchJSON<{ name: string; value: number }[]>('/stats/feed-context');
}

export async function getTopOffenders() {
  return fetchJSON<{
    political: { id: number; name: string; linkedin_url: string; political_post_count: number; avg_political_score: number; ai_slop_post_count: number; avg_ai_slop_score: number; review_status: string }[];
    ai_slop: { id: number; name: string; linkedin_url: string; political_post_count: number; avg_political_score: number; ai_slop_post_count: number; avg_ai_slop_score: number; review_status: string }[];
  }>('/stats/top-offenders');
}

export async function getTimeline() {
  return fetchJSON<{ date: string; total: number; political: number; ai_slop: number; clean: number }[]>('/stats/timeline');
}

export async function getAmplifiers() {
  return fetchJSON<{ name: string; count: number }[]>('/stats/amplifiers');
}
