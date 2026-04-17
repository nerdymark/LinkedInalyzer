import json

from fastapi import APIRouter, Depends
from sqlalchemy import case, cast, func, Float
from sqlalchemy.orm import Session

from backend.api.schemas import StatsResponse
from backend.database import get_session_factory
from backend.models import Analysis, Author, Post, ScrapeSession

router = APIRouter()


def get_db():
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/stats", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    total_authors = db.query(Author).count()
    total_posts = db.query(Post).count()
    analyzed_posts = db.query(Post).filter_by(analyzed=True).count()
    political_posts = db.query(Analysis).filter_by(is_political=True).count()
    ai_slop_posts = db.query(Analysis).filter_by(is_ai_slop=True).count()
    pending_review = db.query(Author).filter(
        Author.review_status == "pending",
        (Author.political_post_count > 0) | (Author.ai_slop_post_count > 0),
    ).count()

    status_counts = db.query(Author.review_status, func.count(Author.id)).group_by(
        Author.review_status
    ).all()
    status_breakdown = {status: count for status, count in status_counts}

    return StatsResponse(
        total_authors=total_authors,
        total_posts=total_posts,
        analyzed_posts=analyzed_posts,
        political_posts=political_posts,
        ai_slop_posts=ai_slop_posts,
        pending_review=pending_review,
        status_breakdown=status_breakdown,
    )


@router.get("/stats/score-distribution")
def get_score_distribution(db: Session = Depends(get_db)):
    """Distribution of political and AI slop scores in buckets."""
    analyses = db.query(
        Analysis.political_confidence,
        Analysis.ai_slop_confidence,
    ).all()

    political_buckets = [0] * 10  # 0-10%, 10-20%, ..., 90-100%
    slop_buckets = [0] * 10

    for a in analyses:
        if a.political_confidence is not None:
            idx = min(int(a.political_confidence * 10), 9)
            political_buckets[idx] += 1
        if a.ai_slop_confidence is not None:
            idx = min(int(a.ai_slop_confidence * 10), 9)
            slop_buckets[idx] += 1

    return {
        "buckets": [f"{i*10}-{(i+1)*10}%" for i in range(10)],
        "political": political_buckets,
        "ai_slop": slop_buckets,
    }


@router.get("/stats/feed-context")
def get_feed_context_breakdown(db: Session = Depends(get_db)):
    """Breakdown of how posts reached the user's feed."""
    posts = db.query(Post.feed_context).filter(Post.feed_context.isnot(None)).all()

    context_map: dict[str, int] = {}
    for (ctx,) in posts:
        if not ctx:
            key = "unknown"
        elif ctx == "direct":
            key = "Direct (your connection)"
        elif any(x in ctx for x in ["likes this", "loves this", "celebrates this",
                                       "finds this insightful", "finds this funny",
                                       "supports this"]):
            key = "Reacted by connection"
        elif "commented" in ctx:
            key = "Commented by connection"
        elif "reposted" in ctx:
            key = "Reposted by connection"
        elif "follow" in ctx:
            key = "Followed by connections"
        elif "Based on" in ctx or "Suggested" in ctx:
            key = "Suggested by LinkedIn"
        elif "Promoted" in ctx:
            key = "Promoted (ad)"
        else:
            key = "Other"

        context_map[key] = context_map.get(key, 0) + 1

    return [{"name": k, "value": v} for k, v in sorted(context_map.items(), key=lambda x: -x[1])]


@router.get("/stats/top-offenders")
def get_top_offenders(db: Session = Depends(get_db)):
    """Top political and AI slop authors."""
    top_political = (
        db.query(Author)
        .filter(Author.political_post_count > 0)
        .order_by(Author.avg_political_score.desc(), Author.political_post_count.desc())
        .limit(10)
        .all()
    )

    top_slop = (
        db.query(Author)
        .filter(Author.ai_slop_post_count > 0)
        .order_by(Author.avg_ai_slop_score.desc(), Author.ai_slop_post_count.desc())
        .limit(10)
        .all()
    )

    def author_to_dict(a):
        return {
            "id": a.id,
            "name": a.name,
            "linkedin_url": a.linkedin_url,
            "political_post_count": a.political_post_count,
            "avg_political_score": a.avg_political_score,
            "ai_slop_post_count": a.ai_slop_post_count,
            "avg_ai_slop_score": a.avg_ai_slop_score,
            "review_status": a.review_status,
        }

    return {
        "political": [author_to_dict(a) for a in top_political],
        "ai_slop": [author_to_dict(a) for a in top_slop],
    }


@router.get("/stats/timeline")
def get_scrape_timeline(db: Session = Depends(get_db)):
    """Posts scraped over time, grouped by date."""
    results = (
        db.query(
            func.date(Post.scraped_at).label("date"),
            func.count(Post.id).label("total"),
            func.sum(case((Analysis.is_political == True, 1), else_=0)).label("political"),
            func.sum(case((Analysis.is_ai_slop == True, 1), else_=0)).label("ai_slop"),
        )
        .outerjoin(Analysis, Analysis.post_id == Post.id)
        .group_by(func.date(Post.scraped_at))
        .order_by(func.date(Post.scraped_at))
        .all()
    )

    return [
        {
            "date": str(r.date),
            "total": r.total,
            "political": int(r.political or 0),
            "ai_slop": int(r.ai_slop or 0),
            "clean": r.total - int(r.political or 0) - int(r.ai_slop or 0),
        }
        for r in results
    ]


@router.get("/stats/amplifiers")
def get_amplifiers(db: Session = Depends(get_db)):
    """Connections who amplify flagged content (appear in feed_context of political/slop posts)."""
    flagged_posts = (
        db.query(Post.feed_context)
        .join(Analysis, Analysis.post_id == Post.id)
        .filter((Analysis.is_political == True) | (Analysis.is_ai_slop == True))
        .filter(Post.feed_context.isnot(None))
        .filter(Post.feed_context != "direct")
        .all()
    )

    amplifier_counts: dict[str, int] = {}
    for (ctx,) in flagged_posts:
        if not ctx:
            continue
        # Extract the person's name from context like "John Smith likes this"
        for pattern in [" likes this", " loves this", " commented", " reposted this",
                        " celebrates this", " finds this insightful", " finds this funny",
                        " supports this"]:
            if pattern in ctx:
                name = ctx.split(pattern)[0].strip()
                # Handle "X, Y and Z like this" patterns
                if " and " in name:
                    names = name.replace(" and ", ", ").split(", ")
                    for n in names:
                        n = n.strip()
                        if n and len(n) > 1 and "connection" not in n.lower():
                            amplifier_counts[n] = amplifier_counts.get(n, 0) + 1
                else:
                    if name and len(name) > 1 and "connection" not in name.lower():
                        amplifier_counts[name] = amplifier_counts.get(name, 0) + 1
                break

    # Try to match amplifier names to known authors for profile URLs
    sorted_amplifiers = sorted(amplifier_counts.items(), key=lambda x: -x[1])[:20]
    results = []
    for name, count in sorted_amplifiers:
        # Look up by exact name match in our authors table
        author = db.query(Author).filter(Author.name == name).first()
        if author:
            url = author.linkedin_url
        else:
            # Fall back to LinkedIn search URL
            url = f"https://www.linkedin.com/search/results/all/?keywords={name.replace(' ', '%20')}"
        results.append({"name": name, "count": count, "url": url})

    return results
