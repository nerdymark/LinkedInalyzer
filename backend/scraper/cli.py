import logging
import sys

import click

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)


@click.group()
def main():
    """LinkedInalyzer — Analyze your LinkedIn feed for political content."""
    pass


@main.command()
def login():
    """Open browser for manual LinkedIn login and save session."""
    from backend.scraper.browser import login_interactive

    login_interactive()


@main.command()
@click.option("--no-analyze", is_flag=True, help="Skip analysis after scraping")
def scrape(no_analyze):
    """Scrape LinkedIn feed for posts."""
    from backend.scraper.feed import scrape_feed

    count = scrape_feed()
    click.echo(f"Scraped {count} posts.")

    if not no_analyze and count > 0:
        click.echo("Running analysis on new posts...")
        from backend.analyzer.pipeline import analyze_pending

        analyzed = analyze_pending()
        click.echo(f"Analyzed {analyzed} posts.")


@main.command()
def analyze():
    """Analyze previously scraped posts that haven't been analyzed yet."""
    from backend.analyzer.pipeline import analyze_pending

    count = analyze_pending()
    click.echo(f"Analyzed {count} posts.")


@main.command()
def stats():
    """Show summary statistics."""
    from backend.database import get_session_factory, init_db

    init_db()
    Session = get_session_factory()
    session = Session()

    from backend.models import Analysis, Author, Post

    total_authors = session.query(Author).count()
    total_posts = session.query(Post).count()
    analyzed_posts = session.query(Post).filter_by(analyzed=True).count()
    political_posts = session.query(Analysis).filter_by(is_political=True).count()
    ai_slop_posts = session.query(Analysis).filter_by(is_ai_slop=True).count()

    pending = session.query(Author).filter_by(review_status="pending").filter(
        Author.political_post_count > 0
    ).count()

    click.echo(f"\n{'='*40}")
    click.echo("  LinkedInalyzer Stats")
    click.echo(f"{'='*40}")
    click.echo(f"  Authors tracked:    {total_authors}")
    click.echo(f"  Posts scraped:      {total_posts}")
    click.echo(f"  Posts analyzed:     {analyzed_posts}")
    click.echo(f"  Political posts:    {political_posts}")
    click.echo(f"  AI slop posts:      {ai_slop_posts}")
    click.echo(f"  Pending review:     {pending}")
    click.echo(f"{'='*40}\n")

    session.close()


@main.command()
def serve():
    """Start the dashboard API server."""
    import uvicorn

    from backend.api.app import create_app

    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
