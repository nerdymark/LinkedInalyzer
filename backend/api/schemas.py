from datetime import datetime

from pydantic import BaseModel


class AnalysisResponse(BaseModel):
    sentiment_score: float | None
    is_political: bool | None
    political_confidence: float | None
    political_topics: list[str]
    is_ai_slop: bool | None
    ai_slop_confidence: float | None

    model_config = {"from_attributes": True}


class PostResponse(BaseModel):
    id: int
    linkedin_post_id: str | None
    content: str
    feed_context: str | None
    post_url: str | None
    scraped_at: datetime
    analysis: AnalysisResponse | None

    model_config = {"from_attributes": True}


class AuthorListItem(BaseModel):
    id: int
    name: str
    linkedin_url: str
    headline: str | None
    political_post_count: int
    avg_political_score: float
    ai_slop_post_count: int
    avg_ai_slop_score: float
    review_status: str
    first_seen_at: datetime

    model_config = {"from_attributes": True}


class AuthorDetail(AuthorListItem):
    posts: list[PostResponse]


class AuthorUpdate(BaseModel):
    review_status: str


class StatsResponse(BaseModel):
    total_authors: int
    total_posts: int
    analyzed_posts: int
    political_posts: int
    ai_slop_posts: int
    pending_review: int
    status_breakdown: dict[str, int]
