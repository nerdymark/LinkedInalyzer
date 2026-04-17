import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.api.schemas import AuthorDetail, AuthorListItem, AuthorUpdate, AnalysisResponse, PostResponse
from backend.database import get_session_factory
from backend.models import Author, Post, Analysis

router = APIRouter()


def get_db():
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/authors", response_model=list[AuthorListItem])
def list_authors(
    status: str | None = Query(None, description="Filter by review_status"),
    political_only: bool = Query(False, description="Only show authors with political posts"),
    ai_slop_only: bool = Query(False, description="Only show authors with AI slop posts"),
    flagged_only: bool = Query(True, description="Only show authors flagged for political or AI slop"),
    sort_by: str = Query("avg_political_score", description="Sort field"),
    sort_dir: str = Query("desc", description="Sort direction: asc or desc"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(Author)

    if status:
        query = query.filter(Author.review_status == status)
    if political_only:
        query = query.filter(Author.political_post_count > 0)
    elif ai_slop_only:
        query = query.filter(Author.ai_slop_post_count > 0)
    elif flagged_only:
        query = query.filter(
            (Author.political_post_count > 0) | (Author.ai_slop_post_count > 0)
        )

    sort_col = getattr(Author, sort_by, Author.avg_political_score)
    if sort_dir == "desc":
        query = query.order_by(sort_col.desc())
    else:
        query = query.order_by(sort_col.asc())

    authors = query.offset(offset).limit(limit).all()
    return authors


@router.get("/authors/{author_id}", response_model=AuthorDetail)
def get_author(author_id: int, db: Session = Depends(get_db)):
    author = db.query(Author).filter_by(id=author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    posts = db.query(Post).filter_by(author_id=author_id).order_by(Post.scraped_at.desc()).all()

    post_responses = []
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
        post_responses.append(PostResponse(
            id=post.id,
            linkedin_post_id=post.linkedin_post_id,
            content=post.content,
            feed_context=post.feed_context,
            post_url=post.post_url,
            scraped_at=post.scraped_at,
            analysis=analysis,
        ))

    return AuthorDetail(
        id=author.id,
        name=author.name,
        linkedin_url=author.linkedin_url,
        headline=author.headline,
        political_post_count=author.political_post_count,
        avg_political_score=author.avg_political_score,
        ai_slop_post_count=author.ai_slop_post_count,
        avg_ai_slop_score=author.avg_ai_slop_score,
        review_status=author.review_status,
        first_seen_at=author.first_seen_at,
        posts=post_responses,
    )


@router.patch("/authors/{author_id}", response_model=AuthorListItem)
def update_author(author_id: int, update: AuthorUpdate, db: Session = Depends(get_db)):
    valid_statuses = {"pending", "reviewed", "keep", "unfollowed", "disconnected"}
    if update.review_status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")

    author = db.query(Author).filter_by(id=author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    author.review_status = update.review_status
    db.commit()
    db.refresh(author)
    return author
