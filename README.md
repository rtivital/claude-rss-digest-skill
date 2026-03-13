# RSS Learning Digest

A personal weekly dev digest powered by RSS feeds and Claude Code. Collects articles from 22+ sources, filters by keyword relevance, then uses a Claude Code skill to analyze and present a curated digest.

## Setup

```bash
pip3 install -r requirements.txt
```

## Usage

Run the `/digest` slash command in Claude Code. It will:
1. Collect articles from all enabled RSS feeds (last 7 days)
2. Pre-filter by keyword relevance
3. Fetch and analyze each remaining article
4. Present a curated digest based on your interest profile
5. Clear the database when done

You can also run collection manually:

```bash
./run_weekly.sh        # Last 7 days (default)
./run_weekly.sh 14     # Last 14 days
```

## Configuration

### Adding/removing feeds

Edit `sources.json`. Set `"enabled": false` to disable a feed without removing it.

### Changing your interests

Edit `topics.json` to adjust priority keywords, roles, and exclusions.
