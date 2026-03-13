# Claude RSS digest skill

A personalized dev digest generator powered by RSS feeds and [Claude Code](https://docs.anthropic.com/en/docs/claude-code). Collects articles from 20+ sources, filters by keyword relevance, then uses Claude Code skills to analyze content and produce a curated Markdown digest tailored to your interests.

## How it works

```
sources.json          topics.json
    │                      │
    ▼                      ▼
collector.py ──► SQLite ◄── filter.py
                   │
                   ▼
           Claude Code /digest skill
                   │
                   ▼
         digest/weekly_dev_digest_YYYY-MM-DD.md
```

1. **Collect** — `collector.py` fetches RSS/Atom feeds defined in `sources.json` and stores articles in a local SQLite database. Feeds that fail 3+ times in a row are auto-disabled.
2. **Filter** — `filter.py` scores each article against keywords derived from `topics.json` and removes low-relevance ones before they reach Claude.
3. **Analyze** — The `/digest` Claude Code skill reads the surviving articles, fetches full content where needed, evaluates each against your interest profile, and writes a Markdown digest to `digest/`.

## Prerequisites

- Python 3.9+
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI installed and authenticated

## Setup

```bash
git clone <repo-url> && cd ai-learning-explorer
pip3 install -r requirements.txt
```

## Usage

Open Claude Code in the project directory and run:

```
/digest
```

This collects the last 7 days of articles by default. Pass a number to change the window:

```
/digest 14
```

The generated digest is saved to `digest/weekly_dev_digest_YYYY-MM-DD.md`.

### Discovering new sources

```
/explore
```

This searches for new RSS feeds matching your interests, validates them, and lets you pick which ones to add to `sources.json`.

### Running collection manually

You can run the Python scripts directly without Claude Code:

```bash
python3 collector.py --days 7    # Fetch articles from last 7 days
python3 filter.py                # Apply keyword filter
```

The articles are stored in `db/articles.db` (SQLite). You can query them directly:

```bash
sqlite3 -json db/articles.db "SELECT title, source, url FROM articles WHERE status = 'new';"
```

## Configuration

### Feeds — `sources.json`

Each source has a name, RSS feed URL, category, and enabled flag:

```json
{
  "name": "Simon Willison's Blog",
  "url": "https://simonwillison.net/atom/everything/",
  "category": "AI Tooling",
  "full_content_rss": true,
  "enabled": true
}
```

- Set `"enabled": false` to disable a feed without removing it.
- Set `"type": "newsletter"` for curated link roundups (e.g., JavaScript Weekly). The digest skill extracts individual items from these rather than treating them as single articles.
- Set `"full_content_rss": true` for feeds that include the full article text in their RSS entries. This skips the web fetch step.

### Interest profile — `topics.json`

Define your roles and topic priorities. Claude uses this to decide which articles make the cut:

```json
{
  "profile": {
    "roles": ["Frontend Engineer", "Node.js Backend Engineer"],
    "topics": {
      "high_priority": ["React", "TypeScript", "Node.js internals"],
      "medium_priority": ["Web performance", "Developer tooling"],
      "low_priority": ["Mobile development"],
      "exclude_if": ["Job listings", "Beginner tutorials"]
    }
  }
}
```

High-priority keywords are weighted 3x during the pre-filter step. Articles need a score of 3+ to pass through to Claude for analysis.

## Project structure

```
├── collector.py        # RSS feed fetcher
├── filter.py           # Keyword pre-filter
├── sources.json        # Feed definitions
├── topics.json         # Interest profile
├── requirements.txt    # Python dependencies
├── db/                 # SQLite database (gitignored)
├── digest/             # Generated digests
└── .claude/skills/     # Claude Code skill definitions
    ├── digest/         #   /digest — generate a curated digest
    └── explore/        #   /explore — discover new feed sources
```
