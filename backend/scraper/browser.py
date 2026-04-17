import logging
from pathlib import Path

from playwright.sync_api import BrowserContext, Playwright, sync_playwright

logger = logging.getLogger(__name__)

# Persistent browser profile — survives between runs, keeps full session state
USER_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "playwright" / "profile"


def _ensure_profile_dir():
    USER_DATA_DIR.mkdir(parents=True, exist_ok=True)


def has_saved_session() -> bool:
    """Check if a persistent profile exists with any stored data."""
    return USER_DATA_DIR.exists() and any(USER_DATA_DIR.iterdir())


def create_persistent_context(pw: Playwright, headless: bool = False) -> BrowserContext:
    """Create a persistent browser context that keeps cookies/session across runs."""
    _ensure_profile_dir()
    logger.info("Using persistent browser profile at %s", USER_DATA_DIR)
    context = pw.chromium.launch_persistent_context(
        user_data_dir=str(USER_DATA_DIR),
        headless=headless,
        slow_mo=50,
        viewport={"width": 1280, "height": 800},
        user_agent=(
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ),
    )
    return context


def login_interactive():
    """Open a browser for manual LinkedIn login using persistent profile."""
    _ensure_profile_dir()
    with sync_playwright() as pw:
        context = create_persistent_context(pw, headless=False)
        # Persistent context always has at least one page
        page = context.pages[0] if context.pages else context.new_page()
        page.goto("https://www.linkedin.com/login")
        print("\n=== LinkedIn Login ===")
        print("Please log in to LinkedIn in the browser window.")
        print("Once you see your feed, press Enter here to save the session...")
        input()
        # No need to explicitly save — persistent context stores everything automatically
        print("Session saved in persistent profile!")
        context.close()


def is_session_valid(page) -> bool:
    """Check if the current page indicates a valid session (not redirected to login)."""
    url = page.url
    return "login" not in url and "checkpoint" not in url and "guest" not in page.evaluate("document.querySelector('meta[data-page-instance]')?.content || ''")
