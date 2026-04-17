# LinkedInalyzer

Analyze your LinkedIn feed for political content and AI-generated slop. Scrape posts from your feed, classify them using Google's Gemini AI, and review flagged connections through an interactive dashboard.

## Why?

After 20 years on LinkedIn, your network accumulates people who've moved on from professional posting to political commentary and AI-generated engagement bait. LinkedInalyzer helps you identify these connections so you can clean up your feed by unfollowing or disconnecting.

## Features

- **Feed Scraper** — Playwright-based scraper that scrolls through your LinkedIn feed, extracting posts, authors, and feed context (how each post reached you)
- **Gemini Analysis** — Each post is analyzed for political content and AI slop using Google Gemini 2.5 Flash with structured scoring
- **SQLite Storage** — All data persisted locally for historical tracking
- **Dashboard** — FastAPI + React dashboard with:
  - Filterable author list with political/slop scores and review status
  - Direct links to LinkedIn profiles for quick unfollowing
  - Feed context tracking (suggested, liked by connection, reposted, etc.)
- **Analytics** — Score distribution charts, feed context breakdown, scrape timeline, top offenders, and amplifier network (which connections spread flagged content)

## Architecture

```
LinkedInalyzer/
├── backend/
│   ├── scraper/        # Playwright feed scraper + LinkedIn selectors
│   ├── analyzer/       # Gemini API client + analysis pipeline
│   ├── api/            # FastAPI REST API + dashboard endpoints
│   ├── models.py       # SQLAlchemy ORM (Author, Post, Analysis)
│   ├── database.py     # SQLite engine + session management
│   └── config.py       # Config loader
├── frontend/           # React + TypeScript + Tailwind + Recharts
│   └── src/
│       ├── components/ # Dashboard, Charts, AuthorRow, etc.
│       ├── api/        # API client
│       └── hooks/      # React Query hooks
├── config.json         # Your API keys (gitignored)
├── config.json.example # Template
└── pyproject.toml      # Python project config
```

## Prerequisites

- Python 3.11+
- Node.js 18+
- A Google Gemini API key ([get one here](https://aistudio.google.com/apikey))
- A LinkedIn account

## Installation

### 1. Clone and setup

```bash
git clone https://github.com/nerdymark/LinkedInalyzer.git
cd LinkedInalyzer
```

### 2. Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -e .
```

### 3. Install Playwright browser

```bash
playwright install chromium
```

### 4. Configure API keys

```bash
cp config.json.example config.json
```

Edit `config.json` and add your Gemini API key:

```json
{
  "gemini_api_key": "YOUR_GEMINI_API_KEY_HERE",
  "database_path": "linkedinalyzer.db",
  "scroll_delay_seconds": 2,
  "max_posts_per_session": 100,
  "political_score_threshold": 0.6
}
```

### 5. Frontend dependencies

```bash
cd frontend
npm install
cd ..
```

## Usage

### First-time login

LinkedInalyzer uses a persistent Chromium browser profile to maintain your LinkedIn session. Log in once:

```bash
linkedinalyzer login
```

This opens a Chromium window. Log in to LinkedIn (including any 2FA), wait until you see your feed, then press Enter in the terminal. Your session is saved in `playwright/profile/` and persists across runs.

### Scrape your feed

```bash
linkedinalyzer scrape
```

This will:
1. Open the browser and navigate to your feed
2. Scroll through posts, extracting content and metadata
3. Analyze each post with Gemini for political content and AI slop
4. Store everything in the SQLite database

Options:
- `linkedinalyzer scrape --no-analyze` — Scrape only, skip analysis
- `linkedinalyzer analyze` — Analyze previously scraped posts that haven't been analyzed yet

### View the dashboard

Start the API server and frontend dev server:

```bash
# Terminal 1: API server
linkedinalyzer serve

# Terminal 2: Frontend
cd frontend && npm run dev
```

Open **http://localhost:5173** in your browser.

### Check stats from the CLI

```bash
linkedinalyzer stats
```

## Dashboard Guide

### Dashboard Tab

- **Stats bar** — Total authors, posts, political/slop counts, pending review
- **Author list** — Filterable by view (All Flagged / Political / AI Slop) and review status
- **Author rows** — Click to expand and see individual posts with analysis details
- **"Profile" link** — Opens the LinkedIn profile in a new tab so you can unfollow/disconnect
- **Status dropdown** — Track your review progress: Pending → Reviewed → Keep / Unfollowed / Disconnected
- **Top Offenders** — Sidebar widget ranking worst political and AI slop authors
- **Amplifiers** — Connections who liked/reposted/commented on flagged content (linked to their profiles)

### Analytics Tab

- **Score Distribution** — Histogram of political and AI slop scores across all posts
- **How Posts Reach You** — Donut chart of feed context (direct, liked by connection, suggested, promoted, etc.)
- **Scrape Timeline** — Stacked area chart showing post volume and quality over time (useful after multiple daily runs)

## Daily Maintenance

For best results, run the scraper daily to build up data over time:

```bash
# Quick daily scrape
source .venv/bin/activate
linkedinalyzer scrape
```

### Re-login if session expires

LinkedIn sessions typically last a few weeks. If the scraper reports an invalid session:

```bash
linkedinalyzer login
```

### Reset analysis

If you update the Gemini prompt or want to re-analyze all posts:

```bash
sqlite3 linkedinalyzer.db "DELETE FROM analyses; UPDATE posts SET analyzed = 0; UPDATE authors SET political_post_count = 0, avg_political_score = 0, ai_slop_post_count = 0, avg_ai_slop_score = 0;"
linkedinalyzer analyze
```

### Database backup

The database is a single SQLite file. Back it up anytime:

```bash
cp linkedinalyzer.db linkedinalyzer.db.backup
```

## Configuration

| Key | Default | Description |
|-----|---------|-------------|
| `gemini_api_key` | (required) | Google Gemini API key |
| `database_path` | `linkedinalyzer.db` | Path to SQLite database file |
| `scroll_delay_seconds` | `2` | Base delay between feed scrolls (seconds) |
| `max_posts_per_session` | `100` | Maximum posts to scrape per run |
| `political_score_threshold` | `0.6` | Score threshold for flagging political content |

## Scoring

### Political Score (0.0 - 1.0)

- **0.0** — Completely non-political (tech announcements, job posts)
- **0.3** — Mildly political (mentions policy in passing)
- **0.6** — Moderately political (advocates for political positions)
- **1.0** — Overtly political (partisan advocacy, culture war, election content)

Posts with `political_score >= 0.4` are flagged as political.

### AI Slop Score (0.0 - 1.0)

- **0.0** — Clearly human-written, original content
- **0.5** — Suspiciously generic but could be human
- **1.0** — Almost certainly AI-generated engagement bait

## Anti-Detection

The scraper uses several techniques to avoid LinkedIn detection:

- Persistent browser profile (not headless)
- Realistic viewport and user agent
- Random scroll delays with jitter
- Periodic longer "reading" pauses
- Configurable session limits

**Important:** LinkedIn's Terms of Service prohibit scraping. Use this tool responsibly and at your own risk. This is intended for personal feed management, not bulk data collection.

## Tech Stack

- **Backend:** Python 3.11+, Playwright, SQLAlchemy, FastAPI, Click
- **AI:** Google Gemini 2.5 Flash via `google-genai` SDK
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, TanStack Query, Recharts
- **Database:** SQLite

## License

MIT
