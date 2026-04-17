import json
import logging
import time

from sqlalchemy import func

from backend.database import get_session_factory, init_db
from backend.models import Analysis, Author, Post
from backend.analyzer.gemini import GeminiAnalyzer

logger = logging.getLogger(__name__)


def analyze_pending() -> int:
    """Analyze all unanalyzed posts. Returns count of posts analyzed."""
    init_db()
    Session = get_session_factory()
    session = Session()

    pending_posts = session.query(Post).filter_by(analyzed=False).all()
    if not pending_posts:
        logger.info("No unanalyzed posts found.")
        return 0

    logger.info("Found %d unanalyzed posts.", len(pending_posts))
    analyzer = GeminiAnalyzer()
    analyzed_count = 0

    for i, post in enumerate(pending_posts):
        logger.info("Analyzing post %d/%d (author: %s)...", i + 1, len(pending_posts), post.author.name)

        result = analyzer.analyze_post(post.content)
        if result is None:
            logger.warning("Analysis failed for post %d, skipping.", post.id)
            continue

        analysis = Analysis(
            post_id=post.id,
            sentiment_score=result.get("sentiment_score"),
            is_political=result.get("is_political"),
            political_confidence=result.get("political_score", result.get("political_confidence")),
            political_topics=json.dumps(result.get("political_topics", [])),
            is_ai_slop=result.get("is_ai_slop"),
            ai_slop_confidence=result.get("ai_slop_score", result.get("ai_slop_confidence")),
            raw_response=json.dumps(result),
        )
        session.add(analysis)
        post.analyzed = True
        analyzed_count += 1

        # Commit in batches of 10
        if analyzed_count % 10 == 0:
            session.commit()
            time.sleep(1)  # Brief pause between batches

    session.commit()

    # Update denormalized author scores
    _update_author_scores(session)

    session.close()
    logger.info("Analysis complete. Analyzed %d posts.", analyzed_count)
    return analyzed_count


def _update_author_scores(session):
    """Recalculate denormalized political and AI slop scores on authors."""
    logger.info("Updating author scores...")

    # Political scores
    political_results = (
        session.query(
            Post.author_id,
            func.count(Analysis.id).label("political_count"),
            func.avg(Analysis.political_confidence).label("avg_score"),
        )
        .join(Analysis, Analysis.post_id == Post.id)
        .filter(Analysis.is_political == True)
        .group_by(Post.author_id)
        .all()
    )

    for author_id, count, avg_score in political_results:
        session.query(Author).filter_by(id=author_id).update({
            "political_post_count": count,
            "avg_political_score": round(avg_score, 4) if avg_score else 0.0,
        })

    # AI slop scores
    slop_results = (
        session.query(
            Post.author_id,
            func.count(Analysis.id).label("slop_count"),
            func.avg(Analysis.ai_slop_confidence).label("avg_score"),
        )
        .join(Analysis, Analysis.post_id == Post.id)
        .filter(Analysis.is_ai_slop == True)
        .group_by(Post.author_id)
        .all()
    )

    for author_id, count, avg_score in slop_results:
        session.query(Author).filter_by(id=author_id).update({
            "ai_slop_post_count": count,
            "avg_ai_slop_score": round(avg_score, 4) if avg_score else 0.0,
        })

    session.commit()
    logger.info("Updated scores for %d political, %d AI slop authors.", len(political_results), len(slop_results))
