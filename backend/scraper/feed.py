import logging
import random
import time
from datetime import datetime, timezone

from playwright.sync_api import sync_playwright

from backend.config import load_config
from backend.database import get_session_factory, init_db
from backend.models import Author, Post, ScrapeSession
from backend.scraper import selectors
from backend.scraper.browser import (
    create_persistent_context,
    is_session_valid,
)

logger = logging.getLogger(__name__)


def _random_delay(base: float) -> float:
    return base + random.uniform(0.5, 1.5)


def _long_pause():
    pause = random.uniform(5.0, 10.0)
    logger.info("Taking a reading pause (%.1fs)...", pause)
    time.sleep(pause)


def scrape_feed() -> int:
    """Scrape LinkedIn feed and store posts in database. Returns number of posts scraped."""
    config = load_config()
    init_db()
    Session = get_session_factory()
    session = Session()

    scroll_delay = config.get("scroll_delay_seconds", 2)
    max_posts = config.get("max_posts_per_session", 100)

    # Track scrape session
    scrape_session = ScrapeSession()
    session.add(scrape_session)
    session.commit()

    seen_post_ids = set()
    posts_saved = 0
    empty_scroll_count = 0

    with sync_playwright() as pw:
        context = create_persistent_context(pw, headless=False)
        page = context.pages[0] if context.pages else context.new_page()

        logger.info("Navigating to LinkedIn feed...")
        page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded", timeout=60000)

        # Wait for the feed LazyColumn to appear
        try:
            page.wait_for_selector(selectors.FEED_CONTAINER, timeout=30000)
        except Exception:
            logger.error("Feed container not found. Check if LinkedIn layout changed.")
            context.close()
            scrape_session.status = "error"
            scrape_session.ended_at = datetime.now(timezone.utc)
            session.commit()
            session.close()
            return 0

        time.sleep(3)  # Let initial posts render

        if not is_session_valid(page):
            logger.error("Session invalid — redirected to login. Run 'linkedinalyzer login' first.")
            context.close()
            scrape_session.status = "error"
            scrape_session.ended_at = datetime.now(timezone.utc)
            session.commit()
            session.close()
            return 0

        logger.info("Starting feed scroll (max %d posts)...", max_posts)

        while posts_saved < max_posts and empty_scroll_count < 5:
            # Expand any truncated posts first
            try:
                expanded = page.evaluate(selectors.EXPAND_POSTS_JS)
                if expanded:
                    logger.debug("Expanded %d truncated posts", expanded)
                    time.sleep(0.5)
            except Exception:
                pass

            # Extract all visible posts via JS
            try:
                raw_posts = page.evaluate(selectors.EXTRACT_POSTS_JS)
            except Exception as e:
                logger.warning("Post extraction failed: %s", e)
                raw_posts = []

            new_posts_this_scroll = 0

            for data in raw_posts:
                if posts_saved >= max_posts:
                    break

                post_id = data.get("post_id", "")
                if post_id in seen_post_ids:
                    continue
                seen_post_ids.add(post_id)

                content = data.get("content", "").strip()
                author_name = data.get("author_name", "").strip()
                author_url = data.get("author_url", "").strip()

                if not content or not author_name:
                    continue

                # Upsert author
                author = session.query(Author).filter_by(linkedin_url=author_url).first()
                if not author:
                    author = Author(
                        linkedin_url=author_url,
                        name=author_name,
                        headline=data.get("author_headline", ""),
                    )
                    session.add(author)
                    session.flush()

                # Check for duplicate post by content similarity
                existing = session.query(Post).filter_by(linkedin_post_id=post_id).first()
                if not existing:
                    feed_context = data.get("feed_context", "")
                    post = Post(
                        linkedin_post_id=post_id,
                        author_id=author.id,
                        content=content,
                        feed_context=feed_context,
                    )
                    session.add(post)
                    posts_saved += 1
                    new_posts_this_scroll += 1
                    logger.info(
                        "Saved post %d/%d from %s", posts_saved, max_posts, author_name
                    )

            if new_posts_this_scroll == 0:
                empty_scroll_count += 1
                logger.info("No new posts found (attempt %d/5)", empty_scroll_count)
            else:
                empty_scroll_count = 0

            session.commit()

            # Periodic long pause to appear human
            if posts_saved > 0 and posts_saved % random.randint(10, 15) == 0:
                _long_pause()

            # Scroll down to load more posts — scroll past current items
            # Use scrollIntoView on the last LazyColumn child to ensure we get past visible items
            page.evaluate("""() => {
                const cols = document.querySelectorAll('[data-component-type="LazyColumn"]');
                let mainCol = null;
                let maxChildren = 0;
                for (const col of cols) {
                    if (col.children.length > maxChildren) {
                        maxChildren = col.children.length;
                        mainCol = col;
                    }
                }
                if (mainCol && mainCol.lastElementChild) {
                    mainCol.lastElementChild.scrollIntoView({ behavior: 'smooth', block: 'center' });
                } else {
                    window.scrollBy(0, window.innerHeight);
                }
            }""")
            time.sleep(_random_delay(scroll_delay))
            # Extra wait for LinkedIn to fetch and render new posts
            time.sleep(2)

        # Finalize
        scrape_session.posts_scraped = posts_saved
        scrape_session.status = "completed"
        scrape_session.ended_at = datetime.now(timezone.utc)
        session.commit()

        context.close()

    session.close()
    logger.info("Scraping complete. Saved %d posts.", posts_saved)
    return posts_saved
