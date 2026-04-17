import json

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.api.schemas import AnalysisResponse, PostResponse
from backend.database import get_session_factory
from backend.models import Analysis, Post

router = APIRouter()


def get_db():
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/posts", response_model=list[PostResponse])
def list_posts(
    author_id: int | None = Query(None),
    political_only: bool = Query(False),
    ai_slop_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(Post).order_by(Post.scraped_at.desc())

    if author_id:
        query = query.filter(Post.author_id == author_id)

    if political_only or ai_slop_only:
        query = query.join(Analysis, Analysis.post_id == Post.id)
        if political_only:
            query = query.filter(Analysis.is_political == True)
        if ai_slop_only:
            query = query.filter(Analysis.is_ai_slop == True)

    posts = query.offset(offset).limit(limit).all()

    results = []
    for post in posts:
        analysis = None
        if post.analysis:
            a = post.analysis
            topics = []
            if a.political_topics:
                try:
                    topics = json.loads(a.political_topics)
                except (json.JSONDecodeError, TypeError):
                    topics = []
            analysis = AnalysisResponse(
                sentiment_score=a.sentiment_score,
                is_political=a.is_political,
                political_confidence=a.political_confidence,
                political_topics=topics,
                is_ai_slop=a.is_ai_slop,
                ai_slop_confidence=a.ai_slop_confidence,
            )
        results.append(PostResponse(
            id=post.id,
            linkedin_post_id=post.linkedin_post_id,
            content=post.content,
            feed_context=post.feed_context,
            post_url=post.post_url,
            scraped_at=post.scraped_at,
            analysis=analysis,
        ))

    return results
