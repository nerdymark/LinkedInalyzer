from datetime import datetime, timezone

from sqlalchemy import Boolean, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


def _utcnow():
    return datetime.now(timezone.utc)


class Author(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    linkedin_url: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    headline: Mapped[str | None] = mapped_column(String, nullable=True)
    political_post_count: Mapped[int] = mapped_column(Integer, default=0)
    avg_political_score: Mapped[float] = mapped_column(Float, default=0.0)
    ai_slop_post_count: Mapped[int] = mapped_column(Integer, default=0)
    avg_ai_slop_score: Mapped[float] = mapped_column(Float, default=0.0)
    review_status: Mapped[str] = mapped_column(String, default="pending")
    first_seen_at: Mapped[datetime] = mapped_column(default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=_utcnow, onupdate=_utcnow)

    posts: Mapped[list["Post"]] = relationship(back_populates="author")

    __table_args__ = (Index("ix_authors_review_status", "review_status"),)


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    linkedin_post_id: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    feed_context: Mapped[str | None] = mapped_column(String, nullable=True)  # Why this appeared: "suggested", "X likes this", etc.
    post_url: Mapped[str | None] = mapped_column(String, nullable=True)
    scraped_at: Mapped[datetime] = mapped_column(default=_utcnow)
    analyzed: Mapped[bool] = mapped_column(Boolean, default=False)

    author: Mapped["Author"] = relationship(back_populates="posts")
    analysis: Mapped["Analysis | None"] = relationship(back_populates="post", uselist=False)

    __table_args__ = (Index("ix_posts_analyzed", "analyzed"),)


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), unique=True, nullable=False)
    sentiment_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_political: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    political_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    political_topics: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array
    is_ai_slop: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    ai_slop_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    raw_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    analyzed_at: Mapped[datetime] = mapped_column(default=_utcnow)

    post: Mapped["Post"] = relationship(back_populates="analysis")

    __table_args__ = (Index("ix_analyses_is_political", "is_political"),)


class ScrapeSession(Base):
    __tablename__ = "scrape_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    started_at: Mapped[datetime] = mapped_column(default=_utcnow)
    ended_at: Mapped[datetime | None] = mapped_column(nullable=True)
    posts_scraped: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String, default="running")
